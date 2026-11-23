# Direction 1 — Hacks and thefts in blockchain systems: reference moment, post-incident traders, net-loss principle

Working paper for the Gonka bridge-hack compensation proposal. Research date: 23 November 2026. Machine-readable twin: `dir1_crypto.json` (same items, same wording).

Question tested: is it consistent with real-world practice to treat losses from trades made BEFORE the official warning ("Do not trade WGNK", 19 Nov 2026 00:24:07 UTC) as an obligation, and losses from trades made AFTER it as discretionary?

## 1. Method and how to read the verification labels

- **primary** — the judgment, order, regulator report or the project's own plan was opened. Where a PDF was downloaded and text-extracted locally, quotes were copied from the extracted text (Cryptopia 2020 and 2024, FTX, SEC DAO report, Mt. Gox 2015 translation). Where an HTML page was read through an automated fetch-and-extract tool (Find Case Law, eLitigation, project blogs and forums), the quote fragments are what the tool returned as verbatim; they are short and should be re-read against the source before they are printed in a public document.
- **secondary** — a reputable press report or law-firm note was opened, or (where stated in the note) only search-engine summaries of such reports were seen.
- **unverified** — nothing could be opened; the item rests on search summaries or background knowledge. Do not cite these without checking.
- No citation, paragraph number or quote was invented. Where a pinpoint is inferred or assembled from fragments, the verification note says so.
- Every item carries one position label: `hard_cutoff`, `gradient_or_grace`, `net_loss_principle`, `snapshot_at_hack`, `contradicts`, `context`.

## 2. Bottom line

**(a) Reference moment.** Three families exist, and they do not point to the same timestamp.

1. *Last block before the exploit / moment of theft* — the dominant rule in protocol compensation plans and the rule stated by the New Zealand High Court: Cryptopia 2020 ("as at the date of the theft"), Cover (block 11,541,218), Balancer BIP-892 ("last block before first exploit tx"), Beanstalk ("the block prior to the exploit"), KyberSwap ("last block prior to the Primary Exploit"), Eminence, Euler (block the protocol was disabled), Ankr, ByBit v Ho (trust arises "at time of the theft"), Fantom v Multichain (value on the day before the breach).
2. *Moment of the operator's own official action or announcement* — WazirX (withdrawal halt, 18 July 2024 1 PM IST; all later trades voided), Elixir deUSD (snapshot at the wind-down announcement), Binance/COVER (trading halt as the outer limit of its grace window), pNetwork pGALA (second, pre-announced snapshot four days after the incident), Coincheck (price averaged from trading halt to the announcement).
3. *Start of a formal insolvency process* — FTX (petition date; primary), Celsius (petition date; unverified), Quadriga (date of bankruptcy), Mt. Gox (commencement of each proceeding; unverified figures), Cryptopia 2024 (entitlement date 14 May 2019 = liquidation). These are valuation dates, not eligibility cut-offs.

Gonka's proposed line (the official warning) belongs to family 2. It is LATER than the majority rule (family 1), i.e. more generous to people who entered between the hack and the warning.

**(b) People who bought or traded after the incident was public / after a warning.** Four treatments were found:

