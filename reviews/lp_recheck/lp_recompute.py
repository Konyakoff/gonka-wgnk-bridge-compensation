#!/usr/bin/env python3
"""Independent recomputation of the LP part of the WGNK bridge-hack compensation model.

Own implementation: reads Ethereum state at historical blocks through public archive JSON-RPC
endpoints (no API keys), discovers pools/positions from chain logs, applies Uniswap v3/v4
concentrated-liquidity math, and only at the very end compares with the project's output files.

Run (inside the project's docker image, see REPORT.md):
    python /work/lp_recompute.py fetch     # chain discovery + state reads only (cached in /work/cache/rpc_cache.sqlite)
    python /work/lp_recompute.py verify    # re-read every cached eth_call on a second provider; re-pull the logs from a second provider
    python /work/lp_recompute.py compute   # math, comparison with the project, blind-spot checks -> /work/lp_recompute.json
    python /work/lp_recompute.py           # all of the above
Every network answer is cached, so a re-run with the cache present makes no requests.
"""
import sys, os, json, time, sqlite3, hashlib, random
import requests
from Crypto.Hash import keccak as _keccak

WORK = os.environ.get('LP_WORK', '/work')
RESEARCH = os.environ.get('LP_RESEARCH', '/research')
CACHE_DIR = os.path.join(WORK, 'cache')

# ----------------------------------------------------------------------------- constants
WGNK = '0x972a7a92d92796a98801a8818bcf91f1648f2f68'
USDT = '0xdac17f958d2ee523a2206206994597c13d831ec7'
USDC = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
ETH0 = '0x' + '00' * 20
POOL_03 = '0x203ee836d417cf944133bbdd2c62b4bc7388c55d'
POOL_1 = '0xdbc0edbced03c87a7f287f9949e01c012511f117'
V3_POOLS = [POOL_03, POOL_1]
NPM = '0xc36442b4a4522e871399cd717abdd847ab11fe88'
PM = '0x000000000004444c5dc75cb358380d2e3de08a90'      # v4 PoolManager
POSM = '0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e'    # v4 PositionManager
STATEVIEW = '0x7ffe42c4a5deea5b0fec41c94c136cf115597227'
CHAINLINK_ETH_USD = '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'
SNAP, T1, END = 26443612, 26445519, 26475449
BLOCKS = {'snap': SNAP, 't1': T1, 'end': END}
FROM_BLOCK = 25190000     # before the first WGNK transfer (25,196,134)
P0 = 0.1428805
SEED = 20261118
TOKENS = {WGNK: ('WGNK', 9), USDT: ('USDT', 6), USDC: ('USDC', 6), WETH: ('WETH', 18), ETH0: ('ETH', 18)}

STATE_EPS = ['https://gateway.tenderly.co/public/mainnet', 'https://eth.drpc.org',
             'https://eth-mainnet.public.blastapi.io', 'https://rpc.mevblocker.io']
LOG_EPS = ['https://gateway.tenderly.co/public/mainnet']
MIN_INTERVAL = 0.36       # <= 3 requests / second over all providers together

Q96, Q128, U256 = 1 << 96, 1 << 128, 1 << 256


def keccak(b: bytes) -> bytes:
    h = _keccak.new(digest_bits=256)
    h.update(b)
    return h.digest()


def sel(sig): return '0x' + keccak(sig.encode())[:4].hex()
def topic(sig): return '0x' + keccak(sig.encode()).hex()


def w_uint(x): return format(x % U256, '064x')
def w_int(x): return format(x % U256, '064x')
def w_addr(a): return a[2:].lower().rjust(64, '0')
def w_b32(h): return h[2:].lower().rjust(64, '0')
def words(hexs):
    h = hexs[2:] if hexs.startswith('0x') else hexs
    return [h[i:i + 64] for i in range(0, len(h), 64)]
def u(wd): return int(wd, 16)
def s(wd, bits=256):
    v = int(wd, 16) & ((1 << bits) - 1)
    return v - (1 << bits) if v >> (bits - 1) else v
def addr(wd): return '0x' + wd[-40:]


# ----------------------------------------------------------------------------- RPC with cache
class RPC:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.db = sqlite3.connect(os.path.join(CACHE_DIR, 'rpc_cache.sqlite'), timeout=120)
        self.db.execute('create table if not exists kv(k text primary key, method text, params text, v text, ep text)')
        self.db.execute('create table if not exists ver(k text primary key, ep2 text, v2 text, ok int)')
        self.last = 0.0
        self.n_net = 0
        self.rr = 0
        self.sess = requests.Session()

    def _raw(self, ep, method, params):
        dt = time.time() - self.last
        if dt < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - dt)
        self.last = time.time()
        self.n_net += 1
        r = self.sess.post(ep, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=60,
                           headers={'Content-Type': 'application/json', 'User-Agent': 'lp-recheck/1.0'})
        j = r.json()
        if 'error' in j and j['error']:
            msg = json.dumps(j['error'])[:300]
            if 'revert' in msg.lower():
                return {'__revert__': msg}
            raise RuntimeError(f'rpc error {msg}')
        if 'result' not in j:
            raise RuntimeError(f'bad response {str(j)[:200]}')
        return j['result']

    def _try(self, eps, method, params, start=0):
        err = None
        for attempt in range(8):
            ep = eps[(start + attempt) % len(eps)]
            try:
                return self._raw(ep, method, params), ep
            except Exception as e:  # noqa
                err = e
                time.sleep(min(20, 1.5 * (attempt + 1)))
        raise RuntimeError(f'all endpoints failed for {method}: {err}')

    def call(self, method, params, eps=None, trim=None, tag=None):
        key = hashlib.sha256(json.dumps([method, params] + ([tag] if tag else []), sort_keys=True).encode()).hexdigest()
        row = self.db.execute('select v from kv where k=?', (key,)).fetchone()
        if row:
            return json.loads(row[0])
        eps = eps or STATE_EPS
        self.rr += 1
        res, ep = self._try(eps, method, params, start=self.rr)
        if trim:
            res = trim(res)
        self.db.execute('insert or replace into kv values(?,?,?,?,?)', (key, method, json.dumps(params), json.dumps(res), ep))
        if self.n_net % 25 == 0 or method != 'eth_call':
            self.db.commit()
        return res

    def eth_call(self, to, data, block):
        res = self.call('eth_call', [{'to': to, 'data': data}, hex(block)])
        if isinstance(res, dict) and '__revert__' in res:
            return None
        return words(res)

    def get_logs(self, address, topics, frm, to):
        return self.call('eth_getLogs', [{'address': address, 'topics': topics, 'fromBlock': hex(frm), 'toBlock': hex(to)}], eps=LOG_EPS)

    def receipt(self, txh):
        def trim(r):
            return {'status': r['status'], 'blockNumber': r['blockNumber'], 'from': r['from'], 'to': r['to'],
                    'logs': [{'address': l['address'].lower(), 'topics': l['topics'], 'data': l['data'], 'logIndex': l['logIndex']} for l in r['logs']]}
        return self.call('eth_getTransactionReceipt', [txh], trim=trim)

    def verify_all(self, limit=None, where=''):
        """Re-read cached eth_call results on a different provider and compare."""
        rows = self.db.execute("select k, params, v, ep from kv where method='eth_call' and k not in (select k from ver) " + where).fetchall()
        if limit:
            rows = rows[:limit]
        bad = 0
        for i, (k, params, v, ep) in enumerate(rows):
            others = [e for e in STATE_EPS if e != ep]
            try:
                res, ep2 = self._try(others, 'eth_call', json.loads(params), start=i)
            except Exception as e:  # noqa
                print('verify failed to fetch', k, e)
                continue
            ok = int(json.dumps(res) == v) if not (isinstance(res, dict) and '__revert__' in res) else int('__revert__' in v)
            bad += 1 - ok
            self.db.execute('insert or replace into ver values(?,?,?,?)', (k, ep2, json.dumps(res), ok))
            if i % 25 == 0:
                self.db.commit()
                print(f'verify {i}/{len(rows)} bad={bad}', flush=True)
        self.db.commit()
        return len(rows), bad

    def commit(self):
        self.db.commit()


# ----------------------------------------------------------------------------- Uniswap math (own implementation)
_TICK_CONST = [
    (0x1, 0xfffcb933bd6fad37aa2d162d1a594001), (0x2, 0xfff97272373d413259a46990580e213a),
    (0x4, 0xfff2e50f5f656932ef12357cf3c7fdcc), (0x8, 0xffe5caca7e10e4e61c3624eaa0941cd0),
    (0x10, 0xffcb9843d60f6159c9db58835c926644), (0x20, 0xff973b41fa98c081472e6896dfb254c0),
    (0x40, 0xff2ea16466c96a3843ec78b326b52861), (0x80, 0xfe5dee046a99a2a811c461f1969c3053),
    (0x100, 0xfcbe86c7900a88aedcffc83b479aa3a4), (0x200, 0xf987a7253ac413176f2b074cf7815e54),
    (0x400, 0xf3392b0822b70005940c7a398e4b70f3), (0x800, 0xe7159475a2c29b7443b29c7fa6e889d9),
    (0x1000, 0xd097f3bdfd2022b8845ad8f792aa5825), (0x2000, 0xa9f746462d870fdf8a65dc1f90e061e5),
    (0x4000, 0x70d869a156d2a1b890bb3df62baf32f7), (0x8000, 0x31be135f97d08fd981231505542fcfa6),
    (0x10000, 0x9aa508b5b7a84e1c677de54f3e99bc9), (0x20000, 0x5d6af8dedb81196699c329225ee604),
    (0x40000, 0x2216e584f5fa1ea926041bedfe98), (0x80000, 0x48a170391f7dc42444e8fa2)]


