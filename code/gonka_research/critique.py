"""Критика собственного расчёта компенсаций: проверки «глазами независимого аудитора».

Каждая проверка — функция, которая из готовых таблиц и сырых данных считает одну цифру «белого пятна» и
сохраняет список затронутых адресов. Итог — model/critique.json (свод) и model/critique/*.csv (адреса).
Ничего не меняет в расчёте: исправления делаются в exploit_model / comp_variants по итогам этих проверок.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import pandas as pd

from . import exploit_model as M
from .lite import Paths, save_json
from .exploit_const import HACKER_ETH, KEY_BLOCK, MONEY, SNAP_BLOCK, WARN_TS, WGNK, ZERO, ex_paths

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
OTC_WINDOW = 48 * 3600          # встречный платёж ищем в пределах ±48 часов от перевода WGNK
OTC_MIN_USD = 5.0
T_BLOCKAID = 1_795_026_480       # 18.11.2026 18:28:00 UTC — первый публичный сигнал (Blockaid в X)
T_MEDIA = 1_795_041_000          # 18.11.2026 22:30:00 UTC — о взломе написал десяток изданий


def _load(paths: Paths) -> dict:
    ex = ex_paths(paths)
    d = M._load(ex)
    d["ex"] = ex
    d["v"] = pd.read_parquet(ex.model / "parquet" / "variants.parquet")
    d["dw"] = pd.read_parquet(ex.model / "parquet" / "tx_deltas_windows.parquet")
    d["pos"] = pd.read_parquet(ex.model / "parquet" / "lp_positions.parquet")
    d["comp3"] = json.loads((ex.model / "comp3.json").read_text())
    d["base"] = json.loads((ex.model / "ex_model.json").read_text())
    d["ret"] = json.loads((ex.raw / "return.json").read_text())
    d["p0"] = d["meta"]["p0_vwap24h"]
    pools = d["pools"]
    d["pool_addrs"] = {p.lower() for p in pools.loc[pools["version"] == "v3", "pool_id"]} | {M.POOL_MANAGER}
    d["ent_of"] = {a: r.entity for r in d["v"].itertuples() for a in r.addresses.split(";")}
    d["bts"] = {int(k): int(v) for k, v in json.loads((ex.raw / "eth" / "block_ts.json").read_text()).items()}
    tw_path = ex.raw / "eth" / "twins.json"
    d["twins"] = json.loads(tw_path.read_text()) if tw_path.exists() else {}
    otc = ex.raw / "eth" / "otc_history.json"
    d["otc"] = json.loads(otc.read_text()) if otc.exists() else None
    extra = ex.raw / "extra.json"
    d["extra"] = json.loads(extra.read_text()) if extra.exists() else None
    return d


def _ts(d: dict, block: int) -> int:
    return d["bts"].get(int(block)) or WARN_TS + (int(block) - int(d["meta"]["t1_block"])) * 12


def _paid(v: pd.DataFrame, opt: str = "v1") -> pd.DataFrame:
    return v[v[f"{opt}_paid"] & ~v["is_hacker"]]


def _tot(d: dict, opt: str = "v1") -> dict:
    p = _paid(d["v"], opt)
    return {"gnk": float(p[f"{opt}_pay_gnk"].sum()), "money": float(p[f"{opt}_money_usd"].sum()), "value": float(p[f"{opt}_value_usd"].sum()), "n": int(len(p))}


# ── 1. Склейка адресов и внебиржевые сделки ─────────────────────────────────

def _money_between(d: dict, a: str, b: str) -> list[dict]:
    """Все переводы денег между a и b (в обе стороны) из истории адресов: токены, ETH, внутренние переводы."""
    hist = (d["otc"] or {}).get("history") or {}
    rows, seen = [], set()
    for owner in (a, b):
        h = hist.get(owner) or {}
        for action in ("tokentx", "txlist", "txlistinternal"):
            for r in h.get(action) or []:
                f, t = (r.get("from") or "").lower(), (r.get("to") or "").lower()
                if {f, t} != {a, b} or str(r.get("isError") or "0") == "1":
                    continue
                if action == "tokentx":
                    sym, dec = MONEY[(r.get("contractAddress") or "").lower()]
                else:
                    sym, dec = "ETH", 18
                amt = int(r.get("value") or 0) / 10 ** dec
                if amt <= 0:
                    continue
                key = (r.get("hash"), action, f, t, sym, r.get("value"))
                if key in seen:
                    continue
                seen.add(key)
                blk = int(r.get("blockNumber") or 0)
                usd = amt * (M._eth_price(d, blk) if sym in ("ETH", "WETH") else 1.0)
                rows.append({"tx": r.get("hash"), "block": blk, "ts": int(r.get("timeStamp") or 0), "from": f, "to": t, "token": sym, "amount": amt, "usd": usd})
    return rows


def clusters(d: dict) -> dict:
    edges = M.plain_edges(d, d["pool_addrs"])
    deg = defaultdict(set)
    for a, b, *_ in edges:
        deg[a].add(b)
        deg[b].add(a)
    b0 = M.balances(d["tr"], SNAP_BLOCK)
    dw = d["dw"]
    money_by_addr = dw.groupby("address")["d_usd"].sum().to_dict()            # > 0 — получил денег, < 0 — заплатил
    pairs = defaultdict(lambda: {"wgnk_ab": 0.0, "wgnk_ba": 0.0, "n": 0, "first_block": None, "txs": []})
    for a, b, h, w, blk in edges:
        x, y = sorted((a, b))
        p = pairs[(x, y)]
        p["wgnk_ab" if a == x else "wgnk_ba"] += w
        p["n"] += 1
        p["first_block"] = blk if p["first_block"] is None else min(p["first_block"], blk)
        p["txs"].append((h, blk, a, b, w))
    rows = []
    for (x, y), p in pairs.items():
        hub = len(deg[x]) > M.HUB_DEGREE or len(deg[y]) > M.HUB_DEGREE
        pay = _money_between(d, x, y) if d["otc"] else []
        near = []
        for m in pay:
            if any(abs(m["ts"] - _ts(d, blk)) <= OTC_WINDOW for _h, blk, *_ in p["txs"]):
                near.append(m)
        # Встречный платёж: деньги идут навстречу WGNK (получатель WGNK платит отправителю).
        counter = 0.0
        for m in near:
            w_to_payer = sum(w for _h, _blk, a, b, w in p["txs"] if b == m["from"] and a == m["to"])
            if w_to_payer > 0:
                counter += m["usd"]
        rows.append({"addr_1": x, "addr_2": y, "entity_1": d["ent_of"].get(x, ""), "entity_2": d["ent_of"].get(y, ""),
                     "merged": (not hub) and d["ent_of"].get(x) == d["ent_of"].get(y), "via_hub": hub, "transfers": p["n"],
                     "wgnk_1_to_2": p["wgnk_ab"], "wgnk_2_to_1": p["wgnk_ba"], "first_block": p["first_block"],
                     "b0_1": float(b0.get(x, 0.0)), "b0_2": float(b0.get(y, 0.0)),
                     "money_1_usd": float(money_by_addr.get(x, 0.0)), "money_2_usd": float(money_by_addr.get(y, 0.0)),
                     "money_between_usd_48h": float(sum(m["usd"] for m in near)), "counter_payment_usd": counter,
                     "money_between_any_time_usd": float(sum(m["usd"] for m in pay)),
                     "payments": json.dumps([{k: m[k] for k in ("tx", "block", "from", "to", "token", "amount")} for m in pay][:20]),
                     "hacker": x in HACKER_ETH or y in HACKER_ETH})
    df = pd.DataFrame(rows).sort_values(["counter_payment_usd", "wgnk_1_to_2"], ascending=False)
    df.to_csv(d["ex"].model / "critique" / "plain_transfer_pairs.csv", index=False)

    v = d["v"]
    v = v.assign(n_addr=v["addresses"].str.count(";") + 1)
    cl = v[(v["n_addr"] > 1) & ~v["is_hacker"]]
    groups = []
    for r in cl.itertuples():
        ad = r.addresses.split(";")
        bb = {a: float(b0.get(a, 0.0)) for a in ad}
        spent = {a: -float(money_by_addr.get(a, 0.0)) for a in ad}            # > 0 — адрес заплатил больше, чем получил
        holder = max(bb, key=bb.get)
        payer = max(spent, key=spent.get)
        groups.append({"owner_key": r.entity, "addresses": r.addresses, "n": r.n_addr, "honest_wgnk": r.honest_wgnk,
                       "b0_by_address": json.dumps(bb), "net_spent_by_address": json.dumps({a: round(x, 2) for a, x in spent.items()}),
                       "top_holder": holder, "top_payer": payer,
                       "key_is_holder": bb[r.entity] >= max(bb.values()) - 1e-9, "key_is_payer": spent[r.entity] >= max(spent.values()) - 1e-9,
                       "members_with_gain": int(sum(1 for a in ad if spent[a] < -1)), "members_with_b0": int(sum(1 for a in ad if bb[a] >= 1)),
                       "v1_pay_gnk": r.v1_pay_gnk, "v1_money_usd": r.v1_money_usd, "v3_money_usd": r.v3_money_usd})
    g = pd.DataFrame(groups)
    g.to_csv(d["ex"].model / "critique" / "address_groups.csv", index=False)
    # Чужая прибыль вычтена из чужих GNK: в группе один адрес держал WGNK, а другой получил чистую выручку.
    cross = g[(g["members_with_gain"] > 0) & (g["members_with_b0"] > 0)]
    wrong_gnk = g[~g["key_is_holder"] & (g["v1_pay_gnk"] > 0.5)]
    wrong_money = g[~g["key_is_payer"] & (g["v1_money_usd"] > 0.01)]
    otc = df[(df["counter_payment_usd"] >= OTC_MIN_USD) & ~df["hacker"]]
    tot = _tot(d)
    return {"id": "address_groups", "pairs": int(len(df)), "pairs_merged": int(df["merged"].sum()), "pairs_via_hub": int(df["via_hub"].sum()),
            "groups": int(len(g)), "addresses": int(g["n"].sum()), "gnk": float(g["v1_pay_gnk"].sum()), "money_usd": float(g["v1_money_usd"].sum()),
            "share_gnk": float(g["v1_pay_gnk"].sum() / tot["gnk"]), "share_money": float(g["v1_money_usd"].sum() / tot["money"]),
            "payee_not_holder": {"groups": int(len(wrong_gnk)), "gnk": float(wrong_gnk["v1_pay_gnk"].sum())},
            "payee_not_payer": {"groups": int(len(wrong_money)), "usd": float(wrong_money["v1_money_usd"].sum())},
            "gain_netted_against_other_address": {"groups": int(len(cross)), "honest_wgnk": float(cross["honest_wgnk"].sum())},
            "otc_checked": d["otc"] is not None, "history_addresses": len((d["otc"] or {}).get("history") or {}),
            "otc_pairs": [{k: (float(x) if isinstance(x, float) else x) for k, x in r.items() if k != "payments"} for r in otc.to_dict("records")],
            "otc_pairs_n": int(len(otc)), "otc_counter_usd": float(otc["counter_payment_usd"].sum()),
            "pairs_with_any_money_48h": int((df["money_between_usd_48h"] >= OTC_MIN_USD).sum()),
            "hubs": {a: len(x) for a, x in deg.items() if len(x) > M.HUB_DEGREE}}


# ── 2. Сверка «никто не потерян»: выпуск WGNK на снимке ─────────────────────

def supply(d: dict) -> dict:
    b0 = M.balances(d["tr"], SNAP_BLOCK)
    b0 = b0[b0.index != ZERO]
    v = d["v"]
    wallets = float(v["b0_wallet"].sum())
    pools = {a: float(b0.get(a, 0.0)) for a in d["pool_addrs"]}
    infra = {a: float(b0.get(a, 0.0)) for a in M.INFRA if a not in d["pool_addrs"] and a != ZERO and abs(float(b0.get(a, 0.0))) > 1e-9}
    lp = float(v["lp_w_before"].sum())
    total = float(b0.sum())
    unassigned = total - wallets - sum(pools.values()) - sum(infra.values())
    return {"id": "supply", "supply_at_snapshot": total, "owner_wallets": wallets, "pools": pools, "lp_positions_wgnk": lp,
            "pool_minus_positions": sum(pools.values()) - lp, "infra_balances": infra, "unassigned": unassigned,
            "negative_balances": int((b0 < -1e-9).sum())}


# ── 3. Заявки GNK → WGNK «в пути»: GNK заперты в мосте, WGNK не выпущены ────

def bridge_in_flight(d: dict) -> dict:
    from .comp_variants import bridge_in_flight as flight
    df = flight(d["ex"], d)
    if not len(df):
        return {"id": "bridge_in_flight", "available": False}
    df = df.assign(already_in_register=df["eth_destination"].isin(d["ent_of"]))
    df.to_csv(d["ex"].model / "critique" / "bridge_requests_not_minted.csv", index=False)
    big = df.groupby("gonka_sender")["gnk"].sum()
    big = big[big >= 0.5]
    return {"id": "bridge_in_flight", "available": True, "requests": int(len(df)), "gnk": float(df["gnk"].sum()), "senders": int(df["gonka_sender"].nunique()),
            "senders_ge_half_gnk": int(len(big)), "gnk_ge_half": float(big.sum()),
            "before_attack": {"n": int((~df["after_attack"]).sum()), "gnk": float(df.loc[~df["after_attack"], "gnk"].sum())},
            "after_attack": {"n": int(df["after_attack"].sum()), "gnk": float(df.loc[df["after_attack"], "gnk"].sum())},
            "escrow_now_gnk": float(((d["gonka"].get("escrow") or {}).get("now") or {}).get("gnk") or 0.0),
            "usd_at_p0": float(df["gnk"].sum() * d["p0"])}


# ── 4. Покупки и продажи за неотслеживаемые токены ──────────────────────────

def untracked_tokens(d: dict) -> dict:
    dw, rcs = d["dw"], d["rcs"]
    sw = d["swaps"].copy()
    sw["usd"] = sw["usd_value"].astype(float)
    swap_usd = sw.groupby("tx_hash")["usd"].sum().to_dict()
    swap_w = sw.groupby("tx_hash")["amount_wgnk"].apply(lambda s: float(s.astype(float).abs().sum())).to_dict()
    cand = dw[(dw["d_wgnk"].abs() >= M.DUST_WGNK) & (dw["d_usd"].abs() < 0.01) & ~dw["is_lp_tx"] & (dw["via_third_party"].fillna("") == "")]
    rows = []
    for r in cand.itertuples():
        rc = rcs.get(r.tx_hash) or {}
        other = set()
        pad = "0x" + r.address[2:].rjust(64, "0")
        for lg in rc.get("logs") or []:
            tp = lg.get("topics") or []
            tok = (lg.get("address") or "").lower()
            if len(tp) >= 3 and tp[0] == TRANSFER_TOPIC and tok != WGNK and tok not in MONEY:
                if (r.d_wgnk > 0 and tp[1] == pad) or (r.d_wgnk < 0 and tp[2] == pad):
                    other.add(tok)
        if not other or r.tx_hash not in swap_usd:
            continue
        w_tx = swap_w.get(r.tx_hash) or 0.0
        usd = swap_usd[r.tx_hash] * min(1.0, abs(r.d_wgnk) / w_tx) if w_tx else 0.0
        rows.append({"tx": r.tx_hash, "block": r.block, "window": r.win, "address": r.address, "owner": r.entity, "d_wgnk": r.d_wgnk,
                     "side": "buy" if r.d_wgnk > 0 else "sell", "other_tokens": ";".join(sorted(other)), "pool_leg_usd": usd})
    df = pd.DataFrame(rows)
    df.to_csv(d["ex"].model / "critique" / "untracked_token_trades.csv", index=False)
    if not len(df):
        return {"id": "untracked_tokens", "rows": 0}
    out = {"id": "untracked_tokens", "rows": int(len(df))}
    for side in ("buy", "sell"):
        for w in "AB":
            x = df[(df["side"] == side) & (df["window"] == w)]
            out[f"{side}_{w}"] = {"n": int(len(x)), "owners": int(x["owner"].nunique()), "usd": float(x["pool_leg_usd"].sum()), "wgnk": float(x["d_wgnk"].abs().sum())}
    v = d["v"].set_index("entity")
    per = df.assign(sign=df["side"].map({"buy": 1, "sell": -1})).assign(net=lambda t: t["pool_leg_usd"] * t["sign"]).groupby("owner")["net"].sum()
    out["owners"] = int(len(per))
    out["owners_unpaid"] = int(sum(1 for e, x in per.items() if x > 1 and e in v.index and not v.loc[e, "v1_paid"]))
    return out


# ── 5. Прибыль, которую никто не возвращает ─────────────────────────────────

def profit_kept(d: dict) -> dict:
    v, p0 = d["v"], d["p0"]
    v = v[~v["is_hacker"]].copy()
    v["net"] = v["net_a_usd"] + v["net_b_usd"]
    # Без WGNK до взлома: вся чистая выручка остаётся у владельца.
    t = v[(v["honest_wgnk"] < 1) & (v["net"] < -1)].assign(profit=lambda x: -x["net"])
    # С WGNK до взлома: выручка сверх стоимости своего остатка по курсу до взлома (вычет упёрся в ноль).
    h = v[(v["honest_wgnk"] >= 1) & (v["honest_wgnk"] * p0 + v["net"] < -1)].assign(profit=lambda x: -(x["honest_wgnk"] * p0 + x["net"]))
    allp = pd.concat([t, h]).sort_values("profit", ascending=False)
    allp[["entity", "addresses", "category", "honest_wgnk", "net_a_usd", "net_b_usd", "profit", "a_n_tx", "b_n_tx"]].to_csv(
        d["ex"].model / "critique" / "profit_kept.csv", index=False)
    c3 = d["comp3"]["variants"]["v1"]
    return {"id": "profit_kept", "owners": int(len(allp)), "usd": float(allp["profit"].sum()),
            "no_prehack_wgnk": {"owners": int(len(t)), "usd": float(t["profit"].sum())},
            "holders_above_holdings": {"owners": int(len(h)), "usd": float(h["profit"].sum())},
            "top1_usd": float(allp["profit"].iloc[0]) if len(allp) else 0.0, "top5_usd": float(allp["profit"].head(5).sum()),
            "top10_share": float(allp["profit"].head(10).sum() / allp["profit"].sum()) if len(allp) else 0.0,
            "window_a_usd": float(-allp["net_a_usd"].clip(upper=0).sum()),
            "share_of_top_up": float(allp["profit"].sum() / c3["cost_usd"]), "top_up_usd": c3["cost_usd"]}


# ── 6. Концентрация выплат ──────────────────────────────────────────────────

def concentration(d: dict) -> dict:
    p = _paid(d["v"]).sort_values("v1_value_usd", ascending=False)
    tot = _tot(d)
    top = p.head(10)
    top[["entity", "addresses", "category", "honest_wgnk", "lp_w_before", "lp_u_before", "v1_pay_gnk", "v1_money_usd", "v1_value_usd"]].to_csv(
        d["ex"].model / "critique" / "top_recipients.csv", index=False)
    lp = p[(p["lp_w_before"] > 0) | (p["lp_u_before"] > 0)]
    money = p.sort_values("v1_money_usd", ascending=False)
    return {"id": "concentration", "recipients": tot["n"],
            "top1": {"gnk": float(top["v1_pay_gnk"].iloc[0]), "money_usd": float(top["v1_money_usd"].iloc[0]), "value_usd": float(top["v1_value_usd"].iloc[0]),
                     "share_gnk": float(top["v1_pay_gnk"].iloc[0] / tot["gnk"]), "share_money": float(top["v1_money_usd"].iloc[0] / tot["money"]),
                     "share_value": float(top["v1_value_usd"].iloc[0] / tot["value"]), "category": top["category"].iloc[0]},
            "top10_share_value": float(top["v1_value_usd"].sum() / tot["value"]),
            "top10_money_share": float(money["v1_money_usd"].head(10).sum() / tot["money"]),
            "median_value_usd": float(p["v1_value_usd"].median()), "below_100_usd": int((p["v1_value_usd"] < 100).sum()),
            "lp": {"owners": int(len(lp)), "gnk": float(lp["v1_pay_gnk"].sum()), "money_usd": float(lp["v1_money_usd"].sum()),
                   "share_gnk": float(lp["v1_pay_gnk"].sum() / tot["gnk"]), "share_money": float(lp["v1_money_usd"].sum() / tot["money"])},
            "totals": tot}


# ── 7. Граница: сколько возврата приходится на сделки после публичного сигнала ─

def cutoff(d: dict) -> dict:
    dw, v, p0 = d["dw"], d["v"], d["p0"]
    lp_ent = set(v.loc[(v["lp_w_before"] > 0) | (v["lp_u_before"] > 0) | (v["lp_u_end"] > 0), "entity"])
    hk = set(v.loc[v["is_hacker"], "entity"])
    base = v[~v["entity"].isin(lp_ent | hk)].set_index("entity")
    x = dw[~dw["entity"].isin(lp_ent | hk)]
    freeze = float(d["meta"].get("freeze_ts") or 1_795_408_200)

    def run(cut: float) -> dict:
        a = x[x["ts"] <= cut].groupby("entity")["d_usd"].sum().mul(-1)
        b = x[x["ts"] > cut].groupby("entity")["d_usd"].sum().mul(-1)
        m = a.reindex(base.index).fillna(0.0) + b.reindex(base.index).fillna(0.0).clip(upper=0.0)
        money = m.clip(lower=0.0)
        gnk = (base["honest_wgnk"] + m.clip(upper=0.0) / p0 - base["g_credited"]).clip(lower=0.0)
        return {"money_usd": float(money.sum()), "gnk": float(gnk.sum()), "owners_money": int((money > 0.01).sum())}

    buys = x[(x["d_wgnk"] > 0) & (x["d_usd"] < 0) & (x["win"] == "A") & ~x["is_lp_tx"]]
    out = {"id": "cutoff", "note": "владельцы без позиций ликвидности; вариант 1: убытки после границы не возмещаются, прибыль вычитается",
           "at_warning": run(WARN_TS), "at_blockaid_18_28": run(T_BLOCKAID), "at_media_22_30": run(T_MEDIA), "at_hack_start": run(1_795_024_859),
           "buys_window_a": {"n": int(len(buys)), "usd": float(-buys["d_usd"].sum()), "owners": int(buys["entity"].nunique())}}
    for name, ts in (("until_blockaid", T_BLOCKAID), ("until_media", T_MEDIA)):
        y = buys[buys["ts"] <= ts]
        out[f"buys_{name}"] = {"n": int(len(y)), "usd": float(-y["d_usd"].sum()), "owners": int(y["entity"].nunique())}
    for k in ("at_blockaid_18_28", "at_media_22_30", "at_hack_start"):
        out[k]["delta_money_usd"] = out[k]["money_usd"] - out["at_warning"]["money_usd"]
        out[k]["delta_gnk"] = out[k]["gnk"] - out["at_warning"]["gnk"]
    # Сделки сразу после границы: отправлены до предупреждения, исполнены после.
    near = x[(x["ts"] > WARN_TS) & (x["ts"] <= WARN_TS + 300) & (x["d_wgnk"] > 0) & (x["d_usd"] < 0)]
    out["buys_first_5_min_after_warning"] = {"n": int(len(near)), "usd": float(-near["d_usd"].sum()), "owners": int(near["entity"].nunique())}
    out["freeze_ts"] = freeze
    return out


# ── 8. После заморозки: возврат получен, а аннулированные WGNK ещё можно продать ─

def after_freeze(d: dict) -> dict:
    v = d["v"]
    paid = _paid(v)
    money = paid[paid["v1_money_usd"] > 0.01]
    held = money[money["wgnk_end_wallet"] > 1]
    out = {"id": "after_freeze", "refunded_owners_still_holding": int(len(held)), "wgnk_held_by_refunded": float(held["wgnk_end_wallet"].sum()),
           "refund_usd_of_those": float(held["v1_money_usd"].sum()),
           "post_hack_wgnk_in_wallets": float((v.loc[~v["is_hacker"], "wgnk_end_wallet"] - v.loc[~v["is_hacker"], "b0_wallet"]).clip(lower=0).sum())}
    p = d["ex"].raw / "db" / "swaps_after_freeze.parquet"
    if p.exists():
        sw = pd.read_parquet(p)
        out["swaps"] = int(len(sw))
        if len(sw):
            sw["usd"] = sw["usd_value"].astype(float)
            sw["w"] = sw["amount_wgnk"].astype(float)
            out["usd"] = float(sw["usd"].sum())
            out["directions"] = {str(k): {"n": int(g["usd"].count()), "usd": float(g["usd"].sum()), "wgnk": float(g["w"].abs().sum())} for k, g in sw.groupby("direction")}
            out["last_block"] = int(sw["block_number"].max())
            out["last_time"] = str(sw["block_time"].max())
            ent = d["ent_of"]
            who = sw.assign(e=sw["origin_eoa"].str.lower().map(ent))
            rec = set(paid["entity"])
            sells = who[who["direction"].astype(str).str.lower().str.contains("sell")]
            by = sells[sells["e"].isin(rec)]
            out["sells_by_recipients"] = {"n": int(len(by)), "usd": float(by["usd"].sum()), "owners": int(by["e"].nunique()), "wgnk": float(by["w"].abs().sum())}
            by.groupby("e").agg(n=("usd", "count"), usd=("usd", "sum"), wgnk=("w", lambda s: float(s.abs().sum()))).reset_index().rename(columns={"e": "owner"}).to_csv(
                d["ex"].model / "critique" / "sales_after_freeze_by_recipients.csv", index=False)
            buys = who[who["direction"].astype(str).str.lower().str.contains("buy")]
            out["buyers_after_freeze"] = {"n": int(len(buys)), "usd": float(buys["usd"].sum()), "addresses": int(buys["origin_eoa"].nunique())}
    if d["extra"]:
        out["synced_to_block"] = d["extra"].get("synced_to_block")
        out["collected_at"] = d["extra"].get("collected_at")
    return out


# ── 9. Курс до взлома: насколько итог зависит от выбора p₀ ───────────────────

def p0_sensitivity(d: dict) -> dict:
    v, p0 = d["v"], d["p0"]
    v = v[~v["is_hacker"]]
    alts = ((d["extra"] or {}).get("p0_alternatives") or {})
    out = {"id": "p0", "p0": p0, "alternatives": {}}
    sellers = v[(v["v1_m_usd"] < -0.01) & (v["honest_wgnk"] > 0)]
    out["owners_affected"] = int(len(sellers))
    out["deducted_gnk_at_p0"] = float((-sellers["v1_m_usd"] / p0).clip(upper=sellers["honest_wgnk"]).sum())
    for name, a in alts.items():
        px = a.get("price")
        if not px:
            continue
        ded = float((-sellers["v1_m_usd"] / px).clip(upper=sellers["honest_wgnk"]).sum())
        out["alternatives"][name] = {"price": px, "swaps": a.get("swaps"), "delta_gnk": out["deducted_gnk_at_p0"] - ded,
                                     "gnk_value_of_payout_usd": float(_tot(d)["gnk"] * px)}
    return out


# ── 10. Кто платит и кто не может получить: получатели-контракты и адреса без исходящих транзакций ─

def recipients_quality(d: dict) -> dict:
    p = _paid(d["v"])
    tw = d["twins"]
    kinds = Counter()
    gnk = Counter()
    for r in p.itertuples():
        t = tw.get(r.entity) or {}
        k = "contract" if t.get("kind") == "contract" else ("derived" if t.get("gonka") or t.get("gonka_address") else "no_outgoing_tx")
        kinds[k] += 1
        gnk[k] += r.v1_pay_gnk
    return {"id": "recipients_quality", "by_kind": {k: {"n": kinds[k], "gnk": float(gnk[k])} for k in kinds}}


# ── 11. Пассивные участники после предупреждения ────────────────────────────

def passive_after_warning(d: dict) -> dict:
    v = d["v"]
    lp = v[((v["lp_u_t1"] > 0.5) | (v["lp_u_end"] > 0.5)) & ~v["is_hacker"]]
    loss = (lp["lp_u_t1"] - lp["lp_u_end"]).clip(lower=0)
    pos = d["pos"]
    t1 = pos[pos["state"] == "t1"]
    return {"id": "passive_after_warning", "lp_owners_with_money_at_warning": int(len(lp)), "money_in_positions_at_warning_usd": float(lp["lp_u_t1"].sum()),
            "money_in_positions_at_freeze_usd": float(lp["lp_u_end"].sum()), "lp_loss_after_warning_usd": float(loss.sum()),
            "positions_open_at_warning": int((t1["liquidity"].astype(float) > 0).sum()) if "liquidity" in t1 else None,
            "lp_owners_differ_between_options": int((lp["differs"]).sum())}


# ── 12. Позиции LP, сменившие владельца после взлома ────────────────────────

def nft_transfers(d: dict) -> dict:
    lx = d.get("lp_extra") or json.loads((d["ex"].raw / "eth" / "lp_extra.json").read_text())
    moved = lambda o: len({x.lower() for x in o.values() if x}) > 1          # владелец сменился (пустое значение — позиции ещё не было)
    ch = [{"pos": k, **o} for k, o in (lx.get("owners") or {}).items() if moved(o)]
    v4p = d["ex"].raw / "eth" / "v4_extra.json"
    ch4 = []
    if v4p.exists():
        v4 = json.loads(v4p.read_text())
        for k, o in (v4.get("owners") or {}).items():
            if isinstance(o, dict) and moved(o):
                ch4.append({"pos": k, **o})
    return {"id": "nft_transfers", "v3_changed": ch, "v4_changed": ch4, "v3_positions": len(lx.get("owners") or {})}


# ── 13. Заявки на вывод поддельных WGNK в GNK, которые висят в мосте ────────

def pending_burns(d: dict) -> dict:
    v = d["v"][~d["v"]["is_hacker"]]
    x = v[v["burn_pending_post"] > 0.5].sort_values("burn_pending_post", ascending=False)
    x[["entity", "addresses", "category", "honest_wgnk", "burn_pending_post", "net_a_usd", "net_b_usd", "v1_pay_gnk", "v1_money_usd"]].to_csv(
        d["ex"].model / "critique" / "pending_burns_after_attack.csv", index=False)
    return {"id": "pending_burns", "owners": int(len(x)), "wgnk": float(x["burn_pending_post"].sum()), "usd_at_p0": float(x["burn_pending_post"].sum() * d["p0"]),
            "top1_wgnk": float(x["burn_pending_post"].iloc[0]) if len(x) else 0.0, "owners_also_refunded": int((x["v1_money_usd"] > 0.01).sum()),
            "refund_usd_of_those": float(x.loc[x["v1_money_usd"] > 0.01, "v1_money_usd"].sum()),
            "pre_hack_pending_wgnk": float(v["b0_pending_burn"].sum()), "pre_hack_pending_owners": int((v["b0_pending_burn"] > 0).sum()),
            "pre_hack_pending_old_wgnk": float(sum(x["amount_gnk"] for x in (d["base"].get("pending_pre") or []) if int(x["block"]) < KEY_BLOCK - 7200)),
            "escrow_now_gnk": float(((d["gonka"].get("escrow") or {}).get("now") or {}).get("gnk") or 0.0)}


# ── 14. Что изменилось в расчёте после самопроверки ─────────────────────────

def fixes(d: dict) -> dict:
    old_p = d["ex"].model / "first_release" / "comp3.json"
    if not old_p.exists():
        return {"id": "fixes", "available": False}
    old, new = json.loads(old_p.read_text())["variants"], d["comp3"]["variants"]
    out = {"id": "fixes", "available": True, "options": {}}
    for v in ("v1", "v2", "v3"):
        o, n = old[v], new[v]
        out["options"][v] = {"cost_before": o["cost_usd"], "cost_after": n["cost_usd"], "share_before": o["cost_share_pool"], "share_after": n["cost_share_pool"],
                             "gnk_gap_before": o["gnk_gap"], "gnk_gap_after": n["gnk_gap"], "recipients_before": o["recipients"], "recipients_after": n["recipients"],
                             **{f"{k}_delta": n["totals"][k] - o["totals"][k] for k in ("gnk", "usdt", "usdc", "dai", "eth")}}
    cp = d["ex"].root / "registers" / "changes_vs_first_release.csv"
    if cp.exists():
        ch = pd.read_csv(cp)
        c1 = ch[ch["option"] == "v1"]
        out["owners_changed_v1"] = int(c1["owner"].nunique())
        out["money_delta_v1_usd"] = float(c1["usdt_delta"].sum() + c1["usdc_delta"].sum() + c1["dai_delta"].sum() + c1["eth_delta"].sum() * d["comp3"]["eth_usd_now"])
        c3 = ch[ch["option"] == "v3"]
        out["money_delta_v3_usd"] = float(c3["usdt_delta"].sum() + c3["usdc_delta"].sum() + c3["dai_delta"].sum() + c3["eth_delta"].sum() * d["comp3"]["eth_usd_now"])
        out["owners_changed_any"] = int(ch["owner"].nunique())
    # Выплаты, которые после раздела по адресам уходят не на ключевой («первый по алфавиту») адрес группы.
    pp = d["ex"].model / "parquet" / "payees.parquet"
    if pp.exists():
        pt = pd.read_parquet(pp)
        mv = pt[(pt["group_size"] > 1) & ~pt["is_hacker"] & (pt["entity"] != pt["owner"])]
        g_gnk = mv.groupby("owner")["v1_pay_gnk"].sum()
        g_usd = mv.groupby("owner")["v1_money_usd"].sum()
        out["rerouted"] = {"groups_gnk": int((g_gnk > 0.5).sum()), "gnk": float(g_gnk.sum()), "groups_money": int((g_usd > 0.01).sum()), "usd": float(g_usd.sum()),
                           "groups_any": int(((g_gnk > 0.5) | (g_usd > 0.01)).sum())}
    out["escrow_gnk"] = d["comp3"].get("escrow_gnk_now")
    out["in_flight"] = d["comp3"].get("bridge_in_flight")
    out["groups"] = d["comp3"]["counts"].get("groups")
    return out


CHECKS = (clusters, supply, bridge_in_flight, untracked_tokens, profit_kept, concentration, cutoff, after_freeze, p0_sensitivity,
          recipients_quality, passive_after_warning, nft_transfers, pending_burns, fixes)


def build(paths: Paths) -> dict:
    d = _load(paths)
    (d["ex"].model / "critique").mkdir(parents=True, exist_ok=True)
    out = {"generated_utc": pd.Timestamp.now(tz="UTC").isoformat(), "option": "v1", "p0": d["p0"], "totals_v1": _tot(d), "checks": {}}
    for fn in CHECKS:
        try:
            r = fn(d)
        except Exception as e:  # noqa: BLE001 — одна упавшая проверка не должна скрывать остальные
            r = {"id": fn.__name__, "error": f"{type(e).__name__}: {e}"}
        out["checks"][r.get("id", fn.__name__)] = r
    ext = d["ex"].root / "independent_check" / "critique_external.json"     # итоги двух независимых проверок (вносятся после их отчётов)
    if ext.exists():
        out["external"] = json.loads(ext.read_text())
    save_json(out, d["ex"].model / "critique.json")
    write_md(d, out)
    return out


# ── CRITIQUE.md для пакета аудита (английский) ──────────────────────────────

def write_md(d: dict, out: dict) -> str:
    c, s, ext = out["checks"], d["comp3"], out.get("external") or {}
    v1 = s["variants"]["v1"]
    n = lambda x, k=0: f"{x:,.{k}f}"
    pk, cu, k, pb, g, fx, fl = c["profit_kept"], c["cutoff"], c["concentration"], c["pending_burns"], c["address_groups"], c["fixes"], c["bridge_in_flight"]
    o = fx["options"]
    rr = fx.get("rerouted") or {}
    se = v1["sensitivity_eth"]
    tpa = s["checks"]["third_party_attributed"]
    lp = (ext.get("lp_md") or "The independent recomputation of liquidity positions is described in `independent_lp_recheck/REPORT.md`.")
    md = f"""# Self-audit of the compensation calculation — weak points and open questions

