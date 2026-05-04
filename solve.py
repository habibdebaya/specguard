"""
Z3 verification of the requirements in reqs.py.

Three checks:
  1. SPEC internal consistency
  2. PSSA internal consistency
  3. For each PSSA requirement P, does SPEC entail P?
"""

from z3 import Solver, sat, unsat, Not, Bool

from reqs import PSSA_REQUIREMENTS, SPEC_REQUIREMENTS


def check_consistency(name, requirements):
    s = Solver()
    for r in requirements:
        s.assert_and_track(r.constraint, Bool(f"track_{r.id}"))
    result = s.check()
    print(f"\n== {name} internal consistency ==")
    print(result)
    if result == unsat:
        for c in s.unsat_core():
            print(f"  conflicting: {str(c).removeprefix('track_')}")


def check_entailment(spec, pssa):
    print("\n== SPEC entails each PSSA requirement ==")
    for p in pssa:
        s = Solver()
        for r in spec:
            s.add(r.constraint)
        s.add(Not(p.constraint))
        result = s.check()
        if result == unsat:
            print(f"[{p.id}] PASS")
        else:
            m = s.model()
            relevant = str(p.constraint)
            witness = ", ".join(
                f"{d.name()}={m[d]}" for d in m.decls() if d.name() in relevant
            )
            print(f"[{p.id}] FAIL")
            print(f"        text:    {p.text}")
            print(f"        witness: {witness}")


def main():
    ids = [r.id for r in PSSA_REQUIREMENTS + SPEC_REQUIREMENTS]
    assert len(ids) == len(set(ids)), "duplicate requirement IDs"

    check_consistency("SPEC", SPEC_REQUIREMENTS)
    check_consistency("PSSA", PSSA_REQUIREMENTS)
    check_entailment(SPEC_REQUIREMENTS, PSSA_REQUIREMENTS)


if __name__ == "__main__":
    main()
