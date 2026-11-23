"""Три варианта компенсаций с отсечкой по официальному предупреждению Gonka (19.11.2026 00:24:07 UTC).

Окно А — от начала атаки до предупреждения (обязательство): формула без изменений.
Окно Б — после предупреждения до заморозки данных (право, не обязательство):
    net_Б = потрачено_Б − получено_Б (деньги за WGNK, включая операции LP и изменение позиций LP);
    net_Б ≤ 0 → вычитается целиком во всех вариантах (на взломе никто не зарабатывает);
    net_Б > 0 → в расчёт идёт φ · net_Б:  вариант 1 — φ = 0;  вариант 2 — φ = k (средний K(t) покупок владельца,
    взвешенный суммой покупки);  вариант 3 — φ = 1.
Дальше — как раньше: M = M_А + φ·M_Б по валютам; M > 0 → потерянные валюты возвращаются количеством,
GNK = честные WGNK; M ≤ 0 → GNK = max(0, честные + M / p₀).
"""

from __future__ import annotations

import json
from collections import defaultdict

import pandas as pd

from .lite import Paths, save_json, save_parquet
from .exploit_const import FREEZE_TS, GRADIENT, GRADIENT_ALT_0913, KEY_BLOCK, SNAP_BLOCK, WARN_TS, ex_paths
from .exploit_model import GAS, KIND_TOKENS, TOKEN_ALIAS, _eth_price, _load, balances

VARIANTS = ("v1", "v2", "v3")
ALL_V = list(VARIANTS) + ["v0_ignore_b", "v2_exp", "v2_ladder10", "v2_ladder0913"]
PAY = ("gnk", "usdt", "usdc", "dai", "eth")
DUST_USD = 0.01


# ── Коэффициент K(t) ────────────────────────────────────────────────────────

def k_ladder(ts: float) -> float:
    """Основной градиент варианта 2: 1/2 → 1/4 → 1/8 → 0 (границы — в exploit.GRADIENT)."""
    if ts <= WARN_TS:
        return 1.0
    for until, k in GRADIENT:
        if ts <= until:
            return k
    return 0.0


def k_exp(ts: float) -> float:
    """Чувствительность: гладкая экспонента, полураспад 1 час, ноль через 24 часа."""
    if ts <= WARN_TS:
        return 1.0
    dt = ts - WARN_TS
    return 0.5 ** (dt / 3600) if dt <= 86400 else 0.0


def k_ladder_10(ts: float) -> float:
    """Чувствительность: лестница 50 / 25 / 10 % с теми же границами."""
    k = k_ladder(ts)
    return 0.10 if k == 0.125 else k


def k_ladder_0913(ts: float) -> float:
    """Чувствительность: границы «1 час / официальное „средства возвращены“ 09:13:37 / сутки»."""
    if ts <= WARN_TS:
        return 1.0
    for until, k in GRADIENT_ALT_0913:
        if ts <= until:
            return k
    return 0.0


SCHEMES = {"ladder": k_ladder, "exp": k_exp, "ladder10": k_ladder_10, "ladder0913": k_ladder_0913}


# ── Категории окна А ────────────────────────────────────────────────────────

def category_a(r: dict) -> str:
    if r["is_hacker"]:
        return "hacker"
    had = r["b0_wallet"] + r["b0_pending_burn"] > 1e-6
    lp = r["lp_w_before"] + r["lp_u_before"] > 1e-6 or r["a_lp_usd"] > 0.01
    bought, sold = r["a_w_in"] > 1e-9 and r["a_usd_out"] > 0.005, r["a_w_out"] > 1e-9 and r["a_usd_in"] > 0.005
    if lp:
        return "lp"
    if had:
        return "holder" if not bought and not sold else ("holder_sold" if sold and not bought else "holder_traded")
    if not bought and not sold:
        return "b_only" if r["b_usd_out"] + r["b_usd_in"] > 0.01 else "transfers"
    if bought and not sold:
        return "buyer"
    return "trader_loss" if r["net_a_usd"] > 0.005 else "trader_profit"


# ── Расчёт ──────────────────────────────────────────────────────────────────

