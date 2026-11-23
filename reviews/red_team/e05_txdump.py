"""Dump of token movements of given transactions and the model rows for them. Usage: python e05_txdump.py <tx|address> ..."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

d = deltas(); txs, rcs, ints, px = load_raw(); v = variants()
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
bts = jz("02_onchain_raw/ethereum/block_ts.json")


def dump(h):
    t = parse_tx(h, txs, rcs, ints, px)
    ts = bts.get(str(t["block"]))
    print(f"\nTX {h} block {t['block']} ts {ts} ({pd.Timestamp(int(ts), unit='s') if ts else ''}) from {t['from']} to {t['to']} input {t['input']} ethpx {t['px']}")
    for f, to, a in t["wl"]:
        print(f"    WGNK {f} -> {to} {a:.4f}")
    addrs = set(t["dw"]) | set(t["tok"]) | set(t["other"])
    for a in sorted(addrs):
        tk = {k: round(x, 6) for k, x in t["tok"][a].items() if abs(x) > 1e-12}
        ot = {k[:10]: x for k, x in t["other"][a].items() if x}
        if abs(t["dw"].get(a, 0)) > 1e-9 or tk or ot:
            print(f"    {a} dW {t['dw'].get(a, 0):+.4f} usd {t['usd'].get(a, 0):+.2f} {tk} other {ot} {'[' + v.set_index('entity').loc[ent_of[a], 'category'] + ']' if a in ent_of else ''}")
    m = d[d.tx_hash == h]
    for r in m.itertuples():
        print(f"    MODEL {r.address} d_wgnk {r.d_wgnk:+.4f} d_usd {r.d_usd:+.2f} {r.tokens} lp={r.is_lp_tx} via={r.via_third_party} win={r.win}")


for arg in sys.argv[1:]:
    if len(arg) == 66:
        dump(arg)
    else:
        hs = [h for h in rcs if arg in parse_tx(h, txs, rcs, ints, px)["dw"]]
        hs.sort(key=lambda h: hx(txs[h]["blockNumber"]))
        lim = 40
        print(f"\n######## address {arg}: {len(hs)} txs with WGNK change (showing first {lim})")
        for h in hs[:lim]:
            dump(h)
