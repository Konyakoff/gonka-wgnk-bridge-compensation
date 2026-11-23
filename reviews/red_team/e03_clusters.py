"""Clusters, hubs, plain transfers after T0: reconstruct the project's clustering from raw data and measure its effect."""
import sys
sys.path.insert(0, "/work")
from collections import defaultdict
from rt_common import *

v = variants(); d = deltas(); tr = transfers(); reg = register()
txs = jz("02_onchain_raw/ethereum/post_txs.json.gz"); rcs = jz("02_onchain_raw/ethereum/post_receipts.json.gz"); ints = jz("02_onchain_raw/ethereum/post_internal.json.gz")
print("post_txs", len(txs), "receipts", len(rcs), "internal", len(ints))
b0 = balances(tr, SNAP_BLOCK); bend = balances(tr, T2_BLOCK)
attack = open(f"{P}/04_registers/attacker_addresses.csv").read(); print(attack)

multi = v[v["addresses"].str.contains(";")]
print("multi-address owners:", len(multi), "addresses in them:", multi["addresses"].str.split(";").map(len).sum())
post = tr[tr["block_number"] >= T0_BLOCK]
ent_of = {}
for _, r in v.iterrows():
    for a in r["addresses"].split(";"):
        ent_of[a] = r["entity"]
# per-address stats from deltas
da = d.groupby("address").agg(n=("tx_hash", "count"), usd=("d_usd", "sum"), w=("d_wgnk", "sum")).to_dict("index")
rows = []
for _, r in multi.iterrows():
    A = r["addresses"].split(";")
    print("\n=== owner", r["entity"], r["category"], "hacker" if r["is_hacker"] else "", "| H", round(r["honest_wgnk"], 2), "netA", round(r["net_a_usd"], 2), "netB", round(r["net_b_usd"], 2),
          "| v1 gnk", round(r["v1_pay_gnk"], 2), "v1 $", round(r["v1_money_usd"], 2))
    for a in A:
        s = da.get(a, {})
        print("   ", a, "B0", round(b0.get(a, 0), 4), "end", round(bend.get(a, 0), 4), "money_net(-=paid)", round(s.get("usd", 0), 2), "ntx", s.get("n", 0))
    e = post[post["from_addr"].isin(A) & post["to_addr"].isin(A)]
    for _, x in e.iterrows():
        h = x["tx_hash"]
        print("      edge", x["from_addr"][:10], "->", x["to_addr"][:10], round(x["value_wgnk"], 6), "blk", x["block_number"], h, "sender", (txs.get(h) or {}).get("from", "")[:10])
    # separate vs merged payout (option 1 approximated with total M=netA + min(netB,0))
    sep_val = 0.0
    for a in A:
        s = d[d["address"] == a]
        mA = -s.loc[s.win == "A", "d_usd"].sum(); mB = -s.loc[s.win == "B", "d_usd"].sum()
        m = mA + (mB if mB <= 0 else 0)
        h0 = b0.get(a, 0)
        sep_val += (h0 * P0 + m) if m > 0.005 else max(0.0, h0 + m / P0) * P0
    rows.append({"entity": r["entity"], "n_addr": len(A), "merged_v1_value": r["v1_value_usd"], "separate_v1_value_approx": sep_val, "diff": sep_val - r["v1_value_usd"],
                 "min_edge_wgnk": e["value_wgnk"].min() if len(e) else None, "category": r["category"], "is_hacker": r["is_hacker"]})
x = pd.DataFrame(rows)
print(x.round(2).to_string())
print("sum diff (separate - merged), non hacker:", x.loc[~x.is_hacker, "diff"].sum())
x.to_csv(f"{OUT}/clusters_effect.csv", index=False)

# Hubs: reproduce plain edges
INFRA_GUESS = set()
pool_like = set(pools()["pool_id"].str.lower())
print("pools table:"); print(pools().to_string())
