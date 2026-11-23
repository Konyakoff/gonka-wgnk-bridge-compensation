# verify/ — recompute the register yourself

```bash
pip install -r verify/requirements.txt      # pandas, pyarrow, openpyxl
python verify/run.py                        # about a minute; no network, no API keys
```

The script copies `data/raw/` into a temporary directory, runs the model and the three options from `code/`, and compares
the result with `registers/register_detailed.csv`, `registers/register.csv`, `model/summary_three_options.json` and
`model/critique.json`. Expected last line:

```
OK — the published register, summary and self-audit figures are reproduced from data/raw: 0 differences.
```

`--work DIR --keep` leaves the recomputed tables in `DIR/model/` for inspection.

What this proves: the register follows from the raw data and the published code. What it does not prove: that the raw data
is complete and correct (re-fetch transactions from a block explorer to check) and that the method is fair (see
`CRITIQUE.md`).
