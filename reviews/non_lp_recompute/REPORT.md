# Independent recomputation of WGNK bridge-exploit compensation — audit report

Date: 2026-11-23. Implementation: `02_recompute.py` (this directory).
The auditor (a separate AI agent with no access to the model code) did not open or import the project's model code
(`exploit_model.py`, `comp_variants.py`). Project outputs were used only for: sample selection, cluster membership
(`addresses`), `b0_pending_burn`, the comparison, and — after the first comparison — diagnosis
(`model/parquet/tx_deltas_windows.parquet`, `model/comp3.json`).

> **Follow-up by the project (same day) — read first.** Two things changed after this audit ran; see section 7.
> (1) The auditor's brief quoted an earlier draft of the option-2 ladder (boundaries +1h / 09:13:37); the final ladder is
> 01:35:41 / 12:03:00 / +24h. This explains the single sample mismatch. (2) The auditor's finding 5.1/5.2 (purchases and
> sales settled through a third party) was accepted and fixed in the model. Re-running the auditor's unchanged method on the
> final table: 1,181 of 1,256 non-LP owners match in full; all 75 differences are exactly the owners affected by the new
> third-party rule, which the independent script does not implement.

## 1. Result

- Sample: 30 owners, 29 match in full, 1 mismatch: `k_eff` and variant-2 USDT of
  `0xd0162a989355b507f696feec3b835f073fe092d3` (0.1508 vs 0.1765; 120.97 vs 122.19 USDT).
- Cause: the K(t) gradient, not the transaction reading. `variants.parquet` (`k_eff`, `v2_*`) is reproduced by the ladder
  0.5 until 1795052141 (01:35:41 UTC), 0.25 until 1795089780 (12:03:00 UTC), 0.125 until +24h; the audit brief specified
  0.5 until 1795051447, 0.25 until 1795079617 (09:13:37 UTC), 0.125 until 1795134247.
- B0, net_A, net_B, variant 1, variant 3 and GNK in all variants match for every sampled owner
  (max diff: B0 0.0 WGNK, USD 1.5e-6, GNK 1.7e-6).
- Extra population check (1,256 non-LP owners): 1,241 match, 15 differ, all only in `k_eff`/`v2`, all explained by the ladder.
- Methodology gaps not visible as mismatches are listed in section 5.

## 2. Method

Run: `docker run --rm -v <R>:/research:ro -v <this dir>:/work <python-image> python /work/02_recompute.py`

Sample. Seed 20261123 (`numpy.random.default_rng`). Stratified draw from `variants.parquet`, excluding the hacker,
category `lp` and owners with any non-zero LP field (removes 1 `b_only`, 1 `trader_profit`). Strata: holder 6 (2 largest
by `honest_wgnk` + 4 random), holder_sold 4 (all), holder_traded 6, buyer 6, trader_loss 3, trader_profit 3, b_only 2.
Constraints (>=10 `has_b`, >=3 ETH payers) by rejection on the same RNG stream; accepted on attempt 55
(10 `has_b`, 7 ETH payers, 2 two-address clusters).

Computation.
1. B0 per address = sum(in) - sum(out) of `value_raw` in `wgnk_transfers.parquet`, `block_number <= 26443612`;
   cluster = sum over listed addresses; `honest_wgnk` = B0 + project `b0_pending_burn`.
2. Per-tx deltas from receipts (status 0x1): ERC-20 Transfer of WGNK/USDT/USDC/DAI/WETH; WETH Deposit (+topic1) and
   Withdrawal (-topic1); native ETH from `tx.value` and `post_internal.json` entries with `isError == "0"`.
   WETH and ETH are one currency. USD: stables at 1, ETH x `eth_usd[block // 25 * 25]`.
3. Windows: A = blocks 26443607..26445519, B = 26445520..26475449 (block 26445519 ts 1795047839 <= warning 1795047847;
   block 26445520 ts 1795047851). No WGNK transfer exists in blocks 26443607..26443612.
