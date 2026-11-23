"""Plain WGNK transfers after T0: hubs (rule '>3 counterparties'), unclustered flows of pre-hack WGNK, hacker-linked recipients,
dust edges, and what was not merged."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); d = deltas(); tr = transfers()
txs, rcs, ints, px = load_raw()
b0 = balances(tr, SNAP_BLOCK); bend = balances(tr, T2_BLOCK)
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
vi = v.set_index("entity")
post = tr[(tr["block_number"] >= T0_BLOCK) & (tr["block_number"] <= T2_BLOCK)]
print("post transfers", len(post), "txs", post.tx_hash.nunique(), "max block", tr.block_number.max())

edges = []     # plain edges as the project defines them
moneyed = []   # wallet-to-wallet transfers skipped because the tx had money/internal
for h, g in post.groupby("tx_hash"):
    parts = set(g["from_addr"]) | set(g["to_addr"])
    if parts & (INFRA | POOLS):
        continue
    rc, tx = rcs.get(h) or {}, txs.get(h) or {}
    has_money = hx(tx.get("value")) > 0 or any(lg["address"] in MONEY for lg in rc.get("logs") or []) or bool(ints.get(h))
    for r in g.itertuples():
        if r.from_addr != r.to_addr:
            (moneyed if has_money else edges).append((r.from_addr, r.to_addr, h, r.value_wgnk, r.block_number))
E = pd.DataFrame(edges, columns=["a", "b", "tx", "wgnk", "block"])
M = pd.DataFrame(moneyed, columns=["a", "b", "tx", "wgnk", "block"])
print("plain edges", len(E), "distinct pairs", len(E.drop_duplicates(["a", "b"])), "| transfers in txs with money (not edges):", len(M))
deg = defaultdict(set)
for r in E.itertuples():
    deg[r.a].add(r.b); deg[r.b].add(r.a)
hubs = {a for a, s in deg.items() if len(s) > 3}
print("hubs (>3 counterparties):", len(hubs))
da = d.groupby("address").agg(n=("tx_hash", "count"), usd=("d_usd", "sum")).to_dict("index")
hub_rows = []
for hname in sorted(hubs, key=lambda a: -len(deg[a])):
    inn = E[E.b == hname]; out = E[E.a == hname]
    e = ent_of.get(hname)
    row = vi.loc[e] if e in vi.index else None
    print(f"\nHUB {hname} deg {len(deg[hname])} in {len(inn)} tx / {inn.wgnk.sum():.2f} WGNK from {inn.a.nunique()} addrs; out {len(out)} tx / {out.wgnk.sum():.2f} WGNK to {out.b.nunique()} addrs; "
          f"B0 {b0.get(hname, 0):.2f} end {bend.get(hname, 0):.2f} money_net {da.get(hname, {}).get('usd', 0):.2f} ntx {da.get(hname, {}).get('n', 0)}"
          + (f" | cat {row.category} v1 gnk {row.v1_pay_gnk:.2f} v1$ {row.v1_money_usd:.2f} netA {row.net_a_usd:.2f} netB {row.net_b_usd:.2f}" if row is not None else " | NOT IN REGISTER"))
    cps = sorted(deg[hname])
    for c in cps:
        ec = ent_of.get(c); rc_ = vi.loc[ec] if ec in vi.index else None
        to_h = E[(E.a == c) & (E.b == hname)].wgnk.sum(); from_h = E[(E.a == hname) & (E.b == c)].wgnk.sum()
        print(f"     cp {c} ->hub {to_h:.2f} hub-> {from_h:.2f} B0 {b0.get(c, 0):.2f} end {bend.get(c, 0):.2f} money {da.get(c, {}).get('usd', 0):.2f}"
              + (f" cat {rc_.category} H {rc_.honest_wgnk:.2f} netA {rc_.net_a_usd:.2f} netB {rc_.net_b_usd:.2f} v1gnk {rc_.v1_pay_gnk:.2f} v1$ {rc_.v1_money_usd:.2f}" if rc_ is not None else " NOT IN REGISTER"))
        hub_rows.append({"hub": hname, "counterparty": c, "to_hub_wgnk": to_h, "from_hub_wgnk": from_h, "cp_b0": b0.get(c, 0)})
pd.DataFrame(hub_rows).to_csv(f"{OUT}/hubs.csv", index=False)

# Edges not merged (because of hubs) vs merged
E["same_owner"] = [ent_of.get(a) == ent_of.get(b) and ent_of.get(a) is not None for a, b in zip(E.a, E.b)]
print("\nedges merged:", int(E.same_owner.sum()), "not merged:", int((~E.same_owner).sum()))
nm = E[~E.same_owner]
print("not-merged edges not touching hub:", len(nm[~(nm.a.isin(hubs) | nm.b.isin(hubs))]))
print(nm[~(nm.a.isin(hubs) | nm.b.isin(hubs))].to_string())
# dust edges among merged
print("\nmerged edges with < 1 WGNK:", len(E[E.same_owner & (E.wgnk < 1)]), " <100:", len(E[E.same_owner & (E.wgnk < 100)]))
print(E[E.same_owner & (E.wgnk < 20)].to_string())
# transfers in moneyed txs between wallets
print("\nwallet-to-wallet WGNK transfers inside txs with money (never edges):")
M["same_owner"] = [ent_of.get(a) == ent_of.get(b) and ent_of.get(a) is not None for a, b in zip(M.a, M.b)]
print(M.groupby("same_owner").agg(n=("tx", "count"), txs=("tx", "nunique"), wgnk=("wgnk", "sum")).to_string())
print(M.sort_values("wgnk", ascending=False).head(40).to_string())
E.to_csv(f"{OUT}/plain_edges.csv", index=False); M.to_csv(f"{OUT}/transfers_in_money_txs.csv", index=False)
