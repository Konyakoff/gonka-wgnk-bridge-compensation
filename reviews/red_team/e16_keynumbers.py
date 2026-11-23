"""Key numbers quoted in REDTEAM_REPORT.md, computed in one place, plus the remaining CSVs of affected addresses."""
import sys
sys.path.insert(0, "/work")
from rt_common import *

v = variants(); d = deltas(); reg = register()
nh = v[~v.is_hacker].copy(); vi = v.set_index("entity")
K = {}
T_val, T_money, T_gnk, T_usdt, T_eth = nh.v1_value_usd.sum(), nh.v1_money_usd.sum(), nh.v1_pay_gnk.sum(), nh.v1_pay_usdt.sum(), nh.v1_pay_eth.sum()
summ = jz("03_model/summary_three_options.json"); topup = summ["variants"]["v1"]["cost_usd"]
K["totals_v1"] = {"value_usd": T_val, "money_usd": T_money, "gnk": T_gnk, "usdt": T_usdt, "eth": T_eth, "recipients": int(nh.v1_paid.sum()), "top_up_usd": topup}

# F1 concentration
A, B, C, D4 = "0x244186297b43ba43c92d68efe78c04170fbc0b10", "0xbd3ca5a43f72e45faf4b142832110842113dc9f8", "0xdf9f1857b655263c2e8669e7e57a8e4fa57115db", "0x6c07e00cc3847b687fbde78baa184c5098116c51"
g = vi.loc[[A, B, C]]
s = nh.sort_values("v1_value_usd", ascending=False)
lp_like = nh[(nh.lp_w_before.abs() + nh.lp_u_before.abs() + nh.lp_u_t1.abs() + nh.lp_u_end.abs() > 1e-9) | (nh.category == "lp")]
K["F1"] = {"top1_value": vi.v1_value_usd[A], "top1_share_value": vi.v1_value_usd[A] / T_val, "top1_money": vi.v1_money_usd[A], "top1_share_money": vi.v1_money_usd[A] / T_money,
           "top1_share_usdt": vi.v1_pay_usdt[A] / T_usdt, "top1_gnk": vi.v1_pay_gnk[A], "top1_share_gnk": vi.v1_pay_gnk[A] / T_gnk,
           "group3_value": g.v1_value_usd.sum(), "group3_share_value": g.v1_value_usd.sum() / T_val, "group3_gnk": g.v1_pay_gnk.sum(), "group3_share_gnk": g.v1_pay_gnk.sum() / T_gnk,
           "second_lp_value": vi.v1_value_usd[D4], "second_lp_eth": vi.v1_pay_eth[D4], "second_lp_share_eth": vi.v1_pay_eth[D4] / T_eth, "second_lp_share_value": vi.v1_value_usd[D4] / T_val,
           "top5_share_value": s.v1_value_usd.head(5).sum() / T_val, "top10_share_value": s.v1_value_usd.head(10).sum() / T_val, "top20_share_value": s.v1_value_usd.head(20).sum() / T_val,
           "lp_owners": len(lp_like), "lp_share_value": lp_like.v1_value_usd.sum() / T_val, "lp_share_money": lp_like.v1_money_usd.sum() / T_money, "lp_value": lp_like.v1_value_usd.sum(), "lp_money": lp_like.v1_money_usd.sum(),
           "top1_money_share_of_topup": vi.v1_money_usd[A] / topup}
pd.DataFrame([{"address": a, "role": r, "honest_wgnk": vi.honest_wgnk[a], "v1_gnk": vi.v1_pay_gnk[a], "v1_money_usd": vi.v1_money_usd[a], "v1_value_usd": vi.v1_value_usd[a]} for a, r in
              [(A, "main LP of the 0.3% pool; received 2,500,100 WGNK from 0xbd3ca5a4"), (B, "received 3,001,000 WGNK minted for Gonka signer gonka1gyy3…399r on 2026-06-09"), (C, "received 200,100 WGNK from 0xbd3ca5a4"),
               (D4, "sole LP of the WGNK/ETH v4 pool, positions opened 2026-11-13, bridged in 528,168 GNK at 15:30 UTC on the day of the hack")]]).to_csv(f"{OUT}/largest_recipient_group.csv", index=False)

