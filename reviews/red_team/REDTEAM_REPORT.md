# Red-team review of the Gonka bridge compensation package

Date: 23 Nov 2026. Scope: only the published package `Gonka_Bridge_Incident_Audit_Package` (no internet, no other data).
All figures are for **option 1** unless stated; USD values use the package's own conventions (GNK at p0 = 0.1428805 USD,
ETH at 1,729.1468 USD). Option-1 totals reproduced from the package: 938 recipients, 13,032,412.99 GNK, 212,449.19 USDT,
21,879.18 USDC, 26.89 DAI, 34.1621 ETH, value 2,155,504.46 USD, of which money 293,426.47 USD; stated protocol top-up
170,952.43 USD.

Classes: **(a)** provable calculation/register error; **(b)** well-founded suspicion that the package's data cannot settle;
**(c)** policy choice that should be disclosed (including places where the stated principles are contradicted by the data).

"Verified" below means recomputed by my scripts from the package files; "inferred" is marked as such.

## Summary table (ordered by materiality)

| # | Finding | Class | Owners | Key number |
|---|---|---|---|---|
| 1 | One recipient gets 31.6% of all value and 43.1% of all money; with two addresses funded from the same bridge-in, 34.9%. Relationship to the project is not disclosed | b / c | 1 (3) | 681,701.56 USD (751,841.60 USD) |
| 2 | Window A refunds mostly go to people who bought after the hack was public and at crash prices | c | 150 | 106,568.68 USD of 120,893.37 USD non-LP refunds |
| 3 | "Nobody profits from the hack" is contradicted: trading gains are kept | c | 142 | 96,428.58 USD kept (56.4% of the top-up) |
| 4 | Post-hack bridge burns are "voided" only on paper; refunded buyers hold queued burns and voided tokens | b | 41 (24 refunded) | 1,280,942.81 WGNK queued = 183,021.78 USD at p0 |
| 5 | Sources of funds omit the GNK still in the bridge escrow; top-up overstated. ETH held unconverted | a (+c) | — | 13,863.17 USD overstated; 45,657.23 USD ETH price loss |
| 6 | For address clusters the register pays the alphabetically smallest address, not the address that held the tokens or paid the money | a / b | 11 + 11 | 246,997.84 GNK (35,291.18 USD) + 16,545.74 USD |
| 7 | Bridge-ins in flight (GNK locked on Gonka, WGNK never minted) are not in the register | b | unknown | 1,250.46 GNK proven; up to 139,543.94 GNK unexplained |
| 8 | Third-party settlement: refund currency and payee are assumptions | b | 78 | 8,318.05 USD |
| 9 | Window-B netting lets sale proceeds go undeducted | c | 22 | 2,606.39 USD |
| 10 | Money-only Uniswap v4 liquidity operations are invisible to the model | a | 2 proven | 400.17 USD (option 3), 88.07 USD (option 2), 6.09 USD (all) |
| 11 | "Pending pre-hack burns" are mostly months-old stuck bridge records | c | 4 | 5,007.03 GNK (715.41 USD) |
| 12 | Undeliverable / unassigned amounts; EOA-vs-contract status unreliable | c | 149 | 115,899.71 USD needs claims |
| 13 | Option 1 ≤ 2 ≤ 3 is false for one owner | a | 1 | 0.24 USD |
| 14 | Purchases paid in untracked tokens (confirmed small) | c | 14 | ≈1,842 USD |

---

## 1. One recipient receives 31.6% of everything; related-party status is not disclosed

**Claim.** The proposal is presented as compensation of ~940 community members, but payouts are extremely concentrated in
one liquidity provider whose on-chain history points to the party that seeded the market. The package never says whether
this address belongs to the project, its foundation or a contracted market maker. The whole liquidity-provider block was
also outside the previous independent check.

