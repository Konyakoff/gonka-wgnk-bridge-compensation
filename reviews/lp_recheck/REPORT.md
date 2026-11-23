# Independent recomputation of the LP part of the compensation model

Date of run: 23 Nov 2026, 06:32–07:11 UTC. Auditor's code: `lp_recompute.py`. Machine-readable result: `lp_recompute.json`. The project's model code (`exploit_model.py`, `comp_variants.py`, `exploit.py`, `scripts/gonka_research/`, `06_code/`) was not opened. `METHODOLOGY.md` and `DATA_DICTIONARY.md` were read.

## 1. Result in one paragraph

All LP figures of the project match the chain. For every position of every LP owner (not only the sample), at all three blocks, liquidity, owner, WGNK and money agree with `lp_positions.parquet`: 544 of 544 position-state rows pass, largest difference 0.0000021 WGNK and 0.0000010 USD (tolerances 1 WGNK / 0.5 USD). Per owner, `lp_w_before`, `lp_u_before`, `lp_u_t1`, `lp_u_end` agree for 45 of 45 addresses compared, including all 10 sample owners and all 25 owners with a non-zero LP value. There is no mismatch to report. The 897 WGNK reconciliation gap stated in the methodology is explained: it is uncollected Uniswap **protocol** fees, which the project did not count; with them the pools reconcile to 0.41 WGNK and 0.33 USDT at the snapshot. One defect was found outside the position values, in the project's first release of the transaction ledger (24 liquidity transactions without a WGNK movement were absent); the project regenerated its files during this audit and the defect is not present in the current files.

## 2. Which project files were compared

The project regenerated its model while this audit was running.

| Version | Files | Modified (UTC) | Used for |
|---|---|---|---|
| first release | `model/parquet/*` as of 05:31–05:53; `tx_deltas_windows.parquet` 372,664 bytes, `variants.parquet` 424,481 bytes | 23 Nov 05:31 / 05:53 | first comparison run (06:52) and the ledger check of section 8.1 |
| current | `variants.parquet` sha256 `d1358cf3e337d2b5fd0e68e8580e1a1c0dce2597ff2ac010b31d218982d329a5`; `lp_positions.parquet` sha256 `98b0149858080aa2aac1a69ea6fac589a044dc42dab2916cdf3efa03ba76165e`; `tx_deltas_windows.parquet` sha256 `12e72dcdc382d3540a49021f697aa9421858e76e5010889c6988768c3719f56b` | 23 Nov 07:02:54–07:02:57 | final run (07:11); this is what `lp_recompute.json` contains |

`audit_package/…/03_model/` was rebuilt at 07:05:52 and is byte-identical to the current files (same sha256), so the "audit_package" block in the JSON repeats the "live" block. Between the two versions `lp_positions` did not change (`DataFrame.equals` = True) and the four LP columns of `variants` did not change for any owner; the LP comparison result is the same for both. The first-release ledger file no longer exists on disk (only `model/first_release/variants.parquet` and the register were kept).

## 3. Method

