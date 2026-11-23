"""Shared loaders for the red-team scripts. Works only from the published audit package (mounted at /pkg)."""
import gzip
import json

import pandas as pd

P = "/pkg/Gonka_Bridge_Incident_Audit_Package"
OUT = "/work"
P0 = 0.1428805236181846
ETH_NOW = 1729.1468
T0_BLOCK, SNAP_BLOCK, T1_BLOCK, T2_BLOCK = 26443607, 26443612, 26445519, 26475449
WARN_TS = 1795047847
ZERO = "0x0000000000000000000000000000000000000000"
WGNK = None  # filled lazily from data (bridge contract address)

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 70)
pd.set_option("display.max_rows", 500)


def jz(path):
    p = f"{P}/{path}"
    if p.endswith(".gz"):
        with gzip.open(p, "rt") as f:
            return json.load(f)
    with open(p) as f:
        return json.load(f)


def variants():
    return pd.read_parquet(f"{P}/03_model/variants.parquet")


def deltas():
    return pd.read_parquet(f"{P}/03_model/tx_deltas_windows.parquet")


def lp_positions():
    return pd.read_parquet(f"{P}/03_model/lp_positions.parquet")


def transfers():
    t = pd.read_parquet(f"{P}/02_onchain_raw/ethereum/wgnk_transfers.parquet")
    t["v"] = t["value_raw"].map(int)
    return t


def register():
    return pd.read_csv(f"{P}/04_registers/register_all_options.csv")


def swaps():
    return pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/swaps.parquet")


def pools():
    return pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/pools.parquet")


def balances(tr, upto):
    t = tr[tr["block_number"] <= upto]
    inc = t.groupby("to_addr")["v"].sum()
    out = t.groupby("from_addr")["v"].sum()
    bal = inc.sub(out, fill_value=0)
    return bal.map(lambda x: int(x) / 1e9)


def short(a):
    return a[:10] + "…" + a[-4:] if isinstance(a, str) and len(a) > 20 else a
