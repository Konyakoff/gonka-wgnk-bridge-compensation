# Why the official warning (19 Nov 2026, 00:24:07 UTC) is the dividing line — case-law and practice dossier

**Status:** research note prepared on 23 Nov 2026 for the Gonka community. It is **not legal advice**. No court has ruled on a
time cut-off in a DeFi-bridge compensation programme; everything below is analogy and principle. Sources were collected by
three independent research passes (blockchain incidents; traditional finance and private law; principles and
counter-arguments). Every authority is listed in `case_law.csv` / `case_law.json` with its verification level:
`primary` (statute, judgment or official report opened and quoted), `secondary` (reputable law-firm note or press),
`unverified` (not to be cited). Detailed write-ups: `dir1_crypto.md`, `dir2_tradfi.md`; the third pass is in
`dir3_principles.json` and summarised in sections 4–6 here.

## 1. The question

On 18 Nov 2026 (18:00:59–18:02:11 UTC) an attacker drained the Gonka↔Ethereum bridge reserve and minted 22,000,000 unbacked
WGNK. The token kept trading. The first public alert came from a security firm at 18:28; the project confirmed the incident
at 00:18:28 on 19 Nov and at **00:24:07 UTC** posted on its official X account: "Do not trade WGNK", do not use the bridge,
withdraw liquidity. The proposal treats losses on trades **before** that post as a commitment the project takes on, and
losses on trades **after** it as discretionary (three options: nothing / a declining share / in full). Is that line defensible?

## 2. Bottom line

1. **A line at the official, explicit warning is defensible — and it is the latest defensible line, i.e. generous.**
   Compensation programmes after DeFi exploits and the one court that has directed a distribution after an exchange hack
   (New Zealand, *Cryptopia*) draw the line earlier — at the moment of the theft — and take later transactions into account.
2. **After a credible public correction, those who trade bear their own risk.** This is the settled rule of securities law
   (US Supreme Court, *Basic v. Levinson*; UK FSMA 2000 Sch. 10; German WpHG § 97).
3. **Notice is not instantaneous.** It must be of a kind that reaches people and leave reasonable time to react
   (*Mullane*; *SEC v. Texas Gulf Sulphur*). This supports a short, declining grace period rather than a cliff — option 2.
4. **Responsibility after notice is apportioned, not all-or-nothing** (England: Law Reform (Contributory Negligence) Act 1945;
   Germany: BGB § 254; Russia: Civil Code art. 404), and regulators use time-stepped liability after notice (US Regulation E).
5. **Nobody profits:** distributions follow net loss — money in minus money out — and the remedy for an over-issued
   instrument is the price paid (*In re Madoff*; UCC § 8-210).
6. **Wording matters.** The research does not support saying the law *requires* the project to compensate secondary-market
   traders. It supports saying the project **assumes a commitment** towards those who lost money while it was silent, and
   that returned funds are not the project's to keep. Post-warning payments are goodwill.

## 3. The four principles on the slide (one best authority each, all opened in a primary source)

| # | Principle | Best authority | Key text |
|---|---|---|---|
| 1 | After the official correction, trading is at one's own risk | *Basic Inc. v. Levinson*, 485 U.S. 224, 248–249 (1988), US Supreme Court | "…those who traded Basic shares after the corrective statements would have no direct or indirect connection with the fraud." |
| 2 | A warning must be able to reach people and leave time to react | *Mullane v. Central Hanover Bank & Trust Co.*, 339 U.S. 306, 314–315 (1950), US Supreme Court | "…notice reasonably calculated, under all the circumstances, to apprise interested parties… it must afford a reasonable time for those interested to make their appearance." |
| 3 | After notice, fault is shared and compensation reduced proportionately | BGB § 254; Russian Civil Code art. 404; Law Reform (Contributory Negligence) Act 1945 s. 1(1); time tiers: 12 CFR § 1005.6(b) (Regulation E) | "…the damages recoverable… shall be reduced to such extent as the court thinks just and equitable having regard to the claimant's share in the responsibility for the damage." (1945 Act) |
| 4 | Nobody profits: net loss, price paid | *In re Bernard L. Madoff Investment Securities LLC*, 654 F.3d 229 (2d Cir. 2011); UCC § 8-210(d) | "…would have the absurd effect of treating fictitious and arbitrarily assigned paper profits as real…" (Madoff); "…may recover from the issuer the price the person or the last purchaser for value paid for it…" (UCC) |

Supporting authorities for principle 1: *Halliburton Co. v. Erica P. John Fund* (Halliburton II), 573 U.S. 258 (2014) — the
presumption covers a plaintiff who "traded the stock between when the misrepresentations were made and when the truth was
revealed"; UK FSMA 2000, Sch. 10 para 3 — no liability if "before the securities in question were acquired, a correction had
been published in a manner calculated to bring it to the attention of persons likely to acquire the securities"; German
WpHG § 97(1), (3) — issuer liable to those who bought during its delay, unless the buyer knew; *The New Flamenco* [2017]
UKSC 43, para 26 — "If the innocent party chooses to speculate as to the way in which the market is going to go, the result
of such speculation is for his account".

## 4. Practice after blockchain incidents (what actually happened elsewhere)

