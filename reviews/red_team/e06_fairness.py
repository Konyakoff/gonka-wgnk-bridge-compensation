"""Fairness: who keeps profits; purchases after the hack was public (Blockaid alert) but before the official warning;
purchases at crash prices; window-B netting; post-hack bridge burns by refunded buyers; concentration."""
import sys
sys.path.insert(0, "/work")
from rt_common import *

v = variants(); d = deltas()
nh = v[~v.is_hacker].copy()
BLOCKAID = 1795026507; DEFIANT = 1795040665  # 18:28:27 ; 22:24:25 UTC (publications timeline rows 4 and 15)
OFFICIAL1 = 1795047508

# ---- 1. profits kept
nh["raw_value_v1"] = nh.honest_wgnk * P0 + nh.v1_m_usd          # formula value before max(0)
nh["kept_profit"] = (-(nh.honest_wgnk * P0 + nh.v1_m_usd)).clip(lower=0)
kp = nh[nh.kept_profit > 0.01].sort_values("kept_profit", ascending=False)
print("1. PROFIT KEPT (formula value below zero, floored at 0): owners", len(kp), "USD", round(kp.kept_profit.sum(), 2))
print("   >= $100:", int((kp.kept_profit >= 100).sum()), " >= $1000:", int((kp.kept_profit >= 1000).sum()), " top10 sum", round(kp.kept_profit.head(10).sum(), 2))
print(kp[["entity", "category", "honest_wgnk", "net_a_usd", "net_b_usd", "a_w_in", "a_usd_out", "a_w_out", "a_usd_in", "kept_profit", "wgnk_end_wallet"]].head(15).round(2).to_string())
kp[["entity", "addresses", "category", "honest_wgnk", "net_a_usd", "net_b_usd", "kept_profit", "wgnk_end_wallet"]].to_csv(f"{OUT}/profit_keepers.csv", index=False)
print("   by category:"); print(kp.groupby("category").kept_profit.agg(["count", "sum"]).round(2).to_string())
print("   gains deducted from holders (GNK reduced): owners", int(((nh.v1_m_usd < -0.005) & (nh.honest_wgnk > 0)).sum()),
      "GNK deducted", round((nh.honest_wgnk - nh.g_credited - nh.v1_pay_gnk).clip(lower=0)[nh.v1_m_usd <= 0.005].sum(), 2))
print("   total money refunds v1 USD", round(nh.v1_money_usd.sum(), 2), " hacker net (model):", v[v.is_hacker][["net_a_usd", "net_b_usd"]].round(2).to_dict("records"))

# ---- 2. timing & price of window-A purchases (non-LP txs)
a = d[(d.win == "A") & (~d.is_lp_tx)].copy()
buys = a[(a.d_usd < -0.01) & (a.d_wgnk >= 1)].copy()
buys["price"] = -buys.d_usd / buys.d_wgnk
buys["rel"] = buys.price / P0
ent_cat = v.set_index("entity").category
buys = buys[~buys.entity.isin(v[v.is_hacker].entity)]
print("\n2. WINDOW-A PURCHASES (gross): n", len(buys), "USD", round(-buys.d_usd.sum(), 2), "WGNK", round(buys.d_wgnk.sum(), 0), "owners", buys.entity.nunique())
bins = [(-1, BLOCKAID, "before Blockaid alert 18:28:27"), (BLOCKAID, DEFIANT, "alert .. The Defiant 22:24"), (DEFIANT, OFFICIAL1, "22:24 .. first official post 00:18:28"), (OFFICIAL1, WARN_TS + 1, "00:18:28 .. warning 00:24:07")]
for lo, hi, name in bins:
    x = buys[(buys.ts > lo) & (buys.ts <= hi)]
    print(f"   {name:45s} n {len(x):4d} owners {x.entity.nunique():4d} USD {-x.d_usd.sum():12.2f} WGNK {x.d_wgnk.sum():14.0f} avg price/p0 {(-x.d_usd.sum() / x.d_wgnk.sum() / P0 if len(x) else 0):.3f}")
for lo, hi in [(0, 0.1), (0.1, 0.25), (0.25, 0.5), (0.5, 0.8), (0.8, 10)]:
    x = buys[(buys.rel >= lo) & (buys.rel < hi)]
    print(f"   price {lo:.2f}-{hi:.2f} x p0: n {len(x):4d} owners {x.entity.nunique():4d} USD {-x.d_usd.sum():12.2f} WGNK {x.d_wgnk.sum():14.0f}")
print("   median price/p0 of purchases after alert:", round(buys[buys.ts > BLOCKAID].rel.median(), 4), " max price/p0 after the mint:", round(buys.rel.max(), 3))

