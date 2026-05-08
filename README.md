# specguard

A formal-logic checker for aerospace safety standards.

Aerospace standards split their requirements into two layers. The PSSA is the analysis side, the safety claims a system must obey. The SPEC is the contract side, the formal requirements the design will be built against. specguard encodes both layers as Z3 constraints and runs three generic checks: internal consistency of the PSSA, internal consistency of the SPEC, and entailment of every PSSA claim by the SPEC. Defects surface from the algebra itself, wherever the encoded structure exposes them.

## Run

```
pip install z3-solver
python solve.py                                   # runs against the worked example
python solve.py --reqs path/to/your/file.py       # runs against your own encoding
```

A requirements file is any Python file that exposes two lists, `PSSA_REQUIREMENTS` and `SPEC_REQUIREMENTS`, each holding `Req(id, text, constraint)` entries. See the worked example for the shape.

## Worked example

`examples/arp4754b_appendix_e.py` encodes Tables E12 through E14 and Table E19 of ARP4754B Appendix E, the Wheel Brake System for fictional aircraft S18. Running specguard against it surfaces one logical gap in the standard as published.

Writeup: https://habibdebaya.github.io/specguard/

## Encoding from a PDF

`encode.py` takes a PDF of an aerospace safety standard and a free-text section description and produces a PSSA/SPEC requirements file in the same shape as the worked example. The encoding is performed by Claude Opus 4.7. Set `ANTHROPIC_API_KEY` and run:

```
python encode.py pdfs/your_standard.pdf \
    --section "Appendix E, Tables E12 through E14, pages 137-139" \
    --out generated/your_section.py
```

Pass `--dry-run` to see the assembled prompt without making the API call.
