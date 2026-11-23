"""Cluster payout key vs real holder; P2P purchases (seller keeps money, buyer refunded); third-party attributions;
liquidity left at T2; hub that burned; intermediaries listed as owners."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); d = deltas(); tr = transfers(); reg = register()
txs, rcs, ints, px = load_raw()
vi = v.set_index("entity"); ri = reg.set_index("owner_eth_address")
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
b0 = balances(tr, SNAP_BLOCK); bend = balances(tr, T2_BLOCK)
E = pd.read_csv(f"{OUT}/plain_edges.csv")

print("== 1. Clusters: register key (first address) vs the address that actually held pre-hack WGNK / paid money")
rows = []
da = d.groupby("address").d_usd.sum()
for r in v[v.addresses.str.contains(";") & ~v.is_hacker].itertuples():
    A = r.addresses.split(";"); key = r.entity
    hb = {a: b0.get(a, 0.0) for a in A}
    top_holder = max(hb, key=hb.get)
    payer = min(A, key=lambda a: da.get(a, 0.0))
    e = E[E.a.isin(A) & E.b.isin(A)]
    key_in = e[e.b == key].wgnk.sum(); key_out = e[e.a == key].wgnk.sum()
    rows.append({"key": key, "n": len(A), "key_b0": hb[key], "cluster_b0": sum(hb.values()), "pending_burn": r.b0_pending_burn, "gnk_v1": r.v1_pay_gnk, "money_v1": r.v1_money_usd,
                 "gnk_not_held_by_key": max(0.0, min(r.v1_pay_gnk, sum(hb.values()) - hb[key])) if r.v1_pay_gnk > 0 else 0.0,
                 "top_holder": top_holder, "payer": payer, "payer_is_key": payer == key or abs(da.get(payer, 0)) < 0.01,
                 "key_status": ri.gonka_address_status.get(key), "key_received_from_cluster": key_in, "key_sent_to_cluster": key_out})
C = pd.DataFrame(rows)
mis = C[C.gnk_not_held_by_key > 0.5]
print("clusters:", len(C), "| with GNK payout where part of B0 sat on a non-key address:", len(mis), "GNK", round(mis.gnk_not_held_by_key.sum(), 2), "USD", round(mis.gnk_not_held_by_key.sum() * P0, 2))
print(mis[["key", "n", "key_b0", "cluster_b0", "gnk_v1", "gnk_not_held_by_key", "top_holder", "key_status", "key_received_from_cluster", "key_sent_to_cluster"]].round(2).to_string())
mm = C[(C.money_v1 > 0.01) & (~C.payer_is_key)]
print("clusters with a money refund where the paying address is not the key:", len(mm), "USD", round(mm.money_v1.sum(), 2))
print(mm[["key", "payer", "money_v1", "key_status"]].round(2).to_string())
C.to_csv(f"{OUT}/cluster_key_vs_holder.csv", index=False)

print("\n== 2. Where did refunded buyers' WGNK come from (window A, non-LP purchases)")
a = d[(d.win == "A") & (~d.is_lp_tx) & (d.d_usd < -0.01) & (d.d_wgnk >= 1) & (~d.entity.isin(v[v.is_hacker].entity))]
res = []
for r in a.itertuples():
    t = parse_tx(r.tx_hash, txs, rcs, ints, px)
    src_pool = sum(-w for x, w in t["dw"].items() if w < -1e-9 and x in POOLS)
    src_other = {x: -w for x, w in t["dw"].items() if w < -1 and x not in POOLS and x != ZERO}
    tot = src_pool + sum(src_other.values())
    share_p2p = sum(src_other.values()) / tot if tot > 0 else 0.0
    seller = max(src_other, key=src_other.get) if src_other else None
    recv = {x: u for x, u in t["usd"].items() if u > 0.01 and x not in POOLS and x != r.address and x not in INFRA}
    res.append({"tx": r.tx_hash, "buyer": r.address, "entity": r.entity, "usd": -r.d_usd, "wgnk": r.d_wgnk, "share_p2p": share_p2p, "seller": seller,
                "seller_usd": t["usd"].get(seller, 0.0) if seller else 0.0, "third_party_take": sum(u for x, u in recv.items() if x != seller)})
Q = pd.DataFrame(res)
Q["p2p_usd"] = Q.usd * Q.share_p2p
print("window-A purchases USD", round(Q.usd.sum(), 2), "| from pools", round((Q.usd - Q.p2p_usd).sum(), 2), "| from non-pool sellers (P2P / RFQ / limit orders)", round(Q.p2p_usd.sum(), 2), "txs", int((Q.share_p2p > 0.5).sum()))
pp = Q[Q.share_p2p > 0.5]
print(pp.groupby("seller").agg(n=("tx", "count"), buyers=("entity", "nunique"), buyer_paid=("usd", "sum"), seller_got=("seller_usd", "sum"), wgnk=("wgnk", "sum")).sort_values("buyer_paid", ascending=False).head(15).round(2).to_string())
pp = pp.assign(buyer_refund=pp.entity.map(vi.v1_money_usd), seller_cat=pp.seller.map(lambda s: vi.category.get(ent_of.get(s))))
print("buyers in P2P trades:", pp.entity.nunique(), "their v1 refunds:", round(pp.drop_duplicates("entity").buyer_refund.sum(), 2))
print("paid by buyer", round(pp.usd.sum(), 2), "received by seller", round(pp.seller_usd.sum(), 2), "gap (fillers/solvers/fees)", round(pp.usd.sum() - pp.seller_usd.sum(), 2))
pp.to_csv(f"{OUT}/p2p_purchases_window_a.csv", index=False)
# any direct WGNK transfer ever between buyer and P2P seller (relatedness)
pairs = set(zip(pp.buyer, pp.seller))
allp = set(zip(tr.from_addr, tr.to_addr)) | set(zip(tr.to_addr, tr.from_addr))
print("P2P buyer/seller pairs:", len(pairs), "| with any direct WGNK transfer between them in the whole log (single-log txs):", len([p for p in pairs if p in allp]))

print("\n== 3. Third-party attributions")
via = d[d.via_third_party.notna() & (d.via_third_party != "")]
print("rows", len(via), "owners", via.entity.nunique(), "| buys USD", round(-via[via.d_usd < 0].d_usd.sum(), 2), "| sells USD", round(via[via.d_usd > 0].d_usd.sum(), 2))
print(via.groupby(["win", "via_third_party"]).agg(n=("tx_hash", "count"), owners=("entity", "nunique"), usd=("d_usd", "sum"), wgnk=("d_wgnk", "sum")).sort_values("usd").round(2).to_string())
sv = via[via.d_usd > 0].assign(H=lambda x: x.entity.map(vi.honest_wgnk), cat=lambda x: x.entity.map(vi.category))
print("sell-side attributions (money received by another address is charged to the WGNK sender):"); print(sv[["tx_hash", "address", "d_wgnk", "d_usd", "via_third_party", "win", "H", "cat", "tx_from"]].round(2).to_string())

print("\n== 4. Liquidity left at the freeze (what voided WGNK can still be sold into)")
lp = lp_positions(); e = lp[lp.state == "end"]
print("money in positions at T2 by token:"); print(e.groupby("money_token").money_amount.sum().round(2).to_string(), "| USD (priced)", round(e.money_usd.sum(), 2))
print("WGNK transfer log last block:", tr.block_number.max(), "| swaps table last block:", swaps().block_number.max(), "| T2:", T2_BLOCK)
sw = swaps(); sw["usd"] = sw.usd_value.astype(float)
day = sw[sw.block_number > T2_BLOCK - 7200]
print("last 24h before T2: swaps", len(day), "USD", round(day.usd.sum(), 2), "avg price", round(day.usd.sum() / day.amount_wgnk.astype(float).abs().sum(), 5))

print("\n== 5. Intermediary-looking owners that are paid")
allpost = tr[tr.block_number >= T0_BLOCK]
cnt_in = allpost.groupby("to_addr").tx_hash.nunique(); cnt_out = allpost.groupby("from_addr").tx_hash.nunique()
sender = pd.Series({h: (t.get("from") or "").lower() for h, t in txs.items()})
rowsI = []
for r in v[v.v1_paid].itertuples():
    for a in r.addresses.split(";"):
        hs = set(allpost[(allpost.to_addr == a) | (allpost.from_addr == a)].tx_hash)
        if len(hs) >= 5:
            own = sum(1 for h in hs if sender.get(h) == a)
            if own == 0:
                rowsI.append({"address": a, "category": r.category, "txs_touching": len(hs), "sent_by_itself": own, "status": ri.gonka_address_status.get(r.entity), "H": r.honest_wgnk, "v1_gnk": r.v1_pay_gnk, "v1_money": r.v1_money_usd})
I = pd.DataFrame(rowsI).sort_values("txs_touching", ascending=False)
print("paid owners touched by >=5 post-hack txs none of which they sent:", len(I), "GNK", round(I.v1_gnk.sum(), 2), "money", round(I.v1_money.sum(), 2)); print(I.head(25).round(2).to_string())
I.to_csv(f"{OUT}/paid_owners_never_sender.csv", index=False)
