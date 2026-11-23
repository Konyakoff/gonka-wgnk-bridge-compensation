**English** | [Русский](CRITIQUE.ru.md)

> [!IMPORTANT]
> **Draft for community discussion — not an official position of Gonka or its Core Team.** Published by Sergey Konyakov
> ([@Konyakoff](https://github.com/Konyakoff)), a community member. The research was done with Claude Code (Fable 5.2); the
> author has not yet independently verified every address and amount. Community members and the Core Team are asked to
> re-check the logic of the calculation and the listed addresses and amounts. A shared position on compensation is to be
> reached through discussion.

# Critique of the method — weak points and open questions

Status: 23 Nov 2026. This file is written against ourselves: it lists where the method is
weak, whose interests may not be covered, what was wrong in the pre-publication draft and has been corrected, and what cannot be settled
from on-chain data. Figures are for option 1 unless stated; every figure is reproducible from `model/critique.json` and the CSV
files in `model/critique/`. Two separate reviewers worked in parallel with our own checks: an adversarial review of the draft
package (`reviews/red_team/`) and an independent recomputation of liquidity positions (`reviews/lp_recheck/`). Their reports are
included as written (see `reviews/README.md`); where their numbers differ from ours by definition (e.g. 142 vs 131 profit-keeping owners), both are kept.

## 1. Summary

| # | Weak point | Size | Kind | What we did |
|---|---|---|---|---|
| 1 | Traders keep profit made during the hack | 96,606 USD, 131 owners | policy | disclosed; the slogan "nobody profits" now carries a note |
| 2 | The dividing line is generous to those who bought after the hack was public | 107,758 of 122,374 USD refunded to traders | policy | disclosed with the alternative figure |
| 3 | Payouts are concentrated | one address: 29.8% of GNK, 42.9% of money | policy / verification | disclosed; liquidity positions recomputed independently |
| 4 | Bridge claims for unbacked WGNK are pending, old tokens still transferable | 1,280,942 WGNK, 39 owners | risk | disclosed; cancellation proposed as a precondition of payout |
| 5 | An address is not a person; off-chain deals are invisible | 45 groups, 102 addresses | cannot be settled on chain | checked on chain, disclosed, payout split by address |
| 6 | ETH price moves the cost more than the choice of option | ±96,707 USD per 10% | risk | disclosed; immediate conversion proposed |
| 7 | Errors found before publication | top-up 170,952 → 158,074 USD | calculation errors | **fixed** (section 2) |

## 2. Corrected before publication (proven calculation errors)

1. **Bridge escrow left out of the sources.** The attacker took 13,000,000 of 13,098,243 GNK from the escrow; 98,276.76 GNK
   is still there and backs the same holders. Counting it lowers the GNK shortfall from 132,012 to 35,273 GNK.
2. **Bridge requests in flight were missing.** 47 successful GNK → WGNK requests (1,509.96 GNK, 33 senders;
   8 of them, 33.9 GNK, after the attack) have no matching WGNK mint. The GNK is returned to the
   sender on Gonka in every option (`registers/bridge_requests_in_flight.csv`). Each request's status must still be confirmed
   against the bridge module: the escrow arithmetic explains 1,216 of the 1,476 GNK requested before the attack.
   In the draft the request table had no success flag: 9 failed requests (138,034 GNK) looked like in-flight ones.
3. **Payee of a multi-address owner.** The whole payout of an address group went to the alphabetically first address. Now GNK
   goes to the address that held the WGNK and money to the address that paid: 247,998 GNK and 16,610 USD changed
   address in 22 of 45 groups. Owner totals are unchanged.
4. **Trades paid in untracked tokens** were treated as free; they are now valued by the WGNK pool leg of the same transaction.
5. **Liquidity operations without a WGNK movement** (Uniswap v4, money-only adds/removals) were not in the transaction set;
   one owner was credited 400 USD in option 3 for USDC he had withdrawn himself. The transactions were fetched and counted.
6. **Option 1 ≤ 2 ≤ 3** did not hold per currency for one owner (0.24 USD); it is now enforced per currency.

Items 4–6 change payouts of 9 owners; net effect on money to people: +943 USD in option 1,
+600 USD in option 3. Protocol top-up, before → after: option 1 170,952 → 158,074;
option 2 174,528 → 161,563; option 3 188,562 → 175,340 USD.
The three reviews in `reviews/` describe the draft before these corrections.

## 3. Open weak points

### 3.1 Someone did profit (96,606 USD)
127 owners with no pre-hack WGNK ended with more money than they spent (93,555 USD); 4 holders took out
3,051 USD more than their holdings were worth at the pre-hack price (their payout is zero, the excess stays). The ten
largest hold 78%; the largest, a trading bot, 23,260 USD. This equals 61% of the protocol top-up: the cheap
WGNK they sold were bought by people who are now refunded. The protocol cannot claw this back. The attacker kept
13.3 ETH and 99,599 GNK. List: `model/critique/profit_kept.csv`.

### 3.2 The line at the official warning is generous
Among owners without liquidity positions, option 1 refunds 122,374 USD to 154 owners. With the line at the first public
alert (Blockaid, 18:28 UTC on 18 Nov) it would be 14,617 USD to 54 owners; with the line at 22:30 (a dozen outlets) the total differs from the line at the warning by
1,097 USD only. Purchases in window A: 209,566 USD, of which 52,860 USD before the alert. Liquidity providers are
not affected by the choice (their USDT was bought out in the first minutes). Counter-argument: nobody is obliged to follow
security firms on X, and the project itself was silent until 00:24:07. The project's Discord was not checked; an earlier
explicit warning there would move the line.

### 3.3 Concentration
The largest recipient, a liquidity provider, receives 3,886,258 GNK and 126,431 USD — 29.8% of all GNK, 42.9% of all
money, 31.6% of all value. 14 liquidity providers together: 36.8% of GNK and 58.5% of money. The ten largest recipients:
60% of value; the median payout is 55 USD and 552 of 938 paid owners get less than 100 USD. The calculation is
formally consistent — these addresses held the liquidity the attacker bought out — but an error here costs more than in all
small payouts together, and whether any large recipient is related to the project team is not known to us. We propose that
the largest recipients confirm their address by signature and disclose any such link. Liquidity positions were recomputed by a separate reviewer without access to the model code, directly from Ethereum contract state at the three blocks (public archive RPC, 1,378 of 1,383 reads repeated on a second provider and identical): all 200 positions (66 Uniswap v3 NFT, 84 v3 direct, 50 v4 NFT), 544 position-block rows, 45 owners — no mismatch (largest difference 0.000002 WGNK). No position with value is missing from the model. The reconciliation gap of the model (about 1,125 WGNK) is explained: it is uncollected Uniswap protocol fees (897.09 WGNK in the v3 pools, 228.33 in v4), which belong to the fee recipient, not to any liquidity provider. Not reconciled against a balance: the money side of v4 positions (the PoolManager holds all pools together) and a constant 0.33 USDT residual of the 0.3% pool. The same reviewer independently found the missing money-only liquidity transactions (section 2, item 5). See `reviews/lp_recheck/REPORT.md`.
List: `model/critique/top_recipients.csv`; the red-team report gives more detail on the largest recipients.

### 3.4 Pending bridge claims and "voided" tokens
After the attack 39 owners (the attacker excluded) burned 1,280,942 cheaply bought WGNK on the bridge to receive native GNK; the
bridge records are `BRIDGE_PENDING` — not executed and not cancelled (183,022 USD at the pre-hack price; the largest
claim is 500,000 WGNK). 24 of these owners also receive a money refund (32,433 USD). The model treats these claims and all
post-hack WGNK as void, but that is a statement on paper until governance cancels the claims and the old contract is
stopped: 11,570,441 unbacked WGNK are still in wallets and transferable (liquidity left in the old pools at the
freeze: 1,003 USD, so selling them is hardly possible right now). Separately, 6,049 genuine WGNK burned before
the hack await delivery (5,007 of them are records 41–135 days old); they are in the register and must be paid once —
by the bridge or by the register, not both. List: `model/critique/pending_burns_after_attack.csv`.

### 3.5 Addresses, groups and off-exchange deals
Addresses linked by a plain WGNK transfer after the attack (no money in the transaction) are treated as one owner:
45 groups, 102 addresses, 425,370 GNK and 54,827 USD. The concern: such a transfer could be an over-the-counter sale paid for
separately. We pulled the USDT/USDC/DAI/ETH history of all 104 addresses involved (67 pairs) from two days before the
attack to the freeze: money moved between the two addresses in 21 pairs, and against the direction of the WGNK in
11 (7,245 USD in total). By timing and amounts these are top-ups of the owner's own trading wallet and gas (e.g. 3 ETH
sent 31 blocks before the purchase, WGNK sent back afterwards), not sales; no off-exchange sale of pre-hack WGNK was found.
What cannot be seen: payment off chain; one person with two unlinked wallets (GNK for holdings on one, sale proceeds on the
other); a group that is in fact two people — in 2 groups one address's gain is netted against another address's holdings.
The rule has no minimum amount and ignores direction (one merge rests on 0.12 WGNK). Mitigation: payout split by address
(section 2), an objection window, signatures for disputed addresses. Lists: `model/critique/plain_transfer_pairs.csv`,
`model/critique/address_groups.csv`.

### 3.6 ETH price
The 884,799 USD bridge reserve is bought with the returned ETH, so the top-up is 158,074 USD at ETH 1,729.15,
254,780 at −10% and 61,367 at +10%, while options 1 and 3 differ by 17,266 USD. ETH was 1,806.08 USD when the
funds were returned. Converting the stablecoin part right after the decision removes this exposure.

### 3.7 Smaller assumptions
- **Third-party settlement.** For 77 owners the purchase (or sale) was paid by an intermediary in the same transaction (relayers,
  CoW Swap); the refund currency and the payee are inferred from that transaction (4,050 USD net in window A).
- **Window-B netting.** In options 1–2 a net loss after the warning is ignored (or scaled) as a whole, including proceeds of
  sales inside it; the red team measures 2,606 USD of such proceeds for 22 owners.
- **Deliverability.** 123 recipients (793,171 GNK) have never sent an Ethereum transaction and 26 are contracts;
  they need a claim procedure. The account-kind column is not fully reliable (one contract is listed as "no outgoing tx").
- **Nobody's WGNK.** 966.4 pre-hack WGNK sat in the CoW Settlement contract and in the WGNK contract itself and are not paid to anyone;
  liquidity positions add up to the pool balances with a gap of 1,126 WGNK.
- **Pre-hack price.** p0 is the 24-hour VWAP; with windows from 1 hour to 7 days the deductions for sellers change by a few thousand GNK at most.
- **After the freeze.** Trades after 23 Nov 04:30 UTC count in no option (0 swaps were recorded between the freeze and the check).

## 4. Checked and not confirmed

- No WGNK mint after the attack other than the attacker's 22,000,000; every genuine mint is matched to a Gonka request.
- WGNK supply at the snapshot is fully assigned (owners' wallets + pools + two service contracts).
- No liquidity position changed hands between the snapshot and the warning; one v4 position NFT changed owner after it.
- Wrapped USDT/USDC balances of the 18 bridge-reserve holders on Gonka did not change after the attack.
- In the first five minutes after the warning there were 5 purchases for 103 USD — the exact second of the line is not material.

## 5. Independent reviews

- **Red team** (`reviews/red_team/REDTEAM_REPORT.md`, `findings.json`): a separate reviewer who received only the draft package and no hints. 14 findings. It independently reached the five main weak points of section 3 and the errors 1–3 and 5–6 of section 2; its findings 8, 9, 11, 12 and 14 are in section 3.7. It also confirmed: register = model = summary for every owner; pre-hack balances of all 1,292 owners; all 3,128 model rows reproduced from raw receipts; option-1 payouts of 1,258 non-LP owners; 501 v3 position states; p0.
- **Liquidity positions** (`reviews/lp_recheck/REPORT.md`): all 200 positions recomputed from contract state at three blocks — no mismatches; the pool reconciliation gap explained by Uniswap protocol fees; its section 8 lists further observations (liquidity withdrawn before the warning, concentration, tokens that are not valued, pools created after the hack) and section 9 what it could not verify.
The independent recomputation of owners without liquidity positions (`reviews/non_lp_recompute/`) was run against the published tables: 1,173 of 1,256 non-LP owners match in full; the 83 differences are owners affected by the third-party-settlement rule (75) or the untracked-token rule (11), which that script does not implement.

## 6. What cannot be checked from on-chain data

Who owns an address and whether recipients are related to the project; payments off chain; announcements on Discord;
the state of the Gonka bridge module for each pending record; what happens after the freeze.
