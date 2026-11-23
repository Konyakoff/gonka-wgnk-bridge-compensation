"""Independent recomputation of WGNK bridge-exploit compensation for a stratified sample.

Does NOT import or read the project's model code. Inputs: raw on-chain dumps only, plus
variants.parquet (project results) for (a) choosing the sample, (b) cluster membership
(`addresses`), (c) b0_pending_burn, (d) the comparison itself.

Run:
  docker run --rm -v R:/research:ro -v <this dir>:/work <python-image> python /work/02_recompute.py
"""
import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd

R = "/research"
OUT = "/work"
SEED = 20261123
# AUDIT_ALL=1: extra run over every non-LP, non-hacker owner (not the deliverable sample; a population cross-check)
ALL = os.environ.get("AUDIT_ALL") == "1"
SUFFIX = "_ALL" if ALL else ""
# Diagnostic only (found AFTER the first comparison, in the project's own output model/comp3.json -> "gradient"):
# the ladder the project's variants.parquet v2 columns appear to use. NOT used for my payouts or pass/fail.
DIAG_LADDER = [(1795052141, 0.5), (1795089780, 0.25), (1795134247, 0.125)]

# ---- constants given in the audit brief -------------------------------------------------
SNAP_BLOCK = 26443612          # B0 = balance at END of this block
A_FROM, A_TO = 26443607, 26445519
B_FROM, B_TO = 26445520, 26475449
WARN_TS = 1795047847
GRADIENT = [(1795052141, 0.5), (1795089780, 0.25), (1795134247, 0.125)]  # then 0

WGNK = "0x972a7a92d92796a98801a8818bcf91f1648f2f68"
USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
DAI = "0x6b175474e89094c44da98b954eedeac495271d0f"
WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
T_TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
T_DEPOSIT = "0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c"
T_WITHDRAWAL = "0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65"
TOK = {WGNK: "wgnk", USDT: "usdt", USDC: "usdc", DAI: "dai", WETH: "eth"}
DEC = {"wgnk": 9, "usdt": 6, "usdc": 6, "dai": 18, "eth": 18}
MONEY = ["usdt", "usdc", "dai", "eth"]
DUST_RAW = 10 ** 9  # 1 WGNK

TOL = {"b0": 0.01, "usd": 0.02, "gnk": 0.5, "usdt": 0.01, "usdc": 0.01, "dai": 0.01, "eth": 0.00001, "k": 1e-4}


def K(ts, ladder=None):
    for until, k in (ladder or GRADIENT):
        if ts <= until:
            return k
    return 0.0


def addr_of(topic):
    return "0x" + topic[-40:]


# ---- load ---------------------------------------------------------------------------------
tr = pd.read_parquet(f"{R}/raw/eth/wgnk_transfers.parquet")
txs = json.load(open(f"{R}/raw/eth/post_txs.json"))
rcs = json.load(open(f"{R}/raw/eth/post_receipts.json"))
internal = json.load(open(f"{R}/raw/eth/post_internal.json"))
block_ts = {int(k): int(v) for k, v in json.load(open(f"{R}/raw/eth/block_ts.json")).items()}
eth_usd = {int(k): float(v) for k, v in json.load(open(f"{R}/raw/eth/eth_usd.json")).items()}
meta = json.load(open(f"{R}/raw/meta.json"))
P0 = float(meta["p0_vwap24h"])
var = pd.read_parquet(f"{R}/model/parquet/variants.parquet")

# ---- 1. sample ----------------------------------------------------------------------------
STRATA = {"holder": 6, "holder_sold": 4, "holder_traded": 6, "buyer": 6, "trader_loss": 3, "trader_profit": 3, "b_only": 2}
lp_cols = ["lp_w_before", "lp_u_before", "lp_u_t1", "lp_u_end", "a_lp_usd", "b_lp_usd"]
pool = var[(~var.is_hacker) & var.category.isin(STRATA)].copy()
n_pool_before = pool.groupby("category").size().to_dict()
pool = pool[(pool[lp_cols].fillna(0).abs().sum(axis=1) == 0)]
n_pool_after = pool.groupby("category").size().to_dict()
pool["eth_payer"] = (pool[["v1_pay_eth", "v2_pay_eth", "v3_pay_eth"]].max(axis=1) > 0)

