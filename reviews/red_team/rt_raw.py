"""Independent re-reading of raw receipts: per-tx per-address deltas of WGNK, tracked money and other tokens."""
import sys
sys.path.insert(0, "/work")
from collections import defaultdict
from rt_common import *

WGNK_ADDR = "0x972a7a92d92796a98801a8818bcf91f1648f2f68"
USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"; USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"; DAI = "0x6b175474e89094c44da98b954eedeac495271d0f"
MONEY = {USDT: ("USDT", 6), USDC: ("USDC", 6), WETH: ("WETH", 18), DAI: ("DAI", 18)}
POOL_MANAGER = "0x000000000004444c5dc75cb358380d2e3de08a90"
NPM_V3 = "0xc36442b4a4522e871399cd717abdd847ab11fe88"; POSM_V4 = "0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e"
V3_POOLS = {"0x203ee836d417cf944133bbdd2c62b4bc7388c55d", "0xdbc0edbced03c87a7f287f9949e01c012511f117"}
POOLS = V3_POOLS | {POOL_MANAGER}
INFRA = {ZERO, WGNK_ADDR, POOL_MANAGER, NPM_V3, POSM_V4, WETH,
         "0x000000000022d473030f116ddee9f6b43ac78ba3", "0x66a9893cc07d91d95644aedd05d03f95e1dba8af", "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",
         "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45", "0xe592427a0aece92de3edee1f18e0157c05861564", "0x111111125421ca6dc452d289314280a0f8842a65",
         "0x9008d19f58aabd9ed0d60971565aa8510560ab41", "0x881d40237659c251811cec9c364ef91dc08d300c", "0xdef1c0ded9bec7f1a1670819833240f027b25eff",
         "0x6131b5fae19ea4f9d964eac0408e4408b66337b5", "0x00000011f84b9aa48e5f8aa8b9897600006289be", "0x23617e59a5925b2a4bf75d73ff6711cd0b29de85"}
T_TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
T_DEP = "0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c"
T_WD = "0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65"


def hx(x):
    if x is None or x in ("0x", ""):
        return 0
    return int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)


def load_raw():
    txs = jz("02_onchain_raw/ethereum/post_txs.json.gz"); rcs = jz("02_onchain_raw/ethereum/post_receipts.json.gz")
    ints = jz("02_onchain_raw/ethereum/post_internal.json.gz")
    px = {int(k): v for k, v in jz("02_onchain_raw/ethereum/eth_usd.json").items()}
    return txs, rcs, ints, px


def eth_price(px, block):
    b = block // 25 * 25
    if b in px:
        return px[b]
    return px[min(px, key=lambda k: abs(k - b))]


def parse_tx(h, txs, rcs, ints, px):
    """Returns dict: block, from, to, dw{addr}, tok{addr}{sym}, usd{addr}, other{addr}{token: raw}, wgnk_logs[(from,to,amt)]"""
    rc, tx = rcs[h], txs.get(h) or {}
    block = hx(tx.get("blockNumber")); p = eth_price(px, block)
    dw = defaultdict(float); tok = defaultdict(lambda: defaultdict(float)); usd = defaultdict(float)
    other = defaultdict(lambda: defaultdict(int)); wl = []
    for lg in rc["logs"]:
        a = lg["address"].lower(); tp = lg["topics"]; t0 = tp[0] if tp else None
        if t0 == T_TRANSFER and len(tp) == 3:
            f, to = "0x" + tp[1][-40:], "0x" + tp[2][-40:]
            val = hx(lg["data"])
            if a == WGNK_ADDR:
                dw[f] -= val / 1e9; dw[to] += val / 1e9; wl.append((f, to, val / 1e9))
            elif a in MONEY:
                sym, dec = MONEY[a]
                q = val / 10 ** dec
                tok[f][sym] -= q; tok[to][sym] += q
                u = q * (p if a == WETH else 1.0)
                usd[f] -= u; usd[to] += u
            else:
                other[f][a] -= val; other[to][a] += val
        elif a == WETH and t0 in (T_DEP, T_WD) and len(tp) == 2:
            who = "0x" + tp[1][-40:]; val = hx(lg["data"]) / 1e18; s = 1 if t0 == T_DEP else -1
            tok[who]["WETH"] += s * val; usd[who] += s * val * p
    val = hx(tx.get("value")) / 1e18
    if val:
        f, to = (tx.get("from") or "").lower(), (tx.get("to") or "").lower()
        tok[f]["ETH"] -= val; tok[to]["ETH"] += val; usd[f] -= val * p; usd[to] += val * p
    for it in ints.get(h) or []:
        if it.get("isError") not in (None, "0"):
            continue
        q = int(it["value"]) / 1e18
        if q:
            tok[it["from"]]["ETH"] -= q; tok[it["to"]]["ETH"] += q; usd[it["from"]] -= q * p; usd[it["to"]] += q * p
    return {"block": block, "from": (tx.get("from") or "").lower(), "to": (tx.get("to") or "").lower(), "input": tx.get("input"), "px": p,
            "dw": dw, "tok": tok, "usd": usd, "other": other, "wl": wl, "status": rc.get("status")}
