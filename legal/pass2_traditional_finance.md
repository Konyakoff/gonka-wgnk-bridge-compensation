# Direction 2 — Traditional finance and general private law: why an official, explicit public notice is the dividing line

Research date: 23 Nov 2026. Scope: analogies for the Gonka/WGNK compensation proposal (bridge exploit 18 Nov 2026; official warning "Do not trade WGNK" published 19 Nov 2026 00:24:07 UTC).

**This is an analogy file, not a legal opinion.** None of the authorities below governs a token bridge directly. They show how mature legal systems allocate loss around the moment of notice.

## How to read this file

Verification levels used:

- **primary** — I opened the text of the source itself (judgment, statute, regulation, rule text) and the quote is copied from it. Where the copy is an unofficial mirror, that is stated.
- **secondary** — I did not open the source itself; the content comes from a commentary, a case summary, or a later judgment quoting it.
- **unverified** — stated from general knowledge or search snippets only; do not quote on a slide.

Access problems (so nobody repeats them): `supreme.justia.com`, `law.justia.com`, `openjurist.org`, `leagle.com`, `caselaw.findlaw.com` return 403; `bailii.org` is behind a bot wall; `listingcenter.nasdaq.com` (Nasdaq rulebook) returns 403; `sec.gov` blocks plain curl. Working substitutes: Cornell LII, `law.resource.org`, `govinfo.gov`, court sites (`ca1.uscourts.gov`, `ca5.uscourts.gov`), `caselaw.nationalarchives.gov.uk`, `elitigation.sg`, EUR-Lex, `legislation.gov.uk`, `gesetze-im-internet.de`.

`supports` tags: `hard_cutoff` · `gradient_or_grace` · `net_loss_principle` · `price_paid_remedy` · `contradicts` · `context`.

---

## 1. The short answer

1. **Hard cut-off at notice is the mainstream rule** in three independent bodies of law: securities disclosure liability (purchasers after a credible correction have "no direct or indirect connection with the fraud" — *Basic*), statutory prospectus liability (UK FSMA Sch. 10 para 3: no liability if a correction was published before acquisition; German WpHG § 97(3); US Securities Act § 11(a)), and securities property law (UCC §§ 8-202, 8-205, 8-303: protection only for a purchaser "for value and without notice").
2. **The remedy for an overissued security is the price paid**, not the market value (UCC § 8-210(d)). This is the closest black-letter analogue to 22M unbacked WGNK.
3. **Net loss, not paper value**, is the measure when a scheme has corrupted prices (*Madoff*, *Janvey v. Brown*, SIPA; *Dura*: no "broad insurance against market losses").
4. **A time gradient after notice has real statutory precedent**, but it is always a *step function or a short grace period*, never a smooth decay curve: Regulation E tiers ($50 / $500 / unlimited), HGB § 15(2) and EU Directive 2017/1132 art. 16 (15 days after official publication, with the burden on the third party), RUPA § 704(c) (deemed notice 90 days after filing; 60 in Delaware), *Texas Gulf Sulphur* (a "reasonable waiting period"), the EU Prospectus Regulation (2–3 working days to withdraw after a supplement), PSLRA 90-day look-back.
5. **Main caveat**: every one of these systems makes the cut-off depend on the notice being *adequately disseminated* and, in organised markets, on trading being *halted* while it spreads. A single post on X at 00:24 UTC with a DEX that never stops trading is weaker than a regulated corrective disclosure. That argues for a short grace window rather than a to-the-second line.

---

## 2. Securities disclosure liability — the class period ends at the corrective disclosure

### 2.1 Basic Inc. v. Levinson, 485 U.S. 224 (1988)

- Jurisdiction / forum / year: USA, Supreme Court, 1988.
- Rule: investors who trade in an efficient market are presumed to rely on the integrity of the market price (fraud-on-the-market). The presumption is rebuttable; one way to rebut it is to show that the truth had already credibly entered the market.
- Quote (opinion of the Court, at 248–249): "Any showing that severs the link between the alleged misrepresentation and either the price received (or paid) by the plaintiff, or his decision to trade at a fair market price, will be sufficient to rebut the presumption of reliance."
- Quote (same passage): "if, despite petitioners' allegedly fraudulent attempt to manipulate market price, news of the merger discussions credibly entered the market and dissipated the effects of the misstatements, those who traded Basic shares after the corrective statements would have no direct or indirect connection with the fraud."
- Quote (footnote 28): "By accepting this rebuttable presumption, we do not intend conclusively to adopt any particular theory of how quickly and completely publicly available information is reflected in market price."
- Mapping: the single best authority for "after the corrective statement, later traders are outside the protected group". Note two honest qualifiers that come from the same passage: the correction must have "credibly entered the market", and the Court refused to say how fast that happens.
- URL opened: https://www.law.cornell.edu/supremecourt/text/485/224
- Verification: **primary**. Supports: `hard_cutoff`.

### 2.2 Halliburton Co. v. Erica P. John Fund, Inc., 573 U.S. 258 (2014) ("Halliburton II")

- USA, Supreme Court, 2014.
- Rule: reaffirms *Basic*. To invoke the presumption a plaintiff must show, among other things, that it traded in the window between the misstatement and the revelation of the truth. Defendants may rebut by showing no price impact.
- Quote: "a plaintiff must prove that: (1) the alleged misrepresentations were publicly known, (2) they were material, (3) the stock traded in an efficient market, and (4) the plaintiff traded the stock between when the misrepresentations were made and when the truth was revealed."
- Quote: "in making the presumption rebuttable, Basic recognized that market efficiency is a matter of degree and accordingly made it a matter of proof."
- Mapping: element (4) is the class-period rule in one sentence — trade *before* "the truth was revealed" or you are out. The second quote is the counter-point: how fast a market absorbs news is a question of fact, not an axiom.
- URL opened: https://www.law.cornell.edu/supremecourt/text/13-317
- Verification: **primary**. Supports: `hard_cutoff` (and `contradicts` on speed of absorption).

### 2.3 Dura Pharmaceuticals, Inc. v. Broudo, 544 U.S. 336 (2005)

- USA, Supreme Court, 2005.
- Rule: paying an inflated price is not itself a loss; the plaintiff must show an economic loss caused by the truth coming out (loss causation).
- Quote: "if, say, the purchaser sells the shares quickly before the relevant truth begins to leak out, the misrepresentation will not have led to any loss."
- Quote: the statutes make private actions available "not to provide investors with broad insurance against market losses, but to protect them against those economic losses that misrepresentations actually cause."
- Mapping: (a) compensation should track realised economic loss attributable to the event, not every adverse price move; (b) a compensation scheme is not market insurance — useful language for declining to cover post-warning speculation.
- URL opened: https://www.law.cornell.edu/supct/html/03-932.ZO.html
- Verification: **primary**. Supports: `net_loss_principle`.

### 2.4 PSLRA 90-day look-back, 15 U.S.C. § 78u-4(e) (1995)