- **Source of truth: Ethereum archive state**, read with `eth_call` at block numbers 26,443,612 (snap), 26,445,519 (t1), 26,475,449 (end) through public endpoints without API keys (`gateway.tenderly.co/public/mainnet`, `eth.drpc.org`, `eth-mainnet.public.blastapi.io`, `rpc.mevblocker.io`). The rate was held below 3 requests per second inside each process; for a few minutes two processes ran at the same time. `ethereum-rpc.publicnode.com` refuses archive requests without a token and `eth.llamarpc.com` returned HTTP 525; they were not used.
- **State reads were repeated on a second provider**: 1,378 of 1,378 `eth_call` results re-read are identical. 5 later calls of the 1,383 cached were read once.
- **Discovery of positions is my own**, from chain logs (`eth_getLogs`, blocks 25,190,000–26,475,449): v3 `Mint`/`Burn`/`Collect`/`CollectProtocol` of both pools (1,170 events); NPM token ids from the receipts of every pool `Mint` whose owner is the NonfungiblePositionManager (74 mints → 66 token ids, none unmatched); v4 `Initialize` events with WGNK as either currency (25 pools) and their `ModifyLiquidity` events (236, all sent by the v4 PositionManager, so there are no direct v4 positions); ERC-6909 claims on WGNK in the PoolManager (one, 8.99 WGNK, after t1). The same logs pulled from a second provider in 10,000-block chunks give identical sets (symmetric difference 0 for all three). Against the project's export: its 511 v3 mint/burn/collect rows and 236 v4 rows are the same events (difference 0); the export does not contain `CollectProtocol`.
- **State read per block**: v3 `slot0`, `liquidity`, `feeGrowthGlobal0/1X128`, `protocolFees`, `ticks(tick)`, `positions(key)` for every (owner, range) ever minted, ERC-20 `balanceOf(pool)`; `NPM.positions(tokenId)` and `NPM.ownerOf(tokenId)`; v4 through StateView `0x7ffe42c4a5deea5b0fec41c94c136cf115597227`: `getSlot0`, `getLiquidity`, `getFeeGrowthGlobals`, `getPositionInfo`, `getFeeGrowthInside`; `PositionManager.ownerOf`; `PoolManager.protocolFeesAccrued(WGNK)`; WGNK `balanceOf(PoolManager)`; Chainlink ETH/USD `latestAnswer` (1,766.72 / 1,770.8279 / 1,729.1468).
- **Math is my own**: `TickMath.getSqrtRatioAtTick` (self-tested against the two boundary constants and against 1.0001^(tick/2) for every power-of-two tick), amounts from liquidity rounded down, fee growth inside from the two ticks' `feeGrowthOutside`, uncollected fees = L·(inside − last)/2^128, plus `tokensOwed`.
- Money valuation as in the methodology: USDT and USDC at 1, ETH inside positions at the snapshot price (1,766.72, equal to the project's bucket), other tokens (AURS, UDS) not valued.
- Owner → entity mapping (clusters) was taken from `variants.addresses`; clustering itself is outside this audit.
- The USDC address in the task text (`…d19d4a54e9eb0…`) is a typo; the data and my code use `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48`.

**Verified against chain state: all positions (v3 NFT, v3 direct, v4), all three blocks. Nothing in the comparison relies on the event export alone.**

## 4. Sample

Universe: the 25 entities of `variants.parquet` with a non-zero `lp_w_before`, `lp_u_before`, `lp_u_t1` or `lp_u_end`. Top 5 by `lp_w_before·0.1428805 + lp_u_before`; 5 more with `random.Random(20261118).sample(sorted(rest), 5)` (seed **20261118**).

| Group | Owner | Positions with value | lp_w_before (WGNK) | lp_u_before (USD) | lp_u_t1 | lp_u_end | Max abs diff vs project | Result |
|---|---|---|---|---|---|---|---|---|
| top5 | 0x244186297b43ba43c92d68efe78c04170fbc0b10 | v3: 1304610, 1304618, 1304619, 1304621, 1304626, 1304628, 1304629, 1304630, 1304639, 1304643 | 3,637,166.036619 | 146,950.554644 | 0 | 0 | 0.0000034 | match |
| top5 | 0x6c07e00cc3847b687fbde78baa184c5098116c51 | v4: 512840, 512910 (ETH/WGNK) | 332,302.890808 | 38,213.100595 | 196.255196 | 0 | 0.0000008 | match |
| top5 | 0x94f54486593069fd969737889f957b4b8be4fbfb | v3: 1357060, 1359412, 1360516 | 15.675751 | 7,003.416023 | 2.000993 | 2.000993 | 0.0000030 | match |
| top5 | 0xd9a22cd1c6f1520e51340e0a9505b9640d97fa3d | v3: 1304014 (1% pool) | 5,654.333122 | 798.961894 | 392.138015 | 358.183561 | 0.0000009 | match |
| top5 | 0x20e63816e5704a2c05f7fc7cccd056dd554d7583 | v3: 1370329; v4: 420442 | 3,405.616541 | 0.048083 | 0.368119 | 0.368119 | 0.0000004 | match |
| random5 | 0x4467aa359654154abfc0eb18e88672a1b0339d76 | v4: 517928, 517958, 517973 | 0 | 0 | 7.145576 | 6.543286 | 0.0000024 | match |
| random5 | 0x780e76c5a65a78fbeb38527ede89803b8ec917e5 | v3: 1310168 | 794.139379 | 113.578995 | 49.644038 | 38.774936 | 0.0000008 | match |
| random5 | 0x125ab0a1d919962879838e71dce989a8a87c0dda | v4: 360998, 525607, 525610 | 13.861662 | 1.277963 | 0.405181 | 11.990115 | 0.0000014 | match |
| random5 | 0x11748a7012a700e05e89e22f806fbab04f847ea0 | v4: 526614 | 0 | 0 | 0 | 56.871568 | 0.0000002 | match |
| random5 | 0x024860b646a1221a802df406f8a6acadd2c37622 (3 addresses) | v4: 491819, 518124 | 0 | 0 | 1.441709 | 0 | 0.0000010 | match |

Per-position values (liquidity, tick range, amounts, owed, fees, owner, at each block) for these and all other positions are in `lp_recompute.json` → `positions`.

## 5. Comparison with the project

- Positions found on chain: 200 (66 v3 NFTs, 84 v3 direct, 50 v4 NFTs). 89 position-state rows are non-zero.
- `lp_positions.parquet`: 217 position keys. The 17 extra keys are `npm?:…` placeholders with owner = NPM and zero liquidity, WGNK and money in all three states. They have no chain counterpart and no value.
- No position with liquidity, owed tokens or fees on chain is missing from the project list, in any state.
- Position-state rows compared: 544; pass: 544. Liquidity is equal as an integer in every row; owner is equal in every non-empty row.
- Owners compared: 45 (25 with LP value, 20 with only empty positions); pass: 45. Eight further addresses hold only empty positions and are not in `variants.parquet`.
- Totals, mine vs project: `lp_w_before` 3,982,829.673112 vs 3,982,829.673111; `lp_u_before` 193,577.386552 vs 193,577.386564; `lp_u_t1` 1,231.892026 vs 1,231.892036; `lp_u_end` 1,003.670812 vs 1,003.670824.

**Mismatches: none.**

## 6. Ownership

`ownerOf` was read at the three blocks for all 66 v3 and 50 v4 position NFTs.

- For every position that has value in any state, the owner is the same at every block at which the NFT exists and equals the owner in the project file.
- One NFT changed hands: `v4:327836`, from 0xf5e560de074e3610e7daab19d9a093b9e279bc37 (snap, t1) to 0x9df59ccf737746743b6a1789a954982926d7d0c1 (end). Its liquidity is 0 at all three blocks; nobody is credited anything for it.
- 17 (NFT, block) pairs are burned tokens (`ownerOf` reverts); all are empty.
- Not checked: transfers that happened and were reversed between two of the three blocks (only the three points were read).

## 7. Pool-level reconciliation

Sum over **all** positions of (amount from liquidity + tokens owed + uncollected LP fees) + protocol fees, versus the token balance of the pool.

| Block | Pool | WGNK balance | WGNK protocol fees | WGNK gap | USDT balance | USDT protocol fees | USDT gap |
|---|---|---|---|---|---|---|---|
| snap | v3 0.3% `0x203e…c55d` | 3,639,174.077344 | 892.889501 | 0.405888 | 154,525.071158 | 0.088121 | 0.330168 |
| snap | v3 1% `0xdbc0…f117` | 8,887.924896 | 4.200729 | 0.000257 | 838.043945 | 0.000001 | 0.000479 |
| snap | v4 PoolManager, WGNK side, 11 pools existing | 335,893.498803 | 228.331555 | 0.0000003 | not reconcilable | – | – |
| t1 | v3 0.3% | 79,370.151653 | 8,708.850356 | 16.132373 | 174.945414 | 102.199773 | 0.330613 |
| t1 | v3 1% | 22,849.402846 | 1,032.100440 | 0.005999 | 445.040339 | 12.643981 | 0.000650 |
| t1 | v4 PoolManager, WGNK side, 22 pools | 2,149,406.480131 | 2,179.341285 | 0.0000006 | not reconcilable | – | – |
| end | v3 0.3% | 79,522.959327 | 8,739.902148 | 16.132598 | 44.182947 | 0.001012 | 0.330723 |
| end | v3 1% | 32,886.374874 | 1,841.892889 | 0.006528 | 398.447554 | 0.000001 | 0.006299 |
| end | v4 PoolManager, WGNK side, 25 pools (incl. 8.993755 WGNK ERC-6909 claim) | 58,778.218006 | 2,274.447658 | 0.0000015 | not reconcilable | – | – |

Further checks, all passed:
- `pool.liquidity()` equals the sum of liquidity of in-range positions in every pool at every block (64 pool-block pairs).
- For every NPM range, the sum of liquidity of its token ids equals the pool-level NPM position (difference 0); the sums of WGNK and USDT differ by at most 0.000000004 WGNK and 0.000004 USDT.
- WGNK total supply and the three pool balances computed from `raw/eth/wgnk_transfers.parquet` equal the on-chain values at all three blocks.

**The project's stated gap ("897 WGNK and 0.42 USDT").** Both v3 pools have the protocol fee switched on (`slot0.feeProtocol` = 102). Uncollected protocol fees at the snapshot are 892.889501 + 4.200729 = 897.090230 WGNK and 0.088122 USDT. Without them my gap is 893.295389 + 4.200986 = 897.496375 WGNK and 0.418769 USDT, i.e. the project's figure. The project's positions are complete; the gap is money that belongs to the Uniswap fee recipient, not to any LP.

**Residual 0.405888 WGNK at snap, 16.132373 at t1 (0.3% pool).** Explained: transactions in which more WGNK was transferred to the pool than the pool's own events account for (overpaid swaps). Sum of these differences: 0.405886 WGNK up to the snapshot, 15.726485 between snapshot and t1 (of which 15.531902 in tx `0xf17a54563de63cf75be8352e5a6ba5e0457f75a179b1ac9cabfe56b5dbed54cf`, block 26,443,658), 0.000225 after. 0.405886 + 15.726485 = 16.132371. What is left is 0.000002–0.000003 WGNK.

**Residual 0.330168 USDT (0.3% pool), constant over the three blocks.** Not explained; USDT transfers were not pulled. Its constancy is consistent with a pre-snapshot overpayment of the same kind. Assumption, not verified.

**v4.** The PoolManager holds the tokens of all Uniswap v4 pools together, so only the WGNK side can be reconciled, and only for all WGNK pools at once. It closes to 0.0000003 WGNK. The money side (USDT, USDC, ETH) of v4 positions **could not be reconciled against a balance**. It rests on the same liquidity, price and formulas that close on the WGNK side and on the in-range liquidity check. In the ETH pools WGNK is currency1 and ETH currency0; the currency0 formula is the one validated on the v3 pools.

## 8. Blind spots

### 8.1 Liquidity operations without a WGNK movement — defect in the first release, fixed in the current files

There are 220 liquidity transactions after the snapshot (102 before the warning, 118 after).

- Against the **first-release** ledger (runs at 06:57 and 07:04 UTC, files since overwritten): 25 of the 220 were absent from `tx_deltas_windows` altogether. 24 of them move only USDT or USDC between the owner and the pool, with no WGNK transfer; 1 moves nothing. Their position-side effect (`lp_u_t1`, `lp_u_end`) was counted while the matching cash flow was not, which produced fake gains or losses. Example: 0x5ec2ea4ecfa01e864c3c115c96613e93d99adaa7 withdrew 400.166666 USDC in block 26,447,492; the first release paid it 401.00 USDC in option 3, the current release 0.833334.
- Against the **current** ledger: 219 of 220 are present and flagged `is_lp_tx`. The missing one (`0x4252b13a08721910bc8512b6e2cc5ffdf9815d181e30fa51fbe6bcc1f792cbae`, block 26,446,408, liquidityDelta 0) moves no tokens. For the 224 ledger rows of these transactions, WGNK, USDT, USDC and DAI flows recomputed from chain receipts equal the project's values (0 differences). The project's `registers/changes_vs_first_release.csv` records the correction ("liquidity operation without a WGNK movement is now counted").
- The 25 transactions absent in the first release (evidence is from my session output only, not stored in the JSON): `0xb679b99d455915fac56747c2fa4795b2b11ed125de5b6f9a98a22e4be8dd2d2e`, `0x61b148de47417a2471fde1825b330c1c3dd0fcd2693e4595c2583087dc73dd3f`, `0x60bbd7aaa5d50126d54b72a9cf43ea2600327cdbcc3ecdf11ba96251a534d420`, `0xb4991bfb069a6d2cc8f954088a450928fd385398f2373c8ee9576c3999ad02e4`, `0x6b8709eb21d02bbbaa15b4ec2cc28104d0b1d6b9865f5e7c992941dd174ddb95`, `0xcb7424eabaca04fd05022b5b40e26b5ad7276afcb59984fb16b1c792a6fd00f1`, `0xde9e9cf332d640f99f065e9c14afe6961930517a96c2b690425b4743141fc3d2`, `0xd875956aa46ac9bbc60d4aa55105c26394ebe8fe85ab2a052981d4e957cec437`, `0xeb26897efb08ecf87f7d2b3053eb25ec0864efe24128a7469c635c2f258fa52f`, `0x34a4c54f1ea2cdd46d103555c264207b6779395161aeaef1279765de6592f0ae`, `0x9913d26536868bbb0fc16bf6fea0feeab2269b11168a8a3ae3f0d43734c75f42`, `0xb5d2f8e86b441bd126cea67ec843d6638c6422497640bc4eb06a4e4f8759b01e`, `0x8fd8c1346689aa201e8e4e2bc177e11a528b63a954ad3b3b138d105602b4f87d`, `0xaaa7ca1ebc979c2177c1edf721d98f4000594176f02678fa45c33dafa6e6ebf2`, `0x70e796f7cc575c2c9bfffe01b85f3c96e6fc1f876a46a1383fa9cf1e239958a6`, `0x4252b13a08721910bc8512b6e2cc5ffdf9815d181e30fa51fbe6bcc1f792cbae`, `0xff016b38b9be6c732d577bbaccce8aa82763ac4b35792177df773d6a7de26044`, `0x3d668577ab5da69bc5a8783fd29f41684d1f9b7017698d4d306616b83968ce7f`, `0x08376dae78caeab5463b6f7fc239430453f6bdfc8a35a3dcfc67937b363d1d7a`, `0x5ee77c4ee005ecc78f65e89e8960be4d3381e6645ddc68c246a3e88b00b635f2`, `0xe5e02ec2f0479bb9dce999fb6c3006183d994e40fbd263319c19356769664349`, `0xde5460b370fc1a73477c32e09991d71ac00579245ccb3c6b8fbf51ee0ba69b00`, `0x9eb90e94185e2eae271e1d04d5fc0a928cbfc53fdd4a8ca290339f6aa3b81cc9`, `0x8954622128bd1237110efea847946d48a99cdbf98df99dd4c7cf96a078e8bca7`, `0x730a1c9bca52ec4398424c15e52e3e9509b05f7200f2c31b053816deac35a7ec`.
- Between the two releases, money payouts changed for 5 owners in option 1 and 9 in option 3 (sum of absolute changes 959.80 USD and 1,416.67 USD); part of that is a different correction (trades paid in untracked tokens).
- Anything published from the first release (register, deck) carries the old figures.

### 8.2 Liquidity removed between the snapshot and the warning

- The largest LP, 0x244186297b43ba43c92d68efe78c04170fbc0b10, removed all 10 positions in blocks 26,445,140–26,445,177, i.e. 342–379 blocks before the warning block (about 68–76 minutes at 12 s per block) and about 5 hours after the mint. It received 5,209,718.819338 WGNK and 20,519.590657 USDT. 146,950.554647 − 0 − 20,519.590657 = 126,430.963990 = the project's `net_a_usd` and its money payout. Of the WGNK withdrawn, 3,637,166.04 is its pre-hack WGNK; the remaining 1,572,552.78 is WGNK its positions bought during the dump.
- 0x6c07e00cc3847b687fbde78baa184c5098116c51 made no liquidity operation before the warning: 21.629404 ETH in its positions at the snapshot, 0.111085 ETH at t1. Its two withdrawals after the warning (0.005755 and 0.105385 ETH) equal the project's ledger rows to 1e-9 ETH (native ETH measured as balance change over the block plus gas).
- For all 25 LP owners the project's `net_a_usd` equals −Σ ledger `d_usd` (window A) + `lp_u_before` − `lp_u_t1`, and likewise for window B, to within 0.000004 USD. Combined with the verified positions and the verified LP-transaction flows, this confirms the LP contribution to M. Ledger rows of non-liquidity transactions (swaps) of these owners were **not** verified here.
- No liquidity event occurred between the start of the attack (block 26,443,607) and the snapshot. The 22,000,000 WGNK mint is in block 26,443,613.

### 8.3 Concentration

Current files, option 1: 0x244186…0b10 holds 91.3% of all LP WGNK and 75.9% of all LP money at the snapshot and receives 3,886,258.09 GNK and 126,430.96 USD — 29.8% of all GNK and 42.9% of all money paid. 0x6c07…6c51: 8.3% / 19.7% of LP value; 891,355.11 GNK and 37,208.24 USD (21.518264 ETH) — 6.8% and 12.6%. Together the two receive 55.6% of all money paid. 0x244186…0b10 owns token id 1304610, the first position ever minted in the 0.3% pool (block 25,280,147), and minted its ten positions within the next 334 blocks. Who controls the address was not established here.

### 8.4 Who holds the positions

All 26 addresses that hold a position with value are externally owned accounts: 19 plain, 7 with an EIP-7702 delegation (among them 0x244186…, 0x6c07…, 0x94f544…, 0x780e76…). No locker, vault or multisig holds LP value. The 9 contracts that minted directly on the 0.3% pool (e.g. 0x1f2f10d1c40777ae1da742455c65828ff36df387 with 64 mints, 0x672061b75f770331b0c7c2a566a9ac0a9ba331d2 with 12) have zero liquidity, owed tokens and fees at all three blocks. All 25 v4 pools have no hook contract.

### 8.5 Protocol fees are honoured to nobody

Pre-hack WGNK held as Uniswap protocol fees at the snapshot: 897.090230 (v3) + 228.331555 (v4) = 1,125.421785 WGNK (160.80 USD at p0). Check: 3,982,829.673112 (LP) + 1,125.421785 + 0.406145 (residual) = 3,983,955.501042 = the three pool balances. This WGNK is in no LP position and, pools being intermediaries, in no wallet balance of the model.

### 8.6 ETH leg valuation

ETH inside positions is valued at the snapshot price in all three states. The effect of using the price of the state instead: +0.43 and +0.02 USD (0x6c07…, t1), +0.001 and −0.03 USD (0x125ab0…). Immaterial.

### 8.7 Tokens that are not valued

`v4:328189` (0x54e40e6442d7d395d136ff34a6ea9ee788a591e6, WGNK/AURS): 40.049785 WGNK honoured at the snapshot; 105.161072 AURS on the other side is ignored, as is its change (63.013298 at t1, 15,952.178908 at end). `v4:491819` (cluster 0x024860b6…, WGNK/UDS): 1,000 UDS at the snapshot, 0 WGNK. Any loss or gain on the AURS/UDS side is outside the model.

### 8.8 Pools created after the hack

14 of the 25 v4 pools were created after the snapshot, with fees from 5% to 99.99%. Money placed in them counts as "still theirs" at t1/end. Owners with no pre-hack LP position receive in option 1: 0x33f0bbdb… 2.00 USD, 0x7c949b88… 2.00 USD, 0x5ec2ea4e… 0.83 USD; the others 0. The cluster of 0x024860b6… held 1,484,664 WGNK in a 99.88%-fee pool at t1 and receives 0.

### 8.9 Other venues

Uniswap v3 factory lookups (USDT, USDC, WETH, DAI × 4 fee tiers) and Uniswap v2 / Sushi pair lookups found two pools the project does not track: WGNK/USDT 0.05% `0xfeb94ae4574318315486a0d73d1c6cbd132b554b` (0.000000001 WGNK) and WGNK/WETH 0.3% `0xfaa8177f2041bef63bb6c4ec4dfd3e80394fd8c2` (0.0000126 WGNK). Neither had a WGNK transfer after the snapshot. Of 391 holders with at least 500 WGNK at the snapshot, 6 are contracts: the two v3 pools, the PoolManager, CoW Settlement (706.90 WGNK), 0xa1e16bc461142117207382f02f365407722bfca7 (600 WGNK) and 0xd0162a989355b507f696feec3b835f073fe092d3 (2,892.40 WGNK, classified by the project as a holder). The last one was not identified.

## 9. What could not be verified

- The money side of v4 positions against a pool balance (section 7).
- The 0.33 USDT residual of the 0.3% pool (section 7).
- NFT transfers reversed between two of the three blocks (section 6).
- The first-release ledger defect cannot be re-run: the file was overwritten; the list in 8.1 comes from two runs made before that.
- Ledger rows of swaps and other non-liquidity transactions of LP owners. WETH/ETH netting in two ledger rows of the contract 0x1f2f10d1… (blocks 26,443,787 and 26,444,681), where my ERC-20 view and the project's ETH view differ by 0.005449 and 0.041948 WETH; that contract holds no LP value.
- `v4:328189` was increased after the warning by 22,720.987579 WGNK sent by 0x9df59ccf737746743b6a1789a954982926d7d0c1 (tx `0x50a2f0ab4cb6bfb883636f87a5e60d96f0665874c6316b470b779b46baafbd0c`, block 26,457,878), which is not the NFT owner (0x54e40e64…). The 18,880.23 WGNK at the end is listed under the NFT owner. It does not enter any payout field checked here; how the model treats the depositor (its `net_b_usd` is 350.19) was not examined.
- Address clustering, the identity of owners, the choice of blocks and p0 are inputs taken as given.
- The project files may be regenerated again; the comparison holds for the sha256 values in section 2.

## 10. Reproduce

```
docker run --rm -i \
  -v <data-dir>:/research:ro \
  -v <work-dir>:/work -w /work \
  <python-image> python /work/lp_recompute.py
```

Stages: `fetch`, `verify`, `compute` (default: all). All network answers are cached in `cache/rpc_cache.sqlite`; with the cache present a re-run makes no requests. Without the cache a full run is about 3,500 requests (roughly 25 minutes).