def sqrt_ratio_at_tick(tick: int) -> int:
    a = abs(tick)
    assert a <= 887272
    ratio = 1 << 128
    for bit, c in _TICK_CONST:
        if a & bit:
            ratio = (ratio * c) >> 128
    if tick > 0:
        ratio = (U256 - 1) // ratio
    return (ratio >> 32) + (1 if ratio % (1 << 32) else 0)


def _selftest_tickmath():
    from decimal import Decimal, getcontext
    getcontext().prec = 60
    assert sqrt_ratio_at_tick(0) == Q96
    assert sqrt_ratio_at_tick(-887272) == 4295128739
    assert sqrt_ratio_at_tick(887272) == 1461446703485210103287273052203988822378723970342
    base = Decimal('1.0001').sqrt()
    for t in [1 << i for i in range(20) if (1 << i) <= 887272] + [-88551, -106241, -112833, 887220, -887200, 60, -200]:
        for sg in (1, -1):
            tt = t * sg
            if abs(tt) > 887272:
                continue
            exact = (base ** tt) * Decimal(Q96)
            got = Decimal(sqrt_ratio_at_tick(tt))
            assert abs(got / exact - 1) < Decimal('1e-18') or abs(got - exact) < 2, (tt, got, exact)


def amounts_for_liquidity(L: int, sqrtP: int, tl: int, tu: int):
    """Token amounts a burn of L would return (rounded down), v3/v4 formulas."""
    sa, sb = sqrt_ratio_at_tick(tl), sqrt_ratio_at_tick(tu)
    if L == 0:
        return 0, 0

    def amt0(x, y):  # x < y
        return (L << 96) * (y - x) // y // x

    def amt1(x, y):
        return L * (y - x) // Q96
    if sqrtP <= sa:
        return amt0(sa, sb), 0
    if sqrtP < sb:
        return amt0(sqrtP, sb), amt1(sa, sqrtP)
    return 0, amt1(sa, sb)


def fee_growth_inside(tick_cur, tl, tu, g0, g1, lo, up):
    """lo/up = (feeGrowthOutside0X128, feeGrowthOutside1X128) of the lower/upper tick."""
    out = []
    for i, g in enumerate((g0, g1)):
        below = lo[i] if tick_cur >= tl else (g - lo[i]) % U256
        above = up[i] if tick_cur < tu else (g - up[i]) % U256
        out.append((g - below - above) % U256)
    return out


def fees_owed(L, inside, last):
    return L * ((inside - last) % U256) // Q128


# ----------------------------------------------------------------------------- selectors / topics
S = {n: sel(sig) for n, sig in {
    'slot0': 'slot0()', 'liquidity': 'liquidity()', 'fg0': 'feeGrowthGlobal0X128()', 'fg1': 'feeGrowthGlobal1X128()',
    'protocolFees': 'protocolFees()', 'pool_positions': 'positions(bytes32)', 'ticks': 'ticks(int24)',
    'balanceOf': 'balanceOf(address)', 'npm_positions': 'positions(uint256)', 'ownerOf': 'ownerOf(uint256)',
    'token0': 'token0()', 'token1': 'token1()', 'fee': 'fee()',
    'sv_slot0': 'getSlot0(bytes32)', 'sv_liq': 'getLiquidity(bytes32)', 'sv_fgg': 'getFeeGrowthGlobals(bytes32)',
    'sv_pos': 'getPositionInfo(bytes32,address,int24,int24,bytes32)', 'sv_fgi': 'getFeeGrowthInside(bytes32,int24,int24)',
    'sv_tick': 'getTickInfo(bytes32,int24)',
    'pm_protofees': 'protocolFeesAccrued(address)', 'latestAnswer': 'latestAnswer()',
    'posm_liq': 'getPositionLiquidity(uint256)',
}.items()}
T = {n: topic(sig) for n, sig in {
    'Mint': 'Mint(address,address,int24,int24,uint128,uint256,uint256)',
    'Burn': 'Burn(address,int24,int24,uint128,uint256,uint256)',
    'Collect': 'Collect(address,address,int24,int24,uint128,uint128)',
    'CollectProtocol': 'CollectProtocol(address,address,uint128,uint128)',
    'IncreaseLiquidity': 'IncreaseLiquidity(uint256,uint128,uint256,uint256)',
    'DecreaseLiquidity': 'DecreaseLiquidity(uint256,uint128,uint256,uint256)',
    'NpmCollect': 'Collect(uint256,address,uint256,uint256)',
    'Transfer': 'Transfer(address,address,uint256)',
    'Initialize4': 'Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)',
    'ModifyLiquidity4': 'ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32)',
    'Transfer6909': 'Transfer(address,address,address,uint256,uint256)',
}.items()}


def v3_key(owner, tl, tu):
    return '0x' + keccak(bytes.fromhex(owner[2:]) + (tl % (1 << 24)).to_bytes(3, 'big') + (tu % (1 << 24)).to_bytes(3, 'big')).hex()


# ----------------------------------------------------------------------------- discovery from chain logs
def discover(rpc):
    out = {'v3_events': [], 'npm_tokens': {}, 'v4_pools': [], 'v4_events': []}
    for pool in V3_POOLS:
        for ev in ('Mint', 'Burn', 'Collect', 'CollectProtocol'):
            logs = rpc.get_logs(pool, [T[ev]], FROM_BLOCK, END)
            for l in logs:
                tp, d = l['topics'], words(l['data'])
                e = {'ev': ev, 'pool': pool, 'block': int(l['blockNumber'], 16), 'tx': l['transactionHash'], 'li': int(l['logIndex'], 16)}
                if ev == 'Mint':
                    e.update(owner=addr(tp[1]), tl=s(tp[2][2:], 24), tu=s(tp[3][2:], 24), sender=addr(d[0]), L=u(d[1]), a0=u(d[2]), a1=u(d[3]))
                elif ev == 'Burn':
                    e.update(owner=addr(tp[1]), tl=s(tp[2][2:], 24), tu=s(tp[3][2:], 24), L=u(d[0]), a0=u(d[1]), a1=u(d[2]))
                elif ev == 'Collect':
                    e.update(owner=addr(tp[1]), tl=s(tp[2][2:], 24), tu=s(tp[3][2:], 24), recipient=addr(d[0]), a0=u(d[1]), a1=u(d[2]))
                else:
                    e.update(a0=u(d[0]), a1=u(d[1]))
                out['v3_events'].append(e)
    # NPM token ids: every pool Mint with owner == NPM is followed in the same tx by NPM.IncreaseLiquidity(tokenId)
    for e in out['v3_events']:
        if e['ev'] == 'Mint' and e['owner'] == NPM:
            rc = rpc.receipt(e['tx'])
            cands = [l for l in rc['logs'] if l['address'] == NPM and l['topics'][0] == T['IncreaseLiquidity'] and int(l['logIndex'], 16) > e['li']]
            cands.sort(key=lambda l: int(l['logIndex'], 16))
            hit = None
            for l in cands:
                d = words(l['data'])
                if u(d[0]) == e['L'] and u(d[1]) == e['a0'] and u(d[2]) == e['a1']:
                    hit = l
                    break
            if hit is None:
                e['token_id'] = None
                continue
            tid = u(hit['topics'][1][2:])
            e['token_id'] = tid
            t = out['npm_tokens'].setdefault(str(tid), {'pool': e['pool'], 'tl': e['tl'], 'tu': e['tu'], 'first_block': e['block']})
            assert (t['pool'], t['tl'], t['tu']) == (e['pool'], e['tl'], e['tu'])
    # v4 pools containing WGNK
    for pos_idx in (2, 3):
        topics = [T['Initialize4'], None, None, None]
        topics[pos_idx] = '0x' + w_addr(WGNK)
        for l in rpc.get_logs(PM, topics, FROM_BLOCK, END):
            tp, d = l['topics'], words(l['data'])
            out['v4_pools'].append({'id': tp[1], 'c0': addr(tp[2]), 'c1': addr(tp[3]), 'fee': u(d[0]), 'spacing': s(d[1], 24),
                                    'hooks': addr(d[2]), 'init_sqrt': u(d[3]), 'init_tick': s(d[4], 24), 'block': int(l['blockNumber'], 16)})
    ids = [p['id'] for p in out['v4_pools']]
    for l in rpc.get_logs(PM, [T['ModifyLiquidity4'], ids], FROM_BLOCK, END):
        tp, d = l['topics'], words(l['data'])
        out['v4_events'].append({'id': tp[1], 'sender': addr(tp[2]), 'tl': s(d[0], 24), 'tu': s(d[1], 24), 'dL': s(d[2]), 'salt': '0x' + d[3],
                                 'block': int(l['blockNumber'], 16), 'tx': l['transactionHash'], 'li': int(l['logIndex'], 16)})
    # ERC-6909 claims on WGNK inside the PoolManager (would be part of its WGNK balance)
    out['pm_6909_wgnk'] = [{'from': addr(l['topics'][1]), 'to': addr(l['topics'][2]), 'amount': u(words(l['data'])[1]), 'block': int(l['blockNumber'], 16)}
                           for l in rpc.get_logs(PM, [T['Transfer6909'], None, None, '0x' + w_addr(WGNK)], FROM_BLOCK, END)]
    rpc.commit()
    return out


