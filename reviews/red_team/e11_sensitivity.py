"""Re-implementation of option 1 for owners without LP fields, and sensitivity to the cut-off time, p0 and the escrow."""
import sys
sys.path.insert(0, "/work")
from collections import defaultdict
from rt_common import *

v = variants(); d = deltas()
ALIAS = {"WETH": "ETH", "ETH": "ETH", "USDT": "USDT", "USDC": "USDC", "DAI": "DAI"}
lp_like = (v.lp_w_before.abs() + v.lp_u_before.abs() + v.lp_u_t1.abs() + v.lp_u_end.abs() > 1e-9) | (v.category == "lp")
base = v[~v.is_hacker & ~lp_like].set_index("entity")
print("owners recomputed (no LP fields):", len(base), "of", len(v))
rows = [(r.entity, r.ts, json.loads(r.tokens or "{}"), r.eth_usd) for r in d.itertuples()]


def option1(cut_ts, p0=P0):
    qa = defaultdict(lambda: defaultdict(float)); ua = defaultdict(lambda: defaultdict(float))
    qb = defaultdict(lambda: defaultdict(float)); ub = defaultdict(lambda: defaultdict(float))
    for e, ts, tok, px in rows:
        q, u = (qa, ua) if ts <= cut_ts else (qb, ub)
        for t, x in tok.items():
            k = ALIAS.get(t)
            if k:
                q[e][k] -= x; u[e][k] -= x * (px if k == "ETH" else 1.0)
    out = {}
    for e, r in base.iterrows():
        nb = sum(ub[e].values()); phi = 0.0 if nb > 0 else 1.0
        qq = {t: qa[e][t] + phi * qb[e][t] for t in ("USDT", "USDC", "DAI", "ETH")}
        uu = {t: ua[e][t] + phi * ub[e][t] for t in ("USDT", "USDC", "DAI", "ETH")}
        m = sum(uu.values()); pay = {"gnk": 0.0, "usdt": 0.0, "usdc": 0.0, "dai": 0.0, "eth": 0.0}
        honest = r.honest_wgnk - r.g_credited
        if m > 0.005:
            pos = sum(x for x in uu.values() if x > 0); f = m / pos
            for t in uu:
                if uu[t] > 0:
                    pay[t.lower()] = qq[t] * f
            pay["gnk"] = max(0.0, honest)
        else:
            pay["gnk"] = max(0.0, honest + m / p0)
        pay["money_usd"] = pay["usdt"] + pay["usdc"] + pay["dai"] + pay["eth"] * ETH_NOW
        out[e] = pay
    return pd.DataFrame(out).T


chk = option1(WARN_TS)
diff = pd.DataFrame({"gnk": (chk.gnk - base.v1_pay_gnk).abs(), "usdt": (chk.usdt - base.v1_pay_usdt).abs(), "usdc": (chk.usdc - base.v1_pay_usdc).abs(), "eth": (chk.eth - base.v1_pay_eth).abs()})
print("CHECK my option 1 vs package for", len(base), "owners: max abs diff", diff.max().round(8).to_dict())
tot0 = chk[["gnk", "usdt", "usdc", "dai", "eth", "money_usd"]].sum()
print("baseline (T1 = official warning):", tot0.round(2).to_dict())
cuts = [("Blockaid alert 18:28:27", 1795026507), ("first press article 18:43:22 (TokenPost)", 1795027402), ("T0 + 1h (19:00:59)", 1795024859 + 3600), ("The Defiant 22:24:25", 1795040665),
        ("first official post 00:18:28", 1795047508), ("official warning 00:24:07 (package)", WARN_TS), ("warning + 1h", WARN_TS + 3600), ("press repeats warning 01:35:41", 1795052141), ("funds returned 09:13:37", 1795079617)]
res = []
for name, ts in cuts:
    x = option1(ts); t = x[["gnk", "usdt", "usdc", "dai", "eth", "money_usd"]].sum()
    res.append({"cut-off": name, "money_usd": t.money_usd, "delta_money_vs_package": t.money_usd - tot0.money_usd, "gnk": t.gnk, "delta_gnk": t.gnk - tot0.gnk, "owners_with_money": int((x.money_usd > 0.01).sum())})
S = pd.DataFrame(res); print(S.round(2).to_string()); S.to_csv(f"{OUT}/sensitivity_cutoff.csv", index=False)

print("\n== p0 sensitivity (GNK deducted for gains; all owners, from package columns)")
nh = v[~v.is_hacker]
for mult in (0.5, 0.8, 1.0, 1.25, 2.0):
    p = P0 * mult
    gnk = ((nh.honest_wgnk - nh.g_credited + nh.v1_m_usd.where(nh.v1_m_usd <= 0.005, 0) / p).clip(lower=0)).sum()
    print(f"   p0 x{mult}: GNK payout {gnk:,.2f} (delta {gnk - nh.v1_pay_gnk.sum():+,.2f})")
sw = swaps(); sw["usd"] = sw.usd_value.astype(float); sw["w"] = sw.amount_wgnk.astype(float).abs()
pre = sw[sw.block_number < T0_BLOCK]
for hrs in (1, 6, 24, 72, 168, 720):
    x = pre[pre.block_number >= T0_BLOCK - hrs * 300]
    print(f"   VWAP last {hrs}h before T0: {x.usd.sum() / x.w.sum():.6f} ({len(x)} swaps, ${x.usd.sum():,.0f})")
last = pre.sort_values(["block_number", "log_index"]).tail(3)
print("   last swaps before T0:"); print(last[["block_number", "block_time", "price_usdt", "usd_value", "direction"]].to_string())

print("\n== escrow as a source of funds")
g = jz("02_onchain_raw/gonka/gonka_chain.json.gz"); esc = g["escrow"]["now"]["gnk"]
summ = jz("03_model/summary_three_options.json")["variants"]["v1"]
supply = 13090977.714566352; pend = float(nh.b0_pending_burn.sum())
print("   escrow now", esc, "| supply at snapshot", supply, "| pending pre-hack burns", pend)
mr = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/bridge_mint_requests_gonka.parquet")
post_req = mr[pd.to_datetime(mr.block_time, utc=True) >= pd.Timestamp("2026-11-18T18:00:59Z")].gnk.astype(float).sum()
pre_esc = esc + 13_000_000 - post_req
print("   post-hack mint requests locked:", post_req, "| escrow before the hack (reconstructed):", pre_esc, "| excess over supply + pending burns:", pre_esc - supply - pend)
avail = esc - post_req - (pre_esc - supply - pend)
print("   escrow GNK available for register needs:", avail, "| stated GNK gap:", summ["gnk_gap"], "| gap after escrow:", summ["gnk_gap"] - avail, "| top-up overstated by USD:", avail * P0,
      "| share of stated top-up:", avail * P0 / summ["cost_usd"])
ret = jz("02_onchain_raw/return.json")
print("   ETH price at return", ret["eth_usd_at_return"], "now", ret["eth_usd_now"], "| value lost on returned ETH held unconverted:", (ret["eth_usd_at_return"] - ret["eth_usd_now"]) * summ["eth_returned"])
print("   stated top-up", summ["cost_usd"], "eth_gap", summ["eth_gap"], "usd", summ["eth_gap"] * ret["eth_usd_now"], "gnk part usd", summ["gnk_gap"] * P0)
