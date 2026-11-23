"""Coverage checks: B0 recomputation, excluded balances, contracts / never-signed recipients, hub-like holders, mints and burns around
the hack, pending burns, LP event coverage, hacker links, non-monotonic owner."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); d = deltas(); tr = transfers(); reg = register()
txs, rcs, ints, px = load_raw()
vi = v.set_index("entity")
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
b0 = balances(tr, SNAP_BLOCK); bend = balances(tr, T2_BLOCK)

print("== 1. B0 recomputation for every owner")
v["b0_mine"] = v.addresses.map(lambda s: sum(b0.get(a, 0.0) for a in s.split(";")))
print("   max |b0_wallet - mine|:", (v.b0_wallet - v.b0_mine).abs().max(), " supply at snapshot from log:", b0[b0.index != ZERO].sum())
allreg = set(ent_of)
miss = b0[(~b0.index.isin(allreg)) & (b0.index != ZERO) & (b0.abs() > 1e-9)]
print("   addresses with B0 != 0 not in the register:", len(miss), "WGNK", miss.sum())
print(miss.sort_values(ascending=False).head(15).to_string())
print("   negative balances at snapshot:", int((b0[b0.index != ZERO] < -1e-9).sum()))

print("\n== 2. Recipients by address status (option 1)")
r = reg[reg.v1_paid]
g = r.groupby("gonka_address_status").agg(n=("v1_gnk", "count"), gnk=("v1_gnk", "sum"), value=("v1_value_usd", "sum"))
g["share_value"] = g.value / r.v1_value_usd.sum()
print(g.round(4).to_string())
for st in ("smart contract - claim needed", "no outgoing tx - claim needed"):
    print("  top", st); print(r[r.gonka_address_status == st].sort_values("v1_value_usd", ascending=False)[["owner_eth_address", "category", "honest_wgnk", "v1_gnk", "v1_value_usd"]].head(12).round(2).to_string())
print("   'derived from signature' but key never signed on Gonka:", int(((r.gonka_address_status == "derived from signature") & (~r.gonka_key_already_signed)).sum()),
      "GNK", round(r[(r.gonka_address_status == "derived from signature") & (~r.gonka_key_already_signed)].v1_gnk.sum(), 2))

print("\n== 3. Pre-hack counterparties of large holders (custodian / exchange / distributor pattern)")
pre = tr[tr.block_number <= SNAP_BLOCK]
indeg = pre.groupby("to_addr").from_addr.nunique(); outdeg = pre.groupby("from_addr").to_addr.nunique()
big = v[(v.honest_wgnk > 1000) | (v.v1_value_usd > 500)]
rows = []
for x in big.itertuples():
    for a in x.addresses.split(";"):
        rows.append((a, x.category, round(x.honest_wgnk, 1), int(indeg.get(a, 0)), int(outdeg.get(a, 0)), reg.set_index("owner_eth_address").gonka_address_status.get(x.entity)))
dd = pd.DataFrame(rows, columns=["address", "cat", "H", "senders_in", "recipients_out", "status"])
print(dd.sort_values("recipients_out", ascending=False).head(15).to_string())
print(dd.sort_values("senders_in", ascending=False).head(10).to_string())
alldeg = pd.DataFrame({"in": indeg, "out": outdeg}).fillna(0)
alldeg["tot"] = alldeg["in"] + alldeg["out"]
print("  most connected addresses in the whole pre-hack log:");
top = alldeg.sort_values("tot", ascending=False).head(15)
top["in_register"] = top.index.isin(allreg); top["b0"] = [b0.get(a, 0) for a in top.index]
print(top.to_string())

print("\n== 4. Mints / burns around the hack")
mints = tr[tr.from_addr == ZERO]; burns = tr[tr.to_addr == ZERO]
pm = mints[mints.block_number > SNAP_BLOCK]
print("   mints after snapshot:", len(pm), "WGNK", pm.value_wgnk.sum()); print(pm[["block_number", "tx_hash", "to_addr", "value_wgnk"]].to_string())
print("   mints in the 48h before (blocks >= T0-14400):", len(mints[(mints.block_number > T0_BLOCK - 14400) & (mints.block_number <= SNAP_BLOCK)]))
pb = burns[burns.block_number > SNAP_BLOCK]
print("   burns after snapshot:", len(pb), "WGNK", pb.value_wgnk.sum(), " by non-hacker:", pb[~pb.from_addr.isin(["0x6650a1cb0c3b970a0e4ced26984fe06db7844d80"])].value_wgnk.sum())
bt = pd.read_parquet(f"{P}/03_model/bridge_transactions_wgnk.parquet")
print("   bridge_transactions cols", list(bt.columns)); print(bt.status.value_counts().to_string())
x = bt[bt.status != "BRIDGE_COMPLETED"]
print(x.groupby(["status", x.block >= T0_BLOCK]).agg(n=("amount_gnk", "count"), gnk=("amount_gnk", "sum")).to_string())
pend_pre = bt[(bt.status == "BRIDGE_PENDING") & (bt.block < 26443613)]
print("   pending pre-hack burns:"); print(pend_pre[["block", "amount_gnk", "eth_owner", "ownerAddress"]].to_string() if "ownerAddress" in bt.columns else pend_pre.to_string())
comp_post = bt[(bt.status == "BRIDGE_COMPLETED") & (bt.block >= T0_BLOCK)]
print("   completed after T0:"); print(comp_post[["block", "amount_gnk", "eth_owner"]].to_string())
mr = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/bridge_mint_requests_gonka.parquet")
print("   gonka mint requests cols", list(mr.columns), len(mr)); print(mr.tail(8).T.to_string()[:3000])

print("\n== 5. LP event coverage")
lp = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/lp_events.parquet")
lpp = lp[(lp.block_number >= T0_BLOCK) & (lp.block_number <= T2_BLOCK)]
print("   v3/v4 lp events after T0:", len(lpp), lpp.groupby(["pool_version", "event"]).size().to_dict())
missing = lpp[~lpp.tx_hash.str.lower().isin(rcs)]
print("   lp events whose tx is NOT in post_receipts (never counted in tx deltas):", len(missing), "txs", missing.tx_hash.nunique())
print(missing[["block_number", "pool_version", "event", "owner", "amount_wgnk", "amount_usdt", "tx_hash"]].to_string())
vm = pd.read_parquet(f"{P}/02_onchain_raw/ethereum/v4_modify_liquidity.parquet")
vmp = vm[(vm.block_number >= T0_BLOCK) & (vm.block_number <= T2_BLOCK)]
m4 = vmp[~vmp.tx_hash.isin(rcs)]
print("   v4 modify events after T0:", len(vmp), "not in receipts:", len(m4)); print(m4.head(20).to_string())
sw = swaps(); swp = sw[(sw.block_number >= T0_BLOCK) & (sw.block_number <= T2_BLOCK)]
ms = swp[~swp.tx_hash.str.lower().isin(rcs)]
print("   swaps after T0:", len(swp), "not in receipts:", len(ms), "usd", ms.usd_value.astype(float).sum())
print(ms[["block_number", "pool_version", "origin_eoa", "amount_wgnk", "amount_usdt", "usd_value", "tx_hash"]].head(20).to_string())
lpos = lp_positions()
print("   lp positions: unpriced rows:"); print(lpos[lpos.get("unpriced", False) == True][["pos", "pair", "state", "owner", "wgnk", "money_token", "money_amount"]].to_string() if "unpriced" in lpos else "n/a")
print("   pairs:", lpos.groupby("pair").agg(n=("pos", "nunique")).to_dict())
ow = lpos.pivot_table(index="pos", columns="state", values="owner", aggfunc="first")
chg = ow[(ow.nunique(axis=1) > 1)]
print("   positions whose owner differs between states:", len(chg)); print(chg.head(20).to_string())

print("\n== 6. Hacker links")
h = v[v.is_hacker]
print(h[["entity", "addresses", "b0_wallet", "honest_wgnk", "net_a_usd", "wgnk_end_wallet", "g_credited", "burn_pending_post"]].to_string())
for a in ["0x2ba3d1b5648d64f292cac81cbb0dbee18c1c25cd"]:
    print("   funder", a, "in register:", a in ent_of, "B0", b0.get(a, 0))
hk = ["0x6650a1cb0c3b970a0e4ced26984fe06db7844d80", "0xde356f654e9b6ebcc7e3af869e5168885293434a"]
ht = tr[(tr.from_addr.isin(hk) | tr.to_addr.isin(hk))]
print("   hacker WGNK transfers:", len(ht));
cp = ht.assign(cp=ht.apply(lambda r: r.to_addr if r.from_addr in hk else r.from_addr, axis=1), sign=ht.from_addr.isin(hk).map({True: -1, False: 1}))
print(cp.groupby("cp").apply(lambda g: pd.Series({"n": len(g), "net_to_hacker": (g.value_wgnk * g.sign).sum(), "first_block": g.block_number.min()})).sort_values("net_to_hacker").to_string())

print("\n== 7. Non-monotonic owner (v2 value > v3 value)")
nm = v[(v.v2_value_usd - v.v3_value_usd) > 0.01]
print(nm[["entity", "category", "honest_wgnk", "net_a_usd", "net_b_usd", "k_eff", "v1_value_usd", "v2_value_usd", "v3_value_usd", "v1_pay_eth", "v2_pay_eth", "v3_pay_eth", "v2_pay_usdt", "v3_pay_usdt", "v2_pay_usdc", "v3_pay_usdc", "v2_m_usd", "v3_m_usd"]].T.to_string())
