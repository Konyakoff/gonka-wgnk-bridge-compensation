# code/

## gonka_research/ — the calculation (runs with pandas only)

| File | Role |
|---|---|
| `exploit_const.py` | constants: contract addresses, key blocks, the warning time, the option-2 ladder |
| `lite.py` | paths and file writing |
| `exploit_model.py` | balances at the snapshot, per-transaction changes of WGNK and money, address groups, liquidity positions, per-owner base table |
| `comp_variants.py` | windows A and B, the three options, payout split by address, protocol top-up, checks |
| `critique.py` | the self-audit checks behind `CRITIQUE.md` |

Run it through [`verify/run.py`](../verify/run.py). Comments and docstrings are in Russian (the author's working
language); the method is described in English in [`METHODOLOGY.md`](../METHODOLOGY.md).

## collector/ — how the raw data was obtained (reference only)

`exploit.py` is the collector that produced `data/raw/`; `bridge.py` derives the Gonka address from an Ethereum public
key. They are published so that the provenance of every file can be read, but they do not run from this repository: they
depend on the author's private tooling (an Etherscan client, an archive-RPC client and a database sync of Uniswap and
bridge logs) and need API keys. To check the data, re-fetch any transaction from a public block explorer instead.

The code that renders the PDF slides is not included: it needs brand fonts and images and adds nothing to the audit.