**Evidence (verified).**
- `0x244186297b43ba43c92d68efe78c04170fbc0b10`: 3,886,258.09 GNK + 126,430.96 USDT = 681,701.56 USD = **31.63%** of total value,
  **43.09%** of all money, **59.51%** of all USDT, 29.82% of all GNK. Its USDT alone equals 73.96% of the stated protocol top-up.
- It made the first liquidity event of the main 0.3% pool (2026-06-09 13:23:59 UTC) and seeded it the same day with
  475,000 USDT and 2,253,256 WGNK in 10 mints; at the snapshot it owned 3,637,166.04 of the pool's 3,639,174.08 WGNK (99.94%)
  and 146,950.55 of 154,525.07 USDT (95.1%).
- Its WGNK came from `0xbd3ca5a43f72e45faf4b142832110842113dc9f8` (2,500,100 WGNK on 2026-06-09), which received 3,001,000 WGNK
  minted on 2026-06-09 08:25–08:33 UTC for Gonka signer `gonka1gyy3nmdmh7cerfe39suze5uqutyq35xfx0399r` — the largest bridger
  ever (15.37% of all GNK requested through the bridge). `0xbd3ca5a4…` itself is recipient #8 (290,800 GNK, 41,549.66 USD) and
  also funded `0xdf9f1857b655263c2e8669e7e57a8e4fa57115db` (200,100 GNK, 28,590.39 USD). These three addresses together:
  4,377,158.09 GNK + 126,430.96 USDT = **751,841.60 USD = 34.88%** of total value.
- It removed all ten positions between 23:08:11 and 23:15:35 UTC on 18 Nov (txs
  `0x4b7ddcd84feb0ffa2f1760c6e7358358491c934c63214134a754d9a22bed813f` … `0xfcfbc8dae928b6747036294137dd16437b851b49b0a0c748b683a97d1d09377d`),
  i.e. 63–70 minutes **before** the project's first public statement (00:18:28) and its call to withdraw liquidity (00:24:07).
- Second largest: `0x6c07e00cc3847b687fbde78baa184c5098116c51`, 891,355.11 GNK + 21.5183 ETH = 164,565.52 USD (7.63%; 62.99% of all ETH
  refunds). It was the sole LP of the WGNK/ETH v4 pool, opened its positions on 13 Nov (5 days before the hack) and bridged in
  another 528,168 GNK at 15:29–15:30 UTC on 18 Nov, 2.5 hours before the hack.
- Concentration: top 5 owners 50.56%, top 10 60.30%, top 20 70.60% of value. 33 owners with liquidity positions: 858,555.28 USD
  (39.83% of value) and 172,533.10 USD (58.80% of money).
- The previous independent check excluded all LP owners (`05_independent_check/REPORT.md` §5.6).

**What I could and could not verify.** The arithmetic of the largest position is right: I recomputed all 501 v3
position-states from liquidity, ticks and pool price (max difference 0) and the 20,519.59 USDT it withdrew. Affiliation
with the project is **inferred** from the pattern (first LP, single funding source, early exit); the package cannot settle it.
For `0x6c07…` the timing is a coincidence I cannot interpret; its v4 amounts were not independently recomputed by me.

**Materiality.** 681,701.56 USD (31.6%) for one address; 751,841.60 USD (34.9%) for the funding group; 39.8% for all LPs.

**Remedy.** Disclose whether the top recipients are related parties (team, foundation, treasury, paid market maker) and, if so,
show the totals with and without them: the "community" cost and the "1.04% of the community pool" framing change materially.
Extend the independent check to LP owners, including v4. Ask `0x6c07…` for identity confirmation before paying 21.5 ETH.

## 2. Window A refunds go mostly to buyers who traded after the hack was public, at crash prices

**Claim.** The methodology treats everyone who bought before the official warning (00:24:07 UTC, 6 h 22 min after the mint) as
having traded blind. The data show the opposite: the hack was public from 18:28:27 UTC (Blockaid), in the press from 18:43:22,
and nobody bought at anything near the pre-hack price.