rng = np.random.default_rng(SEED)
attempt = 0
while True:
    attempt += 1
    chosen = []
    for cat, n in STRATA.items():
        p = pool[pool.category == cat].sort_values("entity")
        if cat == "holder":
            top2 = p.sort_values(["honest_wgnk", "entity"], ascending=[False, True]).entity.tolist()[:2]
            rest = p[~p.entity.isin(top2)].entity.tolist()
            chosen += top2 + list(rng.choice(rest, size=n - 2, replace=False))
        else:
            ents = p.entity.tolist()
            chosen += list(rng.choice(ents, size=min(n, len(ents)), replace=False))
    s = pool[pool.entity.isin(chosen)]
    if int(s.has_b.sum()) >= 10 and int(s.eth_payer.sum()) >= 3:
        break
    if attempt > 10000:
        raise SystemExit("cannot satisfy sample constraints")
if ALL:
    allp = var[(~var.is_hacker) & (var.category != "lp") & (var.category != "hacker")].copy()
    allp = allp[(allp[lp_cols].fillna(0).abs().sum(axis=1) == 0)]
    allp["eth_payer"] = (allp[["v1_pay_eth", "v2_pay_eth", "v3_pay_eth"]].max(axis=1) > 0)
    pool = allp
    chosen = allp.entity.tolist()
sample = pool.set_index("entity").loc[chosen].reset_index()
print(f"seed={SEED} attempt={attempt} n={len(sample)} has_b={int(sample.has_b.sum())} eth_payers={int(sample.eth_payer.sum())}")
print("pool before LP filter:", n_pool_before)
print("pool after LP filter:", n_pool_after)

owner_addrs = {r.entity: [a.strip().lower() for a in r.addresses.split(";") if a.strip()] for r in sample.itertuples()}
addr_owner = {}
for o, al in owner_addrs.items():
    for a in al:
        assert a not in addr_owner
        addr_owner[a] = o

# ---- 2. B0 from the transfer log ----------------------------------------------------------
pre = tr[tr.block_number <= SNAP_BLOCK]
b0_raw = defaultdict(int)
for f, t, v in zip(pre.from_addr, pre.to_addr, pre.value_raw):
    v = int(v)
    if f in addr_owner:
        b0_raw[f] -= v
    if t in addr_owner:
        b0_raw[t] += v

# ---- 3. per-tx deltas from receipts / tx value / internal transfers ----------------------
def tx_deltas(h):
    """{addr: {cur: raw int delta}} for every address touched in tx h; plus other-token touches."""
    tx, rc = txs[h], rcs[h]
    d = defaultdict(lambda: defaultdict(int))
    other = defaultdict(lambda: defaultdict(int))
    for lg in rc["logs"]:
        tp = lg["topics"]
        if not tp:
            continue
        a = lg["address"]
        cur = TOK.get(a)
        if tp[0] == T_TRANSFER and len(tp) == 3:
            val = int(lg["data"], 16) if lg["data"] not in ("0x", "") else 0
            f, t = addr_of(tp[1]), addr_of(tp[2])
            if cur:
                d[f][cur] -= val
                d[t][cur] += val
            else:
                other[f][a] -= val
                other[t][a] += val
        elif a == WETH and tp[0] == T_DEPOSIT:
            d[addr_of(tp[1])]["eth"] += int(lg["data"], 16)
        elif a == WETH and tp[0] == T_WITHDRAWAL:
            d[addr_of(tp[1])]["eth"] -= int(lg["data"], 16)
    v = int(tx["value"], 16)
    if v:
        d[tx["from"]]["eth"] -= v
        if tx.get("to"):
            d[tx["to"]]["eth"] += v
    for x in internal.get(h, []):
        if str(x.get("isError", "0")) != "0":
            continue
        v = int(x["value"])
        if v:
            d[x["from"]]["eth"] -= v
            if x.get("to"):
                d[x["to"]]["eth"] += v
    return d, other


