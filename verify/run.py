#!/usr/bin/env python3
"""Recompute the compensation register from the raw data in this repository and compare it with the published one.

    pip install -r verify/requirements.txt
    python verify/run.py [--work DIR] [--keep]

No network access and no API keys are needed. Steps:
  1. copy data/raw into a working directory (decompressing *.json.gz);
  2. run the model (code/gonka_research/exploit_model.py) and the three options (comp_variants.py);
  3. compare every payee address and every option with registers/register_detailed.csv and registers/register.csv,
     the totals with model/summary_three_options.json, and the self-audit figures with model/critique.json.
Exit code 0 means no differences beyond rounding (1e-6).
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "code"))

from gonka_research import comp_variants, critique, exploit_model  # noqa: E402
from gonka_research.lite import Paths  # noqa: E402

TOL = 1e-6
PAY = ("gnk", "usdt", "usdc", "dai", "eth")
OPTIONS = ("v1", "v2", "v3")


def materialise(work: Path) -> int:
    """data/raw → <work>/raw in the layout the model reads; *.json.gz are decompressed."""
    n = 0
    for src in sorted((REPO / "data" / "raw").rglob("*")):
        if src.is_dir() or src.name == "README.md":
            continue
        dst = work / "raw" / src.relative_to(REPO / "data" / "raw")
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.name.endswith(".json.gz"):
            dst.with_name(src.name[:-3]).write_bytes(gzip.decompress(src.read_bytes()))
        else:
            shutil.copy2(src, dst)
        n += 1
    return n


def numeric_diffs(a, b, path: str = "") -> list[str]:
    """Leaves of two JSON-like structures that differ by more than the tolerance."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: present on one side only")
            else:
                out += numeric_diffs(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: list length {len(a)} vs {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += numeric_diffs(x, y, f"{path}[{i}]")
    elif isinstance(a, bool) or isinstance(b, bool) or a is None or b is None or isinstance(a, str) or isinstance(b, str):
        if a != b:
            out.append(f"{path}: {a!r} vs {b!r}")
    else:
        if abs(float(a) - float(b)) > TOL * max(1.0, abs(float(a)), abs(float(b))):
            out.append(f"{path}: {a} vs {b}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--work", help="working directory (default: a temporary one)")
    ap.add_argument("--keep", action="store_true", help="keep the working directory")
    args = ap.parse_args()
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="wgnk-verify-"))
    work.mkdir(parents=True, exist_ok=True)
    problems: list[str] = []

    print(f"[1/5] raw data → {work} ({materialise(work)} files)")
    paths = Paths(work)
    print("[2/5] model: balances, transactions, liquidity positions, owners …")
    exploit_model.build(paths)
    print("[3/5] three options …")
    summary = comp_variants.compute(paths)

    print("[4/5] compare with the published register and summary")
    mine = pd.read_parquet(work / "model" / "parquet" / "payees.parquet").set_index("entity")
    det = pd.read_csv(REPO / "registers" / "register_detailed.csv").set_index("payee_eth_address")
    if set(mine.index) != set(det.index):
        problems.append(f"payee addresses differ: {len(set(mine.index) ^ set(det.index))} not in both")
    common = sorted(set(mine.index) & set(det.index))
    worst = 0.0
    for v in OPTIONS:
        for k in PAY:
            d = (mine.loc[common, f"{v}_pay_{k}"].astype(float) - det.loc[common, f"{v}_{k}"].astype(float)).abs()
            worst = max(worst, float(d.max()))
            bad = d[d > TOL * 10]
            if len(bad):
                problems.append(f"{v} {k}: {len(bad)} addresses differ, e.g. {bad.index[0]} by {bad.iloc[0]:.9f}")
        if int(mine[f"{v}_paid"].sum()) != int(det[f"{v}_paid"].astype(str).str.lower().eq("true").sum()):
            problems.append(f"{v}: number of recipients differs")
    simple = pd.read_csv(REPO / "registers" / "register.csv").set_index("payee_eth_address")
    paid = det[det[[f"{v}_paid" for v in OPTIONS]].astype(str).apply(lambda c: c.str.lower().eq("true")).any(axis=1)]
    if set(simple.index) != set(paid.index):
        problems.append("register.csv does not list exactly the paid rows of register_detailed.csv")
    for v, n in zip(OPTIONS, (1, 2, 3)):
        for k in PAY:
            d = (simple[f"option{n}_{k}"].astype(float) - paid.loc[simple.index, f"{v}_{k}"].astype(float)).abs()
            if float(d.max()) > 1e-5:
                problems.append(f"register.csv option{n}_{k} differs from register_detailed.csv by up to {float(d.max()):.9f}")
    published = json.loads((REPO / "model" / "summary_three_options.json").read_text())
    for v in OPTIONS:
        problems += numeric_diffs({k: summary["variants"][v][k] for k in ("recipients", "totals", "gnk_gap", "eth_gap", "cost_usd")},
                                  {k: published["variants"][v][k] for k in ("recipients", "totals", "gnk_gap", "eth_gap", "cost_usd")}, f"summary/{v}")
    print(f"      {len(common)} payee addresses, 3 options, 5 currencies; largest difference {worst:.2e}")
    for v in OPTIONS:
        x = summary["variants"][v]
        print(f"      option {v[1]}: {x['recipients']} recipients, {x['totals']['gnk']:,.2f} GNK, top-up {x['cost_usd']:,.0f} USD")
    checks = summary["checks"]
    for name in ("v1_gnk_formula_max_diff", "payee_split_max_diff"):
        if abs(checks[name]) > 1e-6:
            problems.append(f"model check {name} = {checks[name]}")
    for name in ("monotonic_v1_le_v2", "monotonic_v2_le_v3", "payout_monotonic_violations", "no_b_identical"):
        if checks[name]:
            problems.append(f"model check {name} = {checks[name]}")

    print("[5/5] self-audit figures (model/critique.json)")
    d = critique._load(paths)
    (work / "model" / "critique").mkdir(parents=True, exist_ok=True)
    pub = json.loads((REPO / "model" / "critique.json").read_text())["checks"]
    skipped = []
    for fn in critique.CHECKS:
        got = fn(d)
        name = got.get("id", fn.__name__)
        if name == "fixes" or name not in pub:      # compares with the pre-publication draft, which is not part of this repository
            skipped.append(name)
            continue
        diffs = numeric_diffs({k: v for k, v in got.items() if k not in ("otc_pairs",)}, {k: v for k, v in pub[name].items() if k not in ("otc_pairs",)}, f"critique/{name}")
        problems += diffs[:5]
    print(f"      {len(critique.CHECKS) - len(skipped)} checks recomputed; not recomputed here: {', '.join(skipped) or 'none'}")

    if not args.keep and not args.work:
        shutil.rmtree(work, ignore_errors=True)
    if problems:
        print(f"\nDIFFERENCES FOUND ({len(problems)}):")
        for p in problems[:40]:
            print("  -", p)
        return 1
    print("\nOK — the published register, summary and self-audit figures are reproduced from data/raw: 0 differences.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
