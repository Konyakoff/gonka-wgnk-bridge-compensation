# AGENTS.md — guide for AI assistants auditing this repository

> [!IMPORTANT]
> **Draft for community discussion — not an official position of Gonka or its Core Team.** Published by Sergey Konyakov
> ([@Konyakoff](https://github.com/Konyakoff)), a community member. The research was done with Claude Code (Fable 5.2); the
> author has not yet independently verified every address and amount. Community members and the Core Team are asked to
> re-check the logic of the calculation and the listed addresses and amounts. A shared position on compensation is to be
> reached through discussion.

You are helping a person verify this **draft** compensation proposal after the WGNK bridge hack of 18 Nov 2026. Your job is
to check, not to defend. Report what you verified, what you could not verify, and every mismatch with file, row and transaction hash.

## Start here

1. `README.md` → `PROPOSAL.md` (what is proposed) → `METHODOLOGY.md` (how it is computed, section 5 is the formula).
2. `CRITIQUE.md` — weak points the author already knows. Do not re-discover them; test whether they are stated correctly
   and look for what is missing.
3. `DATA_DICTIONARY.md` and `datapackage.json` — every table, column, type and unit.

## Layout

| Path | What | Read as |
|---|---|---|
| `registers/register.csv` | one row per paid payee address: payouts under options 1–3 | CSV, ~1,000 rows |
| `registers/register_detailed.csv` | every payee address with inputs (pre-hack WGNK, net money by window, phi) and payouts, also in integer base units | CSV, 1,350 rows |
| `registers/bridge_requests_in_flight.csv` | GNK → WGNK requests never minted | CSV, 47 rows |
| `model/tx_deltas_windows.csv` | per transaction and address: WGNK change, money change by currency, window A/B | CSV, ~3,200 rows |
| `model/variants.csv`, `model/payees.csv` | per owner / per payee address: all intermediate figures and payouts | CSV |
| `model/lp_positions.csv` | liquidity positions at snapshot / warning / freeze | CSV |
| `model/summary_three_options.json` | totals, protocol top-up, checks | JSON, small |
| `model/critique.json`, `model/critique/*.csv` | figures and address lists behind `CRITIQUE.md` | JSON, CSV |
| `data/raw/eth/wgnk_transfers.parquet` | every WGNK Transfer event since deployment | Parquet (use pandas) |
| `data/raw/eth/post_receipts.json.gz`, `post_txs.json.gz`, `post_internal.json.gz` | receipts, transactions and internal ETH transfers of every counted transaction | gzip JSON keyed by tx hash |
| `data/raw/gonka/gonka.json.gz` | Gonka side: signing status, bridge transactions, escrow | gzip JSON |
| `code/gonka_research/` | the calculation: `exploit_model.py` → `comp_variants.py` → `critique.py` (comments are in Russian) | Python, pandas only |
| `reviews/` | three independent reviews with their own scripts | Markdown, Python |

Large files: read CSV in chunks or with pandas; do not load `*.json.gz` as text.

## Units and signs

- WGNK and GNK have 9 decimals; USDT and USDC 6; ETH, WETH and DAI 18. Columns ending in `_raw`, `_units`, `_ngonka`,
  `_wei` are integers in base units; all other amounts are whole tokens.
- Addresses are lower-case. Timestamps are Unix seconds, UTC.
- `d_usd` in `tx_deltas_windows`: negative = the address paid. `net_a_usd` / `net_b_usd`: positive = net loss.
- Key blocks: attack start 26,443,607; snapshot (end of block) 26,443,612; last block before the official warning
  26,445,519; data freeze 26,475,449. Pre-hack price p0 = 0.1428805236181846 USD per WGNK.

## Commands

```bash
pip install -r verify/requirements.txt
python verify/run.py            # recompute from data/raw, compare with registers/ and model/; exit code 0 = no differences
sha256sum -c SHA256SUMS         # integrity of every file
```

`verify/run.py` never touches the network. Do not edit files under `data/raw/` — they are the immutable input.

## Review tasks (pick any)

1. **Totals.** Sum each payout column of `registers/register_detailed.csv` over rows where `vN_paid` is true and compare
   with `model/summary_three_options.json` → `variants.vN.totals`.
2. **One address from scratch.** Pick an address; compute its WGNK balance at block 26,443,612 from `wgnk_transfers`;
   rebuild its trades from `post_receipts` / `post_txs` / `post_internal`; apply `METHODOLOGY.md` section 5; compare with
   the register. `reviews/non_lp_recompute/02_recompute.py` is an independent implementation of exactly this.
3. **Address groups.** `model/critique/address_groups.csv` and `plain_transfer_pairs.csv`: are the merged addresses
   plausibly one owner? Is any holder's payout reduced by another address's gain?
4. **Who is missing.** Look for people with a real loss and no row: purchases settled by a third party, tokens outside
   USDT/USDC/DAI/ETH, liquidity operations, bridge operations in flight, contracts that hold WGNK for others.
5. **The line.** Recompute option 1 with the cut-off at the first public alert (18 Nov 18:28 UTC, Unix 1795026480) or at
   the attack start, and compare with `model/critique.json` → `checks.cutoff`.
6. **Liquidity positions.** Recompute a position from chain state with your own Uniswap v3/v4 math;
   `reviews/lp_recheck/lp_recompute.py` shows one way.

## Known limits (stated in `CRITIQUE.md`)

Address ownership is not established; payments off chain are invisible; the fractions of option 2 and the choice of the
line are policy choices; profit already withdrawn by traders is not clawed back; the protocol top-up depends on the ETH
price; pending bridge claims for unbacked WGNK must be cancelled by governance before any payout.