# ----------------------------------------------------------------------------- state reads
def read_state(rpc, disc):
    st = {}
    for name, blk in BLOCKS.items():
        b = {'v3': {}, 'npm': {}, 'v4': {}, 'misc': {}}
        # --- v3 pools
        for pool in V3_POOLS:
            w = rpc.eth_call(pool, S['slot0'], blk)
            p = {'sqrtP': u(w[0]), 'tick': s(w[1], 24), 'feeProtocol': u(w[5]),
                 'L': u(rpc.eth_call(pool, S['liquidity'], blk)[0]),
                 'fg0': u(rpc.eth_call(pool, S['fg0'], blk)[0]), 'fg1': u(rpc.eth_call(pool, S['fg1'], blk)[0])}
            w = rpc.eth_call(pool, S['protocolFees'], blk)
            p['protoFees'] = [u(w[0]), u(w[1])]
            p['bal0'] = u(rpc.eth_call(WGNK, S['balanceOf'] + w_addr(pool), blk)[0])
            p['bal1'] = u(rpc.eth_call(USDT, S['balanceOf'] + w_addr(pool), blk)[0])
            keys = sorted({(e['owner'], e['tl'], e['tu']) for e in disc['v3_events'] if e['ev'] == 'Mint' and e['pool'] == pool and e['block'] <= blk})
            p['positions'] = {}
            ticks_needed = set()
            for owner, tl, tu in keys:
                w = rpc.eth_call(pool, S['pool_positions'] + v3_key(owner, tl, tu)[2:], blk)
                rec = {'L': u(w[0]), 'last0': u(w[1]), 'last1': u(w[2]), 'owed0': u(w[3]), 'owed1': u(w[4])}
                p['positions'][f'{owner}:{tl}:{tu}'] = rec
                if rec['L'] > 0:
                    ticks_needed.update((tl, tu))
            p['ticks'] = {}
            for t in sorted(ticks_needed):
                w = rpc.eth_call(pool, S['ticks'] + w_int(t), blk)
                p['ticks'][str(t)] = {'gross': u(w[0]), 'net': s(w[1], 128), 'o0': u(w[2]), 'o1': u(w[3]), 'init': u(w[7])}
            b['v3'][pool] = p
        # --- NPM tokens
        for tid, meta in disc['npm_tokens'].items():
            if meta['first_block'] > blk:
                continue
            own = rpc.eth_call(NPM, S['ownerOf'] + w_uint(int(tid)), blk)
            w = rpc.eth_call(NPM, S['npm_positions'] + w_uint(int(tid)), blk)
            rec = {'owner': addr(own[0]) if own else None}
            if w:
                rec.update(token0=addr(w[2]), token1=addr(w[3]), fee=u(w[4]), tl=s(w[5], 24), tu=s(w[6], 24), L=u(w[7]),
                           last0=u(w[8]), last1=u(w[9]), owed0=u(w[10]), owed1=u(w[11]))
            b['npm'][tid] = rec
        # --- v4
        for pool in disc['v4_pools']:
            if pool['block'] > blk:
                continue
            pid = pool['id']
            w = rpc.eth_call(STATEVIEW, S['sv_slot0'] + pid[2:], blk)
            p = {'sqrtP': u(w[0]), 'tick': s(w[1], 24), 'protocolFee': u(w[2]), 'lpFee': u(w[3]),
                 'L': u(rpc.eth_call(STATEVIEW, S['sv_liq'] + pid[2:], blk)[0])}
            w = rpc.eth_call(STATEVIEW, S['sv_fgg'] + pid[2:], blk)
            p['fg0'], p['fg1'] = u(w[0]), u(w[1])
            keys = sorted({(e['sender'], e['tl'], e['tu'], e['salt']) for e in disc['v4_events'] if e['id'] == pid and e['block'] <= blk})
            p['positions'] = {}
            for owner, tl, tu, salt in keys:
                w = rpc.eth_call(STATEVIEW, S['sv_pos'] + pid[2:] + w_addr(owner) + w_int(tl) + w_int(tu) + salt[2:], blk)
                rec = {'L': u(w[0]), 'last0': u(w[1]), 'last1': u(w[2])}
                if rec['L'] > 0:
                    w = rpc.eth_call(STATEVIEW, S['sv_fgi'] + pid[2:] + w_int(tl) + w_int(tu), blk)
                    rec['in0'], rec['in1'] = u(w[0]), u(w[1])
                if owner == POSM:
                    own = rpc.eth_call(POSM, S['ownerOf'] + salt[2:], blk)
                    rec['nft_owner'] = addr(own[0]) if own else None
                p['positions'][f'{owner}:{tl}:{tu}:{salt}'] = rec
            b['v4'][pid] = p
        b['misc']['pm_wgnk'] = u(rpc.eth_call(WGNK, S['balanceOf'] + w_addr(PM), blk)[0])
        b['misc']['pm_protofees_wgnk'] = u(rpc.eth_call(PM, S['pm_protofees'] + w_addr(WGNK), blk)[0])
        b['misc']['eth_usd'] = u(rpc.eth_call(CHAINLINK_ETH_USD, S['latestAnswer'], blk)[0]) / 1e8
        st[name] = b
        rpc.commit()
        print('state read', name, 'net requests so far', rpc.n_net, flush=True)
    return st


# ============================================================================= cross-checks that need extra chain reads
SECOND_LOG_EP = ['https://rpc.mevblocker.io']


def verify_logs(rpc, disc):
    """Event discovery (one provider, one big range) vs a second provider (10,000-block chunks)."""
    ids = [p['id'] for p in disc['v4_pools']]
    got_v3, got_v4, got_init = set(), set(), set()
    blk = FROM_BLOCK
    while blk <= END:
        to = min(blk + 9999, END)
        for l in rpc.call('eth_getLogs', [{'address': V3_POOLS, 'topics': [[T['Mint'], T['Burn'], T['Collect'], T['CollectProtocol']]],
                                           'fromBlock': hex(blk), 'toBlock': hex(to)}], eps=SECOND_LOG_EP):
            got_v3.add((l['transactionHash'], int(l['logIndex'], 16)))
        for l in rpc.call('eth_getLogs', [{'address': PM, 'topics': [T['ModifyLiquidity4'], ids], 'fromBlock': hex(blk), 'toBlock': hex(to)}], eps=SECOND_LOG_EP):
            got_v4.add((l['transactionHash'], int(l['logIndex'], 16)))
        for idx in (2, 3):
            tp = [T['Initialize4'], None, None, None]
            tp[idx] = '0x' + w_addr(WGNK)
            for l in rpc.call('eth_getLogs', [{'address': PM, 'topics': tp, 'fromBlock': hex(blk), 'toBlock': hex(to)}], eps=SECOND_LOG_EP):
                got_init.add(l['topics'][1])
        blk = to + 1
    rpc.commit()
    mine_v3 = {(e['tx'], e['li']) for e in disc['v3_events']}
    mine_v4 = {(e['tx'], e['li']) for e in disc['v4_events']}
    return {'first_provider': LOG_EPS[0], 'second_provider': SECOND_LOG_EP[0], 'block_range': [FROM_BLOCK, END],
            'v3_pool_events': {'first': len(mine_v3), 'second': len(got_v3), 'symmetric_difference': len(mine_v3 ^ got_v3)},
            'v4_modify_liquidity': {'first': len(mine_v4), 'second': len(got_v4), 'symmetric_difference': len(mine_v4 ^ got_v4)},
            'v4_pools_with_wgnk': {'first': len(ids), 'second': len(got_init), 'symmetric_difference': len(set(ids) ^ got_init)}}


def code_kind(rpc, a, blk=END):
    c = rpc.call('eth_getCode', [a, hex(blk)])
    if c in ('0x', '0x0'):
        return 'EOA'
    if c.startswith('0xef0100'):
        return 'EIP-7702 delegated EOA -> 0x' + c[8:48]
    return f'contract ({(len(c) - 2) // 2} bytes)'