Status: 23 Nov 2026, version 2 of the calculation. This file is written against ourselves: it lists where the method is
weak, whose interests may not be covered, what was wrong in version 1 and has been corrected, and what cannot be settled
from on-chain data. Figures are for option 1 unless stated; every figure is reproducible from `critique.json` and the CSV
files in `data/`. Two separate reviewers worked in parallel with our own checks: an adversarial review of the published
package (`red_team/`) and an independent recomputation of liquidity positions (`independent_lp_recheck/`). Their reports are
included unedited; where their numbers differ from ours by definition (e.g. 142 vs {pk['owners']} profit-keeping owners), both are kept.

## 1. Summary

| # | Weak point | Size | Kind | What we did |
|---|---|---|---|---|
| 1 | Traders keep profit made during the hack | {n(pk['usd'])} USD, {pk['owners']} owners | policy | disclosed; the slogan "nobody profits" now carries a note |
| 2 | The dividing line is generous to those who bought after the hack was public | {n(-cu['at_blockaid_18_28']['delta_money_usd'])} of {n(cu['at_warning']['money_usd'])} USD refunded to traders | policy | disclosed with the alternative figure |
| 3 | Payouts are concentrated | one address: {k['top1']['share_gnk']*100:.1f}% of GNK, {k['top1']['share_money']*100:.1f}% of money | policy / verification | disclosed; liquidity positions recomputed independently |
| 4 | Bridge claims for unbacked WGNK are pending, old tokens still transferable | {n(pb['wgnk'])} WGNK, {pb['owners']} owners | risk | disclosed; cancellation proposed as a precondition of payout |
| 5 | An address is not a person; off-chain deals are invisible | {g['groups']} groups, {g['addresses']} addresses | cannot be settled on chain | checked on chain, disclosed, payout split by address |
| 6 | ETH price moves the cost more than the choice of option | ±{n((abs(se['-10%']['cost_usd']-v1['cost_usd'])+abs(se['+10%']['cost_usd']-v1['cost_usd']))/2)} USD per 10% | risk | disclosed; immediate conversion proposed |
| 7 | Errors found in version 1 | top-up {n(o['v1']['cost_before'])} → {n(o['v1']['cost_after'])} USD | calculation errors | **fixed** (section 2) |

