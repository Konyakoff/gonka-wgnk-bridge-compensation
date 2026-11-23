"""Bridge operations in flight: Gonka-side mint requests vs WGNK mints on Ethereum; signing status of recent mints; escrow; return."""
import sys
sys.path.insert(0, "/work")
from rt_raw import *

tr = transfers(); v = variants()
ent_of = {a: r.entity for r in v.itertuples() for a in r.addresses.split(";")}
vi = v.set_index("entity")
g = jz("02_onchain_raw/gonka/gonka_chain.json.gz")
print("gonka keys:", {k: (type(x).__name__, len(x) if hasattr(x, "__len__") else x) for k, x in g.items()})
mr = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/bridge_mint_requests_gonka.parquet")
mr["ts"] = pd.to_datetime(mr.block_time, utc=True)
mr["gnk"] = mr.gnk.astype(float)
print("mint requests on Gonka:", len(mr), "from", mr.ts.min(), "to", mr.ts.max(), "sum GNK", mr.gnk.sum())
mints = tr[tr.from_addr == ZERO].copy()
mints["ts"] = pd.to_datetime(mints.time, utc=True) if mints.time.dtype == object else pd.to_datetime(mints.time, unit="s", utc=True)
print("WGNK mints on Ethereum:", len(mints), "sum", mints.value_wgnk.sum(), "incl 22M; time dtype", tr.time.dtype, tr.time.iloc[0])
HACK = pd.Timestamp("2026-11-18T18:00:59Z")
# match requests to mints greedily: same dest, same amount (1e-6), mint time >= request time
ms = mints.sort_values("ts").to_dict("records"); used = set(); rows = []
by = {}
for i, m in enumerate(ms):
    by.setdefault((m["to_addr"], round(m["value_wgnk"], 6)), []).append(i)
for r in mr.sort_values("ts").itertuples():
    key = ((r.dest or "").lower(), round(r.gnk, 6)); hit = None
    for i in by.get(key, []):
        if i not in used and ms[i]["ts"] >= r.ts - pd.Timedelta(minutes=5):
            hit = i; break
    if hit is not None:
        used.add(hit)
    rows.append({"height": r.height, "ts": r.ts, "signer": r.signer, "dest": (r.dest or "").lower(), "gnk": r.gnk, "tx": r.tx_hash,
                 "minted": hit is not None, "mint_ts": ms[hit]["ts"] if hit is not None else None, "mint_tx": ms[hit]["tx_hash"] if hit is not None else None})
R = pd.DataFrame(rows)
R["lag_min"] = (R.mint_ts - R.ts).dt.total_seconds() / 60
print("requests matched to an Ethereum mint:", int(R.minted.sum()), "unmatched:", int((~R.minted).sum()), "GNK", R[~R.minted].gnk.sum())
print("matched lag minutes: median", R.lag_min.median(), "p95", R.lag_min.quantile(0.95), "max", R.lag_min.max())
um = R[~R.minted]
print("unmatched before the hack:", len(um[um.ts < HACK]), um[um.ts < HACK].gnk.sum(), "| after:", len(um[um.ts >= HACK]), um[um.ts >= HACK].gnk.sum())
print(um[um.gnk>=100].sort_values("ts")[["height", "ts", "signer", "dest", "gnk"]].to_string())
um.to_csv(f"{OUT}/gonka_mint_requests_not_minted.csv", index=False)
print("mints not matched to a request:", len(ms) - len(used), sum(m["value_wgnk"] for i, m in enumerate(ms) if i not in used))
print(pd.DataFrame([m for i, m in enumerate(ms) if i not in used])[["block_number", "ts", "to_addr", "value_wgnk", "tx_hash"]].tail(15).to_string())
for dd in um.dest.unique():
    e = ent_of.get(dd)
    print("  dest", dd, "unminted GNK", round(um[um.dest == dd].gnk.sum(), 4), "in register:", e is not None, ({k: (round(float(vi.loc[e, k]), 2) if k != "category" else vi.loc[e, k]) for k in ["category", "honest_wgnk", "v1_pay_gnk", "v1_value_usd"]} if e is not None else ""))
last48 = R[(R.ts >= HACK - pd.Timedelta(hours=48)) & (R.ts < HACK)]
print("requests in the 48h before the hack:", len(last48), "minted", int(last48.minted.sum()))
print(R[R.ts >= HACK - pd.Timedelta(hours=6)][["ts","dest","gnk","minted","mint_ts"]].to_string())

print("\n== mint_signing")
ms_ = g["mint_signing"]
print(type(ms_), len(ms_)); k0 = list(ms_)[0]; print(k0, json.dumps(ms_[k0])[:800])
st = []
for k, x in ms_.items():
    stt = sorted({(s.get("status") or "none") for s in x["signing"].values()}) if isinstance(x.get("signing"), dict) else []
    st.append({"id": k, "amount": x.get("amount_wgnk"), "block": x.get("block") or x.get("block_number"), "to": x.get("to") or x.get("recipient"), "statuses": ",".join(stt)})
S = pd.DataFrame(st); print(S.statuses.value_counts().to_string()); print(S[~S.statuses.str.contains("COMPLETED")].to_string())
print("\n== escrow / community pool"); print(json.dumps(g.get("escrow"), indent=1)[:1500]); print(json.dumps(g.get("community_pool"), indent=1)[:600])
ret = jz("02_onchain_raw/return.json"); print("return.json keys", list(ret.keys()))
for k in ("admin_eth", "distribution_balance", "community_pool", "eth_usd_now", "eth_usd_at_return", "gas_price_gwei"):
    print(k, json.dumps(ret.get(k))[:500])
print("\n== withdraw_signing"); print(json.dumps(g.get("withdraw_signing"))[:1500])