- USA, federal statute (Private Securities Litigation Reform Act 1995).
- Rule: damages measured by market price are capped at the difference between the price paid and the *mean trading price over the 90 days after* the corrective information is disseminated (or until the plaintiff's earlier sale).
- Quote (§ 78u-4(e)(1)): damages "shall not exceed the difference between the purchase or sale price paid or received, as appropriate, by the plaintiff for the subject security and the mean trading price of that security during the 90-day period beginning on the date on which the information correcting the misstatement or omission that is the basis for the action is disseminated to the market."
- Legislative purpose (S. Rep. 104-98): "The Committee intends a rectify the uncertainty in calculating damages by providing a ``bounce back'' period, thereby limiting damages to those losses caused by the fraud and not by other market conditions." (typo "a rectify" is in the original).
- Mapping: (a) Congress chose the dissemination date of the correction as the anchor of the whole damages calculation; (b) it then deliberately looked at a *window after* that date, because the price right after a shock overstates the loss and prices bounce back. Directly relevant to WGNK because the attacker returned almost everything: a look-back/mean-price method nets out the recovery. It is a statutory admission that the market needs time after a disclosure.
- URLs opened: https://www.law.cornell.edu/uscode/text/15/78u-4 ; https://www.govinfo.gov/content/pkg/CRPT-104srpt98/html/CRPT-104srpt98.htm
- Verification: **primary** (statute and Senate report). Supports: `gradient_or_grace` (also `net_loss_principle`).

### 2.5 Securities Act of 1933, § 11(a) and § 12(a)(2) — 15 U.S.C. §§ 77k, 77l

- USA, federal statute, 1933.
- Rule: strict-style liability for a false registration statement or prospectus runs to "any person acquiring such security", except an acquirer who knew of the untruth.
- Quote (§ 77k(a)): "any person acquiring such security (unless it is proved that at the time of such acquisition he knew of such untruth or omission) may ... sue".
- Quote (§ 77l(a)(2)): "(the purchaser not knowing of such untruth or omission)".
- Mapping: the issuer's liability is cut off, purchaser by purchaser, by knowledge at the time of acquisition. Note the standard is *actual knowledge* ("knew"), and under § 11 the burden of proving it is on the defendant.
- URLs opened: https://www.law.cornell.edu/uscode/text/15/77k ; https://www.law.cornell.edu/uscode/text/15/77l
- Verification: **primary**. Supports: `hard_cutoff`.

### 2.6 UK FSMA 2000, Schedule 10 paras 1(3), 3 and 6 (and POATR 2024, Sch. 2 para 4)

- UK, statute, 2000 (successor regime: Public Offers and Admissions to Trading Regulations 2024, S.I. 2024/105, Sch. 2).
- Rule: a person responsible for listing particulars / a prospectus is not liable for loss caused by a false statement if a correction was published before the securities were acquired, or if the claimant acquired with knowledge.
- Quote (Sch. 10 para 3(2)(a)): no liability if "before the securities in question were acquired, a correction had been published in a manner calculated to bring it to the attention of persons likely to acquire the securities".
- Quote (Sch. 10 para 6): no liability if "the person suffering the loss acquired the securities in question with knowledge— (a) that the statement was false or misleading".
- Quote (Sch. 10 para 1(3)(b), one of the conditions of the "reasonable belief" defence): "they were acquired before it was reasonably practicable to bring a correction to the attention of persons likely to acquire them".
- POATR 2024 Sch. 2 para 4(2)(a) repeats the correction rule in the same words ("a correction had been published in a manner calculated to bring it to the attention of persons likely to acquire the securities").
- Mapping: **this is the most literal statutory statement of the proposal's thesis**: published correction before acquisition = no liability to that acquirer. It also sets the quality bar ("in a manner calculated to bring it to the attention of persons likely to acquire") and recognises that there is a period in which bringing a correction to buyers' attention is not yet "reasonably practicable".
- URLs opened: https://www.legislation.gov.uk/ukpga/2000/8/schedule/10 ; https://www.legislation.gov.uk/uksi/2024/105/schedule/2
- Verification: **primary**. Not checked: the exact commencement status of the repeal of s. 90 / Sch. 10 in favour of the POATR regime — cite both. Supports: `hard_cutoff`.

### 2.7 Germany, WpHG §§ 97, 98 (liability for late or untrue ad hoc disclosure)

- Germany, statute (Wertpapierhandelsgesetz, current numbering).
- Rule: the issuer must compensate an investor who bought after the omission and still held when the information became known; no claim if the investor knew the information.
- Quote (§ 97(1) no. 1): the third party "die Finanzinstrumente nach der Unterlassung erwirbt und er bei Bekanntwerden der Insiderinformation noch Inhaber der Finanzinstrumente ist".
- Quote (§ 97(3)): "Der Anspruch nach Absatz 1 besteht nicht, wenn der Dritte die Insiderinformation im Falle des Absatzes 1 Nr. 1 bei dem Erwerb oder im Falle des Absatzes 1 Nr. 2 bei der Veräußerung kannte."
- Mapping: a civil-law statute with the same architecture: the protected window closes at "Bekanntwerden" (the information becoming known); knowledge at the time of the trade removes the claim. Standard is actual knowledge ("kannte").
- URLs opened: https://www.gesetze-im-internet.de/wphg/__97.html ; https://www.gesetze-im-internet.de/wphg/__98.html
- Verification: **primary**. Supports: `hard_cutoff`.

### 2.8 Class period ends when curative information is effectively disseminated — W. Va. Pipe Trades Health & Welfare Fund v. Medtronic, Inc. (D. Minn. 30 Jan 2018)

- USA, District of Minnesota, No. 13-cv-01686, 2018.
- Rule (as reported): the class period ends when a corrective disclosure or curative information "is publicly announced or otherwise effectively disseminated to the market"; the court shortened the class period to the first corrective disclosure because from that publication a reasonable investor would no longer rely.
- Mapping: shows courts actually trimming the compensated group at the *first* effective disclosure, and that later repetitions of the same facts do not extend it.
- URL opened: https://www.lit-sl.aoshearman.com/District-Of-Minnesota-Certifies-Securities-Fraud- (law-firm case note; opinion itself not opened).
- Verification: **secondary**. Supports: `hard_cutoff`.

### 2.9 Counter-authority on notice quality — Ganino v. Citizens Utilities Co., 228 F.3d 154 (2d Cir. 2000)

- USA, Second Circuit, 2000 (quoting *In re Apple Computer Sec. Litig.*, 886 F.2d 1109, 1116 (9th Cir. 1989)).
- Rule: the "truth-on-the-market" defence works only if the corrective information was conveyed forcefully enough.
- Quote: "the corrective information must be conveyed to the public 'with a degree of intensity and credibility sufficient to counter-balance effectively any misleading information created by' the alleged misstatements."
- Quote: "The truth-on-the-market defense is intensely fact-specific".
- Mapping: the cut-off is not triggered by any mention of the truth somewhere. Applied to Gonka: an explicit, official, unambiguous "Do not trade WGNK" from the project account scores well on *credibility* and *explicitness*; reach and timing (one channel, 00:24 UTC) are the weak points. It also cuts the other way: earlier third-party alerts about the exploit were probably *not* intense or credible enough to end the protected period, which supports choosing the official warning as the line.
- URL opened: https://law.resource.org/pub/us/case/reporter/F3/228/228.F3d.154.99-7904.1999.html
- Verification: **primary**. Supports: `contradicts` (quality-of-notice condition).

### 2.10 Counter-authority on timing — SEC v. Texas Gulf Sulphur Co., 401 F.2d 833 (2d Cir. 1968) (en banc)

- USA, Second Circuit, 1968.
- Rule: news is not "public" the instant a release is read out; insiders must wait until it has been effectively disseminated, and possibly for a reasonable period beyond.
- Quote: "The reading of a news release ... is merely the first step in the process of dissemination".
- Quote: "at the minimum Coates should have waited until the news could reasonably have been expected to appear over the media of widest circulation, the Dow Jones broad tape".
- Quote (footnote 18): the court noted "the advisability of a 'reasonable waiting period' during which outsiders may absorb and evaluate disclosures".
- Mapping: the leading US authority that publication and effective public knowledge are separated by a real interval. It is about when insiders may trade, not about compensation, but it is the cleanest judicial statement that a to-the-second cut-off at the timestamp of the release is not how securities law treats "public".
- URL opened: https://law.resource.org/pub/us/case/reporter/F2/401/401.F2d.833.296.30882_1.html
- Verification: **primary**. Supports: `gradient_or_grace` (argues against a to-the-second line).

### 2.11 EU Prospectus Regulation (EU) 2017/1129, art. 23(2)

- EU, regulation, 2017; amended by Regulation (EU) 2024/2809 (Listing Act).
- Rule: when a supplement correcting a prospectus is published, investors who had already agreed to buy get a fixed short period to withdraw.
- Quote (original 2017 text): investors "shall have the right, exercisable within two working days after the publication of the supplement, to withdraw their acceptances". Regulation 2024/2809 replaces this with "within three working days after the publication of the supplement".
- Mapping: (a) the people protected are those who committed *before* the correction; (b) the legislator gives them a fixed reaction window measured in working days from publication. A model for a short, fixed grace period.
- URLs opened: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R1129 ; https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R2809
- Verification: **primary**. Supports: `gradient_or_grace`.

---

## 3. Duty to mitigate after notice

The common thread: once the injured party knows of the breach, loss it could reasonably have avoided — and a fortiori loss it chooses to incur by new speculation — is its own.

| # | Source | Text (verbatim) | Verification |
|---|---|---|---|
| 3.1 | *British Westinghouse Electric & Manufacturing Co v Underground Electric Railways Co of London* [1912] AC 673 (HL), Viscount Haldane LC | the compensatory principle is qualified by a second, "which imposes on a plaintiff the duty of taking all reasonable steps to mitigate the loss consequent upon the breach, and debars him from claiming any part of the damage which is due to his neglect to take such steps" | **secondary** — quoted from A. Dyson, "British Westinghouse Revisited" (LSE Research Online); BAILII not reachable. Sources differ by a word or two ("consequent on" / "claiming in respect of any part"); check the AC report before printing. |
| 3.2 | *Globalia Business Travel SAU v Fulton Shipping Inc* ("The New Flamenco") [2017] UKSC 43, para 26, summarising *The Elena D'Amico* | "If the innocent party chooses to speculate as to the way in which the market is going to go, the result of such speculation is for his account not the account of the guilty party." | **primary** (UKSC judgment on the National Archives; the sentence is the Supreme Court's summary of Longmore LJ / Robert Goff J) |
| 3.3 | Germany, BGB § 254 (official English translation) | "(1) Where fault on the part of the injured person contributed to the occurrence of the damage, liability in damages as well as the extent of compensation to be provided depend on the circumstances, in particular on the extent to which the damage was caused mainly by one or the other party. (2) This also applies if the fault of the injured person is limited to ... failing to avert or mitigate the damage." | **primary** |
| 3.4 | Russia, Civil Code art. 404(1) | "Суд также вправе уменьшить размер ответственности должника, если кредитор умышленно или по неосторожности содействовал увеличению размера убытков ... либо не принял разумных мер к их уменьшению." | **primary text, unofficial mirror** (zakonrf.info) |
| 3.5 | Russia, Civil Code art. 1083(2) | "Если грубая неосторожность самого потерпевшего содействовала возникновению или увеличению вреда, в зависимости от степени вины потерпевшего и причинителя вреда размер возмещения должен быть уменьшен." | **primary text, unofficial mirror** |
| 3.6 | CISG art. 77 (1980) | "A party who relies on a breach of contract must take such measures as are reasonable in the circumstances to mitigate the loss ... If he fails to take such measures, the party in breach may claim a reduction in the damages in the amount by which the loss should have been mitigated." | **primary** (UNCITRAL text) |
| 3.7 | UNIDROIT Principles 2016, art. 7.4.8(1) | "The non-performing party is not liable for harm suffered by the aggrieved party to the extent that the harm could have been reduced by the latter party's taking reasonable steps." | **primary** |
| 3.8 | DCFR III.–3:705(1) (2009) | "The debtor is not liable for loss suffered by the creditor to the extent that the creditor could have reduced the loss by taking reasonable steps." | **primary** (full edition PDF) |
| 3.9 | Restatement (Second) of Contracts § 350 (1981) | "(1) Except as stated in Subsection (2), damages are not recoverable for loss that the injured party could have avoided without undue risk, burden or humiliation. (2) The injured party is not precluded from recovery ... to the extent that he has made reasonable but unsuccessful efforts to avoid loss." | **secondary** (University of Miami course reproduction; ALI text is paywalled) |

