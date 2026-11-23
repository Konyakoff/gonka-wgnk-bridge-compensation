import pandas as pd, json, gzip, os
P = "/pkg/Gonka_Bridge_Incident_Audit_Package"
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 80); pd.set_option("display.max_colwidth", 60)
for f in ["03_model/variants.parquet", "03_model/tx_deltas_windows.parquet", "03_model/lp_positions.parquet",
          "03_model/participants_base.parquet", "03_model/bridge_transactions_wgnk.parquet",
          "02_onchain_raw/ethereum/wgnk_transfers.parquet", "02_onchain_raw/ethereum/v4_modify_liquidity.parquet",
          "02_onchain_raw/postgres_export/swaps.parquet", "02_onchain_raw/postgres_export/lp_events.parquet",
          "02_onchain_raw/postgres_export/pools.parquet", "02_onchain_raw/postgres_export/bridge_events.parquet",
          "02_onchain_raw/postgres_export/bridge_mint_requests_gonka.parquet"]:
    df = pd.read_parquet(f"{P}/{f}")
    print("=====", f, df.shape)
    print(df.dtypes.to_string())
    print(df.head(3).to_string())
reg = pd.read_csv(f"{P}/04_registers/register_all_options.csv")
print("===== register", reg.shape); print(reg.dtypes.to_string()); print(reg.head(3).to_string())
for f in ["04_registers/attacker_addresses.csv", "04_registers/bridge_reserve_holders_gonka.csv"]:
    print("=====", f); print(open(f"{P}/{f}").read())
for f in ["02_onchain_raw/return.json", "02_onchain_raw/meta.json", "01_sources/publications/x_post_times_from_ids.json"]:
    print("=====", f); print(open(f"{P}/{f}").read()[:5000])