## 2. Corrected in version 2 (proven calculation errors)

1. **Bridge escrow left out of the sources.** The attacker took 13,000,000 of 13,098,243 GNK from the escrow; {n(fx['escrow_gnk'], 2)} GNK
   is still there and backs the same holders. Counting it lowers the GNK shortfall from {n(o['v1']['gnk_gap_before'])} to {n(o['v1']['gnk_gap_after'])} GNK.
2. **Bridge requests in flight were missing.** {fl['requests']} successful GNK → WGNK requests ({n(fl['gnk'], 2)} GNK, {fl['senders']} senders;
   {fl['after_attack']['n']} of them, {n(fl['after_attack']['gnk'], 1)} GNK, after the attack) have no matching WGNK mint. The GNK is returned to the
   sender on Gonka in every option (`04_registers/bridge_requests_in_flight.csv`). Each request's status must still be confirmed
   against the bridge module: the escrow arithmetic explains 1,216 of the {n(fl['before_attack']['gnk'])} GNK requested before the attack.
   In version 1 the request table had no success flag: 9 failed requests (138,034 GNK) looked like in-flight ones.
3. **Payee of a multi-address owner.** The whole payout of an address group went to the alphabetically first address. Now GNK
   goes to the address that held the WGNK and money to the address that paid: {n(rr.get('gnk', 0))} GNK and {n(rr.get('usd', 0))} USD changed
   address in {rr.get('groups_any', 0)} of {g['groups']} groups. Owner totals are unchanged.