URLs opened: https://researchonline.lse.ac.uk/id/eprint/64695/1/British_Westinghouse_Revisited_LSERO.pdf · https://caselaw.nationalarchives.gov.uk/uksc/2017/43 · https://www.gesetze-im-internet.de/englisch_bgb/englisch_bgb.html · https://www.zakonrf.info/gk/404/ · https://www.zakonrf.info/gk/1083/ · https://uncitral.un.org/sites/uncitral.un.org/files/media-documents/uncitral/en/19-09951_e_ebook.pdf · https://www.unidroit.org/wp-content/uploads/2021/06/Unidroit-Principles-2016-English-bl.pdf · https://www.law.kuleuven.be/personal/mstorme/european-private-law_en.pdf · https://contractslawinaction.law.miami.edu/wp-content/uploads/2009/08/mitigationofdamages.pdf

Mapping to Gonka:

- Mitigation presupposes **knowledge of the breach**. Before the official warning a trader had no authoritative signal; after it, he did. That is why the warning, not the exploit block, is the moment from which avoidable loss shifts.
- **A new purchase after the warning is not a failure to mitigate an existing loss — it is the creation of a new exposure.** The *Elena D'Amico* / *New Flamenco* sentence (3.2) is the sharper analogy: post-notice speculation "is for his account".
- **BGB § 254 and Russian CC arts. 404 / 1083 are the authority for a coefficient.** Civil-law systems do not switch compensation off; they reduce it "depending on the circumstances" and on each side's contribution. A declining percentage for post-warning trades is a contributory-fault apportionment in exactly this sense. Common-law mitigation, by contrast, is closer to all-or-nothing for the avoidable part.
- **Limit of the analogy**: Restatement § 350(2) and comparable rules protect a party who made "reasonable but unsuccessful efforts". Someone who *sold* after the warning to cut an existing pre-hack position was arguably mitigating, not speculating. The proposal should distinguish post-warning **buys** (new risk, voluntarily assumed) from post-warning **sells of pre-existing holdings** (loss crystallised, but caused by the exploit).

