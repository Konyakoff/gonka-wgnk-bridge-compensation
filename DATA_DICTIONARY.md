# Data dictionary

Units: WGNK and GNK have 9 decimals; USDT and USDC 6; ETH, WETH and DAI 18. Amounts are whole tokens (decimal numbers)
unless a column name ends with `_raw`, `_units`, `_ngonka` or `_wei` — those are integers in base units. Timestamps are
Unix seconds, UTC. Ethereum addresses are lower-case. Machine-readable schemas (column names and types) are in
`datapackage.json`; checksums of every file are in `SHA256SUMS`.

## registers/register.csv — the register, simple form

One row per **paid payee address** (a row appears if the address is paid under at least one option).

| Column | Meaning |
|---|---|
| `payee_eth_address` | the Ethereum address that receives the payout |
| `gonka_address` | Gonka address of the same secp256k1 key (default destination of native GNK); empty if it could not be derived |
| `gonka_address_status` | `derived from signature` / `no outgoing tx - claim needed` / `smart contract - claim needed` |
| `category` | activity up to the warning: holder, holder_sold, holder_traded, buyer, trader_loss, trader_profit, lp, b_only, transfers |
| `optionN_gnk`, `optionN_usdt`, `optionN_usdc`, `optionN_dai`, `optionN_eth` | payout under option N (N = 1, 2, 3); GNK may be taken as new WGNK |

## registers/register_detailed.csv — the register, detailed form

One row per payee address (paid or not) of every owner in the model. For an owner with several addresses each address has
its own row and receives its own share (METHODOLOGY §3).