- *Excluded outright* — Ankr ("Do not trade aBNBc or speculatively buy it at a discount"; "we are only able to compensate LP's caught off guard"), Cover's own plan, Balancer, Beanstalk, KyberSwap, Eminence, Cryptopia 2020 (later acquirers are outside the loss-sharing class), WazirX (post-halt trades voided), Elixir (post-snapshot purchases).
- *Paid from a separate, voluntary source* — Binance used its own SAFU fund (US$10.1m) for customers who bought COVER after the protocol's snapshot and before Binance halted trading.
- *Recognised at a lower tier* — pGALA (pre-drain holders restored in kind; later buyers up to a second snapshot receive only a pro-rata share of the recovered BNB), Terra 2.0 (pre-attack LUNA 35% and aUST 10% vs post-attack LUNA 10% and UST 15%), Cryptopia 2024 (claims after the soft cut-off are paid from what remains; after the final cut-off only at the liquidators' discretion).
- *Treated exactly like original holders* — where the remedy restores the token's backing and the claim travels with the token: The DAO, Nomad, Wormhole, Ronin, Bitfinex BFX tokens.

No precedent was found in which trades made after an explicit "do not trade" warning were compensated in full. The only plan found that promised anything to people who bought after an explicit warning is pGALA, and it promised only a pro-rata return of the recovered funds up to a second announced snapshot; that leg was reported as still on hold in 2023.

**(c) "Nobody profits from the hack" / net loss.** Applied expressly by courts: Cryptopia 2024 (up to "100 per cent of accepted pre-hack holdings, taking into account any post-hack transactions"; recoveries "taking into account any later withdrawals"), Fantom v Multichain (pre-breach value "less any residual value"). Applied in programmes: Euler (claims capped at NAV x 1.005), KyberSwap (grant refundable if assets are recovered), Curve (loss minus recoveries), Hyperliquid (everyone made whole "apart from flagged addresses"), Ankr (arbitrage not rewarded). It is NOT universal: bearer-style remedies (The DAO, Bitfinex BFX, Nomad, Elixir, Mt. Gox claim trading) let post-incident buyers profit.

## 3. Points that CONTRADICT or weaken a hard cut-off at the official warning

1. **The majority rule puts the line earlier, at the exploit block.** Under Ankr, Cover, Balancer, Beanstalk, KyberSwap, Eminence and Cryptopia 2020, a person who bought between the hack and the warning is not in the mandatory class at all. Calling pre-warning purchases an "obligation" is defensible (WazirX, Binance/COVER, pGALA and Elixir use an official-action moment), but it is a policy choice in favour of late entrants, not the standard.
2. **Standard schemes are holdings-based, not trade-based.** They compensate the position held at the snapshot and then net off later dealings (Cryptopia 2024). No scheme was found that defines the compensable event as "a loss-making trade before a timestamp". A trade-based design needs its own netting rule (pre-hack holders who sold after the hack; buyers who later sold higher).
3. **Bearer-token precedents ignore acquisition time.** In The DAO (SEC: "All DAO Token holders who adopted the Hard Fork could exchange their DAO Tokens for ETH"), Nomad, Wormhole and Ronin, anyone holding the token at redemption was whole. If WGNK is again fully backed after the hacker's return, current WGNK holders — including post-warning buyers — already benefit from that restoration. A cut-off can only govern compensation of trading losses, not the restored backing.
4. **Some communities did give post-incident buyers something** (Terra, pGALA second snapshot, Cryptopia late claims). These support "discretionary" rather than "excluded".
5. **Trades at distorted prices are legally valid.** Quoine v B2C2 [2020] SGCA(I) 02: no implied right to reverse trades executed at abnormal prices; filled orders are irreversible. Those who gained cannot simply be made to pay; compensation of the losers is funded by the community and is, legally, closer to ex gratia than to a debt — on both sides of the warning.
6. **Quality of notice.** The only court-supervised cut-off found (Cryptopia 2024) required at least 90 days' notice by email, website and social media. A single post on X is weaker notice; people trading minutes after it, or through bots and aggregators, could not all have seen it. A short grace interval or a hardship channel would answer this.
7. **Fixed-date rules create windfalls.** Quadriga (the date shifted value between fiat and crypto claimants), Mt. Gox (re-valuation from about ¥50,058 to ¥749,318.83 per BTC — reported, not verified against trustee documents), Celsius (petition-date CEL price rejected as unreliable — reported, not verified), Fantom v Multichain (day-after prices rejected as "so volatile"). A single timestamp should be paired with a robust reference price (pre-hack, or an average), not a tick taken in a dislocated market.

## 4. Strongest items for a one-page slide

| Item | Why it matters | Verification |
|------|----------------|--------------|
| Ruscoe v Cryptopia [2020] NZHC 728, [204]-[205] | Court: loss class fixed "as at the date of the theft"; later acquirers bear no loss and share no recoveries | primary |
| Ruscoe v Houchens [2024] NZHC 419, [40], orders 2.2-2.6 and 9.2 | Court: cap at 100% of pre-hack holdings net of post-hack transactions; soft and final cut-offs with residual discretion | primary |
| Fantom Foundation v Multichain [2024] SGHC 173, [21]-[27] | Court, bridge collapse: value the day before the breach, less residual value; day-after prices rejected | primary |
| Ankr aBNBc (Dec 2022) | Unbacked mint, explicit "Do not trade", snapshot, post-exploit speculation not compensated | primary (project blog) |
| Binance SAFU / COVER (Dec 2020) | Post-snapshot buyers paid from a separate voluntary fund, window closed at the official trading halt | secondary |
| WazirX (Aug 2024; Singapore scheme 2025) | Cut-off at the operator's official action; all later trades rendered ineffective | secondary |
| Balancer BIP-892, KyberSwap grant, Beanstalk, Euler | Mainstream DeFi rule: last pre-exploit block; anti-windfall devices | primary (project sources) |
| The DAO (SEC Release No. 81207) | Counter-example: redemption followed the token, post-attack buyers made whole | primary |

## 5. Index of all items

| # | Item | Year | Verification | Supports |
|---|------|------|--------------|----------|
| 1 | Ruscoe v Cryptopia Ltd (in liquidation) | 2020 | primary | snapshot_at_hack |
| 2 | Ruscoe v Houchens (Re Cryptopia Ltd (in liq)) (Distribution) — hack losses and recoveries | 2024 | primary | net_loss_principle |
| 3 | Ruscoe v Houchens (Re Cryptopia) — entitlement date, soft cut-off and final cut-off | 2024 | primary | gradient_or_grace |
| 4 | WazirX (Zettai Pte Ltd) — reversal of post-halt trades and court-sanctioned scheme | 2024 | secondary | hard_cutoff |
| 5 | In re FTX Trading Ltd. — estimation of digital asset claims | 2024 | primary | context |
| 6 | In re Celsius Network LLC — petition-date dollarisation of account-holder claims | 2023 | unverified | context |
| 7 | Re Quadriga Fintech Solutions Corp. (QuadrigaCX) — conversion date of cryptocurrency claims | 2021 | secondary | context |
| 8 | Mt. Gox — claim valuation dates in bankruptcy and civil rehabilitation | 2018 | unverified | context |
| 9 | BitGrail (BG Services S.r.l.) bankruptcy | 2019 | secondary | context |
| 10 | Bitfinex hack — 36.067% socialised loss and BFX tokens | 2016 | secondary | contradicts |
| 11 | Coincheck NEM hack — compensation at a fixed reference price | 2018 | secondary | snapshot_at_hack |
| 12 | Youbit (Yapian) hack and bankruptcy filing | 2017 | secondary | context |
| 13 | Ankr aBNBc infinite-mint exploit — snapshot, 'do not trade' warning and exclusion of post-exploit speculation | 2022 | primary | hard_cutoff |
| 14 | pNetwork pGALA (BNB Chain) incident — two snapshots | 2022 | secondary | gradient_or_grace |
| 15 | Cover Protocol infinite-mint exploit — snapshot at the last pre-exploit block | 2020 | secondary | snapshot_at_hack |
| 16 | Binance SAFU compensation for users who bought COVER after the exploit snapshot | 2020 | secondary | gradient_or_grace |
| 17 | The DAO attack and Ethereum hard fork | 2016 | primary | contradicts |
| 18 | Nomad bridge hack — pro-rata bridge-back of recovered funds | 2022 | secondary | contradicts |
| 19 | Euler Finance — redemption of returned funds | 2023 | primary | snapshot_at_hack |
| 20 | KyberSwap Elastic exploit — Treasury Grant Program | 2023 | primary | snapshot_at_hack |
| 21 | Balancer v2 exploit — distribution of rescued funds | 2025 | primary | snapshot_at_hack |
| 22 | Beanstalk governance exploit — 'Unripe' assets for pre-exploit holders | 2022 | primary | snapshot_at_hack |
| 23 | Eminence (EMN) exploit — distribution of funds returned by the hacker | 2020 | secondary | snapshot_at_hack |
| 24 | Terra 2.0 airdrop — pre-attack and post-attack snapshots with different weights | 2022 | secondary | gradient_or_grace |
| 25 | Elixir deUSD wind-down after the Stream Finance loss | 2025 | secondary | hard_cutoff |
| 26 | Hyperliquid JELLY incident — users made whole except flagged addresses | 2025 | secondary | net_loss_principle |
| 27 | Curve / Vyper re-entrancy exploit — DAO vote to reimburse LPs | 2023 | secondary | net_loss_principle |
| 28 | Mango Markets exploit; United States v. Eisenberg | 2022 | secondary | context |
| 29 | Full-replenishment bridge cases: Wormhole (2022), Ronin (2022), Poly Network (2021) | 2022 | secondary | context |
| 30 | Harmony Horizon bridge hack — reimbursement proposals | 2022 | secondary | context |
| 31 | Fantom Foundation Ltd v Multichain Foundation Ltd | 2024 | primary | net_loss_principle |
| 32 | PAID Network infinite-mint exploit | 2021 | unverified | snapshot_at_hack |
| 33 | PancakeBunny flash-loan exploit — compensation of 'Original Holders' | 2021 | unverified | snapshot_at_hack |
| 34 | Cetus (Sui) exploit — validator vote and recovery plan | 2025 | secondary | context |
| 35 | Mt. Gox bitcoin ownership case | 2015 | primary | context |
| 36 | Jump Crypto / Oasis counter-exploit of the Wormhole hacker under an English court order | 2023 | secondary | context |
| 37 | AA v Persons Unknown, Re Bitcoin | 2019 | primary | context |
| 38 | Tulip Trading Ltd v van der Laan (Bitcoin Association for BSV and others) | 2023 | primary | context |
| 39 | Quoine Pte Ltd v B2C2 Ltd | 2020 | primary | context |
| 40 | ByBit Fintech Ltd v Ho Kai Xin and others | 2023 | primary | snapshot_at_hack |
| 41 | CLM v CLN and others | 2022 | primary | context |
| 42 | Osbourne v Persons Unknown and Ozone Networks Inc | 2022 | primary | context |
| 43 | D'Aloia v Persons Unknown Category A and others (Bitkub) | 2024 | primary | context |

Counts by position: context = 18, contradicts = 3, gradient_or_grace = 4, hard_cutoff = 3, net_loss_principle = 4, snapshot_at_hack = 11.

Counts by verification: primary = 19, secondary = 20, unverified = 4.

## 6. Detailed findings

### A. Exchange insolvencies and exchange hacks

#### 1. Ruscoe v Cryptopia Ltd (in liquidation)

- **Citation:** [2020] NZHC 728 (Gendall J, 8 April 2020)
- **Jurisdiction / year / forum:** New Zealand / 2020 / High Court of New Zealand (Christchurch Registry)
- **Facts:** Cryptopia, a NZ exchange, was hacked in January 2019 (roughly 9-14% of some coins stolen), briefly re-opened in March 2019 and went into liquidation on 14 May 2019. Liquidators asked the court whether the coins were property held on trust and how the theft loss and any recoveries should be allocated.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Crypto is property held on a separate express trust per coin. The theft loss is borne only by holders of the stolen coin types, pro rata, and the reference moment is THE DATE OF THE THEFT: liquidators determine the affected account holders and their shares 'as at the date of the theft'. Anyone who acquired the same coin AFTER the theft is carved out: no reduction for the theft is applied to them, and recoveries go only to those affected at the theft date.
- **Relevance to Gonka:** The strongest court authority found for a snapshot at the incident: the class of people who bear/recover the hack loss is fixed at the moment of theft; later acquirers are outside the loss-sharing class (neither burdened nor entitled to recoveries). Supports treating pre-incident holders as the core protected class and later entrants as a separate category.
- **Quote / pinpoint:** [205](a) "as at the date of the theft, the liquidators should determine the accountholders affected and their relative shares in any trust of the digital assets which are the subject of the theft. The liquidators should then apply the loss from the theft pro rata to those existing holdings." [205](b) "to the extent that subsequent to the theft any accountholder acquired digital assets of the type that suffered the theft and those assets were added to the relevant trust assets, no reduction for the theft should be applied to that accountholder's share in the trust assets" [205](c) "any recoveries of cryptocurrency lost as a result of the theft should be applied pro rata to make up the loss suffered by such accountholders as were affected by it". Also [204]: "Those losses, as I see it, should be borne pari passu by those accountholders alone." Property/trust: [133], [187].
- **Sources opened:** <https://www.justice.govt.nz/jdo_documents/workspace___SpacesStore_e58d36af_d708_45cb_a474_6b08bd75ace9.pdf>
- **Verification:** primary. Judgment PDF downloaded and text-extracted; quotes copied from the extracted text.
- **Position:** `snapshot_at_hack`

#### 2. Ruscoe v Houchens (Re Cryptopia Ltd (in liq)) (Distribution) — hack losses and recoveries

- **Citation:** [2024] NZHC 419 (Palmer J, 1 March 2024); orders restated in the liquidators' 2026 draft orders, CIV-2023-485-411
- **Jurisdiction / year / forum:** New Zealand / 2024 / High Court of New Zealand (Wellington Registry)
- **Facts:** Directions for the claims process and in-specie distribution of the trust crypto to Cryptopia account holders, including how unclaimed holdings and any recovered stolen coins are applied to hack losses.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Hack losses are topped up only up to 100% of the PRE-HACK holding and net of what the holder did afterwards: unclaimed holdings may be applied 'pari passu, to account for losses arising from the hack, up to 100 per cent of accepted pre-hack holdings, taking into account any post-hack transactions'; recoveries are distributed 'proportionate to the amount they lost in the hack and up to a maximum of 100% of the value of an account holder's holding in the stolen cryptocurrency as at the date of the hack, taking into account any later withdrawals'. The top-up reference balance is the balance 'as at 14 January 2019' (hack date).
- **Relevance to Gonka:** Court-approved net-loss rule: compensation is capped at the pre-hack position and reduced by post-hack transactions, so nobody ends up better off than before the hack. Directly supports a 'nobody profits from the hack' cap and a hack-date reference balance.
- **Quote / pinpoint:** [40](c): "pari passu, to account for losses arising from the hack, up to 100 per cent of accepted pre-hack holdings, taking into account any post-hack transactions." Order 9.2(b): "proportionate to the amount they lost in the hack and up to a maximum of 100% of the value of an account holder's holding in the stolen cryptocurrency as at the date of the hack, taking into account any later withdrawals". [45]: "to reimburse account holders proportionately on the basis of the valuation as at the date of the hack."
- **Sources opened:** <https://www.justice.govt.nz/jdo_documents/workspace___SpacesStore_5397be10_929f_4475_8fd6_9f246b885d61.pdf> ; <https://www.grantthornton.co.nz/globalassets/1.-member-firms/new-zealand/pdfs/cryptopia/2026/1c-20260423-updated-draft-orders-tracked-changes.pdf>
- **Verification:** primary. Judgment PDF and the liquidators' orders document downloaded and text-extracted. The paragraph number [40] for the (a)-(c) priority list is inferred from the surrounding text ([41] follows immediately); re-check the pinpoint before publication.
- **Position:** `net_loss_principle`

#### 3. Ruscoe v Houchens (Re Cryptopia) — entitlement date, soft cut-off and final cut-off

- **Citation:** [2024] NZHC 419, orders 1.1, 2.2-2.6 (as varied; Final Cut-off Date later moved to 30 September 2025)
- **Jurisdiction / year / forum:** New Zealand / 2024 / High Court of New Zealand
- **Facts:** Same proceeding. The court had to fix (i) the date at which each holder's entitlement is calculated and (ii) deadlines after which the liquidators may distribute without regard to non-participants.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Entitlement date = 14 May 2019 (start of liquidation), not the hack date. Two-stage deadline: a 'Soft Cut-off' (after at least 90 days' notice by email, website and social media) after which liquidators may proceed as if non-registered holders do not exist, but late claimants 'would still receive a distribution' from what remains; then a 'Final Cut-off' after which incomplete claims are treated as abandoned — yet the liquidators keep an express DISCRETION to accept late claims if it does not prejudice the administration.
- **Relevance to Gonka:** A court-sanctioned gradient: full rights before the notified date, residual/discretionary treatment after it. Structurally the same as 'obligation before the warning, discretion after'. Note the cut-off was preceded by formal multi-channel notice of at least 90 days — a much more robust notice than a single X post.
- **Quote / pinpoint:** Order 1.1: "the Liquidators may adopt 14 May 2019 as the date at which the entitlement of each account holder of the respective cryptocurrency trusts shall be calculated." Order 2.5: "This order does not prevent the Liquidators, in the exercise of their discretion, from receiving, considering, resolving and / or accepting a claim after the passing of the Final Cut-off Date". Notice, para 10: "If you, as an account holder, register a claim after [Soft Cut-Off Date] you would still receive a distribution, but only if there is still cryptocurrency in the relevant trust(s) after trust administration costs have been removed."
- **Sources opened:** <https://www.grantthornton.co.nz/globalassets/1.-member-firms/new-zealand/pdfs/cryptopia/2026/1c-20260423-updated-draft-orders-tracked-changes.pdf> ; <https://www.justice.govt.nz/jdo_documents/workspace___SpacesStore_5397be10_929f_4475_8fd6_9f246b885d61.pdf>
- **Sources located but NOT opened:** <https://www.grantthornton.co.nz/insights/important-notice-for-cryptopia-account-holders-to-register-claims-before-the-soft-cut-off-date/>
- **Verification:** primary. Quotes are from the liquidators' April 2026 'updated draft orders (tracked changes)', which restate the 2024 orders as varied; the 2024 judgment itself was also extracted. Outcome of the May-June 2026 hearing on late claims was not found.
- **Position:** `gradient_or_grace`