---

## 4. Unauthorised payments — liability keyed to the moment of notification, and statutory time tiers

Honest framing first: in payments law the notice runs **from the user to the provider**; in Gonka it runs from the project to users. The analogy is one of principle — loss shifts onto the party that has been told and is able to act — not of direction.

### 4.1 EU PSD2, Directive (EU) 2015/2366, arts. 69, 71, 73, 74

- EU, directive, 2015.
- Art. 69(1)(b): the user must "notify the payment service provider ... without undue delay on becoming aware of the loss, theft, misappropriation or unauthorised use of the payment instrument."
- Art. 74(1): before notification, "the payer may be obliged to bear the losses relating to any unauthorised payment transactions, up to a maximum of EUR 50".
- Art. 74(3): "The payer shall not bear any financial consequences resulting from use of the lost, stolen or misappropriated payment instrument after notification in accordance with point (b) of Article 69(1), except where the payer has acted fraudulently."
- Art. 71(1): rectification only if notified "without undue delay ... and no later than 13 months after the debit date".
- Art. 74(1), third subparagraph: the payer bears *all* losses if they result from "failing to fulfil one or more of the obligations set out in Article 69 with intent or gross negligence".
- Mapping: notification is the legal hinge — losses before and after it are allocated differently, by statute. Gross negligence removes protection altogether.
- URL opened: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32015L2366
- Verification: **primary**. Supports: `hard_cutoff`.

### 4.2 UK Payment Services Regulations 2017 (S.I. 2017/752), regs 72, 74, 77

- UK, statutory instrument, 2017.
- Reg 77(1): payer liable "up to a maximum of £35" for losses from a lost, stolen or misappropriated instrument.
- Reg 77(4)(a): "the payer is not liable for any losses incurred in respect of an unauthorised payment transaction— (a) arising after notification under regulation 72(1)(b)".
- Reg 74(1): redress only if notified "without undue delay, and in any event no later than 13 months after the debit date".
- URLs opened: https://www.legislation.gov.uk/uksi/2017/752/regulation/77/made ; .../regulation/72/made ; .../regulation/74/made
- Verification: **primary** (as-made text). Supports: `hard_cutoff`.

### 4.3 US Regulation E, 12 CFR § 1005.6(b) — the statutory time gradient

- USA, federal regulation implementing the Electronic Fund Transfer Act.
- Tier 1, § 1005.6(b)(1): "If the consumer notifies the financial institution within two business days after learning of the loss or theft of the access device, the consumer's liability shall not exceed the lesser of $50 or the amount of unauthorized transfers that occur before notice to the financial institution."
- Tier 2, § 1005.6(b)(2): "If the consumer fails to notify the financial institution within two business days ... the consumer's liability shall not exceed the lesser of $500 or the sum of: (i) $50 or the amount of unauthorized transfers that occur within the two business days, whichever is less; and (ii) The amount of unauthorized transfers that occur after the close of two business days and before notice to the institution, provided the institution establishes that these transfers would not have occurred had the consumer notified the institution within that two-day period."
- Tier 3, § 1005.6(b)(3): the consumer "must report an unauthorized electronic fund transfer that appears on a periodic statement within 60 days of the financial institution's transmittal of the statement to avoid liability for subsequent transfers." Failing that, liability "shall not exceed the amount of the unauthorized transfers that occur after the close of the 60 days and before notice to the institution" — i.e. no dollar cap.
- Safety valve, § 1005.6(b)(4): "If the consumer's delay in notifying the financial institution was due to extenuating circumstances, the institution shall extend the times specified above to a reasonable period."
- Mapping: **the clearest black-letter example of responsibility that grows in steps with elapsed time after knowledge**: ≤ 2 business days → $50; 2 business days to 60 days → $500; beyond 60 days → uncapped for later transfers. Two design features worth copying: (a) the higher tiers apply only to loss that "would not have occurred" with timely action (causation); (b) an explicit extension for extenuating circumstances.
- URL opened: https://www.law.cornell.edu/cfr/text/12/1005.6
- Verification: **primary**. Supports: `gradient_or_grace`.

### 4.4 US Regulation Z, 12 CFR § 1026.12(b) (credit cards)

- Quote: cardholder liability "shall not exceed the lesser of $50 or the amount of money, property, labor, or services obtained by the unauthorized use before notification to the card issuer".
- Mapping: a pure before/after-notification line with a nominal cap before it.
- URL opened: https://www.law.cornell.edu/cfr/text/12/1026.12
- Verification: **primary**. Supports: `hard_cutoff`.

### 4.5 UCC Article 4A §§ 4A-202 – 4A-204 (wholesale funds transfers) and UCC § 4-406 (cheques)

- USA, uniform state law.
- § 4A-202(b): an unauthorised order is still "effective as the order of the customer" if the bank followed a commercially reasonable security procedure in good faith; the bank need not follow an instruction "notice of which is not received at a time and in a manner affording the bank a reasonable opportunity to act on it".
- § 4A-204(a): the bank must refund an unauthorised, unenforceable order, but the customer loses interest if it fails "to notify the bank of the relevant facts within a reasonable time not exceeding 90 days".
- § 4-406(d)(2), (f): a customer who does not examine statements and report is precluded as to later forgeries by the same wrongdoer after "a reasonable period of time, not exceeding 30 days", and is absolutely barred after "one year".
- Mapping: (a) more step-function time limits keyed to the moment information was made available (30 days / 90 days / 1 year); (b) § 4A-202(b) states the counter-principle neatly: a notice counts only if received "at a time and in a manner affording ... a reasonable opportunity to act on it".
- URLs opened: https://www.law.cornell.edu/ucc/4A/4A-202 ; https://www.law.cornell.edu/ucc/4A/4A-204 ; https://www.law.cornell.edu/ucc/4/4-406
- Verification: **primary**. Supports: `gradient_or_grace`.

---

## 5. Overissued or defective securities and the purchaser "without notice"

### 5.1 UCC § 8-210 — Overissue

- USA, uniform state law (Article 8, 1994 revision).
- Quote (a): "'overissue' means the issue of securities in excess of the amount the issuer has corporate power to issue".
- Quote (c): "If an identical security not constituting an overissue is reasonably available for purchase, a person entitled to issue or validation may compel the issuer to purchase the security and deliver it".
- Quote (d): "If a security is not reasonably available for purchase, a person entitled to issue or validation may recover from the issuer the price the person or the last purchaser for value paid for it with interest from the date of the person's demand."
- Mapping: the nearest doctrinal twin of 22M unbacked WGNK. The law does not validate the excess units; it gives the innocent holder either a genuine replacement or **the price paid** (by him or the last purchaser for value), with interest. This supports (a) treating compensation of protected purchasers as an *obligation* of the issuer side, and (b) measuring it by price paid, not by pre-hack or peak market value.
- Limits: Article 8 covers "securities" of an "issuer"; WGNK is a wrapped token on a bridge, and the over-mint was the act of an attacker, not a corporate over-allotment. § 8-210 protects "a person entitled to issue or validation" — i.e. someone who qualifies under § 8-202 / § 8-205 as a purchaser for value without notice.
- URL opened: https://www.law.cornell.edu/ucc/8/8-210
- Verification: **primary**. Supports: `price_paid_remedy`.

