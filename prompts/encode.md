You are encoding numbered requirements from an aerospace safety standard into Z3 constraints. The output feeds a formal-logic checker that runs three operations: internal consistency of the PSSA collection, internal consistency of the SPEC collection, and entailment of every PSSA claim by the SPEC.

Aerospace standards split their requirements into two layers. The PSSA is the analysis side, the safety claims a system must obey. The SPEC is the contract side, the formal requirements the design will be built against. Your task is to encode both layers from the section the user names. If the section contains only one of them, the other list will be empty.

## Section to encode

{SECTION}

Encode every numbered requirement that falls within this section. Ignore everything else in the PDF, including narrative text, figures, and requirements outside the section.

## Output format

Return a single Python file. No prose around it. No markdown fences. The file must be directly executable. Its structure:

1. A module docstring naming the source standard and the section.
2. Imports: `from dataclasses import dataclass` and `from z3 import Bool, Real, And, Or, Not, Implies`.
3. The `Req` dataclass with fields `id: str`, `text: str`, `constraint: object`.
4. A symbol table: declare every Z3 symbol the constraints reference, one per line. Use `Bool(...)` for propositions and `Real(...)` for quantities such as probabilities, distances, pressures.
5. Two module-level lists, `PSSA_REQUIREMENTS` and `SPEC_REQUIREMENTS`. Each entry is a `Req(id, text, constraint)`. The `text` field is the verbatim English from the standard. The `constraint` field is the Z3 expression.

Both lists must be present even if one is empty. If the section is purely analysis-side (PSSA) content, leave `SPEC_REQUIREMENTS = []`. If the section is purely contract-side (SPEC) content, leave `PSSA_REQUIREMENTS = []`.

## Encoding conventions

- Each numbered requirement becomes one `Req`. The `id` is the standard's own identifier verbatim (for example `E12-1`, `S18-WBS-R-0020`).
- Reuse symbols across requirements that refer to the same proposition or quantity. Two requirements that both speak of "loss of normal hydraulic equipment" share one symbol. Do not introduce a fresh symbol for every requirement.
- Propositions are `Bool`. Probabilities, distances, pressures, and other measured quantities are `Real`.
- "Shall not exceed X" and "less than X" become inequality constraints on a `Real`.
- "Shall be" claims about system properties become an assertion of the corresponding `Bool`.
- "When A, then B" becomes `Implies(a, b)`.
- "No single failure shall cause both A and B" becomes `Not(And(a, b))`.
- Preserve the exact English in the `text` field, including punctuation, capitalisation, and any embedded quotation marks.

## Worked example

A miniature illustration of the output shape. Your output for the requested section will be much longer.

```python
"""
Requirements data for [Standard Name], [Section Description].
"""

from dataclasses import dataclass

from z3 import Bool, Real, And, Or, Not, Implies


@dataclass
class Req:
    id: str
    text: str
    constraint: object


# Symbol table

system_has_redundancy = Bool("system_has_redundancy")
single_failure        = Bool("single_failure")
loss_of_function      = Bool("loss_of_function")
p_loss_of_function    = Real("p_loss_of_function")


PSSA_REQUIREMENTS = [
    Req("X-1",
        "No single failure shall cause loss of function",
        Implies(single_failure, Not(loss_of_function))),

    Req("X-2",
        "The probability of loss of function shall not exceed 1.0E-05 per flight hour",
        p_loss_of_function <= 1.0e-05),
]


SPEC_REQUIREMENTS = []
```

## Final instructions

Return the Python file only. Do not wrap it in markdown fences. Do not add commentary before or after. The first character of your response must be the opening triple-quote of the module docstring.