def compute(paths: Paths) -> dict:
    ex = ex_paths(paths)
    d = _load(ex)
    meta, p0 = d["meta"], d["meta"]["p0_vwap24h"]
    t1_block = int(meta["t1_block"])
    part = pd.read_parquet(ex.model / "parquet" / "participants.parquet")
    deltas = pd.read_parquet(ex.model / "parquet" / "tx_deltas.parquet")
    pos = pd.read_parquet(ex.model / "parquet" / "lp_positions.parquet")
    ret = json.loads((ex.raw / "return.json").read_text())
    px_snap = _eth_price(d, SNAP_BLOCK)

    # Время блока: точное (ex_blocks); запасной вариант — 12 с на блок от границы T₁.
    deltas["ts"] = deltas.apply(lambda r: r["ts"] if pd.notna(r.get("ts")) else WARN_TS + (r["block"] - t1_block) * 12, axis=1).astype(float)
    deltas["win"] = deltas["block"].map(lambda b: "A" if b <= t1_block else "B")
    ts_mismatch = int(((deltas["win"] == "A") & (deltas["ts"] > WARN_TS)).sum() + ((deltas["win"] == "B") & (deltas["ts"] <= WARN_TS)).sum())
    for name, fn in SCHEMES.items():
        deltas[f"k_{name}"] = deltas["ts"].map(fn)

    # Коэффициент для потерь позиций LP в окне Б: K, взвешенный объёмом сделок пулов во времени.
    sw = d["swaps"]
    sw = sw[sw["block_number"] > t1_block].copy()
    sw["ts"] = pd.to_datetime(sw["block_time"], utc=True).astype("int64") // 10 ** 9
    sw["usd"] = sw["usd_value"].astype(float)
    k_pool = {name: float((sw["ts"].map(fn) * sw["usd"]).sum() / sw["usd"].sum()) if sw["usd"].sum() else 0.0 for name, fn in SCHEMES.items()}

    qty = {w: defaultdict(lambda: defaultdict(float)) for w in "AB"}
    usd = {w: defaultdict(lambda: defaultdict(float)) for w in "AB"}
    ausd = {w: defaultdict(lambda: defaultdict(float)) for w in "AB"}     # то же по отдельным адресам — для раздела выплаты в группе
    wk = {name: defaultdict(float) for name in SCHEMES}
    wsum = defaultdict(float)
    st = defaultdict(lambda: defaultdict(float))
    for r in deltas.itertuples(index=False):
        e, w = r.entity, r.win
        out_i = 0.0
        for t, v in json.loads(r.tokens or "{}").items():
            k = TOKEN_ALIAS.get(t)
            if not k:
                continue
            u = -v * (r.eth_usd if k == "ETH" else 1.0)
            qty[w][e][k] += -v
            usd[w][e][k] += u
            ausd[w][r.address][k] += u
            if u > 0:
                out_i += u
        if w == "B" and out_i > 0:
            wsum[e] += out_i
            for name in SCHEMES:
                wk[name][e] += getattr(r, f"k_{name}") * out_i
        pre = w.lower()
        if r.is_lp_tx:
            st[e][f"{pre}_lp_usd"] += abs(r.d_usd)
        elif abs(r.d_usd) >= 0.01:
            if r.d_wgnk > 0:
                st[e][f"{pre}_w_in"] += r.d_wgnk
            elif r.d_wgnk < 0:
                st[e][f"{pre}_w_out"] += -r.d_wgnk
            if r.d_usd < 0:
                st[e][f"{pre}_usd_out"] += -r.d_usd
            else:
                st[e][f"{pre}_usd_in"] += r.d_usd
        st[e][f"{pre}_n_tx"] += 1
        if getattr(r, "via_third_party", None):
            st[e][f"{pre}_via_usd"] += -r.d_usd
        if w == "B":
            st[e]["b_first_ts"] = min(st[e].get("b_first_ts") or r.ts, r.ts)
            st[e]["b_last_ts"] = max(st[e].get("b_last_ts") or r.ts, r.ts)

    # Позиции LP: до взлома → T₁ — окно А; T₁ → заморозка — окно Б.
    lp_state = defaultdict(lambda: defaultdict(float))
    for r in pos.itertuples(index=False):
        k = TOKEN_ALIAS.get(r.money_token)
        if not r.entity or not k:
            continue
        amt, u = float(r.money_amount), float(r.money_amount) * (px_snap if k == "ETH" else 1.0)
        lp_state[r.entity][f"u_{r.state}"] += u
        lp_state[r.entity][f"w_{r.state}"] += float(r.wgnk)
        for w, sgn in {"snap": (("A", 1),), "t1": (("A", -1), ("B", 1)), "end": (("B", -1),)}[r.state]:
            qty[w][r.entity][k] += sgn * amt
            usd[w][r.entity][k] += sgn * u
            ausd[w][(r.owner or "").lower()][k] += sgn * u
    for e, s_ in lp_state.items():
        drain = s_["u_t1"] - s_["u_end"]
        if drain > 0:
            wsum[e] += drain
            for name in SCHEMES:
                wk[name][e] += k_pool[name] * drain

    def payout(row, phi: float) -> dict:
        e = row["entity"]
        out = {f"pay_{t}": 0.0 for t in PAY}
        out["m_usd"] = 0.0
        if row["is_hacker"]:
            return out
        q = {t: qty["A"][e][t] + phi * qty["B"][e][t] for t in KIND_TOKENS}
        u = {t: usd["A"][e][t] + phi * usd["B"][e][t] for t in KIND_TOKENS}
        m = sum(u.values())
        out["m_usd"] = m
        honest = row["honest_wgnk"] - row["g_credited"]
        if m > 0.005:
            pos_usd = sum(v for v in u.values() if v > 0)
            f = m / pos_usd if pos_usd > 0 else 0.0
            for t in KIND_TOKENS:
                if u[t] > 0:
                    out[f"pay_{t.lower()}"] = q[t] * f
            out["pay_gnk"] = max(0.0, honest)
        else:
            out["pay_gnk"] = max(0.0, honest + m / p0)
        return out

    rows = []
    known = set(part["entity"])
    for _, row in part.iterrows():
        e = row["entity"]
        net_a, net_b = sum(usd["A"][e].values()), sum(usd["B"][e].values())
        keff = {name: (wk[name][e] / wsum[e] if wsum[e] > 0 else 0.0) for name in SCHEMES}
        phi = {"v1": 0.0 if net_b > 0 else 1.0, "v2": keff["ladder"] if net_b > 0 else 1.0, "v3": 1.0,
               "v0_ignore_b": 0.0, "v2_exp": keff["exp"] if net_b > 0 else 1.0, "v2_ladder10": keff["ladder10"] if net_b > 0 else 1.0,
               "v2_ladder0913": keff["ladder0913"] if net_b > 0 else 1.0}
        r = {"entity": e, "addresses": row["addresses"], "is_hacker": bool(row["is_hacker"]),
             "b0_wallet": row["b0_wallet"], "b0_pending_burn": row["b0_pending_burn"], "lp_w_before": row["lp_w_before"],
             "lp_u_before": lp_state[e]["u_snap"], "lp_u_t1": lp_state[e]["u_t1"], "lp_u_end": lp_state[e]["u_end"],
             "honest_wgnk": row["honest_wgnk"], "g_credited": row["g_credited"], "wgnk_end_wallet": row["wgnk_end_wallet"],
             "burn_pending_post": row["burn_pending_post"],
             "net_a_usd": net_a, "net_b_usd": net_b, "k_eff": keff["ladder"], "k_eff_exp": keff["exp"], "k_eff_ladder10": keff["ladder10"],
             **{k: float(st[e].get(k, 0.0)) for k in ("a_w_in", "a_usd_out", "a_w_out", "a_usd_in", "a_lp_usd", "a_n_tx",
                                                      "b_w_in", "b_usd_out", "b_w_out", "b_usd_in", "b_lp_usd", "b_n_tx", "a_via_usd", "b_via_usd")},
             "b_first_ts": st[e].get("b_first_ts"), "b_last_ts": st[e].get("b_last_ts")}
        r["has_b"] = bool(r["b_n_tx"] > 0 or abs(lp_state[e]["u_t1"] - lp_state[e]["u_end"]) > DUST_USD)
        r["category"] = category_a(r)
        for v, ph in phi.items():
            po = payout(row, ph)
            r[f"{v}_phi"] = ph
            for k, val in po.items():
                r[f"{v}_{k}"] = val
        # Вариант 1 ≤ 2 ≤ 3 по каждой валюте: зачёт валют «в плюсе» идёт по курсу ETH на день сделки, и без этого у владельца
        # с мелкой выручкой в ETH после предупреждения вариант 3 мог дать на доли цента меньше ETH, чем вариант 1.
        for lo, hi in (("v1", "v2"), ("v2", "v3")):
            for k in PAY:
                r[f"{hi}_pay_{k}"] = max(r[f"{hi}_pay_{k}"], r[f"{lo}_pay_{k}"])
        rows.append(r)
    missing = sorted(set(deltas["entity"]) - known)
    vt = pd.DataFrame(rows)

    eth_usd = ret["eth_usd_now"]
    for v in ALL_V:
        vt[f"{v}_money_usd"] = vt[f"{v}_pay_usdt"] + vt[f"{v}_pay_usdc"] + vt[f"{v}_pay_dai"] + vt[f"{v}_pay_eth"] * eth_usd
        vt[f"{v}_paid"] = (~vt["is_hacker"]) & ((vt[f"{v}_pay_gnk"] > 0.5) | (vt[f"{v}_money_usd"] > DUST_USD))
        vt[f"{v}_value_usd"] = vt[f"{v}_pay_gnk"] * p0 + vt[f"{v}_money_usd"]
    vt["differs"] = ((vt["v1_value_usd"] - vt["v3_value_usd"]).abs() > 0.01) | ((vt["v1_value_usd"] - vt["v2_value_usd"]).abs() > 0.01)
    vt = vt.sort_values("v3_value_usd", ascending=False).reset_index(drop=True)
    save_parquet(vt, ex.model / "parquet" / "variants.parquet")
    save_parquet(deltas, ex.model / "parquet" / "tx_deltas_windows.parquet")

    # Получатели по адресам. У владельца из нескольких адресов выплата делится по тому, где возникло право: GNK — адресу,
    # который держал WGNK до взлома; деньги — адресу, который их платил. Раньше вся выплата группы шла на «первый по алфавиту»
    # адрес (в 7 группах это был не тот адрес, что держал WGNK). Итог по владельцу не меняется.
    b0 = balances(d["tr"], SNAP_BLOCK)
    base = json.loads((ex.model / "ex_model.json").read_text())
    pend_by = defaultdict(float)
    for x in base.get("pending_pre") or []:
        if x.get("eth_owner"):
            pend_by[x["eth_owner"].lower()] += float(x["amount_gnk"])
    lpw_by = defaultdict(float)
    for r in pos[pos["state"] == "snap"].itertuples(index=False):
        lpw_by[(r.owner or "").lower()] += float(r.wgnk)
    pay_rows = []
    for _, r in vt.iterrows():
        ad = r["addresses"].split(";")
        if len(ad) == 1 or r["is_hacker"]:
            pay_rows.append({**r.to_dict(), "owner": r["entity"], "group_size": len(ad)})
            continue
        hon = {a: float(b0.get(a, 0.0)) + pend_by[a] + lpw_by[a] for a in ad}
        parts = {a: {"owner": r["entity"], "group_size": len(ad), "entity": a, "b0_wallet": float(b0.get(a, 0.0)), "b0_pending_burn": pend_by[a],
                     "lp_w_before": lpw_by[a], "honest_wgnk": hon[a]} for a in ad}
        for v in ALL_V:
            ph = r[f"{v}_phi"]
            out = {a: {t: ausd["A"][a][t] + ph * ausd["B"][a][t] for t in KIND_TOKENS} for a in ad}
            for k in PAY:
                amount = float(r[f"{v}_pay_{k}"])
                if k == "gnk":
                    w = {a: max(0.0, hon[a]) for a in ad}
                else:
                    w = {a: max(0.0, out[a][k.upper()]) for a in ad}
                    if sum(w.values()) <= 0:
                        w = {a: max(0.0, sum(out[a].values())) for a in ad}
                if sum(w.values()) <= 0:
                    w = {a: 1.0 if a == r["entity"] else 0.0 for a in ad}
                tw_ = sum(w.values())
                for a in ad:
                    parts[a][f"{v}_pay_{k}"] = amount * w[a] / tw_
            # Мелкие остатки (меньше порога выплаты) переносятся на главный адрес группы, чтобы итог сошёлся.
            val = {a: parts[a][f"{v}_pay_gnk"] * p0 + sum(parts[a][f"{v}_pay_{k}"] * (eth_usd if k == "eth" else 1.0) for k in PAY if k != "gnk") for a in ad}
            top = max(val, key=val.get)
            for a in ad:
                money = sum(parts[a][f"{v}_pay_{k}"] * (eth_usd if k == "eth" else 1.0) for k in PAY if k != "gnk")
                if a != top and parts[a][f"{v}_pay_gnk"] <= 0.5 and money <= DUST_USD:
                    for k in PAY:
                        parts[top][f"{v}_pay_{k}"] += parts[a][f"{v}_pay_{k}"]
                        parts[a][f"{v}_pay_{k}"] = 0.0
        keep = {k: r[k] for k in r.index if k not in parts[ad[0]] and not any(k.startswith(f"{v}_pay_") or k in (f"{v}_money_usd", f"{v}_paid", f"{v}_value_usd") for v in ALL_V)}
        pay_rows += [{**keep, **x} for x in parts.values()]
    pt = pd.DataFrame(pay_rows)
    for v in ALL_V:
        pt[f"{v}_money_usd"] = pt[f"{v}_pay_usdt"] + pt[f"{v}_pay_usdc"] + pt[f"{v}_pay_dai"] + pt[f"{v}_pay_eth"] * eth_usd
        pt[f"{v}_paid"] = (~pt["is_hacker"]) & ((pt[f"{v}_pay_gnk"] > 0.5) | (pt[f"{v}_money_usd"] > DUST_USD))
        pt[f"{v}_value_usd"] = pt[f"{v}_pay_gnk"] * p0 + pt[f"{v}_money_usd"]
    pt["differs"] = ((pt["v1_value_usd"] - pt["v3_value_usd"]).abs() > 0.01) | ((pt["v1_value_usd"] - pt["v2_value_usd"]).abs() > 0.01)
    pt = pt.sort_values("v3_value_usd", ascending=False).reset_index(drop=True)
    save_parquet(pt, ex.model / "parquet" / "payees.parquet")

    # Заявки GNK → WGNK «в пути»: GNK заперты в мосте, WGNK не выпущены. Возвращаются отправителю в сети Gonka во всех вариантах.
    flight = bridge_in_flight(ex, d)
    save_parquet(flight, ex.model / "parquet" / "bridge_in_flight.parquet")
    fl = flight.groupby("gonka_sender")["gnk"].sum() if len(flight) else pd.Series(dtype=float)
    fl = fl[fl >= 0.5]
    in_flight = {"requests": int(len(flight)), "senders": int(flight["gonka_sender"].nunique()) if len(flight) else 0,
                 "gnk_all": float(flight["gnk"].sum()) if len(flight) else 0.0, "recipients": int(len(fl)), "gnk": float(fl.sum()),
                 "after_attack_gnk": float(flight.loc[flight["after_attack"], "gnk"].sum()) if len(flight) else 0.0}
    escrow_gnk = float(((d["gonka"].get("escrow") or {}).get("now") or {}).get("gnk") or 0.0)

    summ = {"p0": p0, "eth_usd_now": eth_usd, "t0_block": KEY_BLOCK, "snap_block": SNAP_BLOCK, "t1_block": t1_block, "t1_ts": WARN_TS,
            "t2_block": meta["s_end_block"], "t2_ts": FREEZE_TS, "k_pool": k_pool, "ts_mismatch_rows": ts_mismatch,
            "entities_missing_in_base": missing,
            "gradient": [{"until_ts": int(min(u, FREEZE_TS)), "k": k} for u, k in GRADIENT],
            "windows": windows_stats(deltas, sw, d["swaps"], t1_block),
            "variants": {v: settle(pt, v, ret, d["forensics"], p0, escrow_gnk, in_flight["gnk"]) for v in ALL_V},
            "bridge_in_flight": in_flight, "escrow_gnk_now": escrow_gnk,
            "categories": cat_table(pt, p0), "checks": {**checks(vt, p0, d, ret), **split_checks(vt, pt)},
            "counts": {"owners": int(len(vt)), "owners_paid_v3": int(vt["v3_paid"].sum()), "payees": int((pt["v1_paid"] | pt["v2_paid"] | pt["v3_paid"]).sum()),
                       "groups": int((vt["addresses"].str.contains(";") & ~vt["is_hacker"]).sum()),
                       "differs": int((pt["differs"] & pt["v3_paid"]).sum()),
                       "same": int((pt["v3_paid"] & ~pt["differs"]).sum()), "has_b": int(vt["has_b"].sum())}}
    save_json(summ, ex.model / "comp3.json")
    return summ