# per owner: refund (v1 money) split by whether first purchase was after the alert
first_buy = buys.groupby("entity").ts.min()
gross_after = buys[buys.ts > BLOCKAID].groupby("entity").d_usd.sum().mul(-1)
gross_all = buys.groupby("entity").d_usd.sum().mul(-1)
nh = nh.set_index("entity")
nh["first_buy_ts"] = first_buy; nh["gross_a"] = gross_all; nh["gross_a_after_alert"] = gross_after
m = nh[(nh.v1_money_usd > 0.01) & (nh.category != "lp")]
print("\n   Non-LP owners with a money refund in option 1:", len(m), "USD", round(m.v1_money_usd.sum(), 2))
x = m[m.first_buy_ts > BLOCKAID]
print("   ... all of whose window-A purchases came AFTER the Blockaid alert:", len(x), "USD refund", round(x.v1_money_usd.sum(), 2))
x2 = m[m.first_buy_ts > DEFIANT]
print("   ... all purchases after The Defiant article (22:24):", len(x2), "USD refund", round(x2.v1_money_usd.sum(), 2))
x3 = m[m.first_buy_ts <= BLOCKAID]
print("   ... first purchase before the alert:", len(x3), "USD refund", round(x3.v1_money_usd.sum(), 2), "of which gross spent after alert", round(x3.gross_a_after_alert.fillna(0).sum(), 2))
share_after = (m.gross_a_after_alert.fillna(0) / m.gross_a).clip(upper=1).fillna(0)
print("   refund attributable pro rata to purchases after the alert:", round((m.v1_money_usd * share_after).sum(), 2))
# weighted avg price by owner
wp = buys.groupby("entity").apply(lambda g: -g.d_usd.sum() / g.d_wgnk.sum() / P0)
nh["avg_buy_rel"] = wp
m = nh[(nh.v1_money_usd > 0.01) & (nh.category != "lp")]
for lo, hi in [(0, 0.1), (0.1, 0.25), (0.25, 0.5), (0.5, 0.8), (0.8, 10)]:
    y = m[(m.avg_buy_rel >= lo) & (m.avg_buy_rel < hi)]
    print(f"   refunded owners with avg buy price {lo:.2f}-{hi:.2f} x p0: {len(y):4d} refund USD {y.v1_money_usd.sum():12.2f}")
print("   refunded owners without any tagged purchase (avg price n/a):", int(m.avg_buy_rel.isna().sum()), round(m[m.avg_buy_rel.isna()].v1_money_usd.sum(), 2))
m.reset_index()[["entity", "category", "honest_wgnk", "v1_money_usd", "first_buy_ts", "gross_a", "gross_a_after_alert", "avg_buy_rel", "burn_pending_post", "wgnk_end_wallet"]].sort_values("v1_money_usd", ascending=False).to_csv(f"{OUT}/refunded_buyers_timing_price.csv", index=False)
print(m.reset_index()[["entity", "category", "honest_wgnk", "v1_money_usd", "first_buy_ts", "gross_a_after_alert", "avg_buy_rel", "burn_pending_post", "wgnk_end_wallet"]].sort_values("v1_money_usd", ascending=False).head(25).round(3).to_string())

# ---- 3. post-hack burns
bp = nh[nh.burn_pending_post > 0].sort_values("burn_pending_post", ascending=False)
print("\n3. POST-HACK BRIDGE BURNS (voided): owners", len(bp), "WGNK", round(bp.burn_pending_post.sum(), 2))
print(bp[["category", "honest_wgnk", "burn_pending_post", "v1_pay_gnk", "v1_money_usd", "net_a_usd", "avg_buy_rel"]].head(20).round(2).to_string())
y = bp[(bp.v1_money_usd > 0.01)]
print("   refunded-in-money owners who also tried to burn bought WGNK into GNK after the hack:", len(y), "refund", round(y.v1_money_usd.sum(), 2), "burned", round(y.burn_pending_post.sum(), 2))
y2 = bp[bp.burn_pending_post > bp.honest_wgnk + 1]
print("   owners who burned more than their pre-hack holding:", len(y2), "excess WGNK", round((y2.burn_pending_post - y2.honest_wgnk).sum(), 2))

# ---- 4. window-B netting in option 1
b1 = nh[(nh.net_b_usd > 0) & (nh.b_usd_in > 0.01)]
print("\n4. WINDOW-B NETTING: owners with net_B>0 (ignored in option 1) who also RECEIVED money in window B:", len(b1), "proceeds ignored", round(b1.b_usd_in.sum(), 2))
print(b1[["category", "honest_wgnk", "net_a_usd", "net_b_usd", "b_usd_out", "b_usd_in", "b_w_in", "b_w_out", "v1_money_usd", "v1_pay_gnk"]].sort_values("b_usd_in", ascending=False).head(15).round(2).to_string())
bb = b1[b1.v1_money_usd > 0.01]
print("   of them with a money refund in option 1:", len(bb), "window-B proceeds not deducted", round(bb.b_usd_in.sum(), 2))
# discontinuity: owners with gains in B deducted
g = nh[nh.net_b_usd < -0.01]
print("   owners with net_B<0 (gain deducted in all options):", len(g), "USD", round(g.net_b_usd.sum(), 2))

# ---- 5. tokens still held by refunded owners
r = nh[nh.v1_money_usd > 0.01]
print("\n5. Refunded owners (money, v1):", len(r), "still hold WGNK at T2:", round(r.wgnk_end_wallet.sum(), 0), "of which above pre-hack B0:", round((r.wgnk_end_wallet - r.b0_wallet).clip(lower=0).sum(), 0))
print("   all owners end wallet WGNK", round(nh.wgnk_end_wallet.sum(), 0), "; hacker end", v[v.is_hacker].wgnk_end_wallet.round(0).tolist())
