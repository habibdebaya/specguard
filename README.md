# specguard

A formal-logic checker for aerospace safety standards.

Aerospace standards organise their requirements into a layered PSSA/SPEC
structure. Each system layer has its own analysis-side claims (PSSA) and
contract-side commitments (SPEC). specguard encodes those layers as Z3
constraints and runs three families of generic checks: internal consistency
of every collection, directional entailment of analysis claims by their
corresponding specifications (within and across layers), and bidirectional
equivalence between alternate restatements of the same claim. Defects emerge
from the algebra wherever the encoded structure exposes them.

## Run

```
pip install z3-solver
python solve.py                                  # runs against the worked example
python solve.py --reqs path/to/your/file.py      # runs against your own encoding
```

## What a requirements file declares

A requirements file is any Python module that exposes one or more lists of
`Req(id, text, constraint)` entries plus optional declarations of what to
check:

- Any module-level list of `Req` objects becomes a requirement collection.
  Auto-discovered by name.
- `UNIT_RELATIONS` is an optional list of Z3 expressions used as axioms in
  every check, for unit conversions and shared algebraic relations.
- `ENTAILMENT_PAIRS` is an optional list of `(entailer, target)` tuples.
  For each pair, every constraint in the target must follow from the
  entailer under the axioms.
- `EQUIVALENCE_MAP` is an optional list of `(id_a, id_b)` tuples checked
  for bidirectional entailment under the axioms, surfacing witnesses when
  restatements disagree.

The solver carries no domain knowledge. It runs whatever the file declares.

## Worked example

`examples/arp4754b_appendix_e.py` encodes the full ARP4754B Appendix E,
the worked example of the Wheel Brake System for fictional aircraft S18.
The encoding spans three system layers (airplane, WBS, BSCU) and includes
the master assumption catalogue, with explicit unit-conversion axioms
derived from the five-hour average flight stated in section E.3.3.

Running specguard against it surfaces two logical defects in the standard
as published:

1. **E13-7.** The contract states only one direction of the conditional
   relationship between the HYD 1 Enable signal and the Alt/Emer Ctrl
   signal, leaving a state the analysis forbids that the contract admits.

2. **Unit mismatch between Tables E14 and E28.** Two safety assumptions
   (loss of an airplane electrical power bus, loss of a brake pedal
   position input) are restated in failure-rate-per-hour form rather than
   probability-per-flight form. Under the five-hour flight axiom the
   per-hour statements are five times weaker than the per-flight
   statements. The two formulations are not equivalent restatements.

Writeup: https://habibdebaya.github.io/specguard/

## Encoding from a PDF

`encode.py` takes a PDF of an aerospace safety standard and a free-text
section description and produces a requirements file in the same shape as
the worked example. The encoding is performed by Claude Opus 4.7. Set
`ANTHROPIC_API_KEY` and run:

```
python encode.py pdfs/arp4754b.pdf \
    --section "Appendix E" \
    --out generated/arp4754b_appendix_e.py
```

Pass `--dry-run` to see the assembled prompt without making the API call.

## LaTeX rendering

`python solve.py --latex report.tex` produces a typeset report containing
each requirement's verbatim English alongside its formal Z3 constraint
rendered in proper logical notation, the results of every check, and
witnesses for any failures. Compile with `pdflatex report.tex` to obtain
a PDF suitable for inclusion in a certification dossier or a technical
paper.