def windows_stats(deltas: pd.DataFrame, sw_b: pd.DataFrame, swaps: pd.DataFrame, t1_block: int) -> dict:
    sa = swaps[(swaps["block_number"] >= KEY_BLOCK) & (swaps["block_number"] <= t1_block)]
    out = {"A": {"swaps": int(len(sa)), "usd": float(sa["usd_value"].astype(float).sum()), "txs": int(deltas.loc[deltas["win"] == "A", "tx_hash"].nunique()),
                 "entities": int(deltas.loc[deltas["win"] == "A", "entity"].nunique())},
           "B": {"swaps": int(len(sw_b)), "usd": float(sw_b["usd"].sum()), "txs": int(deltas.loc[deltas["win"] == "B", "tx_hash"].nunique()),
                 "entities": int(deltas.loc[deltas["win"] == "B", "entity"].nunique())}}
    steps, lo = [], WARN_TS
    for until, k in GRADIENT:
        hi = min(until, FREEZE_TS)
        x = sw_b[(sw_b["ts"] > lo) & (sw_b["ts"] <= hi)]
        dd = deltas[(deltas["ts"] > lo) & (deltas["ts"] <= hi) & (deltas["win"] == "B")]
        steps.append({"from_ts": int(lo), "to_ts": int(hi), "k": k, "swaps": int(len(x)), "usd": float(x["usd"].sum()),
                      "entities": int(dd["entity"].nunique())})
        lo = hi
    out["B_steps"] = steps
    return out