4. **Trades paid in untracked tokens** were treated as free; they are now valued by the WGNK pool leg of the same transaction.
5. **Liquidity operations without a WGNK movement** (Uniswap v4, money-only adds/removals) were not in the transaction set;
   one owner was credited 400 USD in option 3 for USDC he had withdrawn himself. The transactions were fetched and counted.
6. **Option 1 ≤ 2 ≤ 3** did not hold per currency for one owner (0.24 USD); it is now enforced per currency.

Items 4–6 change payouts of {fx.get('owners_changed_any', 0)} owners; net effect on money to people: {fx.get('money_delta_v1_usd', 0):+,.0f} USD in option 1,
{fx.get('money_delta_v3_usd', 0):+,.0f} USD in option 3. Protocol top-up, before → after: option 1 {n(o['v1']['cost_before'])} → {n(o['v1']['cost_after'])};
option 2 {n(o['v2']['cost_before'])} → {n(o['v2']['cost_after'])}; option 3 {n(o['v3']['cost_before'])} → {n(o['v3']['cost_after'])} USD.
Per-owner table: `04_registers/changes_vs_first_release.csv`; version 1 outputs: `first_release/`.

## 3. Open weak points

### 3.1 Someone did profit ({n(pk['usd'])} USD)
{pk['no_prehack_wgnk']['owners']} owners with no pre-hack WGNK ended with more money than they spent ({n(pk['no_prehack_wgnk']['usd'])} USD); {pk['holders_above_holdings']['owners']} holders took out
{n(pk['holders_above_holdings']['usd'])} USD more than their holdings were worth at the pre-hack price (their payout is zero, the excess stays). The ten
largest hold {pk['top10_share']*100:.0f}%; the largest, a trading bot, {n(pk['top1_usd'])} USD. This equals {pk['usd']/v1['cost_usd']*100:.0f}% of the protocol top-up: the cheap
WGNK they sold were bought by people who are now refunded. The protocol cannot claw this back. The attacker kept
{606.7 - v1['eth_returned']:.1f} ETH and {n(13_000_000 - v1['gnk_returned'])} GNK. List: `data/profit_kept.csv`.

