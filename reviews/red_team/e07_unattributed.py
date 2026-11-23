"""Transactions where an owner's WGNK changed with no money leg although the tx is not a plain wallet transfer
(pool/route involved, other tokens, or money moved elsewhere) — purchases/sales the model reads as 'transfers'.
Also: third-party attributions, and model rows that look like intermediaries."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); d = deltas(); tr = transfers()
txs, rcs, ints, px = load_raw()
sw = swaps()
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
vi = v.set_index("entity")
b0 = balances(tr, SNAP_BLOCK)
hack_ent = set(v[v.is_hacker].entity)
# pool price per block (USD per WGNK) from the swaps table, forward filled
sw = sw[sw.block_number >= T0_BLOCK - 5000].copy()
sw["price"] = sw["price_usdt"].astype(float)
print("swaps cols", list(sw.columns))

rows = []
for h in rcs:
    t = parse_tx(h, txs, rcs, ints, px)
    if t["block"] < T0_BLOCK or t["block"] > T2_BLOCK:
        continue
    pool_touch = any((f in POOLS or to in POOLS) for f, to, _ in t["wl"])
    any_money = any(abs(x) >= 0.01 for x in t["usd"].values())
    any_other = any(any(o.values()) for o in t["other"].values())
    mint_burn = any((f == ZERO or to == ZERO) for f, to, _ in t["wl"])
    for a, w in t["dw"].items():
        if abs(w) < 1 or a in INFRA or a in POOLS:
            continue
        usd = t["usd"].get(a, 0.0)
        oth = {k: x for k, x in t["other"].get(a, {}).items() if x}
        rows.append({"tx": h, "block": t["block"], "address": a, "entity": ent_of.get(a), "d_wgnk": w, "usd": usd, "other_tokens": ";".join(f"{k}:{x}" for k, x in oth.items()),
                     "pool_touch": pool_touch, "any_money": any_money, "any_other": any_other, "mint_burn": mint_burn, "tx_from": t["from"], "tx_to": t["to"],
                     "n_wgnk_logs": len(t["wl"])})
R = pd.DataFrame(rows)
m = d.set_index(["tx_hash", "address"])
R["model_usd"] = [m.d_usd.get((a, b), float("nan")) if (a, b) in m.index else float("nan") for a, b in zip(R.tx, R.address)]
R["model_via"] = [m.via_third_party.get((a, b)) if (a, b) in m.index else None for a, b in zip(R.tx, R.address)]
R["win"] = R.block.map(lambda b: "A" if b <= T1_BLOCK else "B")
print("rows", len(R), "in model", R.model_usd.notna().sum(), "not in model", R.model_usd.isna().sum())
print("not in model sample:"); print(R[R.model_usd.isna()].head(10).to_string())

nomoney = R[(R.usd.abs() < 0.01) & (R.model_usd.abs().fillna(0) < 0.01)]
plain = nomoney[~nomoney.pool_touch & ~nomoney.any_money & ~nomoney.any_other]
susp = nomoney[(nomoney.pool_touch | nomoney.any_money | nomoney.any_other) & ~((nomoney.n_wgnk_logs == 1) & nomoney.mint_burn)]
print("\nno-money WGNK moves:", len(nomoney), "| plain (no pool, no money, no other tokens):", len(plain), "| in non-plain txs:", len(susp))
susp = susp[~susp.entity.isin(hack_ent)]
# spot price at the block: last swap price
sp = sw.sort_values("block_number")
if "price" in sp and sp["price"].notna().any():
    pr = sp.groupby("block_number").price.last()
    def price_at(b):
        x = pr[pr.index <= b]
        return float(x.iloc[-1]) if len(x) else float("nan")
    susp = susp.assign(spot=susp.block.map(price_at))
    susp["est_usd"] = susp.d_wgnk.abs() * susp.spot
else:
    susp["est_usd"] = float("nan")
susp["side"] = susp.d_wgnk.map(lambda w: "got WGNK" if w > 0 else "gave WGNK")
susp["has_other"] = susp.other_tokens != ""
print(susp.groupby(["win", "side", "has_other", "pool_touch"]).agg(n=("tx", "count"), owners=("entity", "nunique"), wgnk=("d_wgnk", "sum"), est_usd=("est_usd", "sum")).round(2).to_string())
susp.to_csv(f"{OUT}/unattributed_wgnk_moves.csv", index=False)
print("\nTOP unattributed 'got WGNK' (possible unrefunded purchases):")
c = ["tx", "block", "address", "d_wgnk", "est_usd", "other_tokens", "pool_touch", "any_money", "win", "tx_from"]
print(susp[susp.d_wgnk > 0].sort_values("est_usd", ascending=False)[c].head(40).to_string())
print("\nTOP unattributed 'gave WGNK' (possible sales with proceeds elsewhere; holder keeps full B0):")
g = susp[susp.d_wgnk < 0].copy()
g["b0"] = g.address.map(lambda a: b0.get(a, 0)); g["H"] = g.entity.map(lambda e: vi.honest_wgnk.get(e, 0)); g["v1_gnk"] = g.entity.map(lambda e: vi.v1_pay_gnk.get(e, 0))
print(g.sort_values("est_usd", ascending=False)[c + ["H", "v1_gnk"]].head(40).to_string())
# per owner summary
po = susp.groupby(["entity", "side"]).agg(n=("tx", "count"), wgnk=("d_wgnk", "sum"), est_usd=("est_usd", "sum")).reset_index()
po["cat"] = po.entity.map(vi.category); po["H"] = po.entity.map(vi.honest_wgnk); po["v1_value"] = po.entity.map(vi.v1_value_usd); po["v1_money"] = po.entity.map(vi.v1_money_usd)
po.sort_values("est_usd", ascending=False).to_csv(f"{OUT}/unattributed_by_owner.csv", index=False)
print("\nPER OWNER (top 40 by est. USD):"); print(po.sort_values("est_usd", ascending=False).head(40).round(2).to_string())
print("\nowners 'got WGNK' unattributed:", po[po.side == "got WGNK"].entity.nunique(), "est USD", round(po[po.side == "got WGNK"].est_usd.sum(), 2),
      "| 'gave WGNK':", po[po.side == "gave WGNK"].entity.nunique(), "est USD", round(po[po.side == "gave WGNK"].est_usd.sum(), 2))