def extra_chain_checks(rpc, disc):
    """WGNK supply / balances from the raw transfer file vs chain; other venues; residual of the v3 reconciliation."""
    import pandas as pd
    from collections import defaultdict
    tr = pd.read_parquet(f'{RESEARCH}/raw/eth/wgnk_transfers.parquet')
    res = {'supply': {}}
    snap_bal = None
    for name, blk in BLOCKS.items():
        bal = defaultdict(int)
        t = tr[tr.block_number <= blk]
        for f, to_, v in zip(t.from_addr, t.to_addr, t.value_raw):
            bal[f] -= int(v); bal[to_] += int(v)
        supply = -bal.pop(ETH0)
        res['supply'][name] = {'from_transfer_file': supply / 1e9, 'totalSupply_on_chain': u(rpc.eth_call(WGNK, sel('totalSupply()'), blk)[0]) / 1e9}
        if name == 'snap':
            snap_bal = dict(bal)
            res['pool_wgnk_balance_transfers_vs_chain_at_snapshot'] = {
                a: {'transfer_file': bal[a] / 1e9, 'chain': u(rpc.eth_call(WGNK, S['balanceOf'] + w_addr(a), blk)[0]) / 1e9} for a in V3_POOLS + [PM]}
    big = sorted([(a, b) for a, b in snap_bal.items() if b >= 500 * 10 ** 9], key=lambda x: -x[1])
    holders = [{'address': a, 'wgnk_at_snapshot': b / 1e9, 'kind': code_kind(rpc, a, SNAP)} for a, b in big]
    res['holders_ge_500_wgnk_at_snapshot'] = {'n': len(holders), 'n_eoa': sum(h['kind'] == 'EOA' for h in holders),
                                              'n_eip7702': sum('7702' in h['kind'] for h in holders),
                                              'contracts': [h for h in holders if h['kind'].startswith('contract')]}
    V3F, V2F, SUSHI = '0x1f98431c8ad98523631ae4a59f267346ea31f984', '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f', '0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac'
    DAI = '0x6b175474e89094c44da98b954eedeac495271d0f'
    pools = []
    for q, qn in ((USDT, 'USDT'), (USDC, 'USDC'), (WETH, 'WETH'), (DAI, 'DAI')):
        cands = [('univ3 fee %d' % fee, addr(rpc.eth_call(V3F, sel('getPool(address,address,uint24)') + w_addr(WGNK) + w_addr(q) + w_uint(fee), END)[0])) for fee in (100, 500, 3000, 10000)]
        cands += [(fn, addr(rpc.eth_call(fac, sel('getPair(address,address)') + w_addr(WGNK) + w_addr(q), END)[0])) for fac, fn in ((V2F, 'univ2'), (SUSHI, 'sushi'))]
        for venue, p in cands:
            if p == ETH0:
                continue
            t = tr[(tr.to_addr == p) | (tr.from_addr == p)]
            sg = [int(v) if to_ == p else -int(v) for v, to_ in zip(t.value_raw, t.to_addr)]
            pools.append({'venue': venue, 'quote': qn, 'pool': p, 'tracked_by_project': p in V3_POOLS,
                          'wgnk_at_snapshot': sum(x for x, b in zip(sg, t.block_number) if b <= SNAP) / 1e9,
                          'wgnk_at_end': sum(sg) / 1e9, 'wgnk_transfers_after_snapshot': int((t.block_number > SNAP).sum())})
    res['other_pools_checked'] = pools
    # per-transaction difference between WGNK actually moved into/out of each v3 pool and the amounts in the pool's own events
    SWAP = topic('Swap(address,address,int256,int256,uint160,uint128,int24)')
    FLASH = topic('Flash(address,address,uint256,uint256,uint256,uint256)')
    resid = {}
    for pool in V3_POOLS:
        exp, nsw, blk = defaultdict(int), 0, FROM_BLOCK
        while blk <= END:
            to = min(blk + 199999, END)
            for l in rpc.get_logs(pool, [[SWAP, FLASH]], blk, to):
                d = words(l['data'])
                if l['topics'][0] == SWAP:
                    exp[l['transactionHash']] += s(d[0]); nsw += 1
                else:
                    exp[l['transactionHash']] += u(d[2])
            blk = to + 1
        for e in disc['v3_events']:
            if e['pool'] == pool and e['ev'] == 'Mint':
                exp[e['tx']] += e['a0']
            elif e['pool'] == pool and e['ev'] in ('Collect', 'CollectProtocol'):
                exp[e['tx']] -= e['a0']
        act, blkof = defaultdict(int), {}
        t = tr[(tr.to_addr == pool) | (tr.from_addr == pool)]
        for h, to_, v, b in zip(t.tx_hash, t.to_addr, t.value_raw, t.block_number):
            act[h] += int(v) if to_ == pool else -int(v)
            blkof[h] = int(b)
        rows = [{'tx': h, 'block': blkof.get(h), 'actual_minus_events_wgnk': (act.get(h, 0) - exp.get(h, 0)) / 1e9}
                for h in set(exp) | set(act) if act.get(h, 0) != exp.get(h, 0)]
        resid[pool] = {'n_swaps': nsw, 'n_tx_with_difference': len(rows),
                       'sum_until_snapshot': sum(r['actual_minus_events_wgnk'] for r in rows if (r['block'] or 0) <= SNAP),
                       'sum_snapshot_to_t1': sum(r['actual_minus_events_wgnk'] for r in rows if SNAP < (r['block'] or 0) <= T1),
                       'sum_t1_to_end': sum(r['actual_minus_events_wgnk'] for r in rows if T1 < (r['block'] or 0) <= END),
                       'largest': sorted(rows, key=lambda r: -abs(r['actual_minus_events_wgnk']))[:4]}
    res['v3_wgnk_overpayment_residual'] = resid
    m = tr[(tr.from_addr == ETH0) & (tr.value_wgnk > 1e6)]
    res['large_mints'] = [{'block': int(b), 'tx': h, 'to': to_, 'wgnk': float(v)} for b, h, to_, v in zip(m.block_number, m.tx_hash, m.to_addr, m.value_wgnk)]
    rpc.commit()
    return res


# ============================================================================= positions from state
TOL_W, TOL_U = 1.0, 0.5
STATES = ['snap', 't1', 'end']