def split_checks(vt: pd.DataFrame, pt: pd.DataFrame) -> dict:
    """Раздел выплаты по адресам не меняет итогов владельца: суммы по адресам группы = сумме владельца."""
    out = {}
    for v in VARIANTS:
        for k in PAY:
            a = vt.loc[~vt["is_hacker"]].set_index("entity")[f"{v}_pay_{k}"]
            b = pt.loc[~pt["is_hacker"]].groupby("owner")[f"{v}_pay_{k}"].sum().reindex(a.index).fillna(0.0)
            out[f"split_{v}_{k}_max_diff"] = float((a - b).abs().max())
    return {"payee_split_max_diff": max(out.values()), "payee_rows": int(len(pt))}


def bridge_in_flight(ex: Paths, d: dict) -> pd.DataFrame:
    """Успешные заявки MsgRequestBridgeMint, по которым WGNK так и не выпущен: GNK отправителя заперты в залоге моста."""
    cols = ["gonka_sender", "eth_destination", "gnk", "gonka_height", "time_utc", "gonka_tx", "after_attack"]
    p = ex.raw / "db" / "bridge_requests_status.parquet"
    if not p.exists():
        return pd.DataFrame(columns=cols)
    rq = pd.read_parquet(p)
    rq = rq[rq["success"]].sort_values("height")
    m = d["bridge"][d["bridge"]["kind"] == "mint"]
    free = defaultdict(list)
    for i, r in m.iterrows():
        free[r["recipient"].lower()].append([i, float(r["amount_wgnk"])])
    rows = []
    for q in rq.itertuples():
        dest = (q.dest or "").lower()
        hit = next((x for x in free[dest] if abs(x[1] - float(q.gnk)) < 1e-6), None)
        if hit:
            free[dest].remove(hit)
        else:
            rows.append({"gonka_sender": q.signer, "eth_destination": dest, "gnk": float(q.gnk), "gonka_height": int(q.height),
                         "time_utc": str(q.block_time), "gonka_tx": q.tx_hash, "after_attack": pd.Timestamp(q.block_time).timestamp() >= 1_795_024_859})
    return pd.DataFrame(rows, columns=cols)


