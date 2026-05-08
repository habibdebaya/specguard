"""
Z3 verification of a requirements file.

Three checks:
  1. SPEC internal consistency
  2. PSSA internal consistency
  3. For each PSSA requirement P, does SPEC entail P?
"""

import argparse
import importlib.util
from pathlib import Path

import z3
from z3 import Solver, unsat, Not, Bool


DEFAULT_REQS = Path(__file__).parent / "examples" / "arp4754b_appendix_e.py"


def free_vars(expr):
    seen = set()
    stack = [expr]
    out = []
    while stack:
        node = stack.pop()
        if z3.is_const(node) and node.decl().kind() == z3.Z3_OP_UNINTERPRETED:
            key = node.decl().name()
            if key not in seen:
                seen.add(key)
                out.append(node)
        else:
            stack.extend(node.children())
    return out


def load_requirements(path):
    spec = importlib.util.spec_from_file_location("requirements_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PSSA_REQUIREMENTS, module.SPEC_REQUIREMENTS


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
            witness = ", ".join(f"{v}={m[v]}" for v in free_vars(p.constraint))
            print(f"[{p.id}] FAIL")
            print(f"        text:    {p.text}")
            print(f"        witness: {witness}")


def main():
    parser = argparse.ArgumentParser(
        description="Run formal-logic checks against a requirements file."
    )
    parser.add_argument(
        "--reqs",
        default=str(DEFAULT_REQS),
        help="Path to a Python file exposing PSSA_REQUIREMENTS and SPEC_REQUIREMENTS lists.",
    )
    args = parser.parse_args()

    pssa, spec_reqs = load_requirements(Path(args.reqs))

    ids = [r.id for r in pssa + spec_reqs]
    assert len(ids) == len(set(ids)), "duplicate requirement IDs"

    check_consistency("SPEC", spec_reqs)
    check_consistency("PSSA", pssa)
    check_entailment(spec_reqs, pssa)


if __name__ == "__main__":
    main()
