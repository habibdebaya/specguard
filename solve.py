"""
Z3 verification of a requirements file.

The solver carries no domain knowledge. It reads the file and runs whatever
the file declares. The file may expose:

  - Any number of named lists of Req objects. These are auto-discovered
    and treated as requirement collections. Each gets an internal-consistency
    check.
  - UNIT_RELATIONS, an optional list of Z3 expressions used as axioms in
    every check.
  - ENTAILMENT_PAIRS, an optional list of (entailer_name, target_name)
    tuples. For each pair the solver checks that every constraint in the
    target is entailed by the entailer under the axioms.
  - EQUIVALENCE_MAP, an optional list of (id_a, id_b) tuples. Each pair is
    checked for bidirectional entailment under the axioms, surfacing
    witnesses when the two are not equivalent.

A LaTeX report is generated automatically at reports/<stem>.tex, where
<stem> is the basename of the requirements file.
"""

import argparse
import importlib.util
from pathlib import Path

import z3
from z3 import Solver, unsat, Not, Bool

from report import write_report


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


def load_module(path):
    spec = importlib.util.spec_from_file_location("requirements_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def is_req_collection(value):
    if not isinstance(value, list):
        return False
    return all(hasattr(item, "id") and hasattr(item, "constraint") for item in value)


def discover_collections(module):
    collections = {}
    for name, value in vars(module).items():
        if name.startswith("_"):
            continue
        if is_req_collection(value):
            collections[name] = value
    return collections


def get_axioms(module):
    return list(getattr(module, "UNIT_RELATIONS", []))


def get_entailment_pairs(module):
    return list(getattr(module, "ENTAILMENT_PAIRS", []))


def get_equivalence_map(module):
    return list(getattr(module, "EQUIVALENCE_MAP", []))


def index_by_id(collections):
    out = {}
    for reqs in collections.values():
        for r in reqs:
            out[r.id] = r
    return out


def format_value(value):
    if value is None:
        return "?"
    try:
        if z3.is_rational_value(value):
            n = value.numerator_as_long()
            d = value.denominator_as_long()
            if d == 1:
                return str(n)
            f = n / d
            if abs(f) > 0 and (abs(f) < 1e-2 or abs(f) >= 1e4):
                return f"{f:.4e}"
            return f"{f:g}"
        if z3.is_int_value(value):
            return str(value.as_long())
    except Exception:
        pass
    return str(value)


def witness_for(model, constraint):
    vars_ref = free_vars(constraint)
    return ", ".join(f"{v}={format_value(model[v])}" for v in vars_ref)


def check_consistency(name, requirements, axioms):
    s = Solver()
    for ax in axioms:
        s.add(ax)
    for r in requirements:
        s.assert_and_track(r.constraint, Bool(f"track_{r.id}"))
    result = s.check()
    core = []
    if result == unsat:
        core = [str(c).removeprefix("track_") for c in s.unsat_core()]
    return {"name": name, "result": str(result), "core": core}


def entails(entailer_constraints, target_constraint, axioms):
    s = Solver()
    for ax in axioms:
        s.add(ax)
    for c in entailer_constraints:
        s.add(c)
    s.add(Not(target_constraint))
    result = s.check()
    if result == unsat:
        return True, None
    return False, witness_for(s.model(), target_constraint)


def check_entailment(entailer_name, target_name, entailer_reqs, target_reqs, axioms):
    items = []
    entailer_cs = [r.constraint for r in entailer_reqs]
    for p in target_reqs:
        passed, witness = entails(entailer_cs, p.constraint, axioms)
        items.append({
            "id": p.id,
            "text": p.text,
            "passed": passed,
            "witness": witness,
        })
    return {"entailer": entailer_name, "target": target_name, "items": items}


def check_equivalence_pair(id_a, id_b, all_reqs, axioms):
    if id_a not in all_reqs or id_b not in all_reqs:
        return {"id_a": id_a, "id_b": id_b, "skipped": True}
    a = all_reqs[id_a]
    b = all_reqs[id_b]
    a_to_b, witness_ab = entails([a.constraint], b.constraint, axioms)
    b_to_a, witness_ba = entails([b.constraint], a.constraint, axioms)
    return {
        "id_a": id_a,
        "id_b": id_b,
        "text_a": a.text,
        "text_b": b.text,
        "constraint_a": a.constraint,
        "constraint_b": b.constraint,
        "a_to_b": a_to_b,
        "b_to_a": b_to_a,
        "witness_ab": witness_ab,
        "witness_ba": witness_ba,
        "equivalent": a_to_b and b_to_a,
        "skipped": False,
    }


def print_consistency(result):
    print(f"\n== {result['name']} internal consistency ==")
    print(result["result"])
    for c in result["core"]:
        print(f"  conflicting: {c}")


def print_entailment(result):
    print(f"\n== {result['entailer']} entails each {result['target']} ==")
    pass_count = sum(1 for i in result["items"] if i["passed"])
    fail_count = len(result["items"]) - pass_count
    for item in result["items"]:
        if item["passed"]:
            print(f"[{item['id']}] PASS")
        else:
            print(f"[{item['id']}] FAIL")
            print(f"        text:    {item['text']}")
            print(f"        witness: {item['witness']}")
    print(f"  {pass_count} passed, {fail_count} failed")


def print_equivalence(results):
    print("\n== Restatement equivalence (under axioms) ==")
    eq = neq = 0
    for r in results:
        if r["skipped"]:
            print(f"[{r['id_a']} <=> {r['id_b']}] SKIPPED (id not found)")
            continue
        if r["equivalent"]:
            print(f"[{r['id_a']} <=> {r['id_b']}] EQUIVALENT")
            eq += 1
        else:
            print(f"[{r['id_a']} <=> {r['id_b']}] NOT EQUIVALENT")
            print(f"        {r['id_a']}: {r['text_a']}")
            print(f"        {r['id_b']}: {r['text_b']}")
            print(f"        {r['id_a']} entails {r['id_b']}: {'PASS' if r['a_to_b'] else 'FAIL'}")
            if not r["a_to_b"]:
                print(f"          witness: {r['witness_ab']}")
            print(f"        {r['id_b']} entails {r['id_a']}: {'PASS' if r['b_to_a'] else 'FAIL'}")
            if not r["b_to_a"]:
                print(f"          witness: {r['witness_ba']}")
            neq += 1
    print(f"  {eq} equivalent, {neq} not equivalent")


def main():
    parser = argparse.ArgumentParser(
        description="Run formal-logic checks against a requirements file."
    )
    parser.add_argument(
        "--reqs",
        default=str(DEFAULT_REQS),
        help="Path to a Python file declaring requirement collections, axioms, and check pairs.",
    )
    args = parser.parse_args()

    module = load_module(Path(args.reqs))
    collections = discover_collections(module)
    axioms = get_axioms(module)
    entailment_pairs = get_entailment_pairs(module)
    equivalence_map = get_equivalence_map(module)

    all_ids = []
    for reqs in collections.values():
        all_ids.extend(r.id for r in reqs)
    assert len(all_ids) == len(set(all_ids)), "duplicate requirement IDs across collections"

    print(f"Loaded collections: {', '.join(collections.keys())}")
    print(f"Axioms: {len(axioms)} relation(s)")
    print(f"Entailment pairs: {len(entailment_pairs)}")
    print(f"Restatement pairs: {len(equivalence_map)}")

    consistency_results = [
        check_consistency(name, reqs, axioms) for name, reqs in collections.items()
    ]

    entailment_results = []
    for entailer_name, target_name in entailment_pairs:
        if entailer_name in collections and target_name in collections:
            entailment_results.append(check_entailment(
                entailer_name, target_name,
                collections[entailer_name], collections[target_name],
                axioms,
            ))
        else:
            missing = [n for n in (entailer_name, target_name) if n not in collections]
            print(f"\n== {entailer_name} entails each {target_name} ==")
            print(f"SKIPPED (collection not found: {', '.join(missing)})")

    all_reqs = index_by_id(collections)
    equivalence_results = [
        check_equivalence_pair(a, b, all_reqs, axioms) for a, b in equivalence_map
    ]

    for r in consistency_results:
        print_consistency(r)
    for r in entailment_results:
        print_entailment(r)
    if equivalence_results:
        print_equivalence(equivalence_results)

    tex_path, pdf_path = write_report(
        args.reqs, collections, axioms,
        consistency_results, entailment_results, equivalence_results,
    )
    print(f"\nLaTeX report written to {tex_path}")
    if pdf_path is not None:
        print(f"PDF report written to {pdf_path}")
    else:
        print("PDF compilation skipped (pdflatex not found or failed).")


if __name__ == "__main__":
    main()