### 5.2 UCC §§ 8-202(b)(1) and 8-205 — defective or unauthorised issue is good in the hands of a purchaser without notice

- Quote (§ 8-202(b)(1)): a security, "even though issued with a defect going to its validity, is valid in the hands of a purchaser for value and without notice of the particular defect".
- Quote (§ 8-205): an unauthorised signature is "effective in favor of a purchaser for value of the certificated security if the purchaser is without notice of the lack of authority".
- Mapping: the issuer bears the risk of defective issuance toward purchasers **for value and without notice**; a purchaser *with* notice gets nothing from these rules. "Notice of the particular defect" is the statutory hinge — precisely the role of the official warning.
- URLs opened: https://www.law.cornell.edu/ucc/8/8-202 ; https://www.law.cornell.edu/ucc/8/8-205
- Verification: **primary**. Supports: `hard_cutoff`.

### 5.3 UCC § 8-303 (protected purchaser), § 8-105 (notice of adverse claim), § 3-302 (holder in due course), § 1-202 (what "notice" means)

- § 8-303(a): "'Protected purchaser' means a purchaser ... who: (1) gives value; (2) does not have notice of any adverse claim to the security; and (3) obtains control".
- § 3-302(a)(2): a holder in due course takes "(i) for value, (ii) in good faith, (iii) without notice that the instrument is overdue or has been dishonored ...".
- § 8-105(a): "A person has notice of an adverse claim if: (1) the person knows of the adverse claim; (2) the person is aware of facts sufficient to indicate that there is a significant probability that the adverse claim exists and deliberately avoids information that would establish the existence of the adverse claim; or (3) the person has a duty ... to investigate".
- § 1-202(a): a person has notice of a fact if the person "(1) has actual knowledge of it; (2) has received a notice or notification of it; or (3) from all the facts and circumstances known to the person at the time in question, has reason to know that it exists."
- § 1-202(d): a person "notifies" another "by taking such steps as may be reasonably required to inform the other person in ordinary course, whether or not the other person actually comes to know of it."
- § 1-202(e): a person "receives" a notice when "(1) it comes to that person's attention; or (2) it is duly delivered in a form reasonable under the circumstances at the place of business ... or at another location held out by that person as the place for receipt of such communications."
- Mapping: the bona fide purchaser doctrine in statutory form — value plus absence of notice. Two edges: (i) § 1-202(d) helps the project (giving notice = taking reasonable steps, "whether or not the other person actually comes to know of it"); (ii) § 8-105 and § 1-202(e) help post-warning traders (for investment securities, notice means actual knowledge or wilful blindness; a notice is "received" when it reaches the person or a channel that person holds out for communications — a public post is not delivered to anyone in particular).
- URLs opened: https://www.law.cornell.edu/ucc/8/8-303 ; https://www.law.cornell.edu/ucc/8/8-105 ; https://www.law.cornell.edu/ucc/3/3-302 ; https://www.law.cornell.edu/ucc/1/1-202
- Verification: **primary**. Supports: `hard_cutoff` (8-303, 3-302); `contradicts` (8-105, 1-202(e) on what counts as notice).

---

## 6. Ponzi schemes and insolvency distributions — the net-loss principle

### 6.1 In re Bernard L. Madoff Investment Securities LLC, 654 F.3d 229 (2d Cir. 2011)

- USA, Second Circuit, decided 16 Aug 2011, No. 10-2378-bk.
- Rule: customer claims are measured by cash in minus cash out ("Net Investment Method"), not by the balances shown on fictitious statements.
- Quote: "Use of the Last Statement Method in this case would have the absurd effect of treating fictitious and arbitrarily assigned paper profits as real and would give legal effect to Madoff's machinations."
- Quote: customers who had withdrawn imaginary profits "would derive additional benefit at the expense of those customers who had not withdrawn funds before the fraud was exposed."
- Quote (approving the bankruptcy court): "[t]he Net Investment Method is appropriate because it relies solely on unmanipulated withdrawals and deposits".
- Mapping: when prices or balances were corrupted by the event, compensate real money lost, netted per person across all their trades; do not compensate paper value, and do not let one victim's gain from the corrupted market be paid for by another victim. For WGNK: per-address netting of buys and sells over the incident window, counting profits made on the compromised token against losses.
- URL opened: https://www.govinfo.gov/content/pkg/USCOURTS-ca2-10-02378/pdf/USCOURTS-ca2-10-02378-0.pdf (slip opinion)
- Verification: **primary**. Supports: `net_loss_principle`.

### 6.2 Janvey v. Brown, No. 13-10266 (5th Cir. 11 Sep 2014) — Stanford receivership

- USA, Fifth Circuit, 2014. Reporter cite 767 F.3d 430 is from memory — check before printing; docket number and date are verified.
- Rule: investors who got back principal plus purported interest are "net winners"; the excess is recoverable by the receiver as a fraudulent transfer because it was not received for reasonably equivalent value.
- Quote: the investor-defendants "received back their principal, as well as supposed interest on this principal. In other words ... they are 'net winners' in the Ponzi scheme."
- Mapping: confirms the netting logic from the other side — gains extracted from the corrupted system are not earnings. (For a voluntary compensation plan this supports netting, not clawback.)
- URL opened: https://www.ca5.uscourts.gov/opinions/pub/13/13-10266-CV0.pdf
- Verification: **primary** (opinion); reporter citation **unverified**. Supports: `net_loss_principle`.

### 6.3 SIPA, 15 U.S.C. § 78lll(11) — "net equity"

- Quote: "The term 'net equity' means the dollar amount of the account or accounts of a customer, to be determined by— (A) calculating the sum which would have been owed by the debtor to such customer if the debtor had liquidated, by sale or purchase on the filing date— (i) all securities positions of such customer".
- Mapping: statutory precedent for (a) a single reference date for valuing everyone's position and (b) a net figure per customer. In *Madoff* the court held this definition did not require honouring fictitious statements.
- URL opened: https://www.law.cornell.edu/uscode/text/15/78lll
- Verification: **primary**. Supports: `net_loss_principle`.

---

## 7. Pricing errors, knowledge of the mistake, erroneous-trade rules and trading halts

### 7.1 Chwee Kin Keong v Digilandmall.com Pte Ltd [2005] SGCA 2

- Singapore, Court of Appeal, 2005.
- Rule: a contract concluded at an obviously mistaken price is void at common law if the buyer had actual knowledge of the mistake; constructive knowledge plus unconscionable conduct may justify equitable relief.
- Quote (para 93): "Clearly suspecting a mistake, he pounced on the opportunity to make more money before the mistake was discovered. Thus, we do not think that the judge was wrong to have inferred actual knowledge. The apparent contracts are therefore void."
- Quote (para 83): "where the court is not convinced that the non-mistaken party has actual knowledge but is well satisfied that there is constructive knowledge and where there is evidence of unconscionable conduct or sharp practice on the part of the non-mistaken party, relief in equity may be granted".
- Mapping: a trader who knows the asset is mispriced or compromised and "snaps up" the opportunity gets no protection of the bargain. Post-warning buyers of a token the issuer had just declared compromised resemble the "snapping-up" buyers; the case also shows the difference courts draw between actual and constructive knowledge.
- URL opened: https://www.elitigation.sg/gd/s/2005_SGCA_2
- Verification: **primary**. Supports: `hard_cutoff` (knowledge defeats protection).