4. Dust rule per address: tx counts only if |dWGNK| >= 1. (Cluster-level rule gives identical results for all owners.)
5. net_A / net_B = -sum(USD delta) over counted txs; per-currency signed quantities kept.
6. K by tx timestamp, inclusive bounds: 0.5 / 0.25 / 0.125 / 0 at 1795051447 / 1795079617 / 1795134247.
   k_eff = spend-weighted K over counted window-B txs with net money outflow (weight = tx net USD outflow;
   per-currency gross weighting gives identical k_eff for all owners).
7. Variants: phi = 1 if net_B <= 0 else 0 / k_eff / 1; q = q_A + phi*q_B; M = sum usd. M > 0.005: refund each currency with
   positive usd as q * M / sum(positive usd), GNK = max(0, B0_total); else GNK = max(0, B0_total + M/p0).
   p0 = 0.1428805236181846.
8. Tolerances: 0.01 WGNK (B0), $0.02, 0.5 GNK, 0.01 USDT/USDC/DAI, 0.00001 ETH, 1e-4 k_eff.

Nothing in the method was changed after seeing project numbers. `k_eff_diag_project_base_ladder` is a labelled
diagnostic field, not used for payouts or pass/fail.

Data checks: all 3,014 post-attack WGNK-transfer txs are in `post_txs.json`/`post_receipts.json`; all receipts status 0x1;
`block_ts.json` agrees with the transfer log; the internal list does not repeat the top-level call; 4 errored internals skipped.

## 3. The discrepancy

Owner `0xd0162a989355b507f696feec3b835f073fe092d3` (holder_traded, 215 counted txs, never the tx sender).

| field | mine | project |
|---|---|---|
| B0 | 2892.400790 | 2892.400790 |
| net_A / net_B | 113.8109 / 47.4950 | same (<1e-6) |
| k_eff | 0.150780 | 0.176470 |
| v2 USDT | 120.9722 | 122.1923 |
| v1 / v3 USDT | 113.81 / 161.31 | same |

Per-tx reading is identical (215 txs, same windows, max USD diff 4e-16 vs `tx_deltas_windows.parquet`).
The difference is K on 11 window-B purchases:
- `0x3d5ec8b1fcc9d7ea13a9b2d6de91dd4cf7941685a0c54310ab7ef481558766f4`, ts 1795052015, $17.57: 0.25 (brief) vs 0.5 (project);
- 10 txs with ts 1795080743..1795089155, $237.65: 0.125 vs 0.25.

Effect on variant 2, non-LP population (mine - project): -553.48 USDT, -55.28 USDC, -0.003942 ETH, 0 GNK; 11 owners beyond
tolerance, 4 more differ in k_eff only.

## 4. Population cross-check (extra, `AUDIT_ALL=1`)

1,256 non-hacker owners without LP fields: B0 max diff 0.0; net_A/net_B max diff 2.6e-6 USD; v1/v3 max diff 6e-6 GNK;
15 fail, all on k_eff/v2 only, all reproduced by the project's base ladder. Not covered: 32 `lp` owners, 2 owners with LP
fields in other categories, the hacker.

## 5. Doubts about the methodology

My implementation follows the same rule and inherits the same blind spots, so these are not number mismatches.

5.1 Purchases paid by a different address (most material). 152 txs where an address got >=1 WGNK with no money leg while a
pure payer paid in the same tx: window A 61 txs, $5,242.58, 175,001 WGNK; window B 91 txs, $3,075.05, 155,983 WGNK;
68 owners. Nobody is refunded.
- CoW Swap ETH-flow, payer `0xba3cb449bd2b4adddbc894d8697f5170800eadec` (9 txs, $857.58): ETH was deposited in an earlier
  tx that is not in the dataset. Two sampled owners that "pass":
  `0x680408815aa94a20e78a904fe030fc8d5653d426`, tx `0xc8e002dcc45ff3d7da5318b2468c97258708571aed901244e0611a2f1bcb9d21`,
  block 26445401, +6,551.49 WGNK for 0.109865 ETH (~$195.54): reported net_A -33.22, payout 0; real net_A ~ +162.
  `0x2139d49082b47ef480741007a9414b71988b3669`, tx `0xedbafd456422d10b31c2c19e490d0073d06901bede57efade3d73cb37088eb23`,
  block 26445287, +7,513.21 WGNK for 0.1299 ETH (~$229.93): `b_only`, payout 0 in all variants.
