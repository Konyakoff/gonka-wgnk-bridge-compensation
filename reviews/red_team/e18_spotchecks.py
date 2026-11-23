"""Spot checks for individual statements in the report."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *
v = variants(); vi = v.set_index("entity"); nh = v[~v.is_hacker].copy()
E = pd.read_csv(f"{OUT}/plain_edges.csv"); txs = jz("02_onchain_raw/ethereum/post_txs.json.gz")
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
E["ent"] = E.a.map(ent_of); m = E[E.same_owner]
mx = m.groupby("ent").wgnk.max().sort_values()
print("clusters whose largest merging transfer is < 20 WGNK:", int((mx < 20).sum())); print(mx.head(8).to_string())
nh["kept"] = (-(nh.honest_wgnk * P0 + nh.v1_m_usd)).clip(lower=0)
k = nh[nh.kept > 0.01]
print("queued post-hack burns of profit keepers:", k[k.burn_pending_post > 0].burn_pending_post.sum(), "owners", int((k.burn_pending_post > 0).sum()))
u = pd.read_csv(f"{OUT}/unattributed_wgnk_moves.csv")
x = u[(u.entity == "0x024860b646a1221a802df406f8a6acadd2c37622") & (u.d_wgnk < 0) & u.other_tokens.fillna("").str.contains("0x2162fdb1")]
print("0x024860 sales for token 0x2162fdb1…: n", len(x), "WGNK", x.d_wgnk.sum(), "est USD at pool price", x.est_usd.sum(), "token units", sum(int(s.split(":")[1]) for s in x.other_tokens) / 1e18)
r = E[(E.a == "0x34b9a31cd689bb73707f671b4cededad87afd99f")]
for t in r.itertuples():
    print("0x34b9 edge", t.wgnk, t.tx, "tx sender", txs[t.tx]["from"], "block", t.block)
print("refunded owners: WGNK held at T2 above pre-hack wallet balance:", (nh[nh.v1_money_usd > 0.01].wgnk_end_wallet - nh[nh.v1_money_usd > 0.01].b0_wallet).clip(lower=0).sum())
un = nh[(~nh.v1_paid) & (nh.honest_wgnk > 0)]
print("unpaid with H>0:", len(un), "| H<=0.5:", int((un.honest_wgnk <= 0.5).sum()), "| H>0.5:", int((un.honest_wgnk > 0.5).sum()), un[un.honest_wgnk > 0.5].honest_wgnk.sum())
