# specguard

A formal-logic checker for aerospace safety standards.

Built around ARP4754B Appendix E, the worked example of the Wheel Brake System for fictional aircraft S18. The requirements are encoded as Z3 constraints across two collections (`PSSA_REQUIREMENTS` from Tables E12–E14 and `SPEC_REQUIREMENTS` from Table E19), and three checks run over them: SPEC internal consistency, PSSA internal consistency, and entailment of each PSSA requirement by the SPEC.

The entailment check surfaces one logical gap in the standard as published.

## Run

```
pip install z3-solver
python solve.py
```

## Writeup

https://habibdebaya.github.io/specguard/