**Evidence (verified; my re-implementation of option 1 reproduces the package for all 1,258 owners without LP fields, max diff 0).**
- Non-LP owners with a money refund: 150, total 120,893.37 USD. If the commitment line were the first public alert
  (18:28:27 UTC) instead of the official warning: 51 owners, 14,324.70 USD — a difference of **106,568.68 USD (88.2%)**.
  At the first press article (18:43:22): −85,787.57 USD; at T0 + 1 h: −47,022.58 USD; at The Defiant's "unbacked" article
  (22:24:25): −1,080.09 USD. Moving the line later costs little (+558.42 USD at +1 h). Table: `sensitivity_cutoff.csv`.
- 100 of the 150 refunded owners made **all** their purchases after the Blockaid alert (refunds 54,986.06 USD).
- Gross window-A purchases: 210,250.72 USD by 280 owners. 209,654.42 USD (99.72%) was spent at less than half of p0; the
  highest post-mint price paid was 0.98·p0 (596.30 USD in total at ≥0.8·p0). Before the alert the average price was 3.9% of p0
  (53,463.44 USD for 9,525,950 WGNK); between the alert and 22:24 it was 22.0% of p0 (154,783.92 USD).
- 24 owners who get money back (32,432.99 USD) also **burned 740,934.21 purchased WGNK into the bridge** after the hack, i.e.
  tried to turn unbacked tokens bought at 6–22% of p0 into native GNK one for one — the same extraction path the attacker used.
  Examples: `0x4422bfd3397300c853add791cb1eb3b922292cc2` (refund 2,100.00 USD, average price 0.091·p0, burned 162,247.77 WGNK);
  `0x3e8cb56202748d0d9f61ac10241294bf8e371b24` (refund 2,870.00 USD, burned 150,000 WGNK);
  `0x967db5dd618088a300bcb2c742dee3b1150c601c` (refund 18,858.85 USD; bought 53,965.85 WGNK for 500 USDT at 18:17:59 in tx
  `0x46343903e9e69a901e712a72ddd75b8f93d01967219e6d47d42b838e2e4e289d`, another 424,643.94 WGNK for 5,957.06 USDT at 18:29:47,
  80 seconds after the alert, in tx `0x8d8cc171e092b0ce5ababecd941745eeee05c327dd699c7a64a8d0a62c2c119c`, then started test burns
  at 19:03:23, tx `0x27958d3d2e4db144db9b9b87d485417290b44d13de821536d928f44641fcb379`).
- Two addresses were not merged by the cluster rule because the receiving address had four senders ("hub"):
  `0xd46223b86687774ce138d964702852cea8612e33` collected 205,697.23 WGNK from four refunded buyers (refunds 3,135.75 USD) and
  burned 215,955 WGNK into the bridge.

**Who is affected.** The community pays; 150 buyers benefit. People who bought a token that had just fallen 75–99% get a
risk-free round trip, while a holder who did nothing gets exactly the same as before.

**Materiality.** Up to 106,568.68 USD (36.3% of all money refunds, 62.3% of the top-up) depends on this single choice.

**Remedy.** Disclose the sensitivity table; put the "after the first public alert" tranche to the vote as a separate item (as
is already done for window B), or apply the option-2 ladder from the Blockaid alert; exclude from money refunds WGNK that the
buyer burned into the bridge after the hack.

## 3. "Nobody profits from the hack" is not true in the data

**Claim.** Principle 3 ("Gains are always deducted") only holds for owners who had pre-hack WGNK to deduct from. Everyone
else keeps their gains, and the protocol effectively finances them by refunding their counterparties.