# F3 profits kept
nh["kept"] = (-(nh.honest_wgnk * P0 + nh.v1_m_usd)).clip(lower=0)
kp = nh[nh.kept > 0.01]
K["F3"] = {"owners": len(kp), "usd": kp.kept.sum(), "share_of_topup": kp.kept.sum() / topup, "ge_1000": int((kp.kept >= 1000).sum()), "top10": kp.kept.nlargest(10).sum(), "trader_profit_cat": kp[kp.category == "trader_profit"].kept.sum(),
           "hacker_dump_proceeds": float(-v[v.is_hacker].net_a_usd.sum()), "gnk_deducted_from_holders": float((nh.honest_wgnk - nh.g_credited - nh.v1_pay_gnk).clip(lower=0)[nh.v1_m_usd <= 0.005].sum())}

# F6 post-hack burns
x = nh[nh.burn_pending_post > 0]
r = x[x.v1_money_usd > 0.01]
K["F6"] = {"owners": len(x), "wgnk": x.burn_pending_post.sum(), "usd_at_p0": x.burn_pending_post.sum() * P0, "refunded_owners": len(r), "refund_usd": r.v1_money_usd.sum(), "their_burns": r.burn_pending_post.sum(),
           "end_wallet_all": nh.wgnk_end_wallet.sum(), "end_wallet_refunded": nh[nh.v1_money_usd > 0.01].wgnk_end_wallet.sum()}
x.sort_values("burn_pending_post", ascending=False)[["entity", "addresses", "category", "honest_wgnk", "burn_pending_post", "net_a_usd", "v1_pay_gnk", "v1_money_usd"]].to_csv(f"{OUT}/posthack_burners.csv", index=False)

# F9 window-B netting
b1 = nh[(nh.net_b_usd > 0) & (nh.b_usd_in > 0.01)]
K["F9"] = {"owners": len(b1), "proceeds_ignored": b1.b_usd_in.sum(), "refunded_owners": int((b1.v1_money_usd > 0.01).sum()), "their_proceeds": b1[b1.v1_money_usd > 0.01].b_usd_in.sum()}
b1[["entity", "category", "honest_wgnk", "net_a_usd", "net_b_usd", "b_usd_out", "b_usd_in", "v1_money_usd", "v1_pay_gnk"]].to_csv(f"{OUT}/window_b_netting.csv", index=False)

# F13 claims
rr = reg[reg.v1_paid]
gg = rr.groupby("gonka_address_status").agg(n=("v1_gnk", "count"), gnk=("v1_gnk", "sum"), value=("v1_value_usd", "sum"))
K["F13"] = {k: {"n": int(x.n), "gnk": float(x.gnk), "value": float(x.value), "share": float(x.value / rr.v1_value_usd.sum())} for k, x in gg.iterrows()}
K["options"] = {o: {"recipients": int(nh[f"{o}_paid"].sum()), "value": float(nh[f"{o}_value_usd"].sum()), "money": float(nh[f"{o}_money_usd"].sum())} for o in ("v1", "v2", "v3")}
nb = nh[nh.net_b_usd > 0.01]
K["window_b"] = {"owners_net_loss": len(nb), "usd": nb.net_b_usd.sum(), "v2_extra": (nb.v2_value_usd - nb.v1_value_usd).sum(), "v3_extra": (nb.v3_value_usd - nb.v1_value_usd).sum()}
print(json.dumps(K, indent=1, default=float))
json.dump(K, open(f"{OUT}/key_numbers.json", "w"), indent=1, default=float)
