"""Trades right after the warning; passive LP losses in window B; router/filler contracts in the register; a cluster example;
pending post-hack burns of refunded owners; common funding source of the largest recipients."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); d = deltas(); tr = transfers(); reg = register()
txs, rcs, ints, px = load_raw()
vi = v.set_index("entity"); ri = reg.set_index("owner_eth_address")
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
b0 = balances(tr, SNAP_BLOCK)

print("== 1. Purchases shortly after the warning (window B, non-LP, money out)")
b = d[(d.win == "B") & (~d.is_lp_tx) & (d.d_usd < -0.01) & (d.d_wgnk >= 1)]
for name, sec in [("60 s", 60), ("5 min", 300), ("15 min", 900), ("30 min", 1800), ("71.6 min (until press repeat)", 4294)]:
    x = b[b.ts <= WARN_TS + sec]
    print(f"   within {name:30s}: txs {len(x):4d} owners {x.entity.nunique():3d} USD {-x.d_usd.sum():10.2f}")
print("   whole window B purchases: txs", len(b), "owners", b.entity.nunique(), "USD", round(-b.d_usd.sum(), 2))
nb = v[(~v.is_hacker) & (v.net_b_usd > 0.01)]
print("   owners with a net window-B loss:", len(nb), "USD", round(nb.net_b_usd.sum(), 2), "| paid for it in v1: 0; v2:", round((nb.v2_value_usd - nb.v1_value_usd).sum(), 2), "v3:", round((nb.v3_value_usd - nb.v1_value_usd).sum(), 2))
print("   first block of window B:", T1_BLOCK + 1, "ts", jz("02_onchain_raw/ethereum/block_ts.json").get(str(T1_BLOCK + 1)), "warning ts", WARN_TS)

print("\n== 2. Passive LP losses after the warning (position money T1 -> T2, no own liquidity tx in B)")
lpw = v[(v.lp_u_t1 - v.lp_u_end > 0.01)]
print(lpw[["entity", "category", "lp_u_t1", "lp_u_end", "b_lp_usd", "net_b_usd", "v1_money_usd", "v2_money_usd", "v3_money_usd"]].round(2).to_string())
pas = lpw[lpw.b_lp_usd < 0.01]
print("   passive (no LP tx in B): owners", len(pas), "drain USD", round((pas.lp_u_t1 - pas.lp_u_end).sum(), 2))

print("\n== 3. Routers / fillers / fee wallets in the register")
for a in ["0x6fd41c212afff4a24e5e4b561eb79456f4212786", "0x36331e299247e5d0d3261e1d9852f6e0cffee95c", "0x948640fd10c92cfae5df42c3f3f2cb6528a3e3c3", "0x90cbe4bdd538d6e9b379bff5fe72c3d67a521de5",
          "0x1111115af63bfbcc151e5753e2ea1a29c79d2f01", "0x1111110f0f73c0b2ef09ec012eae758b3e03a902", "0x8f10b468b06c6fd214b65f87778827f7d113f996", "0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae",
          "0x74de5d4fcbf63e00296fd95d33236b9794016631", "0xfaa8177f2041bef63bb6c4ec4dfd3e80394fd8c2", "0xd0162a989355b507f696feec3b835f073fe092d3", "0x3e07be15370d8b12d80a159a7ef14b9e51869497",
          "0xb92fe925dc43a0ecde6c8b1a2709c170ec4fff4f", "0x2ba3d1b5648d64f292cac81cbb0dbee18c1c25cd"]:
    e = ent_of.get(a)
    if e is None:
        print("  ", a, "not in register; B0", round(b0.get(a, 0), 4)); continue
    x = vi.loc[e]
    print("  ", a, x.category, "| status:", ri.gonka_address_status.get(e), "| H", round(x.honest_wgnk, 4), "netA", round(x.net_a_usd, 2), "netB", round(x.net_b_usd, 2), "n_tx", int(x.a_n_tx + x.b_n_tx),
          "| v1 gnk", round(x.v1_pay_gnk, 2), "v1 $", round(x.v1_money_usd, 2), "v3 $", round(x.v3_money_usd, 2))

print("\n== 4. Cluster 0x9491d9bf… edges")
E = pd.read_csv(f"{OUT}/plain_edges.csv")
A = vi.loc["0x9491d9bf3f3390f5077ec864f41eee8f6e94feac", "addresses"].split(";")
e = E[E.a.isin(A) & E.b.isin(A)]
for r in e.itertuples():
    print("  ", r.a, "->", r.b, round(r.wgnk, 4), "block", r.block, "tx sender", (txs.get(r.tx) or {}).get("from"), r.tx)
A = vi.loc["0x3bf3d3edf01b3b32c6da935ceee20df24e918a8d", "addresses"].split(";")
e = E[E.a.isin(A) & E.b.isin(A)]
for r in e.itertuples():
    print("  ", r.a, "->", r.b, round(r.wgnk, 4), "block", r.block, "win", "A" if r.block <= T1_BLOCK else "B", "tx sender", (txs.get(r.tx) or {}).get("from"))

print("\n== 5. Pending post-hack burns (BRIDGE_PENDING on Gonka) of owners who are also refunded / paid")
x = v[(v.burn_pending_post > 0) & (~v.is_hacker)]
print("   owners", len(x), "WGNK", round(x.burn_pending_post.sum(), 2), "| of them paid in v1:", int(x.v1_paid.sum()), "v1 value", round(x[x.v1_paid].v1_value_usd.sum(), 2),
      "| money-refunded:", int((x.v1_money_usd > 0.01).sum()), "refund", round(x[x.v1_money_usd > 0.01].v1_money_usd.sum(), 2), "their pending burns", round(x[x.v1_money_usd > 0.01].burn_pending_post.sum(), 2))
print("   pending burns at p0 if the bridge ever completed them: USD", round(x.burn_pending_post.sum() * P0, 2))

print("\n== 6. Common funding source gonka1gyy3… -> 0xbd3ca5a4… -> ...")
src = "0xbd3ca5a43f72e45faf4b142832110842113dc9f8"
pre = tr[tr.block_number <= SNAP_BLOCK]
out = pre[pre.from_addr == src].groupby("to_addr").value_wgnk.sum().sort_values(ascending=False)
tot_v, tot_g, tot_m = 0, 0, 0
for a, w in out.items():
    e = ent_of.get(a)
    if e in vi.index:
        x = vi.loc[e]; tot_v += x.v1_value_usd; tot_g += x.v1_pay_gnk; tot_m += x.v1_money_usd
        print("  ", a, "received", round(w, 2), "|", x.category, "H", round(x.honest_wgnk, 2), "v1 gnk", round(x.v1_pay_gnk, 2), "v1 money", round(x.v1_money_usd, 2), "v1 value", round(x.v1_value_usd, 2))
    else:
        print("  ", a, "received", round(w, 2), "| not in register")
x = vi.loc[src]; tot_v += x.v1_value_usd; tot_g += x.v1_pay_gnk; tot_m += x.v1_money_usd
print("   source itself: H", round(x.honest_wgnk, 2), "v1 value", round(x.v1_value_usd, 2))
T = v[~v.is_hacker]
print(f"   group total: value ${tot_v:,.2f} ({tot_v / T.v1_value_usd.sum():.4f} of all), GNK {tot_g:,.2f} ({tot_g / T.v1_pay_gnk.sum():.4f}), money ${tot_m:,.2f} ({tot_m / T.v1_money_usd.sum():.4f}); USDT share {vi.loc['0x244186297b43ba43c92d68efe78c04170fbc0b10', 'v1_pay_usdt'] / T.v1_pay_usdt.sum():.4f}")
mr = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/bridge_mint_requests_gonka.parquet")
print(mr[mr.dest.str.lower() == src][["block_time", "signer", "gnk"]].to_string())
print("   pool 0.3% first liquidity events by 0x244186: 2026-06-09 13:23-14:30 UTC (see e09)")
