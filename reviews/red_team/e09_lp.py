"""LP checks: v4 liquidity events in transactions that the model never scanned, NFT owner changes between states,
unpriced positions, per-owner LP accounting, who the big LP is."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); d = deltas(); tr = transfers()
txs, rcs, ints, px = load_raw()
vi = v.set_index("entity")
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
lpos = lp_positions()
vm = pd.read_parquet(f"{P}/02_onchain_raw/ethereum/v4_modify_liquidity.parquet")
v4x = jz("02_onchain_raw/ethereum/v4_extra.json")
print("v4x keys", list(v4x.keys()), "pools", len(v4x["pools"]))
pinfo = {p["pool_id"]: p for p in v4x["pools"]}
print("vm cols", list(vm.columns))
POSM = "0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e"
vm["pos"] = vm.apply(lambda r: f"v4:{hx(r['salt'])}" if r["sender"] == POSM else f"v4own:{r['pool_id']}:{r['sender']}:{r['tick_lower']}:{r['tick_upper']}:{r['salt']}", axis=1)
vm["liq"] = vm.liquidity_delta.map(int)
post = vm[(vm.block_number >= T0_BLOCK) & (vm.block_number <= T2_BLOCK)]
miss = post[~post.tx_hash.isin(rcs)]
print("\n== v4 liquidity events after T0 in txs absent from post_receipts:", len(miss), "| with liquidity change:", int((miss.liq != 0).sum()))
tok = v4x["tokens"]
rows = []
for r in miss.itertuples():
    p = pinfo[r.pool_id]
    other = p["currency1"] if p["currency0"] == WGNK_ADDR else p["currency0"]
    sym = (tok.get(other) or {}).get("symbol") or other[:10]
    st = lpos[lpos.pos == r.pos]
    owners = st.set_index("state").owner.to_dict()
    money = st.set_index("state").money_usd.round(2).to_dict()
    wg = st.set_index("state").wgnk.round(2).to_dict()
    ow = next((o for o in owners.values() if o), "")
    e = ent_of.get(ow)
    rows.append({"block": r.block_number, "win": "A" if r.block_number <= T1_BLOCK else "B", "pair": "WGNK/" + sym, "pos": r.pos[:14], "liq_delta": r.liq, "ticks": f"{r.tick_lower}..{r.tick_upper}",
                 "owner": ow, "money_usd_states": money, "wgnk_states": wg,
                 "cat": vi.category.get(e), "v1_value": round(float(vi.v1_value_usd.get(e, 0)), 2), "v3_value": round(float(vi.v3_value_usd.get(e, 0)), 2), "tx": r.tx_hash})
M = pd.DataFrame(rows)
print(M.drop(columns=["tx"]).to_string())
M.to_csv(f"{OUT}/v4_events_not_scanned.csv", index=False)
# full history of the positions involved in liquidity-changing missing events
for pos in miss[miss.liq != 0].pos.unique():
    g = vm[vm.pos == pos].sort_values("block_number")
    print("\n  history", pos[:60]); print(g[["block_number", "liq", "tick_lower", "tick_upper", "tx_hash"]].assign(in_receipts=g.tx_hash.isin(rcs)).to_string())
    print(lpos[lpos.pos == pos][["state", "owner", "liquidity", "wgnk", "money_token", "money_amount", "money_usd"]].to_string())

print("\n== positions whose NFT owner changed between states (with value)")
ow = lpos.pivot_table(index="pos", columns="state", values="owner", aggfunc="first")
for pos, r in ow.iterrows():
    vals = {x for x in r.values if isinstance(x, str) and x}
    if len(vals) > 1:
        print(lpos[lpos.pos == pos][["pos", "state", "owner", "entity", "wgnk", "money_token", "money_amount", "money_usd"]].to_string())
        for o in vals:
            e = ent_of.get(o)
            if e in vi.index:
                x = vi.loc[e]
                print("     owner", o, x.category, "H", round(x.honest_wgnk, 2), "netA", round(x.net_a_usd, 2), "netB", round(x.net_b_usd, 2), "v1", round(x.v1_value_usd, 2), "v2", round(x.v2_value_usd, 2), "v3", round(x.v3_value_usd, 2))

print("\n== LP owners: accounting")
lp_owners = v[(v.lp_w_before.abs() + v.lp_u_before.abs() + v.lp_u_t1.abs() + v.lp_u_end.abs() > 1e-6) | (v.category == "lp")]
c = ["entity", "category", "b0_wallet", "lp_w_before", "lp_u_before", "lp_u_t1", "lp_u_end", "net_a_usd", "net_b_usd", "a_lp_usd", "b_lp_usd", "v1_pay_gnk", "v1_money_usd", "v3_money_usd", "wgnk_end_wallet"]
print(lp_owners[c].round(2).to_string())
print("LP owners", len(lp_owners), "v1 value", lp_owners.v1_value_usd.sum(), "share", lp_owners.v1_value_usd.sum() / v.v1_value_usd.sum(), "money", lp_owners.v1_money_usd.sum(), "share of money", lp_owners.v1_money_usd.sum() / v.v1_money_usd.sum())

print("\n== The largest LP 0x244186…: history")
A = "0x244186297b43ba43c92d68efe78c04170fbc0b10"
lp = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/lp_events.parquet")
print("lp_events cols", list(lp.columns))
first = lp.sort_values("block_number").groupby("pool_id").head(3)
print(first[["pool_id", "block_number", "block_time", "event", "owner", "origin_eoa", "amount_wgnk", "amount_usdt"]].to_string() if "origin_eoa" in lp.columns else first.to_string())
mine = lp[(lp.get("origin_eoa", lp.owner).str.lower() == A) | (lp.owner.str.lower() == A)]
print("events by 0x244186:", len(mine)); print(mine.sort_values("block_number")[["block_number", "block_time", "event", "amount_wgnk", "amount_usdt", "tick_lower", "tick_upper", "tx_hash"]].tail(25).to_string())
t = tr[(tr.from_addr == A) | (tr.to_addr == A)]
pre = t[t.block_number <= SNAP_BLOCK]
print("pre-hack WGNK transfers of 0x244186:", len(pre), "from zero (bridge mints):", pre[pre.from_addr == ZERO].value_wgnk.sum(), "n", len(pre[pre.from_addr == ZERO]),
      "| sent to distinct:", pre[pre.from_addr == A].to_addr.nunique(), "| first block", pre.block_number.min())
print(pre.assign(cp=pre.apply(lambda r: r.to_addr if r.from_addr == A else r.from_addr, axis=1), s=pre.apply(lambda r: -r.value_wgnk if r.from_addr == A else r.value_wgnk, axis=1)).groupby("cp").s.agg(["count", "sum"]).sort_values("sum").to_string())
print("positions of 0x244186:"); print(lpos[lpos.owner == A][["pos", "state", "liquidity", "tick_lower", "tick_upper", "wgnk", "money_amount"]].to_string())
print("model rows:"); print(d[d.entity == A][["tx_hash", "block", "d_wgnk", "d_usd", "tokens", "is_lp_tx", "win"]].sort_values("block").to_string())