### 3.2 The line at the official warning is generous
Among owners without liquidity positions, option 1 refunds {n(cu['at_warning']['money_usd'])} USD to {cu['at_warning']['owners_money']} owners. With the line at the first public
alert (Blockaid, 18:28 UTC on 18 Nov) it would be {n(cu['at_blockaid_18_28']['money_usd'])} USD to {cu['at_blockaid_18_28']['owners_money']} owners; at 22:30 (a dozen outlets) the total changes by
{n(abs(cu['at_media_22_30']['delta_money_usd']))} USD only. Purchases in window A: {n(cu['buys_window_a']['usd'])} USD, of which {n(cu['buys_until_blockaid']['usd'])} USD before the alert. Liquidity providers are
not affected by the choice (their USDT was bought out in the first minutes). Counter-argument: nobody is obliged to follow
security firms on X, and the project itself was silent until 00:24:07. The project's Discord was not checked; an earlier
explicit warning there would move the line.

### 3.3 Concentration
The largest recipient, a liquidity provider, receives {n(k['top1']['gnk'])} GNK and {n(k['top1']['money_usd'])} USD — {k['top1']['share_gnk']*100:.1f}% of all GNK, {k['top1']['share_money']*100:.1f}% of all
money, {k['top1']['share_value']*100:.1f}% of all value. {k['lp']['owners']} liquidity providers together: {k['lp']['share_gnk']*100:.1f}% of GNK and {k['lp']['share_money']*100:.1f}% of money. The ten largest recipients:
{k['top10_share_value']*100:.0f}% of value; the median payout is {n(k['median_value_usd'])} USD and {k['below_100_usd']} of {k['recipients']} paid owners get less than 100 USD. The calculation is
formally consistent — these addresses held the liquidity the attacker bought out — but an error here costs more than in all
small payouts together, and whether any large recipient is related to the project team is not known to us. We propose that
the largest recipients confirm their address by signature and disclose any such link. {lp}
List: `data/top_recipients.csv`; the red-team report gives more detail on the largest recipients.