def usd_of(cur, raw, block):
    amt = raw / 10 ** DEC[cur]
    if cur == "eth":
        return amt * eth_usd[block // 25 * 25]
    return amt


def new_acc():
    return {"q": {c: 0.0 for c in MONEY}, "usd": {c: 0.0 for c in MONEY}, "spent": 0.0, "received": 0.0,
            "w_in": 0.0, "w_out": 0.0, "n_tx": 0, "k_num": 0.0, "k_den": 0.0, "k_num_gross": 0.0, "k_den_gross": 0.0,
            "k_num_diag": 0.0}


acc = {o: {"A": new_acc(), "B": new_acc()} for o in owner_addrs}          # per-address dust rule (as in brief)
acc_cl = {o: {"A": new_acc(), "B": new_acc()} for o in owner_addrs}       # alt: dust rule on cluster-level delta
detail = defaultdict(list)
flags = defaultdict(list)
nomoney = defaultdict(list)
signers = {tx["from"] for tx in txs.values()}

order = sorted(txs, key=lambda h: (int(txs[h]["blockNumber"], 16), int(txs[h].get("transactionIndex", "0x0"), 16)))
for h in order:
    tx, rc = txs[h], rcs[h]
    if rc.get("status") != "0x1":
        continue
    blk = int(tx["blockNumber"], 16)
    if A_FROM <= blk <= A_TO:
        win = "A"
    elif B_FROM <= blk <= B_TO:
        win = "B"
    else:
        continue
    ts = block_ts[blk]
    d, other = tx_deltas(h)
    touched = [a for a in d if a in addr_owner]
    if not touched:
        continue
    by_owner = defaultdict(list)
    for a in touched:
        by_owner[addr_owner[a]].append(a)
    for o, al in by_owner.items():
        # cluster-level alt
        cl = defaultdict(int)
        for a in al:
            for c, v in d[a].items():
                cl[c] += v
        for mode, groups in (("addr", [(a, d[a]) for a in al]), ("cluster", [("+".join(al), cl)])):
            target = acc if mode == "addr" else acc_cl
            for a, dd in groups:
                w = dd.get("wgnk", 0)
                counted = abs(w) >= DUST_RAW
                musd = {c: usd_of(c, dd.get(c, 0), blk) for c in MONEY}
                net_usd = sum(musd.values())
                if mode == "addr":
                    oth = {t: v for t, v in other.get(a, {}).items() if v}
                    detail[o].append({"tx": h, "block": blk, "ts": ts, "win": win, "addr": a, "counted": counted,
                                      "d_wgnk": w / 1e9, "K": K(ts) if win == "B" else None,
                                      **{f"d_{c}": dd.get(c, 0) / 10 ** DEC[c] for c in MONEY},
                                      "d_usd": net_usd, "other_tokens": oth,
                                      "is_tx_from": tx["from"] == a, "tx_to": tx.get("to")})
                    if counted and oth:
                        flags[o].append(f"{h}: counted tx also moves non-tracked token(s) {list(oth)} for {a}")
                    if counted and abs(net_usd) < 0.005 and not oth:
                        # WGNK moved with no money for this address: classify how
                        ZERO = "0x" + "0" * 40
                        srcs, dsts = set(), set()
                        for lg in rc["logs"]:
                            tp = lg["topics"]
                            if lg["address"] == WGNK and tp and tp[0] == T_TRANSFER and len(tp) == 3:
                                if addr_of(tp[2]) == a:
                                    srcs.add(addr_of(tp[1]))
                                if addr_of(tp[1]) == a:
                                    dsts.add(addr_of(tp[2]))
                        direct_call = tx.get("to") == WGNK
                        if w > 0:
                            kind = "mint" if srcs == {ZERO} else ("plain_in" if direct_call else "in_via_contract")
                        else:
                            kind = "burn" if dsts == {ZERO} else ("plain_out" if direct_call else "out_via_contract")
                        nomoney[o].append({"tx": h, "win": win, "addr": a, "d_wgnk": w / 1e9, "kind": kind,
                                           "tx_from": tx["from"], "tx_to": tx.get("to"),
                                           "counterparties": sorted((srcs if w > 0 else dsts) - {a})})
                    if not counted and abs(net_usd) >= 0.005:
                        flags[o].append(f"{h}: money moved (${-net_usd:+.2f} net spent) but |dWGNK|<1 for {a} -> excluded by dust rule")
                if not counted:
                    continue
                A_ = target[o][win]
                A_["n_tx"] += 1
                if w > 0:
                    A_["w_in"] += w / 1e9
                else:
                    A_["w_out"] += -w / 1e9
                for c in MONEY:
                    A_["q"][c] += -dd.get(c, 0) / 10 ** DEC[c]
                    A_["usd"][c] += -musd[c]
                if net_usd < 0:
                    A_["spent"] += -net_usd
                else:
                    A_["received"] += net_usd
                if win == "B":
                    k = K(ts)
                    if net_usd < 0:                      # tx-level net money outflow
                        A_["k_num"] += k * (-net_usd)
                        A_["k_den"] += -net_usd
                        A_["k_num_diag"] += K(ts, DIAG_LADDER) * (-net_usd)
                    gross = sum(-u for u in musd.values() if u < 0)   # alt: sum of per-currency outflows
                    if gross > 0:
                        A_["k_num_gross"] += k * gross
                        A_["k_den_gross"] += gross


# ---- 4. variants --------------------------------------------------------------------------
def payouts(a, b0_total):
    net_a = sum(a["A"]["usd"].values())
    net_b = sum(a["B"]["usd"].values())
    k_eff = a["B"]["k_num"] / a["B"]["k_den"] if a["B"]["k_den"] > 0 else 0.0
    res = {"net_a_usd": net_a, "net_b_usd": net_b, "k_eff": k_eff,
           "k_eff_diag_ladder": a["B"]["k_num_diag"] / a["B"]["k_den"] if a["B"]["k_den"] > 0 else 0.0,
           "k_eff_gross_alt": a["B"]["k_num_gross"] / a["B"]["k_den_gross"] if a["B"]["k_den_gross"] > 0 else 0.0}
    for name in ("v1", "v2", "v3"):
        if net_b <= 0:
            phi = 1.0
        else:
            phi = {"v1": 0.0, "v2": k_eff, "v3": 1.0}[name]
        q = {c: a["A"]["q"][c] + phi * a["B"]["q"][c] for c in MONEY}
        usd = {c: a["A"]["usd"][c] + phi * a["B"]["usd"][c] for c in MONEY}
        M = sum(usd.values())
        pay = {c: 0.0 for c in MONEY}
        if M > 0.005:
            pos = sum(u for u in usd.values() if u > 0)
            for c in MONEY:
                if usd[c] > 0:
                    pay[c] = q[c] * (M / pos)
            gnk = max(0.0, b0_total)
        else:
            gnk = max(0.0, b0_total + M / P0)
        res[name] = {"phi": phi, "m_usd": M, "gnk": gnk, **pay}
    return res


def cmp(mine, proj, tol):
    proj = 0.0 if proj is None or (isinstance(proj, float) and np.isnan(proj)) else float(proj)
    diff = abs(mine - proj)
    return {"mine": mine, "project": proj, "abs_diff": diff, "ok": bool(diff <= tol)}


out = []
for r in sample.itertuples():
    o = r.entity
    al = owner_addrs[o]
    b0_wallet = sum(b0_raw[a] for a in al) / 1e9
    pend = float(r.b0_pending_burn or 0.0)
    b0_total = b0_wallet + pend
    mine = payouts(acc[o], b0_total)
    alt = payouts(acc_cl[o], b0_total)
    row = {"entity": o, "addresses": al, "category": r.category, "has_b": bool(r.has_b),
           "b0_pending_burn_project": pend,
           "b0_wallet": cmp(b0_wallet, r.b0_wallet, TOL["b0"]),
           "honest_wgnk": cmp(b0_total, r.honest_wgnk, TOL["b0"]),
           "net_a_usd": cmp(mine["net_a_usd"], r.net_a_usd, TOL["usd"]),
           "net_b_usd": cmp(mine["net_b_usd"], r.net_b_usd, TOL["usd"]),
           "k_eff": cmp(mine["k_eff"], r.k_eff, TOL["k"]),
           "k_eff_gross_alt": mine["k_eff_gross_alt"],
           "k_eff_diag_project_base_ladder": mine["k_eff_diag_ladder"],
           "any_address_signed_a_tx_in_dataset": any(a in signers for a in al)}
    for v in ("v1", "v2", "v3"):
        row[v] = {"phi": cmp(mine[v]["phi"], getattr(r, f"{v}_phi"), 1e-4),
                  "m_usd": cmp(mine[v]["m_usd"], getattr(r, f"{v}_m_usd"), TOL["usd"]),
                  "gnk": cmp(mine[v]["gnk"], getattr(r, f"{v}_pay_gnk"), TOL["gnk"]),
                  "usdt": cmp(mine[v]["usdt"], getattr(r, f"{v}_pay_usdt"), TOL["usdt"]),
                  "usdc": cmp(mine[v]["usdc"], getattr(r, f"{v}_pay_usdc"), TOL["usdc"]),
                  "dai": cmp(mine[v]["dai"], getattr(r, f"{v}_pay_dai"), TOL["dai"]),
                  "eth": cmp(mine[v]["eth"], getattr(r, f"{v}_pay_eth"), TOL["eth"])}
    # pass/fail on the fields the brief lists: B0, net_A, net_B, k_eff, payouts gnk/usdt/usdc/eth (+dai)
    checks = [row["b0_wallet"]["ok"], row["net_a_usd"]["ok"], row["net_b_usd"]["ok"], row["k_eff"]["ok"]]
    for v in ("v1", "v2", "v3"):
        checks += [row[v][c]["ok"] for c in ("gnk", "usdt", "usdc", "dai", "eth")]
    row["pass"] = bool(all(checks))
    row["failed_fields"] = (
        [f for f in ("b0_wallet", "net_a_usd", "net_b_usd", "k_eff") if not row[f]["ok"]]
        + [f"{v}.{c}" for v in ("v1", "v2", "v3") for c in ("gnk", "usdt", "usdc", "dai", "eth") if not row[v][c]["ok"]])
    row["my_window_stats"] = {w: {k: acc[o][w][k] for k in ("spent", "received", "w_in", "w_out", "n_tx")} | {"q": acc[o][w]["q"], "usd": acc[o][w]["usd"]} for w in ("A", "B")}
    row["project_window_stats"] = {w.upper(): {k: float(getattr(r, f"{w}_{k}") or 0) for k in ("w_in", "usd_out", "w_out", "usd_in", "n_tx")} for w in ("a", "b")}
    row["alt_cluster_dust_rule"] = {"net_a_usd": alt["net_a_usd"], "net_b_usd": alt["net_b_usd"], "k_eff": alt["k_eff"],
                                    **{v: {c: alt[v][c] for c in ("gnk", "usdt", "usdc", "dai", "eth")} for v in ("v1", "v2", "v3")}}
    row["flags"] = flags.get(o, [])
    row["wgnk_moves_without_money"] = nomoney.get(o, []) if not ALL else None
    row["wgnk_moves_without_money_summary"] = {}
    for x in nomoney.get(o, []):
        dsum = row["wgnk_moves_without_money_summary"].setdefault(x["kind"], {"n": 0, "wgnk": 0.0})
        dsum["n"] += 1
        dsum["wgnk"] += x["d_wgnk"]
    out.append(row)

n_pass = sum(1 for r in out if r["pass"])
result = {
    "seed": SEED, "sampling_attempt": attempt, "p0": P0,
    "constants": {"snap_block": SNAP_BLOCK, "window_A": [A_FROM, A_TO], "window_B": [B_FROM, B_TO], "gradient": GRADIENT,
                  "dust_wgnk": 1},
    "tolerances": TOL,
    "pool_sizes_before_lp_filter": n_pool_before, "pool_sizes_after_lp_filter": n_pool_after,
    "sample_size": len(out), "sample_has_b": int(sample.has_b.sum()), "sample_eth_payers": int(sample.eth_payer.sum()),
    "n_pass": n_pass, "n_fail": len(out) - n_pass,
    "discrepancy_diagnosis": (
        "All failures are in k_eff / v2 payouts only. My K(t) uses the gradient from the audit brief (= raw/return.json): "
        "0.5 until 1795051447, 0.25 until 1795079617, 0.125 until 1795134247. The project's variants.parquet k_eff / v2_* "
        "columns are reproduced exactly by a different ladder (model/comp3.json -> gradient): 0.5 until 1795052141, "
        "0.25 until 1795089780, 0.125 until 1795134247 (see k_eff_diag_project_base_ladder per owner; diagnostic only, "
        "not used for my payouts). B0, net_A, net_B, v1 and v3 match for every owner."),
    "owners": out,
}
json.dump(result, open(f"{OUT}/independent_recompute{SUFFIX}.json", "w"), indent=1)
json.dump(detail, open(f"{OUT}/my_tx_detail{SUFFIX}.json", "w"), indent=1)
json.dump(nomoney, open(f"{OUT}/my_nomoney_moves{SUFFIX}.json", "w"), indent=1)

pd.set_option("display.width", 250)
print(f"PASS {n_pass}/{len(out)}")
for r in out:
    if ALL and r["pass"]:
        continue
    print(f"{'OK  ' if r['pass'] else 'FAIL'} {r['category']:14s} {r['entity']} n_addr={len(r['addresses'])} has_b={int(r['has_b'])} "
          f"b0={r['b0_wallet']['mine']:.3f} netA={r['net_a_usd']['mine']:.2f}/{r['net_a_usd']['project']:.2f} "
          f"netB={r['net_b_usd']['mine']:.2f}/{r['net_b_usd']['project']:.2f} k={r['k_eff']['mine']:.4f}/{r['k_eff']['project']:.4f} "
          f"v2: gnk {r['v2']['gnk']['mine']:.2f}/{r['v2']['gnk']['project']:.2f} usdt {r['v2']['usdt']['mine']:.2f}/{r['v2']['usdt']['project']:.2f} "
          f"usdc {r['v2']['usdc']['mine']:.2f}/{r['v2']['usdc']['project']:.2f} eth {r['v2']['eth']['mine']:.5f}/{r['v2']['eth']['project']:.5f} "
          f"{r['failed_fields'] if not r['pass'] else ''}")
    for f in (r["flags"] if not ALL else []):
        print("      flag:", f)