| Incident / case | What was done about the reference moment | Level |
|---|---|---|
| *Ruscoe v Cryptopia Ltd (in liq)* [2020] NZHC 728, [205] | "as at the date of the theft, the liquidators should determine the accountholders affected and their relative shares" | primary |
| *Ruscoe v Houchens* (Cryptopia distribution) [2024] NZHC 419, [40](c), orders 2.2–2.6 | "up to 100 per cent of accepted pre-hack holdings, taking into account any post-hack transactions"; soft cut-off date, then discretion of the liquidators for late claims | primary |
| *Fantom Foundation v Multichain Foundation* [2024] SGHC 173, [21]–[27] | loss = value the day before the breach "less any residual value"; post-incident prices rejected as too volatile (default judgment) | primary |
| Ankr aBNBc unbacked mint, Dec 2022 (project report) | "Do not trade aBNBc or speculatively buy it at a discount"; snapshot at the exploit; speculative post-exploit trades not compensated | primary (project source) |
| Cover Protocol, Dec 2020, and Binance SAFU | protocol snapshot at the block before the exploit; Binance separately and voluntarily compensated users who bought before trading was halted (US$10.1m) — an "obligation + discretionary layer" pattern | secondary |
| WazirX, 2024–2025 (Singapore scheme) | balances restored as of the withdrawal halt; all later trades rendered ineffective | secondary |
| KyberSwap Elastic, Euler, Balancer, Beanstalk | snapshot at the last block before the exploit (Euler: block the protocol was disabled) | primary (project sources) |
| The DAO, 2016 (SEC Report 34-81207) — **counter-example** | redemption followed the token: post-attack buyers were made whole | primary |

**Reading.** The prevailing practice is a snapshot at the exploit, i.e. *earlier* than Gonka's line. Buyers between the
exploit and the warning are, under that practice, usually outside the mandatory circle. Gonka's proposal covers them because
during those 6 h 22 min the project had not yet told anyone what to do — and it covers them only for money actually lost.

## 5. Strongest objections, stated candidly

- **"The line is too late — the market knew at 18:28."** A diligent trader is charged with what reasonable inquiry would show;
  NY Fed staff report no. 1153 (2025) finds about 36% of the price decline after hacks happens before the first public
  announcement. Answer: law distinguishes unconfirmed third-party information from a credible official statement
  (*Ganino v. Citizens Utilities*: the correction must be conveyed "with a degree of intensity and credibility sufficient
  to counter-balance"); the closest statutes exclude only buyers who *actually knew*; and the design neutralises informed
  traders without identifying them — gains are always netted and a buyer gets back at most the price paid.
- **"The line is too early — retail users are not on X; the website banner came only by ~12:03."** *Mullane*; SEC Report on
  Netflix (2013): a social-media channel works as disclosure if the market was told to watch it; MiCA art. 88 requires
  publication on the website. Answer: for an anonymous global holder base, publication on the official channel is the only
  feasible notice; the text was explicit; and this objection is exactly what options 2 and 3 are for.
- **"Paying dip buyers is moral hazard."** Answer: they receive the price paid net of all gains, never cheap tokens 1:1; after
  the warning the share declines to zero within a day; old WGNK are voided, so no free option remains.
- **"There is no legal duty at all."** Largely correct (*Risley v. Universal Navigation*, S.D.N.Y. 2023; pure economic loss to an
  indeterminate class is recoverable only exceptionally). Hence the wording "commitment assumed by the project", not
  "legal liability". Returned funds, however, are not the project's to keep and must be distributed fairly — net-loss method.

## 6. Option 2: why steps, and why these boundaries

- **Form.** Apportionment by degree of responsibility is the general rule (section 3, principle 3). Regulation E
  (12 CFR § 1005.6(b)) is a statutory time ladder after notice: US$50 if reported within two business days, US$500 after,
  unlimited after 60 days. German HGB § 15(2) / EU Directive 2017/1132 art. 16(6) give a 15-day grace period after official
  publication for third parties who could not have known. *SEC v. Texas Gulf Sulphur* (2d Cir. 1968): publication is only
  the first step of dissemination; one must wait "until the news could reasonably have been expected to appear over the
  media of widest circulation". NY Fed (2025): prices of hacked tokens stabilise 9–24 hours after the event.
- **Boundaries are notice events** (all documented in `data/sources/`): 00:24:07 official warning on X →
  **01:35:41** the warning repeated in the press (TokenPost; ½ until then) → **12:03:00** the warning on the project's own
  website and docs, confirmed "no later than" this time (¼ until then) → **00:24:07 on 20 Nov**, a full day in every time
  zone (⅛ until then) → 0.
- **Fractions ½, ¼, ⅛ are a policy choice.** No authority prescribes numbers; courts apportion in broad "just and equitable"
  shares. No source prescribes a smooth decay; steps are the form the law actually uses. A sensitivity analysis with other
  ladders and a smooth exponential is in `model/summary_three_options.json` (the totals move by a few hundred dollars).
- **Safeguards recommended:** an individual-review (hardship) clause for people who can show they could not have seen the
  warning; an "actual knowledge" exclusion for addresses linked to the attacker.

## 7. Jurisdiction

There is no international court for private claims of this kind (ICJ Statute art. 34(1): "Only states may be parties in
cases before the Court"). Disputes would go to national courts or arbitration; applicable law may differ holder by holder.
Most authorities above come from securities and consumer-payment law and apply by analogy only; whether WGNK is a security
or a MiCA crypto-asset was not determined.

## 8. What could not be verified

BAILII, Justia, Légifrance, Medium and ScienceDirect blocked automated reading; *British Westinghouse* [1912] AC 673 is quoted
from a secondary source; Mt. Gox, Celsius, PAID Network, PancakeBunny, Coincheck, Youbit and QuadrigaCX items are
secondary/unverified and are not relied on. The Gonka timeline was taken from `data/sources/` and the X post ids;
Discord announcements could not be checked and could move the official line earlier if an earlier explicit warning exists.