| Column | Meaning |
|---|---|
| `payee_eth_address` | the Ethereum address of this row |
| `owner_group` | key of the owner (first address of the group); equals `payee_eth_address` for single-address owners |
| `group_size` | number of addresses of the owner |
| `all_addresses` | all addresses of the owner, `;`-separated (linked by plain WGNK transfers after the attack) |
| `gonka_address`, `gonka_address_status`, `gonka_key_already_signed` | see above; the last one is true if this key has already signed a transaction on Gonka |
| `category` | see above (`hacker` for the attacker's addresses) |
| `b0_wallet_wgnk` | WGNK in the wallet at the end of block 26,443,612 |
| `b0_pending_burn_wgnk` | WGNK burned on the bridge before the hack and not yet delivered as GNK |
| `lp_wgnk_before` | WGNK inside liquidity positions at the snapshot (incl. owed tokens and uncollected fees) |
| `honest_wgnk` | sum of the three columns above — pre-hack WGNK honoured one for one |
| `net_a_usd` / `net_b_usd` | money spent minus money received for WGNK in window A / window B, USD (positive = net loss); owner-level |
| `traded_after_warning` | true if the owner has any transaction or position change in window B |
| `phi_option2` | share applied to the owner's window-B result in option 2 (1 if that result is a gain) |
| `vN_gnk`, `vN_usdt`, `vN_usdc`, `vN_dai`, `vN_eth` | payout under option N, whole tokens |
| `vN_gnk_ngonka`, `vN_usdt_units`, `vN_usdc_units`, `vN_dai_wei`, `vN_eth_wei` | the same in integer base units, rounded down (GNK, DAI and ETH to 9 decimals; USDT and USDC to 6) |
| `vN_value_usd` | payout value: GNK at p0 plus money (ETH at the price on the calculation date) |
| `vN_paid` | true if the address is a recipient under option N (GNK > 0.5 or money > 0.01 USD) |

`registers/Gonka_Compensation_Register_3_Options.xlsx` holds the detailed register and the other tables of this folder as
sheets (English headers, Russian sub-headers).

## Other files in registers/

- `bridge_requests_in_flight.csv` — GNK → WGNK bridge requests that were never minted (METHODOLOGY §8a): `gonka_sender`
  (payee), `eth_destination`, `gnk`, `gonka_height`, `time_utc`, `gonka_tx`, `after_attack`.
- `bridge_reserve_holders_gonka.csv` — Gonka addresses holding wrapped USDT/USDC whose backing is restored: `gonka_address`,
  `token`, `balance_before`, `balance_now` and exact `*_units`.
- `attacker_addresses.csv` — the attacker's addresses on Ethereum and Gonka.
- `parameters_and_totals.csv` — cut-offs, ladder, p0 and the totals of each option.

## model/variants.csv (per owner) and model/payees.csv (per payee address)

Same owners as the register plus diagnostics: `lp_u_before`, `lp_u_t1`, `lp_u_end` (money in liquidity positions at the
snapshot / warning / freeze, USD); `a_*` and `b_*` (window statistics: `w_in`/`w_out` WGNK bought/sold in money trades,
`usd_out`/`usd_in` money spent/received, `lp_usd` liquidity-operation turnover, `n_tx`, `via_usd` money attributed from
third-party settlement); `k_eff`, `k_eff_exp`, `k_eff_ladder10`, `k_eff_ladder0913` (spend-weighted K under each ladder);
`vX_phi`, `vX_pay_*`, `vX_m_usd` (M after applying phi), `vX_money_usd`, `vX_value_usd`, `vX_paid` for X in v1, v2, v3 and
the sensitivity variants v0_ignore_b, v2_exp, v2_ladder10, v2_ladder0913; `differs` (payout differs between options);
`has_b`; `burn_pending_post` (WGNK burned after the attack and stuck — voided); `g_credited` (GNK already delivered by the
bridge after the attack). In `payees.csv`, `entity` is the payee address, `owner` the owner key, `group_size` the number of
addresses of the owner.

## model/tx_deltas_windows.csv

One row per (transaction, address) for every counted transaction from block 26,443,607 to 26,475,449.

| Column | Meaning |
|---|---|
| `tx_hash`, `block`, `ts` | transaction, block number, block time |
| `address`, `entity` | address and its owner (cluster key) |
| `d_wgnk` | change of the address's WGNK balance in the transaction |
| `d_usd` | net money change in USD (negative = paid) |
| `tokens` | JSON: net change per currency (USDT, USDC, DAI, WETH, ETH), in tokens |
| `eth_usd` | ETH price used for this block |
| `is_lp_tx` | the transaction contains a liquidity operation on a WGNK pool |
| `via_third_party` | address(es) whose money was attributed to this row (third-party settlement), else empty |
| `valued_by_pool_leg` | true if the money of this row was taken from the WGNK pool swap (trade paid in an untracked token) |
| `win` | `A` (up to the warning) or `B` (after) |
| `k_ladder`, `k_exp`, `k_ladder10`, `k_ladder0913` | K(t) under the main ladder and the sensitivity ladders |
| `tx_from`, `tx_to` | transaction sender and target |

## model/lp_positions.csv

One row per (position, state). `pos` — position key (`v3:<NFT id>`, `own:<pool>:<owner>:<ticks>`, `v4:<NFT id>`,
`v4own:…`); `state` — `snap` (block 26,443,612), `t1` (26,445,519), `end` (26,475,449); `liquidity`; `owner`, `entity`;
`wgnk` — WGNK in the position incl. owed tokens and fees; `money_token`, `money_amount`, `money_usd` — the other side.

## model/summary_three_options.json

`variants.<v>`: `recipients`, `totals` (per currency), `reserve`, `gnk_need`, `gnk_in_escrow`, `gnk_in_flight`, `eth_need`,
`eth_gap`, `gnk_gap`, `cost_usd` (protocol top-up), `cost_share_pool`, `sensitivity_eth`; `windows` (swap counts and volumes
for A, B and each ladder step); `gradient` (ladder boundaries); `categories` (per option and category); `checks`; `counts`;
`bridge_in_flight`; `escrow_gnk_now`; `k_pool`.

## model/critique.json and model/critique/*.csv

`checks.<id>`: one object per self-audit check — the figures quoted in `CRITIQUE.md` and in the “Critique of the method”
slides. CSV files list the addresses behind each figure: `plain_transfer_pairs.csv` (address pairs linked by plain WGNK
transfers and the money found between them), `address_groups.csv`, `profit_kept.csv`, `top_recipients.csv`,
`pending_burns_after_attack.csv`, `bridge_requests_not_minted.csv`.

## data/raw — inputs of the calculation

| File | Content | Source |
|---|---|---|
| `meta.json` | run parameters: p0 and its window, snapshot / warning / freeze blocks | Uniswap swap log |
| `return.json` | verification of the attacker's return (ETH tx, GNK txs, Safe owners), community pool, ETH price and gas at calculation time, cut-off blocks, option-2 ladder | Ethereum RPC, Etherscan, Gonka LCD |
| `extra.json` | alternative pre-hack prices (VWAP 1 h … 30 d, last trade), swaps recorded after the freeze | Uniswap swap log |
| `eth/wgnk_transfers.parquet` | `block_number`, `time`, `tx_hash`, `log_index`, `tx_index`, `from_addr`, `to_addr`, `value_raw` (integer string, 9 decimals), `value_wgnk`; the zero address is mint/burn | Etherscan `getLogs` on the WGNK contract |
| `eth/post_txs.json.gz`, `post_receipts.json.gz`, `post_internal.json.gz` | keyed by transaction hash: `from`, `to`, `value` (hex wei), `blockNumber`; receipt `status` and `logs[]`; internal ETH transfers `from`, `to`, `value`, `isError` | `eth_getTransactionByHash`, `eth_getTransactionReceipt`, Etherscan `txlistinternal` |
| `eth/block_ts.json.gz`, `eth_usd.json.gz` | block timestamps; ETH/USD per 25-block bucket (Chainlink) | `eth_getBlockByNumber`; Chainlink feed via archive `eth_call` |
| `eth/lp_extra.json.gz`, `lp_fees.json.gz`, `v4_extra.json.gz`, `v4_modify.parquet` | Uniswap v3 position NFT events and owners, pool `slot0` and balances at the three blocks; owed tokens and uncollected fees; v4 pools, position owners and ModifyLiquidity events | `eth_call`, `getLogs` |
| `eth/forensics.json.gz` | the attacker's transactions, decoded bridge calls, bridge reserves and WGNK supply at key blocks | Etherscan, Ethereum RPC |
| `eth/twins.json.gz`, `twins_bridge_check.json.gz` | per address: account kind, a sample outgoing tx, the Gonka address derived from the same public key; validation of the derivation against the bridge's own records | signature recovery; Gonka LCD |
| `eth/balances_end.json.gz` | USDT and USDC balances of every participant at the freeze block | `eth_call balanceOf` |
| `eth/otc_history.json.gz` | USDT/USDC/DAI/WETH/ETH history of the addresses linked by plain WGNK transfers (used by the self-audit only) | Etherscan `txlist`, `txlistinternal`, `tokentx` |
| `db/swaps.parquet`, `lp_events.parquet`, `pools.parquet`, `bridge_events.parquet` | swap, liquidity and bridge mint/burn events of the tracked pools and of the bridge contract | Uniswap and bridge logs (Etherscan) |
| `db/bridge_requests_status.parquet` | `MsgRequestBridgeMint` messages on Gonka with the transaction success flag | Gonka LCD |
| `db/swaps_after_freeze.parquet` | swaps recorded after the data freeze (empty at collection time) | Uniswap swap log |
| `gonka/gonka.json.gz` | threshold-signing status of every mint and of the attacker's withdrawals, bridge transactions, epoch keys, the attacker's GNK trail, escrow balance | Gonka LCD nodes and explorer |
| `gonka/reserve_holders.json.gz` | holders of wrapped USDT/USDC on Gonka before the attack and now | CW20 smart queries |

`data/sources/` holds the timeline of publications about the hack (how the time of the official warning was established).

## legal/case_law.csv

`pass` (research pass), `id`, `name`, `citation`, `jurisdiction`, `year`, `forum`, `rule_or_holding`, `relevance_to_gonka`,
`quote` (verbatim where the source was opened), `urls`, `verification` (`primary` / `secondary` / `unverified`),
`supports` (hard_cutoff, gradient_or_grace, snapshot_at_hack, net_loss_principle, price_paid_remedy, earlier_cutoff,
later_cutoff, no_duty, contradicts, context).