def build_positions(disc, st):
    """One row per (position, state) + pool-level reconciliation."""
    from collections import defaultdict
    rows, pools = [], {}
    for name in STATES:
        b = st[name]
        for pool in V3_POOLS:
            p = b['v3'][pool]

            def inside(tl, tu, p=p):
                lo, up = p['ticks'][str(tl)], p['ticks'][str(tu)]
                return fee_growth_inside(p['tick'], tl, tu, p['fg0'], p['fg1'], (lo['o0'], lo['o1']), (up['o0'], up['o1']))
            agg = {'amt0': 0, 'amt1': 0, 'owed0': 0, 'owed1': 0, 'fee0': 0, 'fee1': 0, 'n_pos': 0, 'n_liq': 0, 'sumL_active': 0}
            npm_pool_level = {}
            for key, r in p['positions'].items():
                owner, tl, tu = key.split(':')
                tl, tu = int(tl), int(tu)
                a0, a1 = amounts_for_liquidity(r['L'], p['sqrtP'], tl, tu)
                f0 = f1 = 0
                if r['L'] > 0:
                    ins = inside(tl, tu)
                    f0, f1 = fees_owed(r['L'], ins[0], r['last0']), fees_owed(r['L'], ins[1], r['last1'])
                    agg['n_liq'] += 1
                    if tl <= p['tick'] < tu:
                        agg['sumL_active'] += r['L']
                agg['n_pos'] += 1
                for k, v in (('amt0', a0), ('amt1', a1), ('owed0', r['owed0']), ('owed1', r['owed1']), ('fee0', f0), ('fee1', f1)):
                    agg[k] += v
                if owner == NPM:
                    npm_pool_level[(tl, tu)] = {'L': r['L'], 'w': a0 + r['owed0'] + f0, 'm': a1 + r['owed1'] + f1}
                else:
                    rows.append({'pos': f'own:{pool}:{owner}:{tl}:{tu}', 'kind': 'v3own', 'pool': pool, 'tl': tl, 'tu': tu, 'state': name,
                                 'L': r['L'], 'owner': owner, 'amt_w': a0, 'amt_m': a1, 'owed_w': r['owed0'], 'owed_m': r['owed1'],
                                 'fee_w': f0, 'fee_m': f1, 'money_token': USDT, 'in_range': tl <= p['tick'] < tu})
            nft_sum = defaultdict(lambda: {'L': 0, 'w': 0, 'm': 0})
            for tid, meta in disc['npm_tokens'].items():
                if meta['pool'] != pool:
                    continue
                r = b['npm'].get(tid)
                tl, tu = meta['tl'], meta['tu']
                row = {'pos': f'v3:{tid}', 'kind': 'v3nft', 'pool': pool, 'tl': tl, 'tu': tu, 'state': name, 'L': 0, 'owner': None,
                       'amt_w': 0, 'amt_m': 0, 'owed_w': 0, 'owed_m': 0, 'fee_w': 0, 'fee_m': 0, 'money_token': USDT, 'in_range': tl <= p['tick'] < tu}
                if r is not None:
                    row['owner'] = r['owner']
                    if 'L' in r:
                        assert (r['token0'], r['token1'], r['tl'], r['tu']) == (WGNK, USDT, tl, tu), (tid, r)
                        a0, a1 = amounts_for_liquidity(r['L'], p['sqrtP'], tl, tu)
                        f0 = f1 = 0
                        if r['L'] > 0:
                            ins = inside(tl, tu)
                            f0, f1 = fees_owed(r['L'], ins[0], r['last0']), fees_owed(r['L'], ins[1], r['last1'])
                        row.update(L=r['L'], amt_w=a0, amt_m=a1, owed_w=r['owed0'], owed_m=r['owed1'], fee_w=f0, fee_m=f1)
                        x = nft_sum[(tl, tu)]
                        x['L'] += r['L']; x['w'] += a0 + r['owed0'] + f0; x['m'] += a1 + r['owed1'] + f1
                rows.append(row)
            chk = []
            for rng in sorted(set(npm_pool_level) | set(nft_sum)):
                pl, nf = npm_pool_level.get(rng, {'L': 0, 'w': 0, 'm': 0}), nft_sum.get(rng, {'L': 0, 'w': 0, 'm': 0})
                chk.append((pl['L'] - nf['L'], (pl['w'] - nf['w']) / 1e9, (pl['m'] - nf['m']) / 1e6))
            tot0 = agg['amt0'] + agg['owed0'] + agg['fee0'] + p['protoFees'][0]
            tot1 = agg['amt1'] + agg['owed1'] + agg['fee1'] + p['protoFees'][1]
            pools[(name, pool)] = {
                'state': name, 'venue': 'v3', 'pool': pool, 'sqrtPriceX96': str(p['sqrtP']), 'tick': p['tick'], 'slot0_feeProtocol': p['feeProtocol'],
                'pool_liquidity': str(p['L']), 'sum_in_range_position_liquidity': str(agg['sumL_active']), 'in_range_liquidity_matches': p['L'] == agg['sumL_active'],
                'n_position_keys': agg['n_pos'], 'n_with_liquidity': agg['n_liq'],
                'wgnk': {'balance': p['bal0'] / 1e9, 'positions_amount': agg['amt0'] / 1e9, 'tokens_owed': agg['owed0'] / 1e9,
                         'uncollected_lp_fees': agg['fee0'] / 1e9, 'protocol_fees': p['protoFees'][0] / 1e9, 'sum': tot0 / 1e9,
                         'gap': (p['bal0'] - tot0) / 1e9, 'gap_if_protocol_fees_ignored': (p['bal0'] - tot0 + p['protoFees'][0]) / 1e9},
                'usdt': {'balance': p['bal1'] / 1e6, 'positions_amount': agg['amt1'] / 1e6, 'tokens_owed': agg['owed1'] / 1e6,
                         'uncollected_lp_fees': agg['fee1'] / 1e6, 'protocol_fees': p['protoFees'][1] / 1e6, 'sum': tot1 / 1e6,
                         'gap': (p['bal1'] - tot1) / 1e6, 'gap_if_protocol_fees_ignored': (p['bal1'] - tot1 + p['protoFees'][1]) / 1e6},
                'npm_token_ids_vs_pool_level_npm_position': {'max_abs_liquidity_diff': max([abs(c[0]) for c in chk] or [0]),
                                                             'sum_wgnk_diff': sum(c[1] for c in chk), 'sum_usdt_diff': sum(c[2] for c in chk)}}
        v4_w_amt = v4_w_fee = 0
        for pool in disc['v4_pools']:
            pid = pool['id']
            p = b['v4'].get(pid)
            if p is None:
                continue
            w_is0 = pool['c0'] == WGNK
            mtok = pool['c1'] if w_is0 else pool['c0']
            sumL_active = 0
            for key, r in p['positions'].items():
                owner, tl, tu, salt = key.split(':')
                tl, tu = int(tl), int(tu)
                a0, a1 = amounts_for_liquidity(r['L'], p['sqrtP'], tl, tu)
                f0 = f1 = 0
                if r['L'] > 0:
                    f0, f1 = fees_owed(r['L'], r['in0'], r['last0']), fees_owed(r['L'], r['in1'], r['last1'])
                    if tl <= p['tick'] < tu:
                        sumL_active += r['L']
                aw, am, fw, fm = (a0, a1, f0, f1) if w_is0 else (a1, a0, f1, f0)
                v4_w_amt += aw; v4_w_fee += fw
                rows.append({'pos': f'v4:{int(salt, 16)}' if owner == POSM else f'v4own:{pid}:{owner}:{tl}:{tu}:{salt}', 'kind': 'v4nft' if owner == POSM else 'v4own',
                             'pool': pid, 'tl': tl, 'tu': tu, 'state': name, 'L': r['L'], 'owner': r.get('nft_owner') if owner == POSM else owner,
                             'amt_w': aw, 'amt_m': am, 'owed_w': 0, 'owed_m': 0, 'fee_w': fw, 'fee_m': fm, 'money_token': mtok, 'in_range': tl <= p['tick'] < tu})
            pools[(name, pid)] = {'state': name, 'venue': 'v4', 'pool': pid, 'currency0': pool['c0'], 'currency1': pool['c1'], 'fee_pips': pool['fee'],
                                  'created_block': pool['block'], 'created_after_snapshot': pool['block'] > SNAP,
                                  'sqrtPriceX96': str(p['sqrtP']), 'tick': p['tick'], 'pool_liquidity': str(p['L']),
                                  'sum_in_range_position_liquidity': str(sumL_active), 'in_range_liquidity_matches': p['L'] == sumL_active,
                                  'n_position_keys': len(p['positions'])}
        claims = sum(c['amount'] for c in disc['pm_6909_wgnk'] if c['block'] <= BLOCKS[name] and c['from'] == ETH0) - \
            sum(c['amount'] for c in disc['pm_6909_wgnk'] if c['block'] <= BLOCKS[name] and c['to'] == ETH0)
        m = b['misc']
        tot = v4_w_amt + v4_w_fee + m['pm_protofees_wgnk'] + claims
        pools[(name, 'zz_v4_poolmanager_wgnk')] = {
            'state': name, 'venue': 'v4', 'pool': 'PoolManager, WGNK side only, all WGNK pools together', 'wgnk': {
                'balance': m['pm_wgnk'] / 1e9, 'positions_amount': v4_w_amt / 1e9, 'uncollected_lp_fees': v4_w_fee / 1e9,
                'protocol_fees_accrued': m['pm_protofees_wgnk'] / 1e9, 'erc6909_claims': claims / 1e9, 'sum': tot / 1e9, 'gap': (m['pm_wgnk'] - tot) / 1e9}}
    return rows, pools