#### 4. WazirX (Zettai Pte Ltd) — reversal of post-halt trades and court-sanctioned scheme

- **Citation:** WazirX announcement of 8 August 2024; scheme of arrangement of Zettai Pte Ltd sanctioned by the Singapore High Court in October 2025 (judgment citation not verified)
- **Jurisdiction / year / forum:** India / Singapore / 2024 / Exchange decision; later Singapore High Court (scheme of arrangement under the Companies Act 1967)
- **Facts:** On 18 July 2024 about US$230-235m was stolen from a WazirX multisig wallet. Withdrawals were halted at 1 PM IST that day, but trading continued for some days. The parent company then restructured through a Singapore scheme of arrangement approved by creditors (95.7% by number in the August 2025 revote).
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The exchange set the reference moment at its own official action — the withdrawal halt on 18 July 2024, 1 PM IST (07:30 UTC) — restored every portfolio to that moment and voided all trades made after it (18-21 July), including fees and referrals. Losses were then socialised through the scheme.
- **Relevance to Gonka:** Closest precedent for using the project's official action/announcement time (not the hack transaction) as the cut-off, with every later trade treated as ineffective. Difference: a custodial exchange can technically reverse internal trades; on-chain DEX trades cannot be reversed, only left uncompensated.
- **Quote / pinpoint:** "All users will have their portfolio balances on the WazirX platform restored to what they were on July 18, 2024"; "All trades following July 18, 07:30 am UTC, are rendered ineffective"; aim: an "equitable outcome for users following the abnormality arising" from the hack (as quoted by Cointelegraph, 8 Aug 2024).
- **Sources opened:** <https://cointelegraph.com/news/wazirx-undo-trades-withdrawal-halt>
- **Sources located but NOT opened:** <https://www.theblock.co/post/310245/wazirx-to-undo-all-trades-following-230-million-hack-related-withdrawal-freeze> ; <https://www.business-standard.com/companies/news/singapore-court-approves-crypto-exchange-wazirx-s-scheme-of-arrangement-125101301118_1.html>
- **Verification:** secondary. Press article opened; WazirX's own blog post and the Singapore sanction judgment were not opened. Scheme facts are from search-result summaries of press reports.
- **Position:** `hard_cutoff`

#### 5. In re FTX Trading Ltd. — estimation of digital asset claims

- **Citation:** Case No. 22-11068 (JTD), Bankr. D. Del., Memorandum Opinion and Order of 26 June 2024 (Re: D.I. 5202); earlier bench ruling of 31 January 2024 approving petition-date pricing
- **Jurisdiction / year / forum:** United States (Delaware) / 2024 / US Bankruptcy Court, District of Delaware (Judge John T. Dorsey)
- **Facts:** FTX filed Chapter 11 on 11 November 2022. Customers objected that valuing crypto claims at depressed petition-date prices deprived them of the later market recovery.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Claims are valued at a single statutory reference moment — the petition date — 'as if the bankruptcy had never occurred' (11 U.S.C. § 502(b)); later price movements are ignored. Prices were derived from a weighted median over the 60 minutes before the petition time (per secondary reports).
- **Relevance to Gonka:** Shows the standard legal technique: one fixed reference timestamp for valuing every claim, chosen by rule rather than by who would benefit. It is a valuation date, not an eligibility cut-off for post-incident traders.
- **Quote / pinpoint:** "As with any estimation, the value of the claims must be determined as of the petition date as if the bankruptcy had never occurred. 11 U.S.C. § 502(b)." (Opinion, p. 1)
- **Sources opened:** <https://www.deb.uscourts.gov/sites/deb/files/opinions/FTX%20Opinion%20and%20Order%20Digital%20Asset%20Estimation.pdf>
- **Sources located but NOT opened:** <https://www.abi.org/feed-item/bankruptcy-court-applies-first-of-its-kind-valuation-method-to-estimate-cryptocurrency>
- **Verification:** primary. Opinion PDF downloaded and text-extracted. The 31 January 2024 ruling and the 60-minute weighted-median detail come from secondary summaries.
- **Position:** `context`

#### 6. In re Celsius Network LLC — petition-date dollarisation of account-holder claims

- **Citation:** Case No. 22-10964 (MG), Bankr. S.D.N.Y. (plan confirmed November 2023)
- **Jurisdiction / year / forum:** United States (New York) / 2023 / US Bankruptcy Court, Southern District of New York (Chief Judge Martin Glenn)
- **Facts:** Crypto lender froze withdrawals in June 2022 and filed Chapter 11 on 13 July 2022.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Per secondary sources, claims were fixed in US dollars at petition-date prices via a conversion table; ballots were stated in dollars at petition-date prices. For the CEL token the petition-date market price ($0.81) was NOT used because the market was found to be dislocated/unreliable; a settlement value of about $0.25 was approved instead.
- **Relevance to Gonka:** Second example of a fixed valuation date, plus a caution: a market price observed in a dislocated market at the reference moment may be replaced by a different value. Relevant if the WGNK price around the cut-off was manipulated or illiquid.
- **Quote / pinpoint:** No verbatim quote verified.
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://natlawreview.com/article/quantifying-cryptocurrency-claims-bankruptcy-does-dollar-still-reign-supreme> ; <https://www.govinfo.gov/content/pkg/USCOURTS-nysb-1_22-bk-10964/pdf/USCOURTS-nysb-1_22-bk-10964-14.pdf>
- **Verification:** unverified. Only search-result summaries were seen; no document opened. The $0.25 CEL figure is from the researcher's background knowledge (search summary mentioned a '$0.34 or under' best-interests figure) — do not cite numbers without checking the confirmation opinion.
- **Position:** `context`

#### 7. Re Quadriga Fintech Solutions Corp. (QuadrigaCX) — conversion date of cryptocurrency claims

- **Citation:** Ontario Superior Court of Justice (Commercial List), endorsement of Hainey J., 1 March 2021 (neutral citation not verified)
- **Jurisdiction / year / forum:** Canada (Ontario) / 2021 / Ontario Superior Court of Justice (Commercial List), bankruptcy of Quadriga
- **Facts:** Exchange collapsed after its founder's death; CCAA protection on 5 February 2019, bankruptcy on 15 April 2019. One creditor (BlockCAT) argued for the earlier CCAA date; crypto prices had moved materially between the two dates.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** All cryptocurrency claims converted to Canadian dollars as of the date of bankruptcy (15 April 2019), by analogy with foreign-currency debts under BIA s. 215.1; one pooled date for about 17,000 claims for efficiency. The choice shifted value between fiat and crypto claimants (reported: fiat claims about 23% lower, crypto claims about 14% higher than under the February date).
- **Relevance to Gonka:** A single uniform reference date is chosen on principle even though it visibly favours one group over another; courts accept that any date creates winners and losers.
- **Quote / pinpoint:** "His Honour ordered that claims made in cryptocurrency be converted as of the date of bankruptcy." (Stikeman Elliott note, 13 April 2021)
- **Sources opened:** <https://www.legal500.com/intelligence/canada/technology/bankruptcy-court-weighs-in-on-how-to-value-bitcoins>
- **Sources located but NOT opened:** <https://cdn.millerthomson.com/wp-content/uploads/2021/03/Endorsement-for-Upload.pdf> ; <https://www.theblock.co/post/83835/quadrigacx-ey-users-claims-crypto-compensation-plan>
- **Verification:** secondary. Law-firm note opened. The endorsement itself (unofficial transcription hosted by representative counsel) could not be fetched; a search summary quoted it as: 'I have concluded that the Cryptocurrency Claims are liquidated claims that should be valued as of the Date of Bankruptcy, April 15, 2019.' — treat that sentence as unverified.
- **Position:** `context`

#### 8. Mt. Gox — claim valuation dates in bankruptcy and civil rehabilitation

- **Citation:** Tokyo District Court, bankruptcy (commenced 24 April 2014) and civil rehabilitation (commenced June 2018) of MtGox Co., Ltd.; trustee Nobuaki Kobayashi
- **Jurisdiction / year / forum:** Japan / 2018 / Tokyo District Court (insolvency proceedings)
- **Facts:** Exchange lost about 850,000 BTC and collapsed in February 2014.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** In bankruptcy, BTC claims were converted to yen at about ¥50,058.12 per BTC (price just before bankruptcy commenced, reported as CoinDesk BPI at 23:59 UTC on 23 April 2014). After the switch to civil rehabilitation in 2018, claims were re-valued at ¥749,318.83 per BTC (rate at commencement of rehabilitation). Creditors holding claims at the later proceeding benefited from the later date; claims were freely assignable, so claim buyers also benefited.
- **Relevance to Gonka:** Reference date = commencement of the formal process, not the hack. Also a caution against assuming 'nobody profits': changing the reference date and allowing claim transfers produced large gains for late claim buyers.
- **Quote / pinpoint:** No verbatim quote verified.
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://blog.wizsec.jp/2021/02/mtgox-claim-calculator.html> ; <https://forklog.com/en/details-emerge-of-mt-gox-creditors-payouts/> ; <https://www.coindesk.com/mt-gox-bankruptcy-details-creditor-reimbursement/>
- **Verification:** unverified. Figures come from search-result summaries of a CoinDesk report, a WizSec blog and ForkLog; the trustee's own documents were not opened (the CoinDesk URL returned 404 on fetch). The exact rehabilitation commencement day (22 June 2018) was not confirmed.
- **Position:** `context`

#### 9. BitGrail (BG Services S.r.l.) bankruptcy

