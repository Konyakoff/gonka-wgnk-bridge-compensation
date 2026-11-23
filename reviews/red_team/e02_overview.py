import sys
sys.path.insert(0, "/work")
from rt_common import *

v = variants(); reg = register(); d = deltas()
print("variants cols:", list(v.columns))
print("deltas cols:", list(d.columns))
print("register cols:", list(reg.columns))
print(d.head(3).T.to_string())
print()
# 1. sums vs summary
summ = jz("03_model/summary_three_options.json")
for o in ("v1", "v2", "v3"):
    x = v[v[f"{o}_paid"]]
    print(o, "recipients", len(x), {k: round(x[f"{o}_pay_{k}"].sum(), 4) for k in ("gnk", "usdt", "usdc", "dai", "eth")},
          "summary:", summ["variants"][o]["recipients"], {k: round(t, 4) for k, t in summ["variants"][o]["totals"].items()})
    r = reg[reg[f"{o}_paid"]]
    print("   register", len(r), {k: round(r[f"{o}_{k}"].sum(), 4) for k in ("gnk", "usdt", "usdc", "dai", "eth")}, "value", round(r[f"{o}_value_usd"].sum(), 2))
print(json.dumps({k: summ["variants"]["v1"][k] for k in summ["variants"]["v1"] if k not in ("totals", "sensitivity_eth")}, indent=1)[:3000])
print("checks", json.dumps(summ["checks"], indent=1))
print("counts", summ["counts"], "k_pool", summ["k_pool"], "missing", summ["entities_missing_in_base"])
print("windows", json.dumps(summ["windows"], indent=1))
print("categories v1")
print(pd.DataFrame(summ["categories"]["v1"]).T.to_string())
print("categories v3")
print(pd.DataFrame(summ["categories"]["v3"]).T.to_string())
# 2. monotonic & sanity
nh = v[~v["is_hacker"]]
print("non-monotonic value v1>v2:", ((nh.v1_value_usd - nh.v2_value_usd) > 0.01).sum(), "v2>v3:", ((nh.v2_value_usd - nh.v3_value_usd) > 0.01).sum())
print("negatives:", {c: int((v[c] < -1e-9).sum()) for c in v.columns if c.endswith(("pay_gnk", "pay_usdt", "pay_usdc", "pay_dai", "pay_eth"))})
print("dup entity", v.entity.duplicated().sum())
alla = v["addresses"].str.split(";").explode()
print("addresses total", len(alla), "dups", alla.duplicated().sum())
print("category counts", v.category.value_counts().to_dict())
print("register status", reg.gonka_address_status.value_counts().to_dict())
# top 25 by v1 value
c = ["entity", "category", "honest_wgnk", "b0_wallet", "lp_w_before", "lp_u_before", "lp_u_t1", "lp_u_end", "net_a_usd", "net_b_usd", "v1_pay_gnk", "v1_money_usd", "v1_value_usd", "v3_value_usd"]
print(v.sort_values("v1_value_usd", ascending=False)[c].head(30).round(2).to_string())
tot = v.v1_value_usd.sum()
s = v.sort_values("v1_value_usd", ascending=False).v1_value_usd.cumsum() / tot
print("total v1 value", tot, "top1", s.iloc[0], "top5", s.iloc[4], "top10", s.iloc[9], "top20", s.iloc[19], "top50", s.iloc[49])
m = v.sort_values("v1_money_usd", ascending=False)
print("money v1 total", m.v1_money_usd.sum(), "top1", m.v1_money_usd.iloc[0] / m.v1_money_usd.sum(), "top5", m.v1_money_usd.iloc[:5].sum() / m.v1_money_usd.sum(), "top10", m.v1_money_usd.iloc[:10].sum() / m.v1_money_usd.sum())
print(m[c].head(25).round(2).to_string())