def settle(vt: pd.DataFrame, v: str, ret: dict, fz: dict, p0: float, escrow_gnk: float = 0.0, in_flight_gnk: float = 0.0) -> dict:
    """Свод варианта: получатели, выплаты по валютам, потребность в ETH, доплата протокола сверх возврата хакера."""
    x = vt[vt[f"{v}_paid"]]
    eth_usd = ret["eth_usd_now"]
    tot = {k: float(x[f"{v}_pay_{k}"].sum()) for k in PAY}
    res = fz["reserves"]
    pre = res.get(str(KEY_BLOCK - 1)) or res.get(str(KEY_BLOCK))
    reserve = {"usdt": pre["usdt"], "usdc": pre["usdc"]}
    n_eth = int((x[f"{v}_pay_eth"] > 1e-9).sum())
    n_tok = int(sum((x[f"{v}_pay_{k}"] > 0.005).sum() for k in ("usdt", "usdc", "dai")))
    n_gnk = int((x[f"{v}_pay_gnk"] > 0.5).sum())
    gas_eth = (n_eth * GAS["eth"] + (n_tok + 2) * GAS["erc20"] + 3 * GAS["swap"]) * ret["gas_price_gwei"] * 1e-9
    eth_returned = ret["admin_eth"]["after_return"] - ret["admin_eth"]["before_return"]
    gnk_returned = sum(int(po["amount"]) / 1e9 for dd in ret["gnk_txs"].values() for msg in ((dd or {}).get("messages") or [])
                       for po in ((msg.get("fields") or {}).get("payouts") or []) if po.get("denom") == "ngonka")
    stables_people = tot["usdt"] + tot["usdc"] + tot["dai"]
    stables_all = stables_people + reserve["usdt"] + reserve["usdc"]

    def cost(px: float) -> dict:
        eth_need = tot["eth"] + stables_all / px + gas_eth
        gap_eth = max(0.0, eth_need - eth_returned)
        # GNK: нужно держателям и по заявкам «в пути»; есть — возврат хакера и остаток залога моста (не украденная часть).
        gnk_gap = max(0.0, tot["gnk"] + in_flight_gnk - gnk_returned - escrow_gnk)
        c = gnk_gap * p0 + gap_eth * px
        return {"eth_usd": px, "eth_need": eth_need, "eth_gap": gap_eth, "eth_surplus": max(0.0, eth_returned - eth_need), "gnk_gap": gnk_gap,
                "cost_usd": c, "cost_gnk_eq": c / p0}
    base = cost(eth_usd)
    cp = ret["community_pool"]["now"]["gnk"]
    return {"recipients": int(len(x)), "recipients_gnk": n_gnk, "recipients_money": int((x[f"{v}_money_usd"] > DUST_USD).sum()),
            "recipients_ge_1usd": int((x[f"{v}_value_usd"] >= 1).sum()),
            "totals": tot, "reserve": reserve, "stables_people_usd": stables_people, "money_people_usd": float(x[f"{v}_money_usd"].sum()),
            "value_people_usd": float(x[f"{v}_value_usd"].sum()),
            "n_eth": n_eth, "n_token_transfers": n_tok, "gas_eth": gas_eth, "gas_usd": gas_eth * eth_usd,
            "eth_returned": eth_returned, "gnk_returned": gnk_returned, "gnk_in_escrow": escrow_gnk, "gnk_in_flight": in_flight_gnk,
            "gnk_need": tot["gnk"] + in_flight_gnk, **base,
            "community_pool_now": cp, "cost_share_pool": base["cost_gnk_eq"] / cp if cp else None,
            "sensitivity_eth": {"-10%": cost(eth_usd * 0.9), "+10%": cost(eth_usd * 1.1)}}