**Evidence (verified).** For 142 owners the formula value `H·p0 + M` is negative and is floored at zero: together they keep
**96,428.58 USD** (16 owners above 1,000 USD; top 10 keep 74,689.72 USD). By category: trader_profit 67,929.58 USD (105 owners),
lp 14,885.62 USD (13), holder_traded 12,964.93 USD (6). Only 62,510.31 GNK (8,931.40 USD) of gains is actually deducted, from 20
owners. Money refunds total 293,426.47 USD while the attacker's own WGNK sales brought 188,343.16 USD: the gap is what
others took out.
- Largest: `0x282b84f2c5b7effa51fe02169c8d48ac13257635` / `0x94fe33075ccda7a456f948828a14e7b7c0707b9b`: bought 4,169,185 WGNK for
  6,000.00 USD (1% of p0), sold 3,669,185 for 29,260.46 USD, keeps 23,260.46 USD, and burned the remaining 500,000 WGNK into
  the bridge. In tx `0x8d8cc171…` it received 3,405.64 USDC for tokens the buyer paid 5,957.06 USDT for (refunded in full); a
  filler kept the difference.
- `0xb2bd9cb06312f0a718773d26e57b938301e315c6` keeps 10,079.27 USD; `0x024860b646a1221a802df406f8a6acadd2c37622` 9,943.80 USD
  (plus 71 sales of 172,987.22 WGNK for 2,787.88 units of an untracked 18-decimal token, about 2,817 USD at the pool price, not
  counted at all);
  `0x39c5b83450f319e5c970d5fd42f7131f203fc2fc` 8,634.33 USD; `0x95fcd56e7df3f4eaf42cc885044feec082771c9a` 8,364.87 USD.
- The EN deck (slide 7) says "Those who traded at a profit made $67K: not compensated and not clawed back" and still closes
  with "Nobody loses. Nobody profits." The 67K figure covers one category only.

**Materiality.** 96,428.58 USD, 56.4% of the stated protocol top-up. List: `profit_keepers.csv`.

**Remedy.** Drop the "nobody profits" wording or state the number (96.4K USD, 142 owners) next to it; publish the list; make
sure none of these addresses receives anything through a related address (see finding 6) and that their queued bridge burns
(537,967.99 WGNK, 9 owners) are cancelled (finding 4).

## 4. Post-hack burns and "voided" tokens are voided only on paper

**Claim.** The method treats WGNK bought after the hack and WGNK burned into the bridge after the hack as void. On chain
they are not: the burns sit in Gonka's bridge queue and the tokens still trade. The package describes no mechanism that
cancels them, so refunded owners can be paid twice.

**Evidence (verified).** 72 bridge records with status `BRIDGE_PENDING` and Ethereum block ≥ 26,443,607: 1,280,942.81 WGNK from
41 owners (`posthack_burners.csv`) = 183,021.78 USD at p0 if they were ever completed. 29 of these owners are paid in option 1;
24 of them receive money refunds (32,432.99 USD) and hold 740,934.21 WGNK of queued burns. The escrow still holds 98,276.76 GNK
that a resumed bridge could pay out. At the freeze, non-attacker wallets held 20,630,541.81 old WGNK; owners who receive money refunds
hold 11,663,826.96 of them, 9,809,250.82 more than before the hack; sales after T2 "count in no option". Liquidity still available to sell into at T2: 698.30 USDT +
303.80 USDC (1,003.67 USD priced) — so the trading leak is small today; the queue is the real exposure.

**Class.** (b): whether a double payment happens depends on governance actions outside the package.

**Remedy.** Make cancellation of all post-hack `BRIDGE_PENDING` records and the freezing/replacement of the old WGNK contract
explicit preconditions of any payout; state what happens to trades after T2.

## 5. The protocol top-up is overstated: the escrow is left out; ETH was not converted

**Claim.** §9 of the methodology counts only what the attacker returned. The bridge escrow on Gonka still holds real GNK that
backed pre-hack WGNK and is not counted as a source.