def file_info(path):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    return {'path': path, 'sha256': h, 'mtime_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(path))), 'bytes': os.path.getsize(path)}


PROJECT_VERSIONS = {
    'live': {'variants': f'{RESEARCH}/model/parquet/variants.parquet', 'lp_positions': f'{RESEARCH}/model/parquet/lp_positions.parquet',
             'ledger': f'{RESEARCH}/model/parquet/tx_deltas_windows.parquet'},
    'audit_package': {'variants': f'{RESEARCH}/audit_package/Gonka_Bridge_Incident_Audit_Package/03_model/variants.parquet',
                      'lp_positions': f'{RESEARCH}/audit_package/Gonka_Bridge_Incident_Audit_Package/03_model/lp_positions.parquet',
                      'ledger': f'{RESEARCH}/audit_package/Gonka_Bridge_Incident_Audit_Package/03_model/tx_deltas_windows.parquet'},
}


def lp_universe(var):
    lpv = var[(var.lp_w_before.abs() > 0) | (var.lp_u_before.abs() > 0) | (var.lp_u_t1.abs() > 0) | (var.lp_u_end.abs() > 0)].copy()
    lpv['score'] = lpv.lp_w_before * P0 + lpv.lp_u_before
    return lpv.sort_values(['score', 'entity'], ascending=[False, True])


def compare_project(df, var, plp, sample):
    """Per position and per owner: mine vs project. df has the entity column already (project's address->owner map)."""
    from collections import defaultdict
    pj = {(r.pos, r.state): r for r in plp.itertuples()}
    mine_pos = set(df.pos)
    pos_out = []
    for pos, g in df.groupby('pos', sort=False):
        rec = {'pos': pos, 'kind': g.kind.iloc[0], 'pool': g.pool.iloc[0], 'tick_lower': int(g.tl.iloc[0]), 'tick_upper': int(g.tu.iloc[0]),
               'money_token': g.money_sym.iloc[0], 'source': 'chain state (eth_call at the block)', 'states': {}}
        ok_all, any_val, ents = True, False, set()
        for r in g.itertuples():
            m = {'liquidity': str(r.L), 'owner': r.owner, 'entity': r.entity, 'in_range': bool(r.in_range),
                 'amount_wgnk': r.amt_w / 1e9, 'owed_wgnk': r.owed_w / 1e9, 'fees_wgnk': r.fee_w / 1e9, 'wgnk': r.wgnk,
                 'money_amount': r.money_amount, 'money_usd': r.money_usd,
                 'money_raw': {'amount': str(r.amt_m), 'owed': str(r.owed_m), 'fees': str(r.fee_m)}}
            p = pj.get((pos, r.state))
            c = {'mine': m}
            nonzero = r.L > 0 or r.wgnk > 0 or r.money_amount > 0
            if r.entity and nonzero:
                ents.add(r.entity)
            if p is not None:
                c['project'] = {'liquidity': str(p.liquidity), 'owner': p.owner, 'entity': p.entity, 'wgnk': float(p.wgnk),
                                'money_token': p.money_token, 'money_amount': float(p.money_amount), 'money_usd': float(p.money_usd)}
                c['diff_wgnk'] = r.wgnk - float(p.wgnk)
                c['diff_usd'] = r.money_usd - float(p.money_usd)
                c['liquidity_equal'] = str(r.L) == str(p.liquidity)
                c['owner_equal'] = (r.owner or '') == (p.owner or '') or not nonzero
                c['pass'] = bool(abs(c['diff_wgnk']) <= TOL_W and abs(c['diff_usd']) <= TOL_U and c['liquidity_equal'] and c['owner_equal'])
            else:
                c['project'] = None
                c['pass'] = not nonzero
                c['note'] = 'missing in the project list' if nonzero else 'not in the project list; empty on chain'
            any_val = any_val or nonzero
            ok_all = ok_all and c['pass']
            rec['states'][r.state] = c
        rec['entities_with_value'] = sorted(ents)
        rec['in_sample'] = bool(ents & set(sample))
        rec['nonzero_in_any_state'] = bool(any_val)
        rec['pass'] = bool(ok_all)
        pos_out.append(rec)
    proj_only = []
    for pos, g in plp.groupby('pos', sort=False):
        missing_states = [st_ for st_ in g.state if (pos, st_) not in set(zip(df.pos, df.state))]
        gm = g[g.state.isin(missing_states)]
        if not len(gm):
            continue
        nz = bool((gm.liquidity.astype(str) != '0').any() or gm.wgnk.abs().sum() > 0 or gm.money_amount.abs().sum() > 0)
        if pos not in mine_pos or nz:
            proj_only.append({'pos': pos, 'owner': g.owner.iloc[0], 'states_not_on_chain': missing_states, 'project_nonzero_there': nz,
                              'sum_wgnk': float(gm.wgnk.sum()), 'sum_money_usd': float(gm.money_usd.sum())})
    zero = lambda: {'lp_w_before': 0.0, 'lp_u_before': 0.0, 'lp_u_t1': 0.0, 'lp_u_end': 0.0, 'lp_w_t1': 0.0, 'lp_w_end': 0.0,
                    'eth_in_positions': {'snap': 0.0, 't1': 0.0, 'end': 0.0}, 'unpriced_other_side': {}}
    mine_ent = defaultdict(zero)
    for r in df.itertuples():
        if not r.entity:
            continue
        e = mine_ent[r.entity]
        if r.state == 'snap':
            e['lp_w_before'] += r.wgnk; e['lp_u_before'] += r.money_usd
        elif r.state == 't1':
            e['lp_u_t1'] += r.money_usd; e['lp_w_t1'] += r.wgnk
        else:
            e['lp_u_end'] += r.money_usd; e['lp_w_end'] += r.wgnk
        if r.money_sym == 'ETH':
            e['eth_in_positions'][r.state] += r.money_amount
        elif r.money_sym not in ('USDT', 'USDC') and r.money_amount > 0:
            k = f'{r.state}:{r.money_sym}'
            e['unpriced_other_side'][k] = e['unpriced_other_side'].get(k, 0) + r.money_amount
    vmap = {r.entity: r for r in var.itertuples()}
    lpv = lp_universe(var)
    own_out = []
    for ent in sorted(set(mine_ent) | set(lpv.entity)):
        m = mine_ent.get(ent) or zero()
        p = vmap.get(ent)
        rec = {'entity': ent, 'in_sample': ent in sample, 'mine': m}
        if p is not None:
            rec['project'] = {k: float(getattr(p, k)) for k in ('lp_w_before', 'lp_u_before', 'lp_u_t1', 'lp_u_end')}
            rec['project_payout'] = {'category': p.category, 'honest_wgnk': float(p.honest_wgnk), 'net_a_usd': float(p.net_a_usd), 'net_b_usd': float(p.net_b_usd),
                                     **{f'{v}_{k}': float(getattr(p, f'{v}_{k}')) for v in ('v1', 'v2', 'v3') for k in ('pay_gnk', 'money_usd')}}
            rec['diff'] = {k: m[k] - rec['project'][k] for k in rec['project']}
            rec['pass'] = bool(abs(rec['diff']['lp_w_before']) <= TOL_W and all(abs(rec['diff'][k]) <= TOL_U for k in ('lp_u_before', 'lp_u_t1', 'lp_u_end')))
        else:
            rec['project'] = None
            rec['pass'] = not (m['lp_w_before'] > TOL_W or max(m['lp_u_before'], m['lp_u_t1'], m['lp_u_end']) > TOL_U)
            rec['note'] = 'address not present in variants.parquet (no LP value on chain at the three blocks)' if rec['pass'] else 'has LP value on chain but is not in variants.parquet'
        rec['positions'] = sorted(set(df[(df.entity == ent)].pos))
        rec['positions_with_value'] = sorted(set(df[(df.entity == ent) & ((df.L > 0) | (df.wgnk > 0) | (df.money_amount > 0))].pos))
        own_out.append(rec)
    return own_out, pos_out, proj_only


def lp_tx_analysis(rpc, disc, ledgers, a2e):
    """Every liquidity operation after the snapshot: token flows from chain receipts vs the project's transaction ledger."""
    from collections import defaultdict
    DAI = '0x6b175474e89094c44da98b954eedeac495271d0f'
    TOK = {WGNK: ('WGNK', 9), USDT: ('USDT', 6), USDC: ('USDC', 6), WETH: ('WETH', 18), DAI: ('DAI', 18)}
    INFRA = {PM, POSM, NPM, *V3_POOLS, '0x000000000022d473030f116ddee9f6b43ac78ba3', '0x66a9893cc07d91d95644aedd05d03f95e1dba8af'}
    eth_pools = {p['id'] for p in disc['v4_pools'] if ETH0 in (p['c0'], p['c1'])}
    ev = defaultdict(list)
    for e in disc['v3_events']:
        if e['block'] > SNAP and e['ev'] in ('Mint', 'Burn', 'Collect'):
            ev[e['tx']].append({'venue': 'v3', 'pool': e['pool'], 'block': e['block'], 'event': e['ev'], 'pool_owner': e['owner'], 'token_id': e.get('token_id'),
                                'wgnk': e['a0'] / 1e9, 'usdt': e['a1'] / 1e6})
    for e in disc['v4_events']:
        if e['block'] > SNAP:
            ev[e['tx']].append({'venue': 'v4', 'pool': e['id'], 'block': e['block'], 'event': 'ModifyLiquidity', 'token_id': int(e['salt'], 16), 'liquidity_delta': str(e['dL'])})
    txs = []
    for tx, evs in ev.items():
        rc = rpc.receipt(tx)
        flows = defaultdict(lambda: defaultdict(int))
        for l in rc['logs']:
            if l['address'] in TOK and l['topics'][0] == T['Transfer'] and len(l['topics']) == 3:
                f, t_, v = addr(l['topics'][1]), addr(l['topics'][2]), u(words(l['data'])[0])
                flows[f][l['address']] -= v
                flows[t_][l['address']] += v
        users = {a: {TOK[k][0]: v / 10 ** TOK[k][1] for k, v in fl.items() if v != 0} for a, fl in flows.items() if a not in INFRA}
        users = {a: f for a, f in users.items() if f}
        blk = evs[0]['block']
        rec = {'tx': tx, 'block': blk, 'window': 'A' if blk <= T1 else 'B', 'sender': rc['from'].lower(), 'events': evs, 'erc20_flows_by_address': users}
        if any(e['pool'] in eth_pools for e in evs):
            # native ETH leg: balance change of the sender over the block plus gas paid (valid if it sent exactly one tx in the block)
            sdr = rc['from'].lower()
            full = rpc.call('eth_getTransactionReceipt', [tx], trim=lambda r: {'gasUsed': r['gasUsed'], 'effectiveGasPrice': r['effectiveGasPrice']}, tag='gas')
            gas = int(full['gasUsed'], 16) * int(full['effectiveGasPrice'], 16)
            b1 = int(rpc.call('eth_getBalance', [sdr, hex(blk)]), 16)
            b0 = int(rpc.call('eth_getBalance', [sdr, hex(blk - 1)]), 16)
            n1 = int(rpc.call('eth_getTransactionCount', [sdr, hex(blk)]), 16)
            n0 = int(rpc.call('eth_getTransactionCount', [sdr, hex(blk - 1)]), 16)
            rec['native_eth'] = {'address': sdr, 'net_eth_excluding_gas': (b1 - b0 + gas) / 1e18, 'txs_by_sender_in_block': n1 - n0,
                                 'method': 'eth_getBalance(block) - eth_getBalance(block-1) + gasUsed*effectiveGasPrice',
                                 'eth_usd_chainlink_at_block': u(rpc.eth_call(CHAINLINK_ETH_USD, S['latestAnswer'], blk)[0]) / 1e8}
        txs.append(rec)
    rpc.commit()
    out = {'n_post_snapshot_lp_txs': len(txs), 'by_window': {w: sum(t['window'] == w for t in txs) for w in ('A', 'B')}, 'versions': {}}
    for vname, td in ledgers.items():
        by_tx = {h: g for h, g in td.groupby('tx_hash')}
        missing, bad_rows, n_rows, eth_rows = [], [], 0, []
        ent_missing = defaultdict(lambda: {'A_usd': 0.0, 'B_usd': 0.0, 'n_txs': 0})
        n_flagged = 0
        for t in txs:
            g = by_tx.get(t['tx'])
            if g is None:
                stable = {a: sum(v for k, v in f.items() if k in ('USDT', 'USDC', 'DAI')) for a, f in t['erc20_flows_by_address'].items()}
                missing.append({'tx': t['tx'], 'block': t['block'], 'window': t['window'], 'sender': t['sender'],
                                'token_ids': sorted({e['token_id'] for e in t['events'] if e.get('token_id') is not None}),
                                'pools': sorted({e['pool'] for e in t['events']}), 'erc20_flows_by_address': t['erc20_flows_by_address']})
                for a, m_ in stable.items():
                    if m_ != 0:
                        e_ = ent_missing[a2e.get(a, a)]
                        e_[t['window'] + '_usd'] += m_; e_['n_txs'] += 1
                continue
            n_flagged += int(bool(g.is_lp_tx.any()))
            for r in g.itertuples():
                mine = t['erc20_flows_by_address'].get(r.address, {})
                ptok = json.loads(r.tokens) if r.tokens else {}
                d = {'WGNK': mine.get('WGNK', 0.0) - r.d_wgnk}
                d.update({k: mine.get(k, 0.0) - ptok.get(k, 0.0) for k in ('USDT', 'USDC', 'DAI')})
                n_rows += 1
                ne = t.get('native_eth')
                if ne and ne['address'] == r.address:
                    pe = ptok.get('ETH', 0.0) + ptok.get('WETH', 0.0)
                    me = ne['net_eth_excluding_gas'] + mine.get('WETH', 0.0)
                    eth_rows.append({'tx': t['tx'], 'block': t['block'], 'address': r.address, 'mine_eth_plus_weth': me, 'project_eth_plus_weth': pe,
                                     'diff_eth': me - pe, 'txs_by_sender_in_block': ne['txs_by_sender_in_block']})
                elif 'ETH' not in ptok:
                    d['WETH'] = mine.get('WETH', 0.0) - ptok.get('WETH', 0.0)
                if any(abs(v) > 1e-6 for v in d.values()):
                    bad_rows.append({'tx': t['tx'], 'block': t['block'], 'address': r.address, 'diff_mine_minus_project': d, 'project_tokens': ptok})
        ents = []
        for e_, f in ent_missing.items():
            ents.append({'entity': e_, 'unrecorded_stablecoin_flow_window_A_usd(+received,-paid)': f['A_usd'],
                         'unrecorded_stablecoin_flow_window_B_usd(+received,-paid)': f['B_usd'], 'n_txs': f['n_txs']})
        out['versions'][vname] = {'lp_txs_present_in_ledger': len(txs) - len(missing), 'lp_txs_flagged_is_lp_tx': n_flagged, 'lp_txs_missing': len(missing),
                                  'missing_with_money_flow': sum(1 for m_ in missing if m_['erc20_flows_by_address']),
                                  'missing_txs': missing, 'entities_affected_by_missing_txs': sorted(ents, key=lambda x: x['entity']),
                                  'ledger_rows_compared_erc20': n_rows, 'ledger_rows_with_erc20_difference': bad_rows,
                                  'native_eth_rows_compared': eth_rows}
    out['txs'] = txs
    return out


def compute(rpc, disc, st):
    import pandas as pd
    from collections import defaultdict
    rows, pools = build_positions(disc, st)
    eth_px = {n: st[n]['misc']['eth_usd'] for n in STATES}
    v4tok = json.load(open(f'{RESEARCH}/raw/eth/v4_extra.json'))['tokens']   # symbols/decimals of the two exotic tokens only

    def tinfo(tok):
        if tok in TOKENS:
            return TOKENS[tok]
        return (v4tok.get(tok, {}).get('symbol', tok[:10]), v4tok.get(tok, {}).get('decimals', 18))
    for r in rows:
        symb, dec_ = tinfo(r['money_token'])
        r['money_sym'] = symb
        r['wgnk'] = (r['amt_w'] + r['owed_w'] + r['fee_w']) / 1e9
        r['money_amount'] = (r['amt_m'] + r['owed_m'] + r['fee_m']) / 10 ** dec_
        # methodology: stablecoins at 1, ETH inside positions at the snapshot price, other tokens unpriced
        r['money_usd'] = r['money_amount'] if symb in ('USDT', 'USDC') else (r['money_amount'] * eth_px['snap'] if symb == 'ETH' else 0.0)
    df = pd.DataFrame(rows)

    # ---- project files (opened only from here on: sample selection and final comparison)
    proj, files = {}, {}
    for vname, paths in PROJECT_VERSIONS.items():
        proj[vname] = {k: pd.read_parquet(p) for k, p in paths.items()}
        files[vname] = {k: file_info(p) for k, p in paths.items()}
    var = proj['live']['variants']
    a2e = {}
    for e, a in zip(var.entity, var.addresses):
        for x in str(a).split(';'):
            a2e[x.strip().lower()] = e
    df['entity'] = [a2e.get(o, o) if o else None for o in df.owner]
    lpv = lp_universe(var)
    top5 = list(lpv.entity[:5])
    rnd5 = random.Random(SEED).sample(sorted(lpv.entity[5:]), 5)
    sample = top5 + rnd5

    comp = {}
    for vname in PROJECT_VERSIONS:
        v_, l_ = proj[vname]['variants'], proj[vname]['lp_positions']
        m2 = {}
        for e, a in zip(v_.entity, v_.addresses):
            for x in str(a).split(';'):
                m2[x.strip().lower()] = e
        d2 = df.copy()
        d2['entity'] = [m2.get(o, o) if o else None for o in d2.owner]
        comp[vname] = compare_project(d2, v_, l_, sample)
    own_out, pos_out, proj_only = comp['live']
    for o_ in own_out:
        o_['sample_group'] = 'top5' if o_['entity'] in top5 else ('random5' if o_['entity'] in rnd5 else None)

    def summary(c):
        o_, p_, po = c
        st_rows = [(p['pos'], s_, x) for p in p_ for s_, x in p['states'].items()]
        return {'owners_compared': sum(1 for x in o_ if x['project'] is not None), 'owners_pass': sum(1 for x in o_ if x['project'] is not None and x['pass']),
                'owners_fail': [x['entity'] for x in o_ if not x['pass']],
                'sample_owners_pass': sum(1 for x in o_ if x['in_sample'] and x['pass']), 'sample_owners': sum(1 for x in o_ if x['in_sample']),
                'positions_mine': len(p_), 'position_states_compared': sum(1 for _, _, x in st_rows if x['project'] is not None),
                'position_states_pass': sum(1 for _, _, x in st_rows if x['project'] is not None and x['pass']),
                'position_states_fail': [f'{a}@{b}' for a, b, x in st_rows if not x['pass']],
                'position_states_nonzero_on_chain': sum(1 for _, _, x in st_rows if x['mine']['liquidity'] != '0' or x['mine']['wgnk'] > 0 or x['mine']['money_amount'] > 0),
                'max_abs_diff_wgnk': max([abs(x.get('diff_wgnk', 0.0)) for _, _, x in st_rows] or [0]),
                'max_abs_diff_usd': max([abs(x.get('diff_usd', 0.0)) for _, _, x in st_rows] or [0]),
                'project_rows_without_chain_counterpart': po,
                'totals_mine': {k: sum(x['mine'][k] for x in o_) for k in ('lp_w_before', 'lp_u_before', 'lp_u_t1', 'lp_u_end')},
                'totals_project': {k: sum(x['project'][k] for x in o_ if x['project']) for k in ('lp_w_before', 'lp_u_before', 'lp_u_t1', 'lp_u_end')}}

    # ---- blind spots
    owners_val = sorted({r.owner for r in df.itertuples() if r.owner and (r.L > 0 or r.wgnk > 0 or r.money_amount > 0)})
    owner_kind = {o_: code_kind(rpc, o_) for o_ in owners_val}
    direct_minters = sorted({e['owner'] for e in disc['v3_events'] if e['ev'] == 'Mint' and e['owner'] != NPM})
    direct_kind = {o_: code_kind(rpc, o_) for o_ in direct_minters}
    transfers = []
    for pos, g in df[df.kind.isin(['v3nft', 'v4nft'])].groupby('pos'):
        o_ = {r.state: r.owner for r in g.itertuples()}
        if len({v for v in o_.values() if v}) > 1:
            transfers.append({'pos': pos, 'owners': o_, 'value_by_state': {r.state: {'liquidity': str(r.L), 'wgnk': r.wgnk, 'money_usd': r.money_usd} for r in g.itertuples()}})
    burned = [{'pos': r.pos, 'state': r.state} for r in df[df.kind.isin(['v3nft', 'v4nft'])].itertuples() if r.owner is None]
    pre = [e for e in disc['v3_events'] if 26443607 <= e['block'] <= SNAP and e['ev'] != 'CollectProtocol'] + [e for e in disc['v4_events'] if 26443607 <= e['block'] <= SNAP]
    lp_tx = lp_tx_analysis(rpc, disc, {v: proj[v]['ledger'] for v in PROJECT_VERSIONS}, a2e)
    # composition identity on the project's own numbers (live): net_a = -sum(d_usd, window A) + lp_u_before - lp_u_t1, same for B
    td = proj['live']['ledger']
    sums = td.groupby(['entity', 'win']).d_usd.sum().to_dict()
    ident = []
    for r in lpv.itertuples():
        ia = -sums.get((r.entity, 'A'), 0.0) + r.lp_u_before - r.lp_u_t1
        ib = -sums.get((r.entity, 'B'), 0.0) + r.lp_u_t1 - r.lp_u_end
        ident.append({'entity': r.entity, 'net_a_usd_project': float(r.net_a_usd), 'net_a_from_ledger_and_positions': float(ia), 'diff_a': float(r.net_a_usd - ia),
                      'net_b_usd_project': float(r.net_b_usd), 'net_b_from_ledger_and_positions': float(ib), 'diff_b': float(r.net_b_usd - ib)})
    # ETH valuation sensitivity and unpriced tokens
    eth_rows = df[(df.money_sym == 'ETH') & (df.money_amount > 0)]
    eth_val = [{'pos': r.pos, 'state': r.state, 'entity': r.entity, 'eth': r.money_amount, 'usd_at_snapshot_price': r.money_usd,
                'usd_at_state_price': r.money_amount * eth_px[r.state], 'diff_usd': r.money_amount * (eth_px[r.state] - eth_px['snap'])} for r in eth_rows.itertuples()]
    unpriced = [{'pos': r.pos, 'state': r.state, 'entity': r.entity, 'token': r.money_sym, 'token_amount': r.money_amount, 'wgnk': r.wgnk}
                for r in df[~df.money_sym.isin(['USDT', 'USDC', 'ETH']) & ((df.money_amount > 0) | (df.wgnk > 0))].itertuples()]
    post_pools = [{'pool': p['id'], 'created_block': p['block'], 'fee_pips': p['fee'], 'pair': f"{tinfo(p['c0'])[0]}/{tinfo(p['c1'])[0]}"} for p in disc['v4_pools'] if p['block'] > SNAP]
    tot = {k: float(var[f'v1_{k}'].sum()) for k in ('pay_gnk', 'money_usd')}
    conc = [{'entity': r.entity, 'kind': code_kind(rpc, r.entity), 'lp_w_before': float(r.lp_w_before), 'lp_u_before': float(r.lp_u_before),
             'share_of_lp_wgnk': float(r.lp_w_before / lpv.lp_w_before.sum()), 'share_of_lp_money': float(r.lp_u_before / lpv.lp_u_before.sum()),
             'v1_pay_gnk': float(r.v1_pay_gnk), 'v1_money_usd': float(r.v1_money_usd), 'v1_value_usd': float(r.v1_value_usd),
             'share_of_all_v1_gnk': float(r.v1_pay_gnk / tot['pay_gnk']), 'share_of_all_v1_money': float(r.v1_money_usd / tot['money_usd'])} for r in lpv.head(5).itertuples()]
    first_mints = {}
    for pool in V3_POOLS:
        ms = sorted([e for e in disc['v3_events'] if e['ev'] == 'Mint' and e['pool'] == pool], key=lambda e: (e['block'], e['li']))
        first_mints[pool] = {'block': ms[0]['block'], 'tx': ms[0]['tx'], 'token_id': ms[0].get('token_id'),
                             'nft_owner_at_snapshot': st['snap']['npm'].get(str(ms[0].get('token_id')), {}).get('owner')}
    extra = extra_chain_checks(rpc, disc)
    vlog_path = os.path.join(CACHE_DIR, 'verify_logs.json')
    nver = rpc.db.execute('select count(*), coalesce(sum(ok), 0) from ver').fetchone()
    ncalls = rpc.db.execute("select count(*) from kv where method='eth_call'").fetchone()[0]
    out = {
        'meta': {'generated_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), 'blocks': BLOCKS, 'seed': SEED, 'p0': P0,
                 'tolerances': {'wgnk': TOL_W, 'usd': TOL_U},
                 'data_source': 'Ethereum archive state through public JSON-RPC (eth_call / eth_getBalance / eth_getCode at a block number); events through eth_getLogs; no API keys',
                 'state_endpoints': STATE_EPS, 'log_endpoint': LOG_EPS,
                 'eth_usd_chainlink_latestAnswer': eth_px,
                 'state_reads': {'eth_call_results_cached': ncalls, 're_read_on_second_provider': nver[0], 'identical': nver[1]},
                 'log_cross_check': json.load(open(vlog_path)) if os.path.exists(vlog_path) else 'not run (python lp_recompute.py verify)',
                 'counts': {'v3_pool_events': len(disc['v3_events']), 'npm_token_ids': len(disc['npm_tokens']), 'v4_pools_with_wgnk': len(disc['v4_pools']),
                            'v4_modify_liquidity_events': len(disc['v4_events']), 'positions_mine': int(df.pos.nunique())},
                 'project_files': files},
        'sample': {'universe': 'entities in live variants.parquet with any non-zero lp_w_before / lp_u_before / lp_u_t1 / lp_u_end', 'universe_size': int(len(lpv)),
                   'top5_by_lp_w_before_x_p0_plus_lp_u_before': top5, 'random5_seed_%d' % SEED: rnd5},
        'summary': {v: summary(c) for v, c in comp.items()},
        'owners': own_out, 'positions': pos_out,
        'pool_reconciliation': [v for k, v in sorted(pools.items(), key=lambda kv: (STATES.index(kv[0][0]), kv[0][1]))],
        'blind_spots': {
            'post_snapshot_liquidity_operations_vs_ledger': lp_tx,
            'ledger_composition_identity_live': ident,
            'owner_account_type_of_positions_with_value': owner_kind, 'direct_pool_minters_account_type': direct_kind,
            'nft_owner_changes_between_blocks': transfers, 'burned_nfts': burned, 'liquidity_events_between_T0_26443607_and_snapshot': pre,
            'eth_leg_valuation': eth_val, 'positions_with_unpriced_other_side': unpriced, 'v4_pools_created_after_snapshot': post_pools,
            'concentration_top5_live': conc, 'first_mint_of_v3_pools': first_mints, 'erc6909_wgnk_claims_in_poolmanager': disc['pm_6909_wgnk'],
            'other_venues_supply_and_residual': extra},
    }
    json.dump(out, open(os.path.join(WORK, 'lp_recompute.json'), 'w'), indent=1, default=str)
    for v, sm in out['summary'].items():
        print(v, {k: sm[k] for k in ('owners_compared', 'owners_pass', 'sample_owners_pass', 'position_states_compared', 'position_states_pass', 'max_abs_diff_wgnk', 'max_abs_diff_usd')})
        print('   fails:', sm['owners_fail'], sm['position_states_fail'])
    for v, x in lp_tx['versions'].items():
        print(v, 'LP txs', lp_tx['n_post_snapshot_lp_txs'], 'missing from ledger', x['lp_txs_missing'], 'of which with money flow', x['missing_with_money_flow'],
              'rows with erc20 diff', len(x['ledger_rows_with_erc20_difference']))
    return out


def main():
    _selftest_tickmath()
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    rpc = RPC()
    disc = discover(rpc)                 # cached after the first run
    json.dump(disc, open(os.path.join(CACHE_DIR, 'discovery.json'), 'w'))
    print('v3 events', len(disc['v3_events']), 'npm tokens', len(disc['npm_tokens']), 'v4 pools', len(disc['v4_pools']),
          'v4 events', len(disc['v4_events']), flush=True)
    st = read_state(rpc, disc)           # cached after the first run
    if stage in ('verify', 'all'):
        n, bad = rpc.verify_all()
        print('state re-read on a second provider:', n, 'new checks, mismatches', bad)
        vl = verify_logs(rpc, disc)
        json.dump(vl, open(os.path.join(CACHE_DIR, 'verify_logs.json'), 'w'), indent=1)
        print(json.dumps(vl))
    if stage in ('compute', 'all'):
        compute(rpc, disc, st)


if __name__ == '__main__':
    main()