def cat_table(vt: pd.DataFrame, p0: float) -> dict:
    out = {}
    for v in VARIANTS:
        t = {}
        for c, g in vt.groupby("category"):
            x = g[g[f"{v}_paid"]]
            t[c] = {"owners": int(len(g)), "paid": int(len(x)), **{k: float(x[f"{v}_pay_{k}"].sum()) for k in PAY},
                    "value_usd": float(x[f"{v}_value_usd"].sum()), "honest_wgnk": float(g["honest_wgnk"].sum()),
                    "net_a_usd": float(g["net_a_usd"].sum()), "net_b_usd": float(g["net_b_usd"].sum())}
        out[v] = t
    return out


def checks(vt: pd.DataFrame, p0: float, d: dict, ret: dict) -> dict:
    x = vt[~vt["is_hacker"]]
    out = {}
    # 1. Стоимость выплаты = формуле: GNK·p₀ + деньги (по курсу сделок) = max(0, честные − выдано)·p₀ + M, если M > 0; иначе max(0, …).
    for v in VARIANTS:
        m = x[f"{v}_m_usd"]
        honest = (x["honest_wgnk"] - x["g_credited"])
        formula_gnk = (honest + m.where(m <= 0.005, 0) / p0).clip(lower=0)
        out[f"{v}_gnk_formula_max_diff"] = float((x[f"{v}_pay_gnk"] - formula_gnk).abs().max())
        out[f"{v}_money_only_when_m_positive"] = bool(((x[f"{v}_money_usd"] > DUST_USD) <= (m > 0.005)).all())
    # 2. Монотонность: вариант 1 ≤ вариант 2 ≤ вариант 3 по стоимости у каждого владельца (допуск — курс ETH на выплату).
    tol = 0.02
    out["monotonic_v1_le_v2"] = int(((x["v1_m_usd"].clip(lower=0) - x["v2_m_usd"].clip(lower=0)) > tol).sum())
    out["monotonic_v2_le_v3"] = int(((x["v2_m_usd"].clip(lower=0) - x["v3_m_usd"].clip(lower=0)) > tol).sum())
    out["gnk_monotonic_violations"] = int(((x["v1_pay_gnk"] - x["v2_pay_gnk"]) > 1e-6).sum() + ((x["v2_pay_gnk"] - x["v3_pay_gnk"]) > 1e-6).sum())
    out["payout_monotonic_violations"] = int(sum(((x[f"{lo}_pay_{k}"] - x[f"{hi}_pay_{k}"]) > 1e-9).sum() for lo, hi in (("v1", "v2"), ("v2", "v3")) for k in PAY))
    out["phi_in_0_1"] = bool(((x["v2_phi"] >= 0) & (x["v2_phi"] <= 1)).all())
    # 3. Владельцы без сделок в окне Б получают одинаково во всех вариантах.
    nb = x[~x["has_b"]]
    out["no_b_identical"] = int(((nb["v1_value_usd"] - nb["v3_value_usd"]).abs() > 0.01).sum())
    # 4. Никто не зарабатывает: выплата деньгами не больше чистых потерь владельца в деньгах.
    out["third_party_attributed"] = {"owners": int(((x["a_via_usd"].abs() + x["b_via_usd"].abs()) > 0.01).sum()),
                                     "window_a_net_usd": float(x["a_via_usd"].sum()), "window_b_net_usd": float(x["b_via_usd"].sum())}
    out["hacker_paid"] = float(vt.loc[vt["is_hacker"], [f"{v}_value_usd" for v in VARIANTS]].sum().sum())
    out["honest_total_wgnk_incl_pending_burns"] = float(x["honest_wgnk"].sum())
    out["pending_pre_hack_burns_wgnk"] = float(x["b0_pending_burn"].sum())
    out["supply_snap_contract"] = d["forensics"]["reserves"][str(SNAP_BLOCK)]["wgnk_supply"]
    return out