**Evidence (verified from `gonka_chain.json` → `escrow.now`, `bridge_mint_requests_gonka`, transfer log).** Escrow now:
98,276.762424 GNK. Reconstruction: 98,276.762424 + 13,000,000 (delivered to the attacker) − 33.9 (requests locked after the
hack) = 13,098,242.862424 GNK before the hack (the deck quotes 13,098,243). Liabilities then: supply 13,090,977.714566 +
pending pre-hack burns 6,048.587858 = 13,097,026.302424; excess 1,216.56 GNK (finding 7). Hence 98,276.76 − 33.9 − 1,216.56 =
**97,026.30 GNK** in escrow is available for the register's needs. The package states a GNK gap of 132,011.99 GNK; with the
escrow it is 34,985.69 GNK. Top-up overstated by 97,026.30 × p0 = **13,863.17 USD (8.1%)**; corrected option-1 top-up
157,089.26 USD.

Separately (c): the returned 593.435 ETH was worth 1,806.084 USD/ETH at return and 1,729.1468 at calculation: 45,657.23 USD of
value was lost by holding ETH while 884,798.61 USD of liabilities are in stablecoins. The package discloses the ±10% sensitivity
but not that this loss has already happened.

**Remedy.** Add the escrow to the sources; convert the stablecoin part immediately; show the top-up with both corrections.

## 6. Clusters are paid at the alphabetically smallest address, and the cluster rule has no safeguards

**Claim.** When addresses are merged, the owner key is the smallest address in sort order (`parent[max(ra, rb)] = min(ra, rb)`
in `plain_clusters`), and "GNK go to the Gonka address of the same key" (deck, slide 10). The key is often not the address that
held the pre-hack tokens or paid the money. Entitlement for pre-hack holdings is thereby moved by a transfer made after the hack.

**Evidence (verified; `cluster_key_vs_holder.csv`).** 45 clusters (102 addresses). In 11 of them, **246,997.84 GNK (35,291.18 USD)**
of the payout corresponds to pre-hack balances held on a non-key address. In 11 clusters money refunds totalling 16,545.74 USD
are keyed to an address that did not pay. Worst cases:
- Owner `0x3bf3d3edf01b3b32c6da935ceee20df24e918a8d` (status "no outgoing tx — claim needed", pre-hack balance 0): 13,042.07 GNK.
  The tokens were held by `0x81f53aaa1558e9514bdbefbfebd8a34e74afa40a`, which moved them **after the warning** (1 WGNK test in tx
  `0xc9b1843c9072c2267c7df58a6b61fab0f8d466fe9713182ee01b2b0c2d5cd7c9`, block 26,446,020, then 13,041.07). The holder's key is known
  (it signed), the listed payee's is not. If the recipient is a buyer, an exchange or a phishing address, it gets the holder's GNK.
- Owner `0x9491d9bf3f3390f5077ec864f41eee8f6e94feac` (never signed, received 67.12 WGNK in tx
  `0x4e77646b3248e557718d3d08936c99da5f1b2365d556a8af639cee5f30dd4c7c`): 14,077.65 GNK that were held by
  `0xd3224e0d7a1fd685a19ebd9c37bd3dfe78587692`, which after the hack sent small amounts to three different addresses.
- Owner `0x2568db3570323e2fe8816d40b738a770ad195733` (pre-hack balance 0): 50,068.70 GNK held by `0xefdffcb9…bc75`.
  Owner `0x2c209bdf…9cc4`: 150,000 of 200,090 GNK were on two other addresses.

Rule weaknesses (verified in code and data): an edge needs no minimum amount (two addresses were merged on 0.123457 WGNK, tx
`0x6864d6eb70f03556fc967be97803c99fed73fd3a36ea1bda21a5bb29c22d6810`; four clusters exist only because of transfers of 14.4 WGNK or less); direction is
ignored, so anyone could attach a profitable address to a holder by sending dust and cut the holder's GNK (in the data the
largest cut caused by merging is 668.46 USD for `0x34b9a31c…d99f`, where the holder itself sent 10 WGNK, tx `0xe4a7a438…71a4`); the "more than three
counterparties" exemption is trivially reachable (finding 2, hub). Net effect of clustering on totals is small: 858.96 USD.