- **Citation:** Tribunale di Firenze, Sezione fallimentare, sentenza n. 18/2019, published 21 January 2019 (number/date as reported by Altalex; another source cites 17/2019)
- **Jurisdiction / year / forum:** Italy / 2019 / Tribunale di Firenze (bankruptcy section)
- **Facts:** Italian exchange lost about 17m NANO (about US$170m) through repeated unauthorised withdrawals in 2017-2018.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The exchange and its owner were declared bankrupt; crypto treated as fungible goods held on an irregular deposit, so customers are creditors for equivalent units; the operator was held responsible for the shortfall. No cut-off or post-incident-trader ruling identified.
- **Relevance to Gonka:** Context only: operator liability for a custody shortfall; no guidance on reference moment.
- **Quote / pinpoint:** No verbatim quote from the judgment verified. Press: the founder "must declare bankruptcy, forfeit personal assets, and return as much of the stolen digital assets as possible" (The Next Web, 28 Jan 2019, reporting documents shared by a victims' group).
- **Sources opened:** <https://thenextweb.com/news/bitgrail-court-cryptocurrency-nano>
- **Sources located but NOT opened:** <https://www.altalex.com/documents/news/2019/02/07/criptovaluta-nano-fallisce-la-piattaforma-bitgrail>
- **Verification:** secondary. Judgment text not opened; case number inconsistent across secondary sources.
- **Position:** `context`

#### 10. Bitfinex hack — 36.067% socialised loss and BFX tokens

- **Citation:** Bitfinex announcements of 6-8 August 2016; BFX tokens fully redeemed 3 April 2017 (no court involvement)
- **Jurisdiction / year / forum:** Hong Kong / BVI (private exchange decision) / 2016 / Exchange (iFinex Inc.), no court
- **Facts:** 119,756 BTC stolen on 2 August 2016. Instead of insolvency, the exchange spread the loss across all customers and all assets.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Every account balance — including accounts holding no bitcoin — was reduced by 36.067% and credited with a transferable BFX token per dollar lost. The tokens traded at a deep discount (reported $0.49-0.65 for much of 2016) and were redeemed at $1 in April 2017, so whoever held the token at redemption was paid, regardless of whether they were an original victim.
- **Relevance to Gonka:** Shows (i) loss socialisation at a single moment and (ii) the opposite of a net-loss rule: once the claim is a tradable bearer token, post-incident buyers of the claim profit. If Gonka wants 'nobody profits from the hack', claims must attach to addresses/positions at the cut-off, not to a transferable token.
- **Quote / pinpoint:** "Upon logging into the platform, customers will see that they have experienced a generalized loss percentage of 36.067%"; "This is the closest approximation to what would happen in a liquidation context." (Bitfinex, as quoted by Computerworld, 8 Aug 2016)
- **Sources opened:** <https://www.computerworld.com/article/1670125/bitfinex-asks-users-to-share-losses-of-bitcoin-theft-2.html>
- **Sources located but NOT opened:** <https://www.coindesk.com/bitfinex-pledges-buy-back-remaining-hack-credit-tokens> ; <https://fortune.com/2016/08/15/bitfinex-bitcoin-hack-hong-kong-customers-law/>
- **Verification:** secondary. Press article quoting the Bitfinex post opened. BFX discount range and redemption date from search summaries of CoinDesk. Some reports (BitMEX, Protos) say not every client received the same haircut.
- **Position:** `contradicts`

#### 11. Coincheck NEM hack — compensation at a fixed reference price

- **Citation:** Coincheck announcement of 27/28 January 2018; refunds paid March 2018
- **Jurisdiction / year / forum:** Japan / 2018 / Exchange decision under supervision of Japan's FSA (no court)
- **Facts:** About 523m XEM (about US$530m) stolen from Coincheck on 26 January 2018, affecting about 260,000 users.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Compensation in yen to all customers who held NEM on the platform at the time of the unauthorised transfer, at ¥88.549 per XEM — a volume-weighted average price on another exchange (Zaif) measured from Coincheck's trading halt (26 Jan 2018 12:09 JST) to the announcement (27 Jan 23:00 JST). Trading in NEM was halted, so there were no post-incident buyers on the platform.
- **Relevance to Gonka:** Eligible class fixed at the moment of the theft; the price is not the pre-hack price but an average over the window between the platform's official action and its compensation announcement. Useful precedent for an averaged reference price instead of a single tick.
- **Quote / pinpoint:** No verbatim English quote verified. Japanese press quoting the release: 「算出期間は、CoincheckにおけるNEMの売買停止時から本リリース時までの加重平均の価格で、JPYにて返金いたします。」 (as surfaced in search results).
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://coinpost.jp/?p=12708> ; <https://www.coindesk.com/coincheck-starts-crypto-hack-refunds-and-allows-limited-trading> ; <https://cointelegraph.com/news/coincheck-to-refund-all-customers-affected-by-hack-faced-by-community-support>
- **Verification:** secondary. Only search-result summaries seen. Sources differ on the eligibility wording (held 'at the time of the unauthorised transfer' vs 'at the close of 26 Jan').
- **Position:** `snapshot_at_hack`

#### 12. Youbit (Yapian) hack and bankruptcy filing

- **Citation:** Yapian announcement of 19 December 2017 (Korea)
- **Jurisdiction / year / forum:** South Korea / 2017 / Exchange decision / bankruptcy filing
- **Facts:** Second hack in eight months took about 17% of the exchange's assets at about 4:35 a.m. on 19 December 2017.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** All customer balances were marked down to 75% as of the incident, with the remainder to follow after the bankruptcy settlement (insurance and sale of the business). Uniform haircut on balances at the incident moment; no post-incident trading class.
- **Relevance to Gonka:** Context: socialised haircut at the incident moment.
- **Quote / pinpoint:** No verbatim quote verified.
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://www.cnbc.com/2017/12/19/yapian-youbit-exchange-files-bankruptcy.html> ; <https://coindesk.com/south-korean-bitcoin-exchange-declare-bankruptcy-hack/>
- **Verification:** secondary. Search-result summaries only.
- **Position:** `context`

### B. Bridge and protocol hacks: compensation programmes

#### 13. Ankr aBNBc infinite-mint exploit — snapshot, 'do not trade' warning and exclusion of post-exploit speculation

- **Citation:** Ankr, 'The aBNBc Token Report' (2 December 2022) and after-action report (20 December 2022)
- **Jurisdiction / year / forum:** DeFi protocol (BNB Chain); no court / 2022 / Protocol team compensation programme
- **Facts:** On 1-2 December 2022 an attacker with a compromised deployer key minted trillions of unbacked aBNBc and dumped them; the token price collapsed to near zero while people kept trading and arbitraging it.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Ankr fixed one snapshot (2 Dec 2022 00:43:18 UTC, described as identifying holders 'before' the exploit), re-issued a new token (ankrBNB) to holders as of the snapshot and bought BNB to compensate affected liquidity providers. It explicitly told users not to trade or speculatively buy the token and stated that trading after the exploit would not be compensated: 'All trades done after this time will not affect the holder's reimbursement' (Cointelegraph paraphrase).
- **Relevance to Gonka:** The closest factual analogue (unbacked mint, price collapse, continued trading, explicit warning). Ankr used a HARD cut-off — and placed it at the exploit snapshot, i.e. earlier than its own warning. Post-exploit buyers got nothing. Gonka's proposal (obligation up to the warning, discretion after) is more generous than Ankr's.
- **Quote / pinpoint:** "Do not trade aBNBc or speculatively buy it at a discount." "We understand diluted aBNBc was speculatively traded after the exploit occurred, but we are only able to compensate LP's caught off guard by the event." "Our snapshot taken on Dec-02-2022 12:43:18 AM +UTC will identify you if you are an affected LP." "We will use a snapshot and airdrop the newly-released ankrBNB tokens to all valid aBNBc holders before the snapshot."
- **Sources opened:** <https://www.ankr.com/blog/the-abnbc-token-report/> ; <https://www.ankr.com/blog/after-action-report-our-findings-from-abnbc-token-exploit/> ; <https://cointelegraph.com/news/ankr-says-no-one-should-trade-abnbc-only-lps-caught-off-guard-will-be-compensated>
- **Verification:** primary. Ankr's own blog posts opened (quotes extracted via an automated fetch tool — re-check wording before publication). Whether the snapshot second coincides exactly with the exploit transaction was not independently checked on-chain.
- **Position:** `hard_cutoff`

#### 14. pNetwork pGALA (BNB Chain) incident — two snapshots

- **Citation:** pNetwork, 'pGALA post-mortem: measures taken to safeguard the ecosystem from malicious actors and recovery plan' (November 2022); Gala v. pNetwork lawsuit (filed 2023)
- **Jurisdiction / year / forum:** DeFi bridge (BNB Chain); US lawsuit by Gala / 2022 / Bridge operator recovery plan
- **Facts:** On 3 November 2022 pNetwork, fearing a compromised key, itself minted billions of unbacked pGALA and drained the PancakeSwap pool ('white-hat' drain, about US$4.3m in BNB). pGALA became worthless but kept trading; pNetwork told users to treat the pool as invalid and not to buy pGALA.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Two-tier plan as reported: (1) new pGALA re-issued 1:1 to holders as of the pre-drain snapshot; (2) a SECOND snapshot on 7 November 2022 08:00 UTC — four days after the incident and warning — for distributing the BNB recovered in the drain to holders of the now-uncollateralised pGALA (0.00000109 BNB per pGALA); any transfer after the second snapshot is void for the plan. So people who bought after the incident but before the announced second cut-off got a refund-type payment from the drained funds, not the full pre-incident value. The BNB leg was reported 'on hold' in 2023 and Gala sued pNetwork.
- **Relevance to Gonka:** A real two-tier model: full restoration for pre-incident holders, a lesser pro-rata refund for post-incident buyers up to a later, publicly announced cut-off, nothing after it. Supports a gradient rather than a single hard line — and shows the post-incident tier was only the return of money actually recovered.
- **Quote / pinpoint:** As surfaced by search from the pNetwork post: "Any on-chain transfer of pGALA happening on BSC after the second snapshot will not be taken into account and thus will be considered void in the scope of the recovery plan." Press paraphrase of the warning: pNetwork told users to "consider the existing pancakeswap pool to be invalid" and not buy pGALA (Cryptopolitan).
- **Sources opened:** <https://www.theblock.co/news/regulation/2022-11-04-developers-of-pnetwork-bridge-drain-4-3-million-from-pancakeswap-in-white-hat-attack-182969> ; <https://support.binance.us/en/articles/9843333-binance-us-will-support-the-pnetwork-pnt-recovery-plan-to-airdrop-bnb-bsc-to-pgala-bsc-holders> ; <https://cointelegraph.com/news/gamefi-project-gala-files-28m-lawsuit-against-pnetwork>
- **Sources located but NOT opened:** <https://medium.com/pnetwork/pgala-post-mortem-measures-taken-to-safeguard-the-ecosystem-from-malicious-actors-and-recovery-6407048f4497>
- **Verification:** secondary. The pNetwork Medium post returned HTTP 403; its wording is known only through search-engine summaries. Binance.US support page (opened) confirms the snapshot window 3 Nov 2022 - 7 Nov 2022 and the BNB ratio. Exact definition of the first snapshot and of who received new pGALA not verified.
- **Position:** `gradient_or_grace`

#### 15. Cover Protocol infinite-mint exploit — snapshot at the last pre-exploit block

- **Citation:** Cover Protocol compensation plan (announced 29-31 December 2020); snapshot at Ethereum block 11,541,218
- **Jurisdiction / year / forum:** DeFi protocol (Ethereum); no court / 2020 / Protocol team compensation plan
- **Facts:** On 28 December 2020 an attacker minted about 40 quintillion COVER; the price fell about 90% and trading continued on DEXs and on Binance. One attacker (Grap.finance) returned about 4,350 ETH.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Snapshot at 'the last transaction block before the exploit began'; new COVER issued 1:1 to holders and LPs as of that block; returned ETH distributed to pre-exploit LPs. Anyone who bought after the snapshot was outside the protocol's plan.
- **Relevance to Gonka:** Classic snapshot-at-hack model: the protocol's own obligation runs only to pre-exploit holders.
- **Quote / pinpoint:** "the Cover Protocol team took a snapshot at block height 11,541,218, the last transaction block before the exploit began." "tokenholders will receive new COVER coins on a one-to-one ratio with their initial wallet balance before the hack." (Cointelegraph, 31 Dec 2020)
- **Sources opened:** <https://cointelegraph.com/news/cover-protocol-announces-compensation-plan-following-mining-contract-attack>
- **Verification:** secondary. Press article quoting the plan opened; Cover's own post not opened.
- **Position:** `snapshot_at_hack`

#### 16. Binance SAFU compensation for users who bought COVER after the exploit snapshot

- **Citation:** Binance announcement of 31 December 2020 (SAFU Fund, US$10,107,505)
- **Jurisdiction / year / forum:** Centralised exchange (voluntary); no court / 2020 / Exchange discretionary compensation
- **Facts:** Many Binance customers bought COVER after the protocol's snapshot block but before Binance halted trading, and would have been left with worthless old tokens.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Binance, at its own discretion and from its own insurance fund, compensated users who bought COVER on Binance after the snapshot time and suffered losses, using the moment Binance HALTED TRADING as the outer limit ('We will also incorporate the time that COVER trading was halted on Binance'). Reported exclusion: no compensation for users who merely deposited tokens between the snapshot and the halt.
- **Relevance to Gonka:** Precedent for exactly the proposed two-layer logic: the issuer's obligation stops at the exploit snapshot; trades between the exploit and the venue's official stop are covered by a separate, voluntary (discretionary) pool. Here the grace window ends at the official halt — the functional equivalent of the 'Do not trade WGNK' warning — and the payer was the venue, not the protocol.
- **Quote / pinpoint:** "Binance will utilize the Binance SAFU Fund to recompense a total of $10,107,505 USD" "(distributed in 8,171,634.10 BUSD and 2,581.16 ETH) to affected and eligible users"; "We will also incorporate the time that COVER trading was halted on Binance" (Binance, as quoted by Decrypt, 31 Dec 2020).
- **Sources opened:** <https://decrypt.co/52936/binance-pledges-10-million-to-compensate-cover-finance-hack-victims>
- **Sources located but NOT opened:** <https://www.fxstreet.com/cryptocurrencies/news/binance-to-reimburse-10-million-to-affected-users-over-cover-incident-202012310636>
- **Verification:** secondary. Press article opened; Binance's announcement itself not opened. The deposit-only exclusion is from a search summary.
- **Position:** `gradient_or_grace`

#### 17. The DAO attack and Ethereum hard fork

- **Citation:** SEC, Report of Investigation Pursuant to Section 21(a) of the Securities Exchange Act of 1934: The DAO, Release No. 81207 (25 July 2017)
- **Jurisdiction / year / forum:** United States (regulator report) / Ethereum / 2016 / Ethereum community hard fork (20 July 2016); facts recorded by the US SEC
- **Facts:** On 17 June 2016 an attacker diverted about 3.6m ETH (about one third of The DAO's funds). DAO tokens kept trading on exchanges at a discount for a month.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The hard fork moved all funds to a recovery contract where 'DAO Token holders could exchange their DAO Tokens for ETH'. There was no holder snapshot at the attack: redemption followed the token, so anyone holding DAO tokens at redemption — including people who bought at a discount after the attack was public — was made whole.
- **Relevance to Gonka:** CONTRADICTS a cut-off model: in the best-known precedent, post-incident buyers were treated identically to original holders (and profited). The distinguishing feature is that the remedy restored the asset's backing in full; it did not compensate trading losses. It also means pre-attack holders who panic-sold after the attack got nothing.
- **Quote / pinpoint:** "The Hard Fork had the effect of transferring all of the funds raised (including those held by the Attacker) from The DAO to a recovery address, where DAO Token holders could exchange their DAO Tokens for ETH." "All DAO Token holders who adopted the Hard Fork could exchange their DAO Tokens for ETH, and avoid any loss of the ETH they had invested." (pp. 9-10)
- **Sources opened:** <https://www.sec.gov/litigation/investreport/34-81207.pdf>
- **Verification:** primary. SEC report PDF downloaded and text-extracted. The observation that post-attack buyers profited is an inference from the bearer-redemption mechanism, not a statement in the report.
- **Position:** `contradicts`

#### 18. Nomad bridge hack — pro-rata bridge-back of recovered funds

- **Citation:** Nomad, 'Bridge Relaunch Guide' (7 December 2022)
- **Jurisdiction / year / forum:** DeFi bridge (Ethereum and others); no court / 2022 / Bridge operator recovery process (KYC via CoinList)
- **Facts:** About US$190m drained from the Nomad bridge on 1 August 2022; roughly 20% was returned by white-hats. Bridged 'madAssets' lost their backing and traded at a discount.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Whoever holds madAssets, passes KYC and bridges back receives a non-transferable NFT entitling them to a pro-rata share of recovered funds. No snapshot and no condition on when the madAssets were acquired was stated in the sources seen.
- **Relevance to Gonka:** CONTRADICTS a cut-off by acquisition time: the claim follows the wrapped token, so post-hack buyers of discounted wrapped assets share equally with original holders. (It is a partial recovery, shared pro rata; nobody is made whole.)
- **Quote / pinpoint:** The protocol "will allow users to bridge back madAssets and access a pro-rata share of recovered funds" (Cointelegraph, 8 Dec 2022, citing Nomad's guide).
- **Sources opened:** <https://cointelegraph.com/news/nomad-releases-bridge-relaunch-guide-after-patching-contract-vulnerability>
- **Sources located but NOT opened:** <https://medium.com/nomad-xyz-blog/nomad-bridge-relaunch-guide-3a4ef6624f90>
- **Verification:** secondary. Nomad's Medium guide could not be opened; absence of an acquisition-date condition is inferred from secondary reporting and should be confirmed against the guide.
- **Position:** `contradicts`

#### 19. Euler Finance — redemption of returned funds

- **Citation:** Euler governance forum, 'Plan for Redemption of Euler Funds V2' (12 April 2023)
- **Jurisdiction / year / forum:** DeFi protocol (Ethereum); no court / 2023 / Protocol/DAO redemption plan
- **Facts:** About US$197m taken on 13 March 2023; the attacker returned essentially all recoverable funds within three weeks. The protocol was paused immediately after the attack.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Each sub-account's position is frozen at 'the block the protocol was disabled' (immediately after the hack): liabilities are notionally repaid at that block, and the resulting net asset value is the claim. Claims are capped (NAV x 1.005 at redemption-time prices); the excess goes to a 'foregone profit' pool for those who would otherwise have gained, instead of being spread as a windfall.
- **Relevance to Gonka:** Returned-funds case like Gonka's: the claim was defined by the position at the block of the protocol's own emergency action, and the plan contains an explicit anti-windfall cap. Positions could not be traded after the pause, so there was no post-incident trading class.
- **Quote / pinpoint:** "For each sub-account, Euler simulates the repayment of all liabilities at the block the protocol was disabled." NAV is computed using "a secure pricing method snapshot taken at a pre-announced future "redemption" block."
- **Sources opened:** <https://forum.euler.finance/t/plan-for-redemption-of-euler-funds-v2/947>
- **Sources located but NOT opened:** <https://forum.euler.finance/t/plan-for-redemption-of-euler-funds/906>
- **Verification:** primary. Governance forum post opened (quotes extracted via an automated fetch tool).
- **Position:** `snapshot_at_hack`

#### 20. KyberSwap Elastic exploit — Treasury Grant Program

- **Citation:** KyberSwap, 'KyberSwap Treasury Grant Program' (20 December 2023)
- **Jurisdiction / year / forum:** DeFi protocol (multi-chain); no court / 2023 / Protocol treasury grant (explicitly a grant, with KYC)
- **Facts:** About US$48.8m drained from Elastic liquidity pools on 22 November 2023 (10:54 PM UTC), followed by copy-cat 'mirror bot' drains.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Affected assets are valued in USD 'at the last block prior to the Primary Exploit' (or prior to the relevant follow-on drain). Only liquidity providers whose assets were taken or locked (Categories 1, 2 and 4) qualify; other categories are outside the grant. Users choose 60% over 3 months or 100% over 12 months, or opt out. Grant terms include a refund obligation if assets are later recovered. The programme is framed as a voluntary treasury grant, not as a debt. Swappers/post-exploit traders are not addressed.
- **Relevance to Gonka:** Reference value at the last pre-exploit block; compensation labelled a grant (discretionary); built-in refund if funds are recovered — a net-loss/no-double-recovery device.
- **Quote / pinpoint:** Reference value "as quoted on CoinGecko at the last block prior to the Primary Exploit"; the Grant Terms "will include Treasury Grant refund requirements in the event that some or all Affected Assets are recovered."
- **Sources opened:** <https://blog.kyberswap.com/kyberswap-treasury-grant-program/>
- **Verification:** primary. KyberSwap's own blog post opened (quotes extracted via an automated fetch tool).
- **Position:** `snapshot_at_hack`

#### 21. Balancer v2 exploit — distribution of rescued funds

- **Citation:** Balancer governance, '[BIP-892] Distribution of Rescued Funds from Balancer v2 November 3rd 2025 Attacks' (posted 27 November 2025)
- **Jurisdiction / year / forum:** DeFi protocol (multi-chain); no court / 2025 / DAO governance proposal
- **Facts:** About US$110-128m drained from Balancer v2 composable stable pools on 3 November 2025; about US$8m was rescued by white-hats and the team.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Eligibility is determined by pool-token (BPT) holdings at the 'last block before first exploit tx on each network' (e.g. Ethereum block 23717626). Distribution is non-socialised (each pool's rescued funds go only to that pool's LPs) and pro rata to holdings at the snapshot. 180-day claim window. Transfers of BPT after the exploit are not addressed — the pre-exploit snapshot makes them irrelevant.
- **Relevance to Gonka:** Recent, primary-sourced example of the mainstream DeFi rule: the snapshot is the last block before the exploit; later holders are simply not in the class.
- **Quote / pinpoint:** Snapshot rule: "last block before first exploit tx on each network". "Pro-rata by BPT holdings — Distribution proportional to each holder's share of the pool's BPT at the snapshot block". "Non-socialized — Each affected pool's rescued funds are distributed only to LPs of that specific pool and network".
- **Sources opened:** <https://forum.balancer.fi/t/bip-892-distribution-of-rescued-funds-from-balancer-v2-november-3rd-2025-attacks/6883>
- **Verification:** primary. Governance forum post opened (quotes extracted via an automated fetch tool). Whether the proposal passed and was executed was not checked.
- **Position:** `snapshot_at_hack`

#### 22. Beanstalk governance exploit — 'Unripe' assets for pre-exploit holders

- **Citation:** Beanstalk documentation ('Barn'), Replant / Barn Raise, 2022
- **Jurisdiction / year / forum:** DeFi protocol (Ethereum); no court / 2022 / DAO recapitalisation plan
- **Facts:** On 17 April 2022 a flash-loan governance attack drained about US$77m of non-Bean liquidity (US$182m gross). BEAN lost its peg.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Claims ('Unripe Beans', 'Unripe LP') were issued only to those who held 'in the block prior to the exploit', 1:1 to pre-exploit balances, vesting as the protocol was recapitalised.
- **Relevance to Gonka:** Another primary-sourced snapshot at the last pre-exploit block.
- **Quote / pinpoint:** "Farmers who held Beans in the block prior to the exploit received 1 Unripe Bean for every pre-exploit Bean"
- **Sources opened:** <https://docs.bean.money/almanac/farm/barn>
- **Verification:** primary. Protocol documentation opened (quote extracted via an automated fetch tool).
- **Position:** `snapshot_at_hack`

#### 23. Eminence (EMN) exploit — distribution of funds returned by the hacker

- **Citation:** Yearn/Eminence refund, September-October 2020 (snapshot at Ethereum block 10954410)
- **Jurisdiction / year / forum:** DeFi protocol (Ethereum); no court / 2020 / Developer-run refund
- **Facts:** About US$15m drained from the unreleased Eminence contracts on 28-29 September 2020; the attacker sent back 8m DAI.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The returned 8m DAI was distributed (about 50% refund) according to balances at 'a snapshot the block before the hack took place' (3,656 addresses). Later buyers were not in the snapshot.
- **Relevance to Gonka:** Hacker-returned funds were allocated strictly by the last pre-hack block.
- **Quote / pinpoint:** "a forthcoming 50% refund as per balances taken at a snapshot the block before the hack took place" (Decrypt, 29 Sep 2020)
- **Sources opened:** <https://decrypt.co/43292/eminence-finance-exploit-leads-to-degen-soul-searching>
- **Verification:** secondary. Press article opened.
- **Position:** `snapshot_at_hack`

#### 24. Terra 2.0 airdrop — pre-attack and post-attack snapshots with different weights

- **Citation:** Terra governance proposal 1623 and 'Terra 2.0 — LUNA Airdrop' (May 2022)
- **Jurisdiction / year / forum:** Layer-1 blockchain; no court (not a hack — de-peg/collapse) / 2022 / On-chain governance
- **Facts:** UST lost its peg from 7 May 2022 and LUNA collapsed; people kept buying both on the way down.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Two snapshots: 'Pre-attack' (block 7,544,910, 7 May 2022 14:59:37 UTC) and 'Post-attack' (block 7,790,000, 26 May 2022 16:38:08 UTC). New LUNA allocation: pre-attack LUNA holders 35%, pre-attack aUST holders 10%, post-attack LUNA holders 10%, post-attack UST holders 15%, community pool 30%. Post-incident buyers were included, but at a far lower per-token rate (reported Binance ratios: 1 LUNC pre-attack = 1.034735071 LUNA vs 1 LUNC post-attack = 0.000015307927 LUNA).
- **Relevance to Gonka:** The best-known gradient: both groups recognised, pre-incident holders heavily favoured. Shows that a community may choose to give post-incident buyers something rather than nothing — supports 'discretionary', not 'excluded'. Not a hack and not a compensation of trading losses, so analogy is by structure only.
- **Quote / pinpoint:** No verbatim quote verified.
- **Sources opened:** <https://www.kucoin.com/blog/all-you-need-to-know-about-terra-2.0-and-the-luna-airdrop>
- **Sources located but NOT opened:** <https://medium.com/terra-money/terra-2-0-luna-airdrop-calculation-logic-3eb752c25837> ; <https://dappradar.com/blog/terra-chain-2-0-and-luna-airdrop-approved-for-may-27>
- **Verification:** secondary. Block heights, timestamps and percentages come from search-result summaries of Terra's Medium posts and exchange notices; the opened KuCoin page confirms only that eligibility was based on 'Pre-Attack and Post-Attack snapshots'.
- **Position:** `gradient_or_grace`

#### 25. Elixir deUSD wind-down after the Stream Finance loss

- **Citation:** Elixir announcements of 6-7 November 2025
- **Jurisdiction / year / forum:** DeFi stablecoin issuer; no court / 2025 / Issuer redemption programme
- **Facts:** After Stream Finance disclosed a US$93m loss, Elixir's deUSD (largely backed by a loan to Stream) fell by up to 98%. Elixir processed redemptions for about 80% of non-Stream holders and then sunset the token.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Elixir took a snapshot of all remaining deUSD/sdeUSD balances at the time of its announcement; snapshotted balances are redeemable 1:1 for USDC through a claims portal; minting and redemptions were disabled. Purchases after the snapshot carry no claim. (Dip-buyers before the snapshot were paid $1.)
- **Relevance to Gonka:** Precedent for a cut-off placed at the issuer's official announcement rather than at the triggering event. Caveat: it did not apply a net-loss test — whoever held at the snapshot was paid in full, including discount buyers.
- **Quote / pinpoint:** Elixir "has reportedly taken a snapshot of all remaining deUSD and sdeUSD holder balances", which "can be redeemed 1:1 for USDC when a claims portal opens" (The Block, 6 Nov 2025).
- **Sources opened:** <https://www.theblock.co/post/377961/elixir-sunsets-deusd-synthetic-stablecoin-following-stream-finance-unwinding-aims-full-redemptions>
- **Verification:** secondary. Press article opened; Elixir's own post not opened; exact snapshot time not established.
- **Position:** `hard_cutoff`

#### 26. Hyperliquid JELLY incident — users made whole except flagged addresses

- **Citation:** Hyperliquid statement of 26 March 2025
- **Jurisdiction / year / forum:** DeFi derivatives exchange; no court / 2025 / Validator vote and Hyper Foundation reimbursement
- **Facts:** A trader manipulated the JELLY perpetual market to load losses onto the protocol vault; validators delisted the market and settled it at a set price.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** All users were reimbursed by the Foundation automatically from on-chain data, EXCEPT addresses flagged as involved in the manipulation.
- **Relevance to Gonka:** Precedent for excluding from compensation those who exploited the incident — supports carving out the attacker's counterparties, arbitrage bots and anyone who knowingly profited.
- **Quote / pinpoint:** "All users apart from flagged addresses will be made whole from the Hyper Foundation"; "This will be done automatically in the coming days based on onchain data." (as quoted by Cointelegraph, 26 Mar 2025)
- **Sources opened:** <https://cointelegraph.com/news/hyperliquid-delists-jelly-perps-citing-suspicious-activity>
- **Verification:** secondary. Press article quoting the statement opened.
- **Position:** `net_loss_principle`

#### 27. Curve / Vyper re-entrancy exploit — DAO vote to reimburse LPs

- **Citation:** Curve DAO vote, December 2023 (about US$49.2m: US$7.2m recovered ETH + about US$42m vested CRV)
- **Jurisdiction / year / forum:** DeFi protocol (Ethereum); no court / 2023 / DAO governance vote (about 94% in favour, as reported)
- **Facts:** On 30 July 2023 several Curve pools compiled with vulnerable Vyper versions were drained (about US$61-70m); most funds were returned by white-hats or the attackers.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The DAO voted to make LPs of the affected pools whole for the shortfall remaining AFTER deducting recovered funds; the unrecovered part was paid in CRV vested for a year. Loss was computed per affected pool; secondary-market traders of the affected tokens were not part of the scheme.
- **Relevance to Gonka:** Net-loss approach (compensation = loss minus recoveries) adopted by token-holder vote; compensation limited to those whose assets were in the exploited contracts.
- **Quote / pinpoint:** No verbatim quote verified.
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://cointelegraph.com/news/curve-finance-disburse-49-million-compensation-hack-victims> ; <https://dlnews.com/articles/defi/curve-votes-44-million-usd-in-crv-tokens-for-lp-hack-victims/>
- **Verification:** secondary. Search-result summaries only; governance proposal text not opened.
- **Position:** `net_loss_principle`

#### 28. Mango Markets exploit; United States v. Eisenberg

- **Citation:** Mango DAO vote of October 2022; United States v. Eisenberg, No. 23-cr-10 (S.D.N.Y.), Opinion and Order of 23 May 2025 (Subramanian J.)
- **Jurisdiction / year / forum:** Solana DeFi protocol / United States (S.D.N.Y.) / 2022 / DAO governance settlement; US federal criminal court
- **Facts:** On 11 October 2022 Avraham Eisenberg inflated the MNGO price and borrowed out about US$110-117m. The DAO voted to let him keep US$47m in exchange for returning about US$67m. He was convicted in April 2024; in May 2025 the court vacated two convictions for improper venue and acquitted on the third.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The DAO used the returned funds plus treasury so that 'all mango depositors will be made whole' — compensation ran to depositors (by their balances at the exploit), not to MNGO secondary-market traders. The criminal ruling turned on venue and on the absence of a false representation to a permissionless protocol.
- **Relevance to Gonka:** Returned-funds settlement by DAO vote; and a reminder that courts may not treat an on-chain exploit as fraud, so a community scheme should not depend on a legal finding of wrongdoing.
- **Quote / pinpoint:** Proposal wording as reported: "all mango depositors will be made whole".
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://blockworks.co/news/mango-dao-readies-42m-to-make-users-whole> ; <https://nysd.uscourts.gov/sites/default/files/2025-05/23cr10%20Opinion%20and%20Order.pdf> ; <https://www.theblock.co/post/355666/u-s-judge-overturns-fraud-convictions-of-mango-markets-exploiter-eisenberg-determining-improper-venue>
- **Verification:** secondary. Search-result summaries only; the SDNY opinion was located but not opened.
- **Position:** `context`

#### 29. Full-replenishment bridge cases: Wormhole (2022), Ronin (2022), Poly Network (2021)

- **Citation:** Wormhole: Jump Crypto replaced 120,000 ETH (February 2022). Ronin: Sky Mavis reimbursed 117,600 ETH and 25.5m USDC and reopened the bridge on 28 June 2022. Poly Network: attacker returned the funds (August 2021).
- **Jurisdiction / year / forum:** DeFi bridges; no court (see separate entry for the Jump/Oasis court order) / 2022 / Sponsor/backer replenishment
- **Facts:** In each case the bridge's backing was drained (about US$326m, US$625m and US$610m respectively) and then restored in full by a backer or by the attacker.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** No cut-off or snapshot was needed: once backing is restored token-for-token, every holder of the wrapped asset — whenever they acquired it — is whole. Ronin restored ETH and USDC in kind (dollar value at reopening was far below the hack-date value). None of these programmes compensated secondary-market trading losses of people who sold at depressed prices in the interim.
- **Relevance to Gonka:** Sets the baseline: restoring the bridge reserves (as happened after the Gonka hacker's return) is what the industry treats as the bridge's core obligation. Compensation of interim trading losses goes beyond what Wormhole, Ronin or Poly did — which supports calling at least part of it discretionary.
- **Quote / pinpoint:** "Sky Mavis has now reimbursed 117,600 ETH and 25.5 million USDC by providing the ETH liquidity to back users' Wrapped ETH (wETH) on the Ronin network" (as surfaced in search results).
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://blockworks.co/news/sky-mavis-reopening-ronin-bridge-with-enhanced-security> ; <https://cointelegraph.com/magazine/the-aftermath-of-axie-infinity-s-650m-ronin-bridge-hack>
- **Verification:** secondary. Search-result summaries only. Poly Network details rest on general reporting; the statement that no trading losses were compensated is the researcher's reading (no programme of that kind was found), not a sourced statement.
- **Position:** `context`

#### 30. Harmony Horizon bridge hack — reimbursement proposals

- **Citation:** Harmony reimbursement proposal (July 2022) and revised recovery plan (September 2022)
- **Jurisdiction / year / forum:** Layer-1 blockchain / bridge; no court / 2022 / Core team proposal to on-chain governance
- **Facts:** About US$99.3m stolen on 23 June 2022 across about 65,000 wallets and 14 asset types; bridged assets on Harmony de-pegged.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The first plan would have minted 2.48-4.97bn ONE and paid it monthly 'based on the value of tokens lost when a snapshot of the blockchain is taken'; it was withdrawn after community backlash against inflation. The revised plan promised '0% minting' and treasury-funded recovery. Final outcome for holders not established.
- **Relevance to Gonka:** Shows a community rejecting compensation that dilutes existing holders — relevant to how a Gonka compensation is funded — and that reimbursement was treated as a matter for governance, not as an automatic debt.
- **Quote / pinpoint:** Harmony stated the goal of "preserving the foundation of the Harmony blockchain with 0% minting" (as surfaced in search results).
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://www.theblock.co/post/172364/harmony-announces-update-on-horizon-bridge-attack-recovery-plan> ; <https://cointelegraph.com/news/backlash-as-harmony-proposes-minting-4-97b-tokens-to-reimburse-victims>
- **Verification:** secondary. Search-result summaries only; snapshot date and final distribution not verified.
- **Position:** `context`

#### 31. Fantom Foundation Ltd v Multichain Foundation Ltd

- **Citation:** [2024] SGHC 173 (Mohamed Faizal JC, 8 July 2024)
- **Jurisdiction / year / forum:** Singapore / 2024 / General Division of the High Court of Singapore (assessment of damages after default judgment)
- **Facts:** On 7 July 2023 the assets backing Multichain-bridged tokens were drained/dissipated; wrapped tokens on Fantom collapsed. Fantom Foundation sued for the lost value of its wrapped assets and for 4.175m FTM under a liquidity agreement.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Damages for the wrapped assets = their value on 6 July 2023 (the day before the breach) LESS their residual value on 18 September 2023. The court applied the general rule of valuing loss by reference to the date of breach, and expressly declined to use 8 July 2023 (the day after the incident became public) because prices that day were too volatile to be reliable. Award: US$58,620.55 on this head; US$2,187,870.55 in total.
- **Relevance to Gonka:** A court judgment on a bridge collapse that (i) takes the last pre-incident day as the reference price, (ii) deducts the residual value of what the claimant still holds (net loss), and (iii) rejects post-incident panic prices as a measure. Strong support for a pre-hack reference price and a net-loss computation.
- **Quote / pinpoint:** [21] "the value of the wrapped assets on 6 July 2023, less any residual value on 18 September 2023." [22] the claimant "invites the court to assess the loss of value with reference to the date of the breach", "which is the general position on valuing compensatory damages for breach of contract in Singapore". [27] "I therefore accept that the damages claim should be valued at US$58,620.55."
- **Sources opened:** <https://www.elitigation.sg/gd/s/2024_SGHC_173>
- **Verification:** primary. Official judgment page opened; quotes are short fragments returned by an automated fetch tool — re-check full paragraph wording before publication. Default judgment (undefended), so the valuation approach was not contested.
- **Position:** `net_loss_principle`

#### 32. PAID Network infinite-mint exploit

- **Citation:** PAID Network post-mortem, March 2021
- **Jurisdiction / year / forum:** DeFi token (Ethereum); no court / 2021 / Project team
- **Facts:** On 5 March 2021 an attacker with the proxy admin key minted about 59.5m PAID and sold about 2.5m for about 2,040 ETH; price fell about 85%.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** The team announced a new contract restoring all balances from a pre-hack snapshot; activity during the exploit was not covered, and the announcement reportedly did not say what would happen to people who bought during the dip.
- **Relevance to Gonka:** Same pattern (pre-hack snapshot; post-exploit buyers unaddressed).
- **Quote / pinpoint:** No verbatim quote verified.
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://beincrypto.com/paid-network-releases-exploit-post-mortem/> ; <https://www.halborn.com/blog/post/explained-the-paid-network-hack-march-2021>
- **Verification:** unverified. Source page returned HTTP 403; only a search-result summary was seen.
- **Position:** `snapshot_at_hack`

#### 33. PancakeBunny flash-loan exploit — compensation of 'Original Holders'

- **Citation:** PancakeBunny 'Go Forward Plan', May 2021
- **Jurisdiction / year / forum:** DeFi protocol (BNB Chain); no court / 2021 / Project team
- **Facts:** On 19 May 2021 an attacker minted about 7m BUNNY via a flash-loan price manipulation and dumped it; BUNNY fell more than 95%.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Compensation (new pBUNNY token plus a fee-funded Compensation Pool) was promised to 'Original Holders' for the difference between the market cap at the time of the exploit and the retained value. Exact snapshot definition not verified.
- **Relevance to Gonka:** Unbacked mint + price crash; compensation directed to pre-exploit holders only.
- **Quote / pinpoint:** As surfaced in search results: "We will compensate Original Holders for the difference between the market cap at the time of the exploit and the current retained value of $39M (the Losses) by issuing a new token, pBUNNY, and by creating a Compensation Pool."
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://beincrypto.com/pancakebunny-postmortem-details-attack-compensation-plan>
- **Verification:** unverified. Source page returned HTTP 403; quote known only through a search-result summary.
- **Position:** `snapshot_at_hack`

#### 34. Cetus (Sui) exploit — validator vote and recovery plan

- **Citation:** Sui on-chain community vote closed 29 May 2025; Cetus recovery plan (June 2025)
- **Jurisdiction / year / forum:** Layer-1 blockchain / DEX; no court / 2025 / Validator governance vote; protocol recovery plan
- **Facts:** About US$223m drained from Cetus liquidity pools on 22 May 2025; validators froze about US$162m of the attacker's funds on Sui.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Validators (about 90.9% in favour) moved the frozen funds to a multisig held in trust for affected accounts; with a US$30m Sui Foundation loan and treasury funds, LPs of the affected pools regained liquidity, and residual losses were covered by a compensation contract in vested CETUS (15% of supply). Compensation ran to LPs of exploited pools; no snapshot detail verified.
- **Relevance to Gonka:** Context: compensation directed at those whose assets were in the exploited contracts; residual paid in vested native tokens.
- **Quote / pinpoint:** No verbatim quote verified.
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://www.sui.io/blog/cetus-incident-response-onchain-community-vote> ; <https://cointelegraph.com/news/sui-passes-governance-vote-to-recover-162m-cetus-funds>
- **Verification:** secondary. Search-result summaries only.
- **Position:** `context`

### C. Crypto as property; recovery and tracing of stolen crypto

#### 35. Mt. Gox bitcoin ownership case

- **Citation:** Tokyo District Court, Civil Division 28, judgment of 5 August 2015, Heisei 26 (Wa) 33320
- **Jurisdiction / year / forum:** Japan / 2015 / Tokyo District Court
- **Facts:** A customer claimed segregation (return) of 'his' bitcoin from the Mt. Gox bankruptcy estate on the basis of ownership.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Bitcoin is not a tangible thing and cannot be the object of ownership under the Civil Code; the customer has only a bankruptcy claim, valued under insolvency rules. Nothing on post-incident participants.
- **Relevance to Gonka:** Counter-example to the common-law 'crypto is property' line: in a civil-law setting victims may be mere creditors, which makes a negotiated/community compensation scheme more important than proprietary remedies.
- **Quote / pinpoint:** "the bitcoin does not have a physical existence, so that it does not constitute a "tangible thing," nor can be the object of ownership. Thus, the plaintiff does not have ownership of the Bitcoin, nor a right of segregation based on any such ownership." (English paraphrase/translation, Digital Assets Project, University of Oxford)
- **Sources opened:** <https://www.law.ox.ac.uk/sites/default/files/migrated/mtgox_judgment_final.pdf>
- **Verification:** primary. Academic English translation (described by its editors as 'a paraphrase in English ... based on a literal translation') downloaded and text-extracted; not the Japanese original.
- **Position:** `context`

#### 36. Jump Crypto / Oasis counter-exploit of the Wormhole hacker under an English court order

- **Citation:** Order of the High Court of England and Wales received by Oasis on 21 February 2023 (order and any judgment not published; case name not verified)
- **Jurisdiction / year / forum:** England and Wales / 2023 / High Court of England and Wales
- **Facts:** The Wormhole attacker had placed about 120,000 ETH-equivalent into Oasis vaults. Under a court order, the Oasis multisig upgraded the vault contracts and transferred the assets to a court-authorised third party (identified by Blockworks as Jump Crypto), about US$140-225m depending on valuation.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Not about cut-offs. Shows an English court ordering an intermediary with technical control to retrieve stolen crypto for the party who had already made victims whole (subrogation-like outcome).
- **Relevance to Gonka:** Recovery by the party that funded compensation is recognised in practice: whoever pays victims can step into their shoes against the attacker and recovered assets.
- **Quote / pinpoint:** Oasis statement (as quoted by Blockworks): it "retain[s] no control or access to these assets."
- **Sources opened:** none (see verification note)
- **Sources located but NOT opened:** <https://blockworks.co/news/jump-crypto-wormhole-hack-recovery> ; <https://cointelegraph.com/news/jump-crypto-oasis-app-counter-exploits-wormhole-hacker-for-225m>
- **Verification:** secondary. Search-result summaries only; the court order is not public.
- **Position:** `context`

#### 37. AA v Persons Unknown, Re Bitcoin

- **Citation:** [2019] EWHC 3556 (Comm) (Bryan J, 13 December 2019)
- **Jurisdiction / year / forum:** England and Wales / 2019 / High Court, Commercial Court
- **Facts:** An insurer paid a ransom of 109.25 BTC after a ransomware attack; 96 BTC were traced to an account at Bitfinex.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Cryptoassets such as bitcoin are property and can be the subject of a proprietary injunction (held for the purposes of interim relief). Nothing on cut-offs.
- **Relevance to Gonka:** Foundation for proprietary claims to stolen/extorted crypto in English law.
- **Quote / pinpoint:** [59] "I consider that a crypto asset such as Bitcoin are property." [61] "crypto currencies are a form of property capable of being the subject of a proprietary injunction."
- **Sources opened:** <https://caselaw.nationalarchives.gov.uk/ewhc/comm/2019/3556>
- **Verification:** primary. Official Find Case Law page opened (quotes extracted via an automated fetch tool).
- **Position:** `context`

#### 38. Tulip Trading Ltd v van der Laan (Bitcoin Association for BSV and others)

- **Citation:** [2023] EWCA Civ 83 (Birss, Popplewell and Lewison LJJ, 3 February 2023)
- **Jurisdiction / year / forum:** England and Wales / 2023 / Court of Appeal (Civil Division)
- **Facts:** A company claiming to have lost access to about US$4bn of bitcoin in a hack argued that the networks' core developers owe fiduciary duties to help owners recover control.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Only that there is a serious issue to be tried on whether developers owe such duties; no finding that they do. The claim did not reach trial (reported discontinued in 2024 — not verified).
- **Relevance to Gonka:** Those who control a protocol or bridge may arguably owe duties to asset holders after a hack; the point is unresolved, so it supports prudence, not a firm legal obligation.
- **Quote / pinpoint:** [91] "The conclusion is not that there is a fiduciary duty in law in the circumstances alleged by Tulip, only that the case advanced raises a serious issue to be tried."
- **Sources opened:** <https://caselaw.nationalarchives.gov.uk/ewca/civ/2023/83>
- **Verification:** primary. Official page opened; the [91] sentence is assembled from two fragments returned by the fetch tool — re-check exact wording.
- **Position:** `context`

#### 39. Quoine Pte Ltd v B2C2 Ltd

- **Citation:** [2020] SGCA(I) 02 (Menon CJ, Phang JA, Prakash JA, French IJ, Mance IJ; 24 February 2020)
- **Jurisdiction / year / forum:** Singapore / 2020 / Singapore Court of Appeal (appeal from the Singapore International Commercial Court)
- **Facts:** After a technical failure on Quoine's exchange, B2C2's algorithm sold ETH for BTC at about 250 times the market rate against margin-called counterparties. Quoine unilaterally reversed the trades the next day.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** By majority the trades stood: no operative mistake, no implied term allowing the platform to reverse trades executed at abnormal prices, and the reversal was a breach of the term that filled orders are irreversible. The court left open whether BTC can be held on trust.
- **Relevance to Gonka:** CAUTION for any argument that trades at hack-distorted prices are legally void or must be unwound: absent an express term or actual knowledge of a mistake, trades at abnormal prices are binding and the counterparty may keep the gain. This points towards compensation funded by the community (ex gratia) rather than a legal clawback from those who traded during the dislocation.
- **Quote / pinpoint:** [7] "no operative mistake on the part of the Counterparties that could be relied upon to vitiate the Trading Contracts". [22] (platform terms) "once an order is filled, you are notified via the Platform and such an action is irreversible." [72] "the Proposed Implied Terms are inherently incompatible with the Irreversible Action Clause".
- **Sources opened:** <https://www.elitigation.sg/gd/s/2020_SGCAI_2>
- **Verification:** primary. Official judgment page opened (first 100,000 characters read by the fetch tool; para 144 on property not reached).
- **Position:** `context`

#### 40. ByBit Fintech Ltd v Ho Kai Xin and others

- **Citation:** [2023] SGHC 199 (Philip Jeyaretnam J, 25 July 2023)
- **Jurisdiction / year / forum:** Singapore / 2023 / General Division of the High Court of Singapore
- **Facts:** A payroll contractor diverted about 4.2m USDT of ByBit's funds to wallets she controlled.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** USDT is a thing in action capable of being held on trust; an institutional constructive trust arises over stolen assets at the time of the theft.
- **Relevance to Gonka:** The victim's proprietary interest crystallises at the moment of theft — the legal analogue of a snapshot at the hack.
- **Quote / pinpoint:** [4] "Like any other thing in action, USDT is capable of being held on trust." [42] "An institutional constructive trust arises over stolen assets at time of the theft".
- **Sources opened:** <https://www.elitigation.sg/gd/s/2023_SGHC_199>
- **Verification:** primary. Official judgment page opened (quotes extracted via an automated fetch tool).
- **Position:** `snapshot_at_hack`

#### 41. CLM v CLN and others

- **Citation:** [2022] SGHC 46 (Lee Seiu Kin J, 4 March 2022)
- **Jurisdiction / year / forum:** Singapore / 2022 / General Division of the High Court of Singapore
- **Facts:** About 109.83 BTC and 1,497.54 ETH were stolen from the claimant's wallets and dissipated through a chain of wallets to exchanges.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Serious arguable case that stolen cryptoassets are property protectable by a proprietary injunction against persons unknown; disclosure orders against exchanges granted. Interlocutory.
- **Relevance to Gonka:** Tracing and freezing of stolen crypto is available against unknown hackers and at exchanges.
- **Quote / pinpoint:** [46] the plaintiff proved "a serious arguable case that the Stolen Cryptocurrency Assets were capable of giving rise to proprietary rights" "which could be protected via a proprietary injunction".
- **Sources opened:** <https://www.elitigation.sg/gd/s/2022_SGHC_46>
- **Verification:** primary. Official judgment page opened (quotes extracted via an automated fetch tool).
- **Position:** `context`

#### 42. Osbourne v Persons Unknown and Ozone Networks Inc

- **Citation:** [2022] EWHC 1021 (Comm) (HHJ Pelling QC, 10 March 2022)
- **Jurisdiction / year / forum:** England and Wales / 2022 / High Court, Commercial Court
- **Facts:** Two NFTs were removed from the claimant's wallet without consent and traced to wallets linked to OpenSea accounts.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** Realistically arguable that NFTs are property; injunction against persons unknown and a Bankers Trust disclosure order against the marketplace granted.
- **Relevance to Gonka:** Further support for proprietary relief over stolen tokens and disclosure orders against platforms.
- **Quote / pinpoint:** [13] "there is at least a realistically arguable case that such tokens are to be treated as property as a matter of English law."
- **Sources opened:** <https://caselaw.nationalarchives.gov.uk/ewhc/comm/2022/1021>
- **Verification:** primary. Official page opened (quote extracted via an automated fetch tool).
- **Position:** `context`

#### 43. D'Aloia v Persons Unknown Category A and others (Bitkub)

- **Citation:** [2024] EWHC 2342 (Ch) (Richard Farnhill, Deputy High Court Judge, 12 September 2024)
- **Jurisdiction / year / forum:** England and Wales / 2024 / High Court, Chancery Division (first full trial of a crypto-fraud tracing claim)
- **Facts:** A fraud victim tried to trace about 2.5m USDT/USDC through mixed wallets to an account at the Thai exchange Bitkub and claimed against the exchange as constructive trustee / in unjust enrichment.
- **Decided or done on the reference moment and on post-incident / post-notice participants:** USDT attracts property rights; but the claim failed because the claimant did not prove that his funds reached the exchange wallet. Tracing through a mixture is available only in equity; FIFO is not the only permissible method, but any method must be methodologically sound and properly evidenced. The judgment's issues summary treats the bona fide purchaser for value without notice defence as available in principle for USDT (though not made out by Bitkub on the facts).
- **Relevance to Gonka:** Two lessons: (i) a compensation scheme based on on-chain tracing must use a documented, defensible methodology; (ii) the law's dividing line for innocent recipients is NOTICE — a purchaser without notice is protected, one with notice is not. An explicit official warning is the natural 'notice' moment, which is the legal logic behind treating post-warning traders differently.
- **Quote / pinpoint:** [5] "USDT attract property rights under English law." [6] "The Claimant has failed to show that any of his funds were received in the 82e6 wallet." [7(iii)] "other methods, if methodologically sound and properly evidenced, are available".
- **Sources opened:** <https://caselaw.nationalarchives.gov.uk/ewhc/ch/2024/2342>
- **Sources located but NOT opened:** <https://cms.law/en/gbr/legal-updates/d-aloia-v-persons-unknown-english-high-court-clarifies-law-on-crypto-and-constructive-trusts>
- **Verification:** primary. Official page opened (first 100,000 characters read by the fetch tool; quotes from the summary section). The bona fide purchaser point is taken from the judgment's summary of issues (paras 22-24) and should be re-read in full before being relied on. The link to an 'official warning = notice' is the researcher's analogy, not a holding.
- **Position:** `context`