### 3.4 Pending bridge claims and "voided" tokens
After the attack {pb['owners']} owners (the attacker excluded) burned {n(pb['wgnk'])} cheaply bought WGNK on the bridge to receive native GNK; the
bridge records are `BRIDGE_PENDING` — not executed and not cancelled ({n(pb['usd_at_p0'])} USD at the pre-hack price; the largest
claim is {n(pb['top1_wgnk'])} WGNK). {pb['owners_also_refunded']} of these owners also receive a money refund ({n(pb['refund_usd_of_those'])} USD). The model treats these claims and all
post-hack WGNK as void, but that is a statement on paper until governance cancels the claims and the old contract is
stopped: {n(c['after_freeze']['post_hack_wgnk_in_wallets'])} unbacked WGNK are still in wallets and transferable (liquidity left in the old pools at the
freeze: {n(c['passive_after_warning']['money_in_positions_at_freeze_usd'])} USD, so selling them is hardly possible right now). Separately, {n(pb['pre_hack_pending_wgnk'])} genuine WGNK burned before
the hack await delivery ({n(pb['pre_hack_pending_old_wgnk'])} of them are records 41–135 days old); they are in the register and must be paid once —
by the bridge or by the register, not both. List: `data/pending_burns_after_attack.csv`.

### 3.5 Addresses, groups and off-exchange deals
Addresses linked by a plain WGNK transfer after the attack (no money in the transaction) are treated as one owner:
{g['groups']} groups, {g['addresses']} addresses, {n(g['gnk'])} GNK and {n(g['money_usd'])} USD. The concern: such a transfer could be an over-the-counter sale paid for
separately. We pulled the USDT/USDC/DAI/ETH history of all {g.get('history_addresses', 0)} addresses involved ({g['pairs']} pairs) from two days before the
attack to the freeze: money moved between the two addresses in {g['pairs_with_any_money_48h']} pairs, and against the direction of the WGNK in
{g['otc_pairs_n']} ({n(g['otc_counter_usd'])} USD in total). By timing and amounts these are top-ups of the owner's own trading wallet and gas (e.g. 3 ETH
sent 31 blocks before the purchase, WGNK sent back afterwards), not sales; no off-exchange sale of pre-hack WGNK was found.
What cannot be seen: payment off chain; one person with two unlinked wallets (GNK for holdings on one, sale proceeds on the
other); a group that is in fact two people — in 2 groups one address's gain is netted against another address's holdings.
The rule has no minimum amount and ignores direction (one merge rests on 0.12 WGNK). Mitigation: payout split by address
(section 2), an objection window, signatures for disputed addresses. Lists: `data/plain_transfer_pairs.csv`,
`data/address_groups.csv`.

