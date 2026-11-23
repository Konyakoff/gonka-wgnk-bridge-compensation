"""Independent verifications: raw receipts vs model rows; v3 position amounts from liquidity math; register vs model;
unscanned v4 withdrawals priced with liquidity math; unpaid dust."""
import sys, math
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); d = deltas(); reg = register(); tr = transfers()
txs, rcs, ints, px = load_raw()

print("== 1. Raw receipts vs model rows (all rows)")
bad_w = bad_u = via_bad = 0; n = 0; max_w = max_u = 0.0
cache = {}
for r in d.itertuples():
    if r.tx_hash not in cache:
        cache[r.tx_hash] = parse_tx(r.tx_hash, txs, rcs, ints, px)
    t = cache[r.tx_hash]; n += 1
    dw = t["dw"].get(r.address, 0.0); max_w = max(max_w, abs(dw - r.d_wgnk))
    if abs(dw - r.d_wgnk) > 1e-6:
        bad_w += 1
    own = t["usd"].get(r.address, 0.0)
    if not r.via_third_party:
        max_u = max(max_u, abs(own - r.d_usd))
        if abs(own - r.d_usd) > 0.005:
            bad_u += 1
    else:
        payers = r.via_third_party.split(";")
        movers = [a for a, w in t["dw"].items() if abs(w) >= 1 and abs(t["usd"].get(a, 0.0)) < 0.01 and (w > 0) == (dw > 0) and a not in INFRA and a not in POOLS]
        tot = sum(abs(t["dw"][a]) for a in movers) or abs(dw)
        exp = own + sum(t["usd"].get(p, 0.0) for p in payers) * abs(dw) / tot
        if abs(exp - r.d_usd) > 0.01:
            via_bad += 1
print(f"   rows {n}: WGNK mismatches {bad_w} (max {max_w:.2e}); money mismatches on rows without third-party attribution {bad_u} (max {max_u:.2e}); third-party rows not reproduced by 'own + pro-rata payer money' {via_bad}")
print("   block range of rows:", d.block.min(), d.block.max(), "| rows with block > T2:", int((d.block > T2_BLOCK).sum()), "| win A/B mislabelled:", int(((d.block <= T1_BLOCK) != (d.win == "A")).sum()))

print("\n== 2. v3 positions at the snapshot from liquidity math (independent of the model's amounts)")
lpx = jz("02_onchain_raw/ethereum/lp_extra.json"); fees = jz("02_onchain_raw/ethereum/lp_fees.json")
print("   lp_extra keys", list(lpx.keys()), "| lp_fees keys", list(fees.keys()))
lp = lp_positions()


def amounts(liq, tl, tu, sp):
    s = sp / 2 ** 96; a = math.sqrt(1.0001 ** tl); b = math.sqrt(1.0001 ** tu)
    if liq <= 0:
        return 0.0, 0.0
    if s <= a:
        return liq * (b - a) / (a * b), 0.0
    if s >= b:
        return 0.0, liq * (b - a)
    return liq * (b - s) / (s * b), liq * (s - a)


rows = []
for r in lp[(lp.version == "v3")].itertuples():
    sp = ((lpx["slot0"].get(r.pool_id) or {}).get(r.state) or {}).get("sqrt_price_x96")
    fx = ((fees.get("v3nft") or {}).get(r.pos) or (fees.get("v3own") or {}).get(r.pos) or {}).get(r.state)
    if not sp:
        continue
    liq = int(fx["liq"]) if fx else int(r.liquidity)
    a0, a1 = amounts(liq, int(r.tick_lower), int(r.tick_upper), int(sp))
    e0, e1 = (int(fx["extra0"]) / 1e9, int(fx["extra1"]) / 1e6) if fx else (0.0, 0.0)
    rows.append({"pos": r.pos, "state": r.state, "owner": r.owner, "liq_state": liq, "liq_model": int(r.liquidity), "w_mine": a0 / 1e9 + e0, "u_mine": a1 / 1e6 + e1, "w_model": r.wgnk, "u_model": r.money_amount,
                 "fees_w": e0, "fees_u": e1})
