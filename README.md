# specguard

**Checking whether written requirements agree.** specguard uses LLM-assisted translation, human review, and Z3 to find disagreements as technical requirements are repeated and refined.

**[Technical Report](https://habibdebaya.github.io/specguard/)**

## A concrete example

An earlier requirement says that when one brake control signal is off, the other must be on. A later specification drops that condition. specguard produces a counterexample: **both signals are off**, satisfying the encoded specification while violating the earlier obligation.

The case study encodes **176 requirements and assumptions** from ARP4754B’s wheel brake system example. The report examines five cases: a missing obligation, changed units, boundary differences, and a gap between component probability bounds and a system target, with their modelling assumptions.

## How it works

Source requirements → LLM-assisted encoding → human review → Z3 checks → counterexamples

Python records preserve source text and identifiers alongside constraints. The solver checks whether collections are consistent, specifications imply earlier obligations, and restatements are equivalent. Results depend on the encoding and declared assumptions.

## Run the example

With Python 3.9 or later:

```bash
pip install z3-solver
python solve.py
```

The included encoding runs locally without an API key. Results appear in the terminal; detailed TeX output is written to `reports/`. Installing `pdflatex` also enables PDF generation.

For another reviewed encoding:

```bash
python solve.py --reqs path/to/requirements.py
```

<details>
<summary>Generate a new encoding with an LLM</summary>

Install `anthropic` and set `ANTHROPIC_API_KEY` in your environment, then run:

```bash
python encode.py path/to/standard.pdf --section "Appendix E" --out examples/new_encoding.py
```

Review the generated Python and its interpretation of the source before running it. Add `--dry-run` to inspect the prompt without an API call.

</details>

## Code

| File | Purpose |
| --- | --- |
| [encode.py](encode.py) | PDF-to-constraints pipeline using the [encoding prompt](prompts/encode.md) |
| [Worked example](examples/arp4754b_appendix_e.py) | Source text, constraints, assumptions, and comparison pairs |
| [solve.py](solve.py) | Generic logical checks and counterexamples |
| [report.py](report.py) | Detailed TeX and PDF output |
