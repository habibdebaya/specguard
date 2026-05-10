# specguard

A formal verification tool for aerospace safety standards. specguard encodes the requirements of a standard as Z3 constraints via a large language model, has the encoding reviewed by a human for fidelity, and runs three families of generic logical checks against the result.

The writeup for the worked example of ARP4754B Appendix E (Wheel Brake System) is at https://habibdebaya.github.io/specguard/.

## Run

```
pip install z3-solver
python solve.py                                  # runs against the worked example
python solve.py --reqs path/to/your/file.py      # runs against your own encoding
```

The `.tex` and `.pdf` reports are written to `reports/` automatically.