V = pd.DataFrame(rows)
V["dw"] = (V.w_mine - V.w_model).abs(); V["du"] = (V.u_mine - V.u_model).abs()
print("   positions x states checked:", len(V), "| liquidity mismatches:", int((V.liq_state != V.liq_model).sum()), "| max WGNK diff", V.dw.max(), "| max USDT diff", V.du.max())
A = "0x244186297b43ba43c92d68efe78c04170fbc0b10"
s = V[(V.owner == A) & (V.state == "snap")]
print("   0x244186 at snapshot: WGNK", s.w_mine.sum(), "USDT", s.u_mine.sum(), "| of which owed/uncollected fees: WGNK", s.fees_w.sum(), "USDT", s.fees_u.sum())
sl = lpx["slot0"]
for pool, x in sl.items():
    for tag, y in x.items():
        p = (int(y["sqrt_price_x96"]) / 2 ** 96) ** 2 * 1e3
        print(f"   pool {pool[:10]} {tag}: price {p:.6f} USDT/WGNK tick {y.get('tick')}")
pb = lpx.get("pool_balances") or {}
for pool, x in pb.items():
    print("   pool balances", pool[:10], {tag: {k[:6]: round(val / (1e9 if k.startswith('0x972a') else 1e6), 2) for k, val in y.items()} for tag, y in x.items()})

print("\n== 3. Unscanned v4 withdrawals priced with liquidity math")
vm = pd.read_parquet(f"{P}/02_onchain_raw/ethereum/v4_modify_liquidity.parquet")
for name, liq, tl, tu in [("v4:517966 (0x4467aa35…) removal blk 26443850, all-USDT case", 3579169777922, -103465, -103459),
                          ("v4:517922 (0x5ec2ea4e…) removal blk 26447492, all-USDC case", 189322381832, -880000, -123200),
                          ("v4:517965 (0xfad497df…) adds blk 26443816/850/862, all-USDC case", 4664733453 + 4261180840 + 4095923738, -177000, -105000)]:
    a = math.sqrt(1.0001 ** tl); b = math.sqrt(1.0001 ** tu)
    print(f"   {name}: money side = {liq * (b - a) / 1e6:,.4f}")
print(d[d.tx_hash == "0x178704ec9d3546382e4ea567a0b00431748e2b5760fcfd6de293ca1bf99db31d"][["address", "d_wgnk", "d_usd", "tokens", "is_lp_tx", "win"]].to_string())
x = v.set_index("entity").loc[["0x4467aa359654154abfc0eb18e88672a1b0339d76", "0x5ec2ea4ecfa01e864c3c115c96613e93d99adaa7"], ["net_a_usd", "net_b_usd", "v1_money_usd", "v2_money_usd", "v3_money_usd", "v1_pay_usdt", "v3_pay_usdt", "v3_pay_usdc"]]
print(x.round(4).to_string())

print("\n== 4. Register CSV vs model table, per owner")
m = v.set_index("entity"); rr = reg.set_index("owner_eth_address")
mx = {}
for o in ("v1", "v2", "v3"):
    for k in ("gnk", "usdt", "usdc", "dai", "eth"):
        mx[f"{o}_{k}"] = float((rr[f"{o}_{k}"] - m.loc[rr.index, f"{o}_pay_{k}"]).abs().max())
print("   owners in register:", len(rr), "in model:", len(m), "| max abs diff per column:", {k: round(x, 9) for k, x in mx.items() if x > 0} or "all zero")
print("   rows with a payout listed in the register although is_hacker:", int((rr.loc[m[m.is_hacker].index, ["v1_paid", "v2_paid", "v3_paid"]]).any(axis=1).sum()))
nh = v[~v.is_hacker]
unpaid = nh[(~nh.v1_paid) & (nh.honest_wgnk > 0)]
print("   owners with pre-hack WGNK > 0 but not paid in option 1:", len(unpaid), "| H total", round(unpaid.honest_wgnk.sum(), 4), "| of them with H > 0.5 (zeroed by deducted gains):", int((unpaid.honest_wgnk > 0.5).sum()),
      "H", round(unpaid[unpaid.honest_wgnk > 0.5].honest_wgnk.sum(), 2))
print(unpaid[unpaid.honest_wgnk > 0.5][["entity", "category", "honest_wgnk", "net_a_usd", "net_b_usd", "burn_pending_post"]].round(2).to_string())
red = nh[(nh.v1_pay_gnk < nh.honest_wgnk - nh.g_credited - 0.5)]
print("   owners whose GNK is reduced by deducted gains:", len(red), "GNK cut", round((red.honest_wgnk - red.v1_pay_gnk).sum(), 2), "USD", round((red.honest_wgnk - red.v1_pay_gnk).sum() * P0, 2))
print(red.assign(cut=red.honest_wgnk - red.v1_pay_gnk)[["entity", "category", "honest_wgnk", "v1_pay_gnk", "cut", "net_a_usd", "net_b_usd"]].sort_values("cut", ascending=False).head(12).round(2).to_string())
