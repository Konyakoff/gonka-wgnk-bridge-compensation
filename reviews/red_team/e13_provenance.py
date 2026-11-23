"""Provenance of the largest recipients: bridge-in signer on Gonka, pre-hack WGNK sources, timing of LP positions vs the hack."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

v = variants(); tr = transfers(); reg = register()
vi = v.set_index("entity")
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
mr = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/bridge_mint_requests_gonka.parquet")
mr["dest"] = mr.dest.str.lower(); mr["gnk"] = mr.gnk.astype(float); mr["ts"] = pd.to_datetime(mr.block_time, utc=True)
pre = tr[tr.block_number <= SNAP_BLOCK]
top = v[~v.is_hacker].sort_values("v1_value_usd", ascending=False).head(25)
ri = reg.set_index("owner_eth_address")
print("== top-25 recipients: where their pre-hack WGNK came from")
sig_of = {}
for r in top.itertuples():
    for a in r.addresses.split(";"):
        inn = pre[pre.to_addr == a]
        src = inn.groupby("from_addr").value_wgnk.sum().sort_values(ascending=False)
        req = mr[mr.dest == a]
        signers = req.groupby("signer").gnk.sum().sort_values(ascending=False)
        for s in signers.index:
            sig_of.setdefault(s, set()).add(a)
        last_in = pd.Timestamp(int(inn.time.max()), unit="s") if len(inn) else None
        print(f"{a} [{r.category}] v1 ${r.v1_value_usd:,.0f} H {r.honest_wgnk:,.0f} | gonka twin {ri.gonka_address.get(r.entity)} | minted to it {src.get(ZERO, 0):,.0f} | last inbound {last_in}")
        print("      top sources:", [(s[:12], round(x)) for s, x in src.head(4).items()])
        print("      gonka signers of its mint requests:", [(s, round(x)) for s, x in signers.head(3).items()])
print("\n== Gonka signers that bridged to more than one top-25 address")
for s, A in sig_of.items():
    if len(A) > 1:
        print(s, sorted(A))
# signers bridging to many destinations overall
g = mr.groupby("signer").agg(dests=("dest", "nunique"), gnk=("gnk", "sum"), n=("gnk", "count")).sort_values("gnk", ascending=False)
print("\n== largest Gonka signers of mint requests (all time)"); print(g.head(15).to_string())
tot_req = mr.gnk.sum()
print("share of top-5 signers in all requested GNK:", g.gnk.head(5).sum() / tot_req)
# twin check: does the mint signer equal the Gonka twin of the dest (self-bridge) or a third party
tw = jz("02_onchain_raw/ethereum/gonka_address_of_same_key.json.gz")
print("twins sample:", list(tw.items())[:1])
def twin(a):
    x = tw.get(a) or {}
    return x.get("gonka")
mr["self"] = [twin(d) == s for d, s in zip(mr.dest, mr.signer)]
print("mint requests where signer == Gonka twin of destination:", int(mr.self.sum()), "of", len(mr), "GNK", mr[mr.self].gnk.sum(), "of", tot_req)

print("\n== LP 0x6c07…: timeline")
A = "0x6c07e00cc3847b687fbde78baa184c5098116c51"
vm = pd.read_parquet(f"{P}/02_onchain_raw/ethereum/v4_modify_liquidity.parquet")
lp = lp_positions(); mine = lp[lp.owner == A]
print(mine[["pos", "pair", "state", "liquidity", "tick_lower", "tick_upper", "wgnk", "money_token", "money_amount", "money_usd"]].to_string())
vm["pos"] = vm.apply(lambda r: f"v4:{hx(r['salt'])}" if r["sender"] == "0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e" else "own", axis=1)
bts = jz("02_onchain_raw/ethereum/block_ts.json")
ev = vm[vm.pos.isin(set(mine.pos))].sort_values("block_number")
tblk = pre.drop_duplicates("block_number").set_index("block_number").time
def when(b):
    if str(b) in bts:
        return pd.Timestamp(int(bts[str(b)]), unit="s")
    x = tr[tr.block_number <= b]
    return f"~{pd.Timestamp(int(x.time.max()), unit='s')} (nearest earlier transfer)"
for r in ev.itertuples():
    print("   ", r.block_number, when(r.block_number), r.pos, "liq", r.liquidity_delta, "ticks", r.tick_lower, r.tick_upper, r.tx_hash)
t = tr[(tr.from_addr == A) | (tr.to_addr == A)].sort_values("block_number")
t = t.assign(when=pd.to_datetime(t.time, unit="s"))
print(t[["block_number", "when", "from_addr", "to_addr", "value_wgnk"]].tail(25).to_string())
print(mr[mr.dest == A][["ts", "signer", "gnk"]].to_string())
d = deltas(); print(d[d.entity == A][["tx_hash", "block", "d_wgnk", "d_usd", "tokens", "is_lp_tx", "win"]].sort_values("block").to_string())
# v4 WGNK/ETH pool liquidity share
p = lp[(lp.pair == "WGNK/ETH") & (lp.state == "snap")]
print("WGNK/ETH positions at snapshot:"); print(p[["pos", "owner", "wgnk", "money_amount", "money_usd"]].to_string())
