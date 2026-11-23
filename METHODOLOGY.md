**English** | [Русский](METHODOLOGY.ru.md)

> [!IMPORTANT]
> **Draft for community discussion — not an official position of Gonka or its Core Team.** Published by Sergey Konyakov
> ([@Konyakoff](https://github.com/Konyakoff)), a community member. The research was done with Claude Code (Fable 5.2); the
> author has not yet independently verified every address and amount. Community members and the Core Team are asked to
> re-check the logic of the calculation and the listed addresses and amounts. A shared position on compensation is to be
> reached through discussion.

# Methodology — compensation after the WGNK bridge hack (18 Nov 2026)

Version of 23 Nov 2026. All times are UTC. All amounts are computed from on-chain data (`data/raw/`) by the code in
`code/`; nothing is entered by hand. The weak points of this method are listed in [`CRITIQUE.md`](CRITIQUE.md). No paid AI services were used for the calculation.

## 1. Principles

1. **What was yours before the hack is yours.** WGNK held at the last block before the unbacked mint is honoured one for one
   (native GNK, or new WGNK at the holder's choice).
2. **Lost money is returned in the same currency.** USDT for USDT, USDC for USDC, ETH for ETH — the amount actually lost,
   net of what was received.
3. **Payouts let nobody profit.** Gains are always deducted; WGNK bought after the hack are voided; the attacker gets nothing.
4. **One dividing line.** Up to the project's explicit official warning the project commits to make losses whole; after it,
   compensation is the community's goodwill and three options are offered.

## 2. Moments and windows

| Name | Moment | Ethereum block | Meaning |
|---|---|---|---|
| T0 | 18 Nov 2026 18:00:59 | 26,443,607 | attack starts: the attacker submits the epoch-462 group key to the bridge |
| snapshot | 18 Nov 2026 18:01:59 | 26,443,612 (end of block) | last block before the 22,000,000 unbacked WGNK were minted; balances "B0" |
| T1 | 19 Nov 2026 00:24:07 | 26,445,519 (last block with time ≤ T1; its time is 00:23:59) | official X post "Do not trade WGNK" (post id 2123210678211318257 → 00:24:07.689) |
| T2 | 23 Nov 2026 04:30:00 | 26,475,449 | data freeze; later transactions count in no option |

- **Window A** = blocks 26,443,607 … 26,445,519 (commitment).
- **Window B** = blocks 26,445,520 … 26,475,449 (goodwill).
- Pre-hack price **p0 = 0.142881 USD per WGNK**: volume-weighted price of all 118 swaps in the four tracked WGNK/USDT pools
  during the 24 hours before T0 (36,124.39 USD / 252,829.34 WGNK).

## 3. Who is an owner

- Balances come from the complete log of WGNK `Transfer` events (`wgnk_transfers`). Check: the sum of balances equals the
  contract's `totalSupply` at the snapshot and at T2 to the last unit.
- In every transaction of windows A and B the **owner** is the address whose WGNK balance changed by at least 1 WGNK
  (dust threshold ≈ 0.14 USD), not the transaction sender. Pools, the v4 PoolManager, the bridge contract, WETH and known
  routers/settlement contracts (Uniswap routers, 1inch, CoW Settlement, UniswapX reactor, Permit2…) are intermediaries.
- **Third-party settlement.** If, in one transaction, an address received (gave) WGNK with no money leg while another
  address with a one-sided money flow and no WGNK change paid (received) money, the money is attributed to the address
  whose WGNK changed, pro rata by WGNK. This covers CoW Swap ETH-flow, relayers/solvers and purchases "to another wallet".
  Pools, addresses moving other tokens in that transaction and block builders are excluded. Rows are flagged
  `via_third_party`. (Added after the independent check found the gap.)
- **Clusters.** Addresses linked by a plain WGNK transfer after T0 (no money in the transaction) are treated as one owner,
  except hubs with more than three counterparties. Otherwise a holder could keep full B0 on one address and sell from another.
  The owner's payout is then **split by address**: GNK goes to the address(es) that held the pre-hack WGNK (pro rata), each
  currency goes to the address(es) that paid it (pro rata by that address's net outlay in the currency); amounts below the
  payout threshold are moved to the group's main address. The owner's total is unchanged (`payee_split_max_diff` in the checks).
- **Trades paid in other tokens.** If an address bought (sold) WGNK and paid (received) a token outside the tracked set in
  the same transaction, the money leg is taken from the WGNK pool swap of that transaction (USD value of the pool trade,
  pro rata by WGNK) and counted in USDT. Rows are flagged `valued_by_pool_leg`.
- **Liquidity positions.** Uniswap v3 positions (direct owners and position NFTs) and all 25 Uniswap v4 pools containing
  WGNK. The owner is the NFT holder (or the owning contract). Position content is computed with concentrated-liquidity
  formulas at the snapshot, T1 and T2, plus owed tokens and uncollected fees read from contract state. Check: positions
  add up to the pool's token balances at the snapshot (gap 897 WGNK and 0.42 USDT on 3.65M WGNK and 155k USDT).

## 4. Money

Per transaction and owner: net change of USDT, USDC, DAI, WETH and native ETH (transaction value + internal transfers).
WETH and ETH are one currency. USD value: stablecoins at 1; ETH at the Chainlink ETH/USD price in the block of the trade
(25-block buckets). Liquidity positions: money in the position at the snapshot counts as "already put in", money still in the
position at the end of a window counts as "still theirs"; ETH inside positions is valued at the snapshot price.

## 5. Formula

For an owner let
- `H` = pre-hack WGNK = wallet balance at the snapshot + WGNK in liquidity positions at the snapshot + WGNK burned before the
  hack but not yet delivered by the bridge;
- `M_A` = money spent − money received for WGNK in window A (incl. liquidity operations and the position change snapshot→T1);
- `M_B` = the same for window B (position change T1→T2);
- `G` = native GNK already delivered by the bridge for burns after T0 (only the attacker has this).

Window B enters with a share `phi`:
- if `M_B ≤ 0` (a gain): `phi = 1` in every option — gains are always deducted;
- if `M_B > 0` (a loss): `phi = 0` (option 1), `phi = k` (option 2), `phi = 1` (option 3).

`M = M_A + phi · M_B` (applied per currency: each currency's window-B quantity is multiplied by `phi`).

- If `M > 0`: every currency with a positive net outlay is refunded **in kind**, scaled so that the total equals `M`
  (currencies in which the owner is net positive are offset proportionally); `GNK = max(0, H − G)`.
- If `M ≤ 0`: no money; `GNK = max(0, H + M / p0 − G)`.

The attacker and linked addresses receive 0. Payouts below 0.5 GNK and 0.01 USD are not listed.

## 6. Option 2 — the ladder K(t)

`k` = average K(t) over the owner's window-B transactions with a money outlay, weighted by the outlay; for a loss on a
liquidity position after T1 the volume-weighted K of all pool swaps in window B is used (0.220).

| Until (UTC) | K | Notice event |
|---|---|---|
| 19 Nov 01:35:41 | 1/2 | the warning exists on X only; at 01:35:41 it is repeated in the press (TokenPost) |
| 19 Nov 12:03:00 | 1/4 | the warning is in the press; the banner on the project's website is confirmed "no later than" 12:03 |
| 20 Nov 00:24:07 | 1/8 | the warning is on every official channel; one full day in every time zone |
| later | 0 | |

The fractions are a policy choice within a legally recognised form (see `legal/LEGAL_RESEARCH.md`).
Sensitivity variants in `model/summary_three_options.json`: `v0_ignore_b` (window B ignored entirely, including gains),
`v2_exp` (smooth half-life of one hour), `v2_ladder10` (½, ¼, 10%), `v2_ladder0913` (boundaries +1 h / 09:13:37 / +24 h).
The total protocol top-up moves by at most about 2,500 USD between them.

## 7. Categories (by activity in window A)

`holder` (held, no trades) · `holder_sold` (held, only sold) · `holder_traded` (held and bought) · `buyer` (no pre-hack WGNK,
only bought) · `trader_loss` / `trader_profit` (no pre-hack WGNK, bought and sold) · `lp` (liquidity provider) · `b_only`
(active only after the warning) · `transfers` (no money trades) · `hacker`.

## 8. Bridge reserve

The attacker withdrew 884,150.874884 USDT and 647.736653 USDC from the bridge contract. On Gonka these back CW20 "wrapped"
USDT/USDC held by 18 addresses (balances read from contract state before the attack and now; totals reconcile with the
stolen reserve; 0.01 USDT is an unpaid withdrawal from 13 Jun 2026). In every option the reserve is restored in the new
bridge; nothing is sent to these addresses.

## 8a. Bridge requests in flight (GNK → WGNK never minted)

A successful `MsgRequestBridgeMint` on Gonka locks the sender's GNK in the bridge escrow; the sender then mints WGNK on
Ethereum with the bridge signature. 47 successful requests (1,509.96 GNK, 33 senders; 8 of them, 33.9 GNK, made after the
attack) have no matching WGNK mint: every one of the 1,448 genuine mints is matched to a request (same destination and
amount), these 47 are what remains. Their GNK is still locked; in every option it is returned to the sender on Gonka
(`registers/bridge_requests_in_flight.csv`, section 4 of the PDF register). The escrow arithmetic explains 1,216 of the
1,476 GNK requested before the attack; the status of each request must be confirmed against the bridge module before payout.

## 9. Sources of funds and protocol top-up

Returned by the attacker: 593.435 ETH to the bridge admin Safe `0x1d806d0e…1768` (2-of-3) and 12,900,401.0037 GNK to the
community pool (two `MsgFundCommunityPool` transactions). **Left in the bridge escrow:** 98,276.76 GNK — the attacker took
13,000,000 of 13,098,243 GNK; the remainder backs the same holders and is counted as a source. Needs: GNK to holders; USDT/USDC/DAI/ETH to people; the bridge
reserve; gas. Stablecoins are assumed to be bought with the returned ETH at the price at calculation time
(1,729.15 USD/ETH, Chainlink, 23 Nov 2026). **Protocol top-up** = (GNK needed − GNK returned − GNK left in the bridge escrow) · p0 +
(ETH needed − ETH returned) · ETH price. GNK needed = payouts to owners + bridge requests in flight (section 8a). A ±10% move in ETH changes the top-up by roughly ∓100,000 USD, because the 884,799 USD reserve is
repaid out of ETH; converting right after the decision removes this exposure.

## 10. Checks (all in `model/`)

- WGNK supply from the transfer log = `totalSupply` at the snapshot and at T2 (difference < 1e-8).
- Liquidity positions = pool balances at the snapshot (see section 3).
- For every owner and option: GNK payout equals the formula; money is paid only when `M > 0`.
- Option 1 ≤ option 2 ≤ option 3 for every owner; owners without window-B activity get identical payouts in all options.
- Gonka address derived from the Ethereum public key equals the owner recorded by the bridge in 1,154 of 1,154 burns.
- Independent recomputation from raw data by a separate reviewer (see `reviews/non_lp_recompute/`).
- Self-audit: `CRITIQUE.md`, `model/critique.json` — checks for address groups and off-exchange deals, supply reconciliation, bridge requests in
  flight, profit kept, concentration, cut-off sensitivity, pending bridge claims, p0 and ETH sensitivity; an independent
  recomputation of liquidity positions and an adversarial review of the draft by two separate reviewers (`reviews/`).

## 11. Limitations

- Purchases paid in tokens other than USDT/USDC/DAI/ETH are valued by the WGNK pool leg of the same transaction and refunded
  in USDT; slippage and fees on the hops before the pool are not refunded.
- Uncollected fees of v4 positions and the ETH leg inside positions are approximated; the reconciliation gap is shown above.
- Address ownership was not established; clustering uses on-chain transfers only. An objection window is proposed.
- Trading in pools not containing WGNK directly (e.g. derivative venues) is out of scope; none was found.
- Discord announcements of the project could not be checked; an earlier explicit warning there would move T1 earlier.
- The ETH price used for the top-up is a snapshot; the final figure depends on the conversion date.
