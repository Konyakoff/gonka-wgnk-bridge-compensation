# data/

- `raw/` — the on-chain data exactly as the calculation reads it. Treat it as immutable input: `verify/run.py` recomputes
  everything in `model/` and `registers/` from these files. JSON files are gzip-compressed; tables are Parquet
  (`pandas.read_parquet`). What each file is and where it came from: [`DATA_DICTIONARY.md`](../DATA_DICTIONARY.md).
- `sources/` — the timeline of publications about the hack (in Russian, with a machine-readable CSV copy) and the times of
  the key X posts derived from their ids; this is how the time of the official warning, 19 Nov 2026 00:24:07 UTC, was
  established.

Collected between 19 and 23 Nov 2026 from public sources only: Ethereum (Etherscan API, an archive RPC node, Chainlink
price feed) and Gonka (public LCD nodes and the gonka.vip explorer). Data is frozen at Ethereum block 26,475,449
(23 Nov 2026 04:30 UTC). Anyone can re-fetch any record from a block explorer by its transaction hash.