**Class.** (a) for the register (payee ≠ holder is provable); (b) for harm (depends on who controls the addresses).

**Remedy.** Pay GNK to the address that held the tokens at the snapshot and money to the address that paid, per address;
use clusters only to net gains against holdings; require a minimum amount and the holder's signature for merges.

## 7. Bridge-ins in flight are missing from the register

**Claim.** People who had locked GNK on Gonka for a mint that never happened have a real loss and are not in the register,
which is built only from Ethereum balances.

**Evidence.** Verified: the escrow arithmetic in finding 5 leaves exactly 1,216.56 GNK locked before the hack beyond WGNK
supply and pending burns, plus 33.9 GNK locked by 8 requests after the hack (2.5 GNK in 7 requests
for `0x0176cce6…6d02` at 02:44–03:53 UTC on 19 Nov; 31.4 GNK at 11:50 UTC, Gonka tx `22134787BF45…5F69`): **1,250.46 GNK (178.67 USD)**.
Not settled: matching all 1,504 `MsgRequestBridgeMint` records to the 1,451 mints by destination and amount leaves 54
requests without a mint, 139,543.94 GNK in total (46 before the hack: 139,510.04 GNK), e.g. three requests of
`gonka1ad7al35f74hdlwl5vzmqla4gg3zlajthqsyeva` for 105,980.47 GNK to `0x40532476f722594ffa6a6e209aa7945e7b6fddb5` (14–18 Oct),
20,226 GNK to `0x8dcea22381c00d75299b93f14e99b9684d6de097` (8 Nov) and 10,000 GNK to `0x85de1523…3641` (10 Nov). The escrow total
implies most of these did not leave GNK locked (failed or refunded), but the package does not show their status, and it does
not say which requests the 1,216.56 GNK belong to. List: `gonka_mint_requests_not_minted.csv`.

**Remedy.** Publish the on-chain status of every unmatched request; return locked GNK to the Gonka signer.

## 8. Third-party settlement: currency and payee are assumed

274 rows, 78 owners: purchases 8,318.05 USD and sales 1,734.97 USD are attributed from another address in the same
transaction (arithmetic verified for every row). The payers are solver/relayer inventories: `0x754dcfb2861547015b221e963b4133a71dbdc024`
(3,291.23 USD), `0xf70da97812cb96acdf810712aa562db8dfa3dbef` (2,225.01 USD), CoW ETH-flow `0xba3cb449…adec` (857.58 USD). What the
user actually paid, in which currency and on which chain, is not in the data; the refund goes to the WGNK recipient in the
solver's currency (example tx `0x001b67abf3bd1e38b4c6511911fcd93eecef4d3c23d49338dbf8a8716293f6a7`). The same rule would
mis-attribute money in batched transactions that combine unrelated operations. Class (b). Remedy: pay these only against a
signed claim that shows the paying leg.

## 9. Window-B netting leaves sale proceeds undeducted

By the formula, a net window-B loss is ignored in option 1 **together with the sales inside it**. 22 owners with a net B loss
received 2,606.39 USD in window B; 4 of them also get window-A refunds and their 1,317.22 USD of proceeds is not deducted
(largest: `0xd0162a989355b507f696feec3b835f073fe092d3`, received 1,279.82 USD in B, refund 113.81 USD plus 2,892.40 GNK). This is
what the formula says, but it contradicts "gains are always deducted". Class (c), immaterial. List: `window_b_netting.csv`.

## 10. Money-only Uniswap v4 liquidity operations are not scanned