### 3.6 ETH price
The {n(v1['reserve']['usdt'] + v1['reserve']['usdc'])} USD bridge reserve is bought with the returned ETH, so the top-up is {n(v1['cost_usd'])} USD at ETH {n(s['eth_usd_now'], 2)},
{n(se['-10%']['cost_usd'])} at −10% and {n(se['+10%']['cost_usd'])} at +10%, while options 1 and 3 differ by {n(s['variants']['v3']['cost_usd'] - v1['cost_usd'])} USD. ETH was {n(d['ret'].get('eth_usd_at_return') or 0, 2)} USD when the
funds were returned. Converting the stablecoin part right after the decision removes this exposure.

### 3.7 Smaller assumptions
- **Third-party settlement.** For {tpa['owners']} owners the purchase (or sale) was paid by an intermediary in the same transaction (relayers,
  CoW Swap); the refund currency and the payee are inferred from that transaction ({n(abs(tpa['window_a_net_usd']))} USD net in window A).
- **Window-B netting.** In options 1–2 a net loss after the warning is ignored (or scaled) as a whole, including proceeds of
  sales inside it; the red team measures 2,606 USD of such proceeds for 22 owners.
- **Deliverability.** {c['recipients_quality']['by_kind'].get('no_outgoing_tx', {}).get('n', 0)} recipients ({n(c['recipients_quality']['by_kind'].get('no_outgoing_tx', {}).get('gnk', 0))} GNK) have never sent an Ethereum transaction and {c['recipients_quality']['by_kind'].get('contract', {}).get('n', 0)} are contracts;
  they need a claim procedure. The account-kind column is not fully reliable (one contract is listed as "no outgoing tx").
