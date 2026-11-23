"""Seed liquidity of the largest recipient and share of the main pool."""
import sys
sys.path.insert(0, "/work")
from rt_common import *
A = "0x244186297b43ba43c92d68efe78c04170fbc0b10"
lp = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/lp_events.parquet")
m = lp[(lp.origin_eoa.str.lower() == A)].copy()
m["u"] = m.amount_usdt.astype(float); m["w"] = m.amount_wgnk.astype(float)
print(m.groupby([m.block_time.astype(str).str[:10], "event"]).agg(n=("u", "count"), usdt=("u", "sum"), wgnk=("w", "sum")).to_string())
pool = lp[lp.pool_id == "0x203ee836d417cf944133bbdd2c62b4bc7388c55d"].sort_values("block_number")
print("first event in pool:", pool.iloc[0][["block_time", "event", "origin_eoa"]].to_dict())
mr = pd.read_parquet(f"{P}/02_onchain_raw/postgres_export/bridge_mint_requests_gonka.parquet")
print("share of gonka1gyy3 in all requested GNK:", mr[mr.signer == "gonka1gyy3nmdmh7cerfe39suze5uqutyq35xfx0399r"].gnk.astype(float).sum() / mr.gnk.astype(float).sum())
tr = transfers()
x = tr[(tr.from_addr == "0xbd3ca5a43f72e45faf4b142832110842113dc9f8") & (tr.to_addr == A)]
print(x.assign(when=pd.to_datetime(x.time, unit="s"))[["when", "value_wgnk"]].to_string())