The transaction set is built from WGNK `Transfer` logs, so a liquidity add or removal that moves only USDT/USDC is missing:
25 of 162 post-hack v4 `ModifyLiquidity` events (13 with a liquidity change) are in transactions absent from
`post_receipts` (`v4_events_not_scanned.csv`). Provable effects:
- `0x5ec2ea4ecfa01e864c3c115c96613e93d99adaa7` added 400 USDC below the price at block 26,443,661 and removed it at block
  26,447,492 (tx `0xff016b38b9be6c732d577bbaccce8aa82763ac4b35792177df773d6a7de26044`, no WGNK moved; liquidity maths gives
  400.02 USDC). The model sees 400.17 USDC "in the position at T1, gone at T2" and books a loss: option 3 pays 401.00 USDC,
  option 2 pays 88.90, for money the owner withdrew himself.
- `0x4467aa359654154abfc0eb18e88672a1b0339d76`: a 6.09 USDT withdrawal (tx `0xd875956a…c437`) is unseen; payout 8.22 USD in all options.
- The reverse also occurs (money-only adds by `0xfad497df…3039`, 66.48 USDC, unseen), understating outlays.

Class (a), small: 400.17 USD in option 3. Remedy: collect transactions by pool/PositionManager events, not only by WGNK transfers.

## 11. "Burned before the hack, not yet delivered" is mostly old stuck records

Of 6,048.59 WGNK counted as pending pre-hack burns (8 records), only 1,041.56 is from the day of the hack (block 26,442,974).
The other 5,007.03 WGNK (715.41 USD; 4,000 + 1,000 + 7.03) were burned at blocks 25,473,317–26,149,505, i.e. 41 to 135 days
earlier, and never delivered — stuck bridge transactions unrelated to the hack. Honouring them is reasonable but should be
said, and the old records must be cancelled so they cannot be delivered twice. Class (c).

## 12. Deliverability and unassigned amounts

- 123 recipients (793,171.18 GNK, 115,050.38 USD, 5.34%) never sent an Ethereum transaction, 26 are contracts (849.33 USD):
  115,899.71 USD depends on a claim procedure the package does not define.
- The status column is unreliable: `0x36331e299247e5d0d3261e1d9852f6e0cffee95c` is the target contract of a fill transaction yet
  is listed as "no outgoing tx" (33.11 GNK); 12 paid owners appear in ≥5 post-hack transactions and sent none of them.
- 966.40 pre-hack WGNK sat in CoW Settlement (706.90) and the WGNK contract (259.50) and belong to nobody in the register.
- 726 of 789 "derived" Gonka addresses (10,623,318.90 GNK) have never signed on Gonka; fine technically, but recipients
  should confirm they can use the same key there.

## 13. Option 1 ≤ 2 ≤ 3 does not hold for one owner

`0x12ff7e2aea4162b63c6d1ed3b4f7e1f54a985c7b`: option 3 pays 0.024864 ETH, options 1 and 2 pay 0.025 ETH (−0.24 USD), because
proportional offsetting uses trade-time ETH prices. The package's check passes only because it compares M, not payouts.

## 14. Purchases paid in untracked tokens

Confirmed as small: WGNK received for other tokens in pool transactions — window A 14 moves, 8 owners, 54,028.76 WGNK
(≈1,586.74 USD at the pool price); window B 11 moves, 6 owners (≈255.62 USD). Four liquidity position rows are unpriced
(1,000 UDS of `0x0b711dfa…428d` at the snapshot; AURS). List: `unattributed_wgnk_moves.csv`.

---

## Sensitivity (verified)

- **Cut-off time:** see finding 2. **p0:** GNK payout changes by −35,183 GNK at p0 × 0.5 and +29,711 GNK at p0 × 2 (0.3%); p0
  itself reproduces (24 h VWAP 0.142881; 1 h 0.143142; 72 h 0.147293; 7 d 0.152970).
- **ETH:** package figure (±10% → ∓100K USD) reproduces; see finding 5 for the loss already incurred.
- **Options:** option 2 adds 3,575.49 USD and option 3 adds 17,608.69 USD for 97 owners with a net window-B loss of
  18,075.75 USD. Only 3 purchases (79.86 USD) fall within 60 seconds after the warning and 12 (220.83 USD) within 15 minutes.
  Passive liquidity drained after the warning with no action by the owner: 3 owners, 444.99 USD.