- Solver/relayer inventories: `0x754dcfb2861547015b221e963b4133a71dbdc024` (34 txs, $3,291.23),
  `0xf70da97812cb96acdf810712aa562db8dfa3dbef` (37 txs, $2,224.48). The users' paying leg cannot be verified from this dataset.

5.2 Sales whose proceeds went to another address: 49 txs; window A $1,388.80 / 40,989 WGNK; window B $317.73 / 26,818 WGNK.
Such a holder keeps full B0 in GNK.

5.3 Money legs in non-tracked tokens: 14 owners; e.g. `0x71196be3…` got 9,160.97 WGNK for a non-tracked token worth ~$76.58.

5.4 Intermediaries listed as owners: routers/fee collectors appear as holder/holder_sold/trader_profit/transfers; harmless
where M <= 0, small GNK payouts where B0 > 0. 16 owners due a money refund never signed a tx in `post_txs.json`
(v1 $2,268.81, v3 $2,661.22); EOA vs contract cannot be told from this data — check `eth_getCode`.

5.5 The dust rule drops money-only legs for 43 owners (mostly fee wallets; also the mechanism behind 5.1).

5.6 Not verified: LP owners (4.80M of 13.03M GNK and $134k of $209k USDT in v1); cluster composition and
`b0_pending_burn` (taken from the project table). ETH priced on 25-block buckets; gas not compensated.

## 6. Files

- `02_recompute.py` — independent implementation (`AUDIT_ALL=1` for the population run)
- `independent_recompute.json` — 30 owners, auditor vs project, diffs, pass/fail, flags (state before the follow-up fix)
- `independent_recompute_ALL.json` — same for 1,256 non-LP owners (state before the follow-up fix)
- `third_party_cases.json` — txs behind 5.1 and 5.2
- `recheck_after_fix/` — the same script (only the ladder constants updated to the final ones) run against the final table

## 7. Follow-up by the project team (2026-11-23, after the audit)

1. **Ladder.** The audit brief was written before the option-2 step boundaries were finalised. After legal review the
   boundaries were tied to notice events: the warning on X (00:24:07) → the warning repeated in the press (01:35:41, TokenPost)
   → the warning on the project's website (no later than 12:03:00) → 24 hours. The earlier draft (+1h / 09:13:37 "funds
   returned") is kept as sensitivity variant `v2_ladder0913` in `model/comp3.json`. `raw/return.json` was updated to the
   final ladder.
2. **Third-party settlement (5.1, 5.2) — fixed.** `exploit_model.tx_deltas` now attributes, within one transaction, money
   paid (received) by an address with a one-sided money flow and no WGNK change to the address whose WGNK increased
   (decreased) with no money leg, pro rata by WGNK. Other tokens' counterparties, pools, known routers and block builders are
   excluded. Result: purchases through intermediaries in window A $5,243.7 (auditor: $5,242.58), window B $3,074.3
   (auditor: $3,075.05); sales $1,193 / $542 (auditor: $1,389 / $318 — the project rule is narrower). Affected rows carry
   `via_third_party` in `tx_deltas_windows`; 77 owners.
3. **Recheck.** `recheck_after_fix/independent_recompute_ALL.json`: the auditor's method with the final ladder against the
   final `variants.parquet` — 1,181 of 1,256 owners pass; the 75 that differ are all owners with third-party attribution.
4. **Not changed (accepted limitations):** 5.3 (payment in non-tracked tokens, ~14 owners, small amounts), 5.4 (fee wallets
   holding pre-hack WGNK are holders like anyone else), 5.5. LP owners are covered by the project's own reconciliation of
   positions against pool balances (`checks.json`), not by this independent check.

## 8. Version 2 of the calculation (2026-11-23, after the self-audit)

The calculation was revised after a self-audit (`08_critique/CRITIQUE.md`). The auditor's unchanged script was run again
against the version 2 table (`recheck_v2/`): 1,173 of 1,256 non-LP owners match in full. The 83 that differ are the owners
affected by the third-party-settlement rule (75) or by the new rule that values trades paid in untracked tokens by the WGNK
pool leg (11; 3 owners fall under both) — neither rule is implemented in the independent script. Liquidity-position owners,
not covered by this check, were recomputed separately from contract state (`08_critique/independent_lp_recheck/`).