### 7.2 Quoine Pte Ltd v B2C2 Ltd [2020] SGCA(I) 02

- Singapore, Court of Appeal (appeal from the International Commercial Court), 2020. A crypto-exchange case decided on general contract principles.
- Rule: trades executed by deterministic algorithms at an absurd rate (about 250 times the market) stood; the exchange's unilateral reversal was a breach of contract. Knowledge is assessed in the programmer's mind at the time of programming.
- Quote (para 80): "(a) for unilateral mistake at common law, the non-mistaken party must have had actual knowledge of the mistaken party's mistake, and if this is established, the contract will be rendered void; but (b) for unilateral mistake in equity, the non-mistaken party must have had at least constructive knowledge of the mistaken party's mistake and must have engaged in some unconscionable conduct".
- Mapping: mostly a **counter-point**. (i) Trades on a functioning venue are not undone merely because the price was abnormal; without knowledge, the bargain stands. (ii) Bots do not read announcements — for algorithmic traders, "notice" at 00:24:07 is a fiction unless the operator intervened. Positive use: absent knowledge, pre-warning trades are legitimate and the people who lost on them are genuine victims, not gamblers.
- URL opened: https://www.elitigation.sg/gd/s/2020_SGCAI_2
- Verification: **primary**. Supports: `contradicts` / `context`.

### 7.3 Exchange "clearly erroneous execution" rules — NYSE Rule 7.10, Nasdaq Rule 11890 and sister rules

- USA, self-regulatory organisation rules, harmonised across exchanges after the 2010 Flash Crash; made permanent in 2022. I opened the harmonised text in an SEC Exhibit 5 for NYSE Chicago Rule 7.10; I could not open the NYSE or Nasdaq rulebook pages, so treat NYSE 7.10 / Nasdaq 11890 paragraph numbering as unverified.
- Quote (definition): "the terms of a transaction executed on the Exchange are 'clearly erroneous' when there is an obvious error in any term, such as price, number of shares or other unit of trading, or identification of the security."
- Quote (timing): "Requests for review must be received by the Exchange within thirty (30) minutes of execution time"; exchange action on its own motion "generally within thirty (30) minutes of the detection of the erroneous transaction".
- Quote (halts): an Officer "will nullify any transaction in a security that occurs after the primary listing market for such security declares a regulatory trading halt, suspension or pause with respect to such security and before such regulatory trading halt ... has officially ended".
- Mapping: (a) **the official declaration of a halt is a hard line: trades after it are nullified, not compensated** — the strongest TradFi image of "official stop = cut-off"; (b) the remedy for erroneous trades is undoing them, within minutes, by a neutral official — something a DEX cannot do, which is why Gonka has to compensate instead of bust; (c) the 30-minute windows show the time-scale at which organised markets expect participants to react.
- URL opened: https://www.sec.gov/files/rules/sro/nysechx/2022/34-95825-ex5.pdf
- Verification: **primary** for NYSE Chicago Rule 7.10 text; **secondary** for the statement that NYSE 7.10 and Nasdaq 11890 are substantively identical. Supports: `hard_cutoff`.

### 7.4 Knight Capital (1 Aug 2012) — SEC press release 2013-222