## Checked and found correct

1. Register CSV = model table = summary JSON for every owner and every option (max difference 0); README table matches.
2. Pre-hack wallet balances of all 1,292 owners equal the transfer log (max difference 0); supply at the snapshot
   13,090,977.714566; no negative balances; no address appears in two owners; pools, PoolManager, WGNK contract and the zero
   address are not recipients; the attacker, his sale router `0x6fd41c21…2786` and his gas funder receive nothing.
3. All 3,128 model rows reproduce from raw receipts: WGNK changes, money changes, and the third-party attribution arithmetic.
4. Option-1 payouts of the 1,258 owners without LP fields reproduce exactly from the per-transaction table.
5. 501 v3 position-states reproduce from liquidity maths and stored fees (max difference 0), including the largest position.
6. All 3,280 post-hack swaps and all 94 v3 liquidity events are inside scanned transactions; no row lies after T2; window
   labels agree with block numbers.
7. Only one mint happened after the snapshot (the 22,000,000); the 17 other recent mints have completed threshold signing;
   every other mint ever (1,450) matches a Gonka request by destination and amount.
8. No negative or absurd payout values. 166 owners with pre-hack WGNK are unpaid: 159 hold 0.5 WGNK or less, 7 (6,810.32 WGNK)
   are offset by their gains.
9. Purchases from non-pool sellers are 9,338.67 USD of 210,250.72 USD (4.4%) in window A; one buyer/seller pair has a direct
   transfer between them. No sign of wash trading at scale.
10. Top-up arithmetic reproduces (87.957 ETH + 132,011.99 GNK = 170,952.43 USD).

## Cannot be checked from the package

- Who controls any address (related parties, one person behind several owners, custodians).
- Gonka-side history: escrow before the hack (node state pruned), status of mint requests, whether queued burns can execute.
- Contract vs externally-owned account (no code lookups), completeness of the transfer log against the chain, Chainlink prices,
  fee values read from contract state (`lp_fees.json`), v4 position amounts (not recomputed by me).
- Anything after T2, off-chain or OTC payments, limit orders placed before the hack, Discord announcements, the current GNK
  price (payout "value" and the pool share assume GNK is still worth p0).
- The register PDFs and XLSX were not compared line by line with the CSV.

## Files

Scripts (run each with the Docker command from the brief; `e04` must run before `e12` and `e14`):
`rt_common.py`, `rt_raw.py` (loaders, raw receipt parser), `e01_schema.py`, `e02_overview.py`, `e03_clusters.py`,
`e04_hubs_transfers.py`, `e05_txdump.py <tx or address>`, `e06_fairness.py`, `e07_unattributed.py`, `e08_coverage.py`, `e09_lp.py`,
`e10_bridge.py`, `e11_sensitivity.py`, `e12_misc.py`, `e13_provenance.py`, `e14_boundary.py`, `e15_verify.py`, `e16_keynumbers.py`,
`e17_toplp.py`, `e18_spotchecks.py`.

Data: `findings.json`, `key_numbers.json`, `largest_recipient_group.csv`, `refunded_buyers_timing_price.csv`, `sensitivity_cutoff.csv`,
`profit_keepers.csv`, `posthack_burners.csv`, `cluster_key_vs_holder.csv`, `clusters_effect.csv`, `plain_edges.csv`, `hubs.csv`,
`gonka_mint_requests_not_minted.csv`, `v4_events_not_scanned.csv`, `window_b_netting.csv`, `unattributed_wgnk_moves.csv`,
`unattributed_by_owner.csv`, `p2p_purchases_window_a.csv`, `paid_owners_never_sender.csv`, `transfers_in_money_txs.csv`.