- **Nobody's WGNK.** {n(sum(c['supply']['infra_balances'].values()), 1)} pre-hack WGNK sat in the CoW Settlement contract and in the WGNK contract itself and are not paid to anyone;
  liquidity positions add up to the pool balances with a gap of {n(c['supply']['pool_minus_positions'])} WGNK.
- **Pre-hack price.** p0 is the 24-hour VWAP; with windows from 1 hour to 7 days the deductions for sellers change by a few thousand GNK at most.
- **After the freeze.** Trades after 23 Nov 04:30 UTC count in no option ({c['after_freeze'].get('swaps', 0)} swaps were recorded between the freeze and the check).

## 4. Checked and not confirmed

- No WGNK mint after the attack other than the attacker's 22,000,000; every genuine mint is matched to a Gonka request.
- WGNK supply at the snapshot is fully assigned (owners' wallets + pools + two service contracts).
- No liquidity position changed hands between the snapshot and the warning; one v4 position NFT changed owner after it.
- Wrapped USDT/USDC balances of the 18 bridge-reserve holders on Gonka did not change after the attack.
- In the first five minutes after the warning there were {cu['buys_first_5_min_after_warning']['n']} purchases for {n(cu['buys_first_5_min_after_warning']['usd'])} USD — the exact second of the line is not material.

## 5. Independent reviews

{ext.get('reviews_md') or 'See `red_team/REDTEAM_REPORT.md` and `independent_lp_recheck/REPORT.md`.'}
The earlier independent recomputation (`05_independent_check/`) was re-run against version 2: {ext.get('recheck_v2') or 'see `05_independent_check/recheck_v2/`'}.

## 6. What cannot be checked from on-chain data

Who owns an address and whether recipients are related to the project; payments off chain; announcements on Discord;
the state of the Gonka bridge module for each pending record; what happens after the freeze.
"""
    p = d["ex"].root / "audit_docs" / "CRITIQUE.md"
    p.parent.mkdir(exist_ok=True)
    p.write_text(md)
    return str(p)
