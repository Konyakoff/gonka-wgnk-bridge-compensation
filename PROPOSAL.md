**English** | [Русский](PROPOSAL.ru.md)

> [!IMPORTANT]
> **Draft for community discussion — not an official position of Gonka or its Core Team.** Published by Sergey Konyakov
> ([@Konyakoff](https://github.com/Konyakoff)), a community member. The research was done with Claude Code (Fable 5.2); the
> author has not yet independently verified every address and amount. Community members and the Core Team are asked to
> re-check the logic of the calculation and the listed addresses and amounts. A shared position on compensation is to be
> reached through discussion.

# Proposal: how to make people whole after the WGNK bridge hack

This is the proposal in words. The slides in [`presentations/`](presentations/) show the same content visually; the
calculation is specified in [`METHODOLOGY.md`](METHODOLOGY.md); the weak points of this proposal are in
[`CRITIQUE.md`](CRITIQUE.md).

## 1. What happened

| Time (UTC) | Event |
|---|---|
| 18 Nov 2026, 18:00:59 | the attacker submits the epoch-462 group key to the bridge contract (Ethereum block 26,443,607) |
| 18:01:35 – 18:01:59 | withdraws the bridge reserve: 884,150.87 USDT and 647.74 USDC |
| 18:02:11 | mints 22,000,000 WGNK with no backing; the last block before the mint is 26,443,612 |
| 18:04 – 18:24 | dumps WGNK into the Uniswap pools (price −95%); the bridge delivers 13,000,000 GNK to the attacker out of the escrow that backed WGNK |
| 18:28 | first public alert (a security firm on X) |
| 19 Nov, 00:18 | the project confirms the incident |
| **19 Nov, 00:24:07** | **the project's official X account: “Do not trade WGNK”** |
| 19 Nov, 07:40 – 09:07 | the attacker returns 593.435 ETH and 12,900,401 GNK |

Returned: 99.2% of the GNK and 97.8% of the ETH. Not returned: 13.3 ETH and 99,599 GNK.

## 2. Three rules, the same for everyone

1. **What was yours before the hack is yours.** WGNK in a wallet, in a liquidity position or in transit through the bridge
   at the end of block 26,443,612 is honoured one for one in native GNK (or, at the holder's choice, in new WGNK).
2. **Lost money is returned in the same currency.** What a person paid for WGNK after the hack, minus what they received,
   comes back in the currency they paid: USDT, USDC, DAI, ETH.
3. **Payouts let nobody profit.** WGNK bought after the hack is voided; a gain made on trading is deducted from the payout;
   the attacker and linked addresses get nothing.

Where WGNK and money have to be compared, the pre-hack price **p0 = $0.142881** is used — the volume-weighted price of all
118 Uniswap trades in the 24 hours before the attack.

## 3. One dividing line

Until the project itself said “do not trade”, people traded while the project was silent; their losses are treated as a
**commitment the project takes on**. After the warning, a trader knew or could have known the risk; compensating those
losses is **goodwill**, and the community decides how much.

| | Swaps | Volume | Share of volume |
|---|---:|---:|---:|
| Window A — attack start to the warning (blocks 26,443,607–26,445,519) | 2,019 | $554,429 | 97% |
| Window B — warning to the data freeze (to block 26,475,449, 23 Nov 04:30 UTC) | 1,261 | $15,841 | 3% |

Why this second: case law and practice are summarised in [`legal/LEGAL_RESEARCH.md`](legal/LEGAL_RESEARCH.md). In short —
after an official correction a trader bears their own risk; a warning must be able to reach people and leave time to react;
after notice, responsibility is shared rather than all-or-nothing; distributions follow net loss. There is **no direct court
precedent** for a bridge hack, and practice after DeFi incidents is sometimes stricter (a snapshot at the moment of the
hack). The line at the official warning is the latest defensible one, i.e. it favours people. This is not legal advice.

## 4. Three options for trades after the warning

A gain made after the warning is deducted in every option. A net loss made after the warning is compensated:

- **Option 1 — not at all.**
- **Option 2 — a declining share**, tied to when the warning reached each channel:

  | Bought (UTC) | Share | Why |
  |---|---:|---|
  | until 19 Nov 01:35:41 | ½ | the warning exists on X only |
  | until 19 Nov 12:03:00 | ¼ | repeated in the press; not yet on the project's website |
  | until 20 Nov 00:24:07 | ⅛ | on every official channel; one full day in every time zone |
  | later | 0 | |

  The fractions are a policy choice, not a rule of law.
- **Option 3 — in full**, up to the data freeze.

| | Option 1 | Option 2 | Option 3 |
|---|---:|---:|---:|
| Recipients (payee addresses) | 948 | 989 | 997 |
| GNK (or new WGNK) | 13,032,441 | 13,035,064 | 13,037,901 |
| USDT | 213,395.34 | 215,650.17 | 225,171.55 |
| USDC | 21,880.08 | 22,345.27 | 24,192.27 |
| DAI | 26.89 | 30.40 | 35.83 |
| ETH | 34.1599 | 34.3856 | 35.5408 |
| Bridge reserve restored | $884,799 | $884,799 | $884,799 |
| **Protocol top-up** | **$158,074** | **$161,563** | **$175,340** |
| Share of the community pool | 0.96% | 0.98% | 1.06% |

Only 90 recipients are paid differently under the three options; the other 907 get the same in each. The choice
between options moves the cost by $17,266: it is a choice of principle more than of money.

## 5. Who gets what (option 1)

| Who | What they receive | Addresses | Total |
|---|---|---:|---|
| Held WGNK and did not trade | GNK one for one | 761 | 7,092,186 GNK |
| Sold cheap after the hack | pre-hack WGNK minus proceeds / p0, in GNK | 3 | 8,899 GNK |
| Bought cheap or traded at a loss | money spent minus money received, same currency | 92 | $44,124 + 9.53 ETH |
| Held and traded | GNK one for one plus net money spent | 72 | 1,129,986 GNK + $56,560 + 2.67 ETH |
| Liquidity providers | WGNK of the position one for one, plus the money and fees taken out of it | 20 | 4,801,369 GNK + $134,618 + 21.96 ETH |
| Holders of bridged USDT/USDC on Gonka | nothing is sent: the backing is restored in the new bridge | 18 on Gonka | 884,150.87 USDT + 647.74 USDC |
| Sent GNK into the bridge, WGNK never minted | the locked GNK goes back to the sender | 27 on Gonka | 1,509.70 GNK |
| Traded at a profit; the attacker | nothing | — | 0 |

Money columns are USDT, USDC and DAI together. The full per-address list is in [`registers/`](registers/).

## 6. Where the money comes from (option 1)

- **Money.** The attacker returned 593.435 ETH ($1,026,136 at $1,729.15). Needed: 34.1599 ETH and
  $235,302 in stablecoins to people, and $884,799 for the bridge reserve. Shortfall: 88.50 ETH.
- **GNK.** Needed: 13,033,951 GNK. Available: 12,900,401 GNK returned by the attacker (already in the community
  pool) and 98,277 GNK still in the bridge escrow. Shortfall: 35,273 GNK.
- **Protocol top-up** = the two shortfalls = **$158,074**, or 0.96% of the community pool (115,520,511 GNK).
- The stablecoins are bought with the returned ETH, so the figure depends on the ETH price: at ETH −10% the top-up is
  $254,780, at +10% it is $61,367. Converting right after the decision removes this exposure.

## 7. Steps to payout

1. **Discussion and vote.** The community agrees on the line and chooses option 1, 2 or 3; payouts from the community pool
   are decided only by on-chain governance.
2. **Check yourself in the register.** Address, category and amount under every option; an objection window; a separate
   review for those who can show they could not have seen the warning.
3. **Confirm the address.** GNK goes to the Gonka address of the same key; another address, or new WGNK instead of GNK, on
   a signature with the Ethereum key.
4. **Preconditions.** Cancel by governance the bridge claims for unbacked WGNK (1,280,942 WGNK are pending), stop the old
   WGNK contract, convert the returned ETH.
5. **Payout.** GNK from the community pool and the escrow; USDT, USDC and ETH from the returned ETH. Old WGNK is voided.

## 8. What you are asked to check

- Is the dividing line right — or should it be earlier (the first public alert at 18:28) or softer?
- Which option for trades after the warning?
- Is your address in the register, with the right amounts?
- The weak points listed in [`CRITIQUE.md`](CRITIQUE.md): profit that stays with traders ($96,606), the generosity of
  the line, the concentration of payouts, the pending bridge claims, addresses that are not people, the ETH price.
- Everything else: the code, the data, the arithmetic. See [`AGENTS.md`](AGENTS.md) and [`verify/`](verify/).