- USA, SEC administrative settlement, 2013.
- Facts: a faulty router "rapidly sent more than 4 million orders into the market" while filling 212 customer orders, traded "more than 397 million shares" in "the first 45 minutes", and the firm "suffered a loss of more than $460 million"; $12 million penalty under the market access rule (Rule 15c3-5).
- Mapping: context only. The party whose systems failed bore the loss; counterparties who traded without knowledge kept their bargains except where trades met the clearly-erroneous thresholds. (That only a small subset of Knight's trades was cancelled is general knowledge — **unverified** here.)
- URL opened: https://www.sec.gov/newsroom/press-releases/2013-222
- Verification: **primary** for the quoted facts. Supports: `context`.

### 7.5 News-pending trading halts (Nasdaq halt codes T1/T2)

- Quote (Nasdaq Trader halt codes): "T1 Halt - News Pending — Trading is halted pending the release of material news. T2 Halt - News Released — The news has begun the dissemination process through a Regulation FD compliant method(s)."
- Mapping: organised markets do not rely on instant absorption; they **stop trading while material news is released and disseminated** and resume afterwards. WGNK had no such circuit: the pool kept trading through the announcement. This is the structural reason a to-the-second cut-off is harsher in DeFi than its TradFi model, and the best justification for a short grace window.
- URL opened: https://nasdaqtrader.com/trader.aspx?id=tradehaltcodes
- Verification: **primary** for the codes; the usual length of such halts (commonly said to be about 30 minutes) is **unverified**. Supports: `gradient_or_grace`.

---

## 8. Official publication and third parties — statutory grace periods after notice (added; closest in *direction* to Gonka)

These are the best analogies for "the issuer publishes officially → third parties are bound", because here, unlike payments law, the notice runs from the entity to the public.

### 8.1 Germany, HGB § 15(2) — negative/positive publicity of the commercial register

- Quote: "Ist die Tatsache eingetragen und bekanntgemacht worden, so muß ein Dritter sie gegen sich gelten lassen. Dies gilt nicht bei Rechtshandlungen, die innerhalb von fünfzehn Tagen nach der Bekanntmachung vorgenommen werden, sofern der Dritte beweist, daß er die Tatsache weder kannte noch kennen mußte."
- In English (my translation): once a fact has been registered and published, a third party must accept it against himself; this does not apply to acts done within fifteen days after publication if the third party proves he neither knew nor ought to have known the fact.
- § 15(1) is the mirror image: before registration and publication the fact cannot be invoked against a third party "es sei denn, daß sie diesem bekannt war" (unless he knew it).
- Mapping: **official publication is the dividing line, with a fixed 15-day grace period during which the burden of proof flips to the third party.** Before publication: protected unless actual knowledge. After publication: bound, except within the grace window if he proves he neither knew nor should have known. This three-zone structure maps one-to-one onto: before warning = obligation; short window after warning = compensable on showing lack of knowledge; later = no claim.
- URL opened: https://www.gesetze-im-internet.de/hgb/__15.html
- Verification: **primary**. Supports: `gradient_or_grace`.

### 8.2 EU Directive (EU) 2017/1132, art. 16(6) (codifying the First Company Law Directive)

- Quote: "The documents and particulars may be relied on by the company as against third parties only after they have been disclosed in accordance with paragraph 5, unless the company proves that the third parties had knowledge thereof. However, with regard to transactions taking place before the sixteenth day following the disclosure, the documents and particulars shall not be relied on as against third parties who prove that it was impossible for them to have had knowledge thereof."
- Mapping: the same three-zone rule at EU level, so it is not a German peculiarity. Note the strict test in the grace window: "impossible for them to have had knowledge".
- URL opened: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017L1132 (text as originally adopted; later amendments, including Directive (EU) 2019/1151, not checked).
- Verification: **primary** (original 2017 text). Supports: `gradient_or_grace`.

### 8.3 Revised Uniform Partnership Act § 704(c) / Delaware 6 Del. C. §§ 15-703, 15-704

- Quote (Delaware § 15-704(c)): "a person not a partner is deemed to have notice of the dissociation 60 days after the statement of dissociation is filed."
- Quote (Delaware § 15-703(b)): the dissociated partner remains liable on transactions within 1 year if the other party "(1) Reasonably believed that the dissociated partner was then a partner and reasonably relied on such belief ...; (2) Did not have notice of the partner's dissociation; and (3) Is not deemed to have had ... notice under § 15-704(c)".
- The uniform act (RUPA 1997) uses 90 days and 2 years — **unverified** here; I opened only the Delaware enactment.
- Mapping: a public filing becomes *deemed* notice only after a statutory lag; until then liability continues toward people who reasonably relied and lacked actual notice. Authority for "constructive notice starts later than publication".
- URL opened: https://delcode.delaware.gov/title6/c015/sc07/index.html
- Verification: **primary** (Delaware). Supports: `gradient_or_grace`.

---

## 9. Product warnings and recalls (weak — not recommended for the slide)

- Restatement (Second) of Torts § 402A, comment j, is usually quoted for the proposition that where a warning is given the seller may reasonably assume it will be read and heeded. I did **not** open the Restatement text; courts are divided on the resulting "heeding presumption" and the Restatement (Third) of Torts: Products Liability moved away from comment j.
- On recalls, the practitioner literature I found says a consumer's failure to respond to a recall notice can be raised as comparative fault, but that the manufacturer "probably will not be completely exonerated". I found no clear appellate authority holding that an ignored recall notice ends the manufacturer's liability.
- Mapping: at most supports a *reduction* (comparative fault → gradient), not a cut-off. It cuts against the hard line.
- Sources seen: search results only (law.com practitioner article; Drug & Device Law blog on Restatement (Third) § 11).
- Verification: **unverified / secondary**. Supports: `context`.

---

## 10. Counter-arguments and limits (state these openly)

1. **Notice must be reasonably communicated.** *Ganino* / *Apple*: "intensity and credibility". FSMA Sch. 10 para 3: published "in a manner calculated to bring it to the attention of persons likely to acquire the securities". UCC § 1-202(d): "such steps as may be reasonably required to inform the other person in ordinary course". UCC § 4A-202(b): "at a time and in a manner affording ... a reasonable opportunity to act on it". One post on X is a single channel; whether the warning also appeared where traders actually trade (DEX front-ends, Telegram/Discord, block-explorer token page, CoinGecko/CMC banners) matters for the strength of the cut-off.
2. **Reasonable time to react.** *Texas Gulf Sulphur* (dissemination is a process; "reasonable waiting period"); HGB § 15(2) and Directive 2017/1132 art. 16(6) (15 days); RUPA § 704(c) (60–90 days); Regulation E (2 business days; extension for extenuating circumstances); Prospectus Regulation art. 23(2) (2–3 working days); FSMA Sch. 10 para 1(3)(b) (acquired "before it was reasonably practicable to bring a correction to the attention"). No system surveyed treats the publication timestamp as the instant at which everyone knows. The periods in corporate law are long because they were written for gazettes; the principle, not the number of days, is what transfers.
3. **Actual versus constructive notice.** The statutory bars are mostly phrased in terms of *actual* knowledge: Securities Act § 11 ("knew"), WpHG § 97(3) ("kannte"), FSMA Sch. 10 para 6 ("with knowledge"), UCC § 8-105 (knowledge or wilful blindness), *Chwee Kin Keong* (actual knowledge voids; constructive knowledge needs unconscionability). The fraud-on-the-market line is the exception: it treats public disclosure as binding the whole market. So a post-warning trader who credibly did not see the warning sits closer to the protected side under most of these texts than under *Basic*.
4. **Efficient-market assumptions.** *Basic* fn. 28 and *Halliburton II* expressly decline to hold that markets absorb information instantly ("a matter of degree ... a matter of proof"). *In re PolyMedica Corp. Sec. Litig.*, 432 F.3d 1 (1st Cir. 2005): an efficient market is one where "market price responds so quickly to new information that ordinary investors cannot make trading profits on the basis of such information" — a property to be proved with evidence. The *Cammer v. Bloom*, 711 F. Supp. 1264 (D.N.J. 1989) factors (weekly volume, analyst coverage, market makers/arbitrageurs, Form S-3 eligibility, cause-and-effect between news and price) — listed here from a NERA summary, **secondary** — would largely fail for a thin, just-exploited DEX token. Empirics for liquid US equities: Patell & Wolfson (1984, J. Fin. Econ. 13:223) — "The returns earned by simple trading rules dissipate within five to ten minutes ... Disturbances in the variance and serial correlation persist for several hours and extend into the following trading day" (abstract, opened on Stanford GSB); Busse & Green (2002, J. Fin. Econ. 65:415) — prices respond within seconds and positive news is absorbed within about a minute (**secondary**, search summary only). Fair reading: minutes for the price, hours for the dust to settle, in the best-covered market in the world. That is an argument for a grace window measured in tens of minutes to a few hours, not days.
5. **The truth can enter the market before the official notice.** Under *Basic* the protected period ends when the truth "credibly entered the market" from any source, and a plaintiff who traded while believing the truth is not protected. On-chain evidence of the exploit and third-party security alerts preceded the official post. So the official warning is the *latest* defensible cut-off, not necessarily the earliest; individual pre-warning traders who demonstrably knew (for example addresses linked to the attacker, or arbitrageurs who traded on the mint) can be excluded on the same logic.
6. **Direction and fault.** Most of these rules presuppose a wrongdoer (misstatement, breach, defective issue) or a contract. Gonka was itself the victim of a third party. The "obligation" for pre-warning losses is therefore strongest under the *issuer-risk* analogies that do not depend on fault (UCC §§ 8-202, 8-205, 8-210) and under the late-disclosure analogy (WpHG § 97: liability for not publishing promptly — which makes the *interval between the exploit and the warning* the issuer's responsibility). It is weaker as a matter of strict legal liability than as a matter of fair allocation.
7. **Buys versus sells after the warning.** A post-warning *purchase* is new, voluntary exposure ("speculation ... for his account"). A post-warning *sale* of tokens held from before the exploit crystallises a loss that the exploit caused; mitigation rules would not penalise it, and the warning itself said not to trade. The discretionary bucket should not lump the two together.
8. **Algorithms.** *Quoine v B2C2*: knowledge is tested in the programmer's mind when the code was written. Bots and limit orders placed before the warning but filled after it did not "trade after notice" in any meaningful sense. Consider treating order placement time, not fill time, as decisive, or giving the grace window specifically for this.
9. **No smooth decay curve in the sources.** Every "gradient" authority is a step function (Reg E tiers), a fixed grace period with a burden shift (HGB § 15(2)), or a judicial apportionment (BGB § 254). A continuously declining coefficient is a defensible policy design assembled from these, not something any statute prescribes.
10. **Halts.** In TradFi the cut-off is enforced by stopping the market (T1/T2 halts; nullification of post-halt trades). Where trading cannot be stopped, the announcement has to do the work of both the halt and the disclosure, which is a reason for humility about the first minutes after it.

---

## 11. Suggested mapping onto the proposal

| Zone | Analogy | Treatment supported |
|---|---|---|
| Trades before 19 Nov 2026 00:24:07 UTC by people without knowledge | *Basic* / *Halliburton II* class period; UCC §§ 8-202, 8-205, 8-210; WpHG § 97(1); HGB § 15(1) | Obligation. Measure: price paid / net out-of-pocket (§ 8-210(d); *Madoff*), netted per address; consider a look-back reference price (PSLRA § 78u-4(e)) so the hacker's return is reflected. |
| Short window after the warning | HGB § 15(2); Directive 2017/1132 art. 16(6); *Texas Gulf Sulphur* fn. 18; Reg E tier 1; T1/T2 halts; FSMA Sch. 10 para 1(3)(b) | Grace: full or near-full, ideally conditional on absence of knowledge (burden on the claimant, as in HGB § 15(2)). |
| Later post-warning buys | *Basic* ("no direct or indirect connection"); FSMA Sch. 10 para 3; § 11(a) Securities Act; *Elena D'Amico* / *New Flamenco*; *Chwee Kin Keong*; nullification of post-halt trades | No obligation. Any payment is ex gratia; a declining coefficient is an apportionment in the spirit of BGB § 254 / Russian CC art. 404. |
| Net winners on the compromised token | *Madoff*; *Janvey v. Brown* | Net gains against losses; no compensation of paper value. |

---

## 12. Sources opened (all URLs)

US Supreme Court and federal statutes/regulations
- https://www.law.cornell.edu/supremecourt/text/485/224 (Basic)
- https://www.law.cornell.edu/supct/html/03-932.ZO.html (Dura)
- https://www.law.cornell.edu/supremecourt/text/13-317 (Halliburton II)
- https://www.law.cornell.edu/uscode/text/15/78u-4 (PSLRA)
- https://www.govinfo.gov/content/pkg/CRPT-104srpt98/html/CRPT-104srpt98.htm (S. Rep. 104-98)
- https://www.law.cornell.edu/uscode/text/15/77k ; https://www.law.cornell.edu/uscode/text/15/77l
- https://www.law.cornell.edu/uscode/text/15/78lll (SIPA)
- https://www.law.cornell.edu/cfr/text/12/1005.6 (Reg E) ; https://www.law.cornell.edu/cfr/text/12/1026.12 (Reg Z)

US courts of appeals
- https://law.resource.org/pub/us/case/reporter/F2/401/401.F2d.833.296.30882_1.html (Texas Gulf Sulphur)
- https://law.resource.org/pub/us/case/reporter/F3/228/228.F3d.154.99-7904.1999.html (Ganino)
- https://www.govinfo.gov/content/pkg/USCOURTS-ca2-10-02378/pdf/USCOURTS-ca2-10-02378-0.pdf (Madoff)
- https://www.ca5.uscourts.gov/opinions/pub/13/13-10266-CV0.pdf (Janvey v. Brown)
- https://www.ca1.uscourts.gov/sites/ca1/files/opnfiles/05-1220-01A.pdf (PolyMedica)

UCC (Cornell LII)
- https://www.law.cornell.edu/ucc/8/8-210 ; /8/8-202 ; /8/8-205 ; /8/8-303 ; /8/8-105 ; /3/3-302 ; /1/1-202 ; /1/1-205 ; /4A/4A-202 ; /4A/4A-203 ; /4A/4A-204 ; /4/4-406

Market rules and regulators
- https://www.sec.gov/files/rules/sro/nysechx/2022/34-95825-ex5.pdf (Rule 7.10 text, NYSE Chicago)
- https://www.sec.gov/newsroom/press-releases/2013-222 (Knight Capital)
- https://nasdaqtrader.com/trader.aspx?id=tradehaltcodes
- https://delcode.delaware.gov/title6/c015/sc07/index.html

EU / UK / Germany / Russia / international
- https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32015L2366 (PSD2)
- https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017L1132 (Directive 2017/1132)
- https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R1129 ; ...CELEX:32024R2809 (Prospectus Regulation; Listing Act)
- https://www.legislation.gov.uk/uksi/2017/752/regulation/72/made ; /74/made ; /77/made (UK PSR 2017)
- https://www.legislation.gov.uk/ukpga/2000/8/schedule/10 (FSMA Sch. 10) ; https://www.legislation.gov.uk/uksi/2024/105/schedule/2 (POATR Sch. 2)
- https://caselaw.nationalarchives.gov.uk/uksc/2017/43 (The New Flamenco)
- https://www.gesetze-im-internet.de/englisch_bgb/englisch_bgb.html ; /hgb/__15.html ; /wphg/__97.html ; /wphg/__98.html
- https://www.zakonrf.info/gk/404/ ; https://www.zakonrf.info/gk/1083/
- https://uncitral.un.org/sites/uncitral.un.org/files/media-documents/uncitral/en/19-09951_e_ebook.pdf (CISG)
- https://www.unidroit.org/wp-content/uploads/2021/06/Unidroit-Principles-2016-English-bl.pdf
- https://www.law.kuleuven.be/personal/mstorme/european-private-law_en.pdf (DCFR)
- https://www.elitigation.sg/gd/s/2005_SGCA_2 ; https://www.elitigation.sg/gd/s/2020_SGCAI_2

Secondary
- https://researchonline.lse.ac.uk/id/eprint/64695/1/British_Westinghouse_Revisited_LSERO.pdf
- https://contractslawinaction.law.miami.edu/wp-content/uploads/2009/08/mitigationofdamages.pdf
- https://www.lit-sl.aoshearman.com/District-Of-Minnesota-Certifies-Securities-Fraud-
- https://corpgov.law.harvard.edu/2012/08/23/do-courts-count-cammer-factors/
- https://www.gsb.stanford.edu/faculty-research/publications/intraday-speed-adjustment-stock-prices-earnings-dividend-announcements

## 13. Not verified — do not quote without checking

- Exact wording of Viscount Haldane's sentence in [1912] AC 673 at 689 (two secondary versions differ by a word).
- *Cammer v. Bloom* opinion text; the *Medtronic* opinion text.
- NYSE Rule 7.10 / Nasdaq Rule 11890 paragraph numbering and the current numerical guidelines table (a 2026 NYSE filing reorganising Rule 7.10 showed up in search).
- Reporter citations 767 F.3d 430 for *Janvey v. Brown* and 432 F.3d 1 for *PolyMedica* (both from memory; the opinions were opened by docket number: 5th Cir. No. 13-10266, 1st Cir. No. 05-1220).
- Knight Capital figures were read through an automated page fetch of the SEC press release, not from a downloaded copy.
- Uniform RUPA (1997) § 704(c) "90 days" and § 703(b) "two years".
- Busse & Green (2002) figures; the usual length of Nasdaq news halts; how many Knight Capital trades were cancelled.
- Restatement (Second) of Torts § 402A comment j wording; any recall-notice case law.
- Current in-force status of FSMA s. 90 / Sch. 10 versus POATR 2024, and later amendments to Directive 2017/1132 art. 16.
