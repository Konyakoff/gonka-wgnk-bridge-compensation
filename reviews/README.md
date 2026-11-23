# reviews/ — three independent reviews, published as they were written

| Folder | What it is |
|---|---|
| `non_lp_recompute/` | recomputation of owners without liquidity positions from raw data by a separate reviewer who had no access to the model code; `REPORT.md`, the script, and the result of its run against the published tables |
| `lp_recheck/` | recomputation of every liquidity position directly from Ethereum contract state at the three blocks, again without the model code |
| `red_team/` | adversarial review by a reviewer who received only the draft package and no hints: 14 findings, scripts and address lists |

The reviewers were separate AI agents (Claude) working in isolated sessions; the reports were not edited for content.

**Please read with these points in mind.**

- **Observations about specific addresses are facts read from the blockchain, nothing more.** Who controls an address was
  not established by anyone. Where a report notes, for example, that one address created a pool or withdrew liquidity
  before the warning, it describes on-chain events; the author draws no conclusion about any person, team or organisation
  and asks readers not to either. The reports themselves flag such passages as inference.
- **The reports describe the pre-publication draft.** Errors they found were corrected before this repository was
  published; the list is in [`CRITIQUE.md`](../CRITIQUE.md) section 2. Numbers quoted in a report may therefore differ from
  the published register (for example the protocol top-up, or the count of profit-keeping owners, which the reviewers
  define slightly differently). Where a report says “version 1” or “first release”, it means that draft.
- **File paths inside the reports refer to the author's working package**, not to this repository:
  `02_onchain_raw/` → `data/raw/`, `03_model/` → `model/`, `04_registers/` → `registers/`,
  `05_independent_check/` → `reviews/non_lp_recompute/`, `06_code/` → `code/`, `08_critique/` → `CRITIQUE.md`,
  `model/critique/` and `reviews/`. In the published draft the register was a single file `register_all_options.csv`;
  here it is `registers/register_detailed.csv`.
- **The only edit:** absolute paths of the author's machine and the name of its container image in run commands were
  replaced by neutral placeholders (`<data-dir>`, `<work-dir>`, `<python-image>`).
