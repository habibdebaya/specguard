You are encoding numbered requirements from an aerospace safety standard into Z3 constraints. The output feeds a formal-logic checker that runs three families of operations: internal consistency of each collection, directional entailment of analysis claims by their corresponding specifications (within and across system layers), and bidirectional equivalence between alternate restatements of the same claim.

Aerospace standards organise their requirements into a layered PSSA/SPEC structure. Each system layer (airplane, system, subsystem, item) has its own analysis-side claims and contract-side commitments. Your task is to encode every assertable table within the section the user names, faithfully and comprehensively.

## Section to encode

{SECTION}

## Methodology: three passes

Encode the section in three deliberate passes.

**First pass — plan the symbol table.** Walk the section and identify every distinct logical concept that needs a Z3 symbol. Use `Bool` for propositional claims and properties. Use `Real` for probabilities, failure rates, durations, distances, pressures, response times, and any other measured quantity. Reuse one symbol across requirements that name the same physical concept. Introduce a new symbol when concepts differ even if the names sound similar (for example, a per-flight probability and a per-hour failure rate are distinct symbols, related through an axiom).

**Second pass — encode each requirement.** Pair the verbatim English text with a Z3 constraint that captures its meaning. Preserve the original text exactly, including punctuation, capitalisation, and embedded quotation marks. The constraint should follow the structure of the English faithfully: conditional language becomes `Implies`, conjunction becomes `And`, disjunction becomes `Or`, negation becomes `Not`, comparisons become inequalities on `Real` symbols.

**Third pass — cross-reference.** Verify that constraints referencing the same physical concept use the same symbol across collections. Identify pairs of requirements that purport to be restatements of the same claim, possibly in different units or different language. Identify the entailment direction the standard expects to hold between analysis-side and contract-side collections. Encode these in `EQUIVALENCE_MAP` and `ENTAILMENT_PAIRS`.

## What to encode and what to skip

Encode tables that carry numbered requirements expressible as logical claims about the system. These include analysis-side claims (PSSA), contract-side specifications (SPEC), assumption catalogues, and interface requirements that contain real constraints (timing, response).

Skip tables whose content is evidence, metadata, or pure traceability. These include correctness checks, completeness checks, validation matrices, verification matrices, configuration indices, allocation tables that duplicate other tables verbatim, and figures. Note skipped tables in the file's docstring with the reason.

## Output format

Return a single Python file. No prose around it. No markdown fences. The first character of your response must be the opening triple-quote of the module docstring. The file's structure:

1. **Module docstring** describing what was encoded, what was skipped (with reasons), the system layers covered, and any encoding decisions that depart from a literal translation. Flag anything that may need solver-side attention (capabilities beyond Z3's standard linear arithmetic, axioms with non-trivial assumptions, non-standard logical structure).

2. **Imports**: `from dataclasses import dataclass` and `from z3 import Bool, Real, And, Or, Not, Implies`.

3. **The `Req` dataclass** with fields `id: str`, `text: str`, `constraint: object`.

4. **Symbol table**: every Z3 symbol the constraints reference, declared once at the top.

5. **`UNIT_RELATIONS`** (when applicable): a Python list of Z3 expressions used as axioms during every check. Use this for unit conversions (per-flight to per-hour, etc.) and shared algebraic relations the standard relies on.

6. **One Python list per requirement collection** discovered in the section. Use descriptive uppercase names that reflect the layer and table type, such as `PSSA_REQUIREMENTS`, `SPEC_REQUIREMENTS`, `BSCU_PSSA_REQUIREMENTS`, `BSCU_SPEC_REQUIREMENTS`, `AIRPLANE_REQUIREMENTS`, `ALT_PSSA_REQUIREMENTS`. Each entry is a `Req(id, text, constraint)`. The `text` field is verbatim English from the standard. The `constraint` field is the Z3 expression.

7. **`ENTAILMENT_PAIRS`** (when applicable): a list of `(entailer_collection_name, target_collection_name)` tuples declaring directional entailment checks the solver should run. Standard pattern: each layer's SPEC entails its PSSA.

8. **`EQUIVALENCE_MAP`** (when applicable): a list of `(id_a, id_b)` tuples declaring pairs of requirements that should be equivalent restatements. The solver checks each pair for bidirectional entailment under the axioms.

## Encoding conventions

- The `id` field is the standard's own identifier verbatim (for example `E12-1`, `S18-WBS-R-0020`).
- Reuse one symbol across requirements that refer to the same proposition or quantity.
- "Shall not exceed X" and "less than X" become inequality constraints on a `Real`.
- "Shall be" claims about system properties become an assertion of the corresponding `Bool`.
- "When A, then B" becomes `Implies(a, b)`.
- "No single failure shall cause both A and B" becomes `Not(And(a, b))`.
- Two requirements stated in different units (per flight versus per hour, per landing versus per flight) use distinct symbols joined by axioms in `UNIT_RELATIONS`.

## Worked example of the file shape

A miniature illustration. Your output for the requested section will be substantially longer.

```python
"""
Encoding of <STANDARD> <SECTION>.

Tables encoded:
  - Table X: <description> (PSSA)
  - Table Y: <description> (SPEC)

Tables skipped:
  - Table Z: validation matrix, evidence rather than claims.

Notes:
  - Tables X and Y use different units for the same physical quantity;
    UNIT_RELATIONS carries the conversion under the <N>-hour flight
    assumption from section <S>.
"""

from dataclasses import dataclass

from z3 import Bool, Real, And, Or, Not, Implies


@dataclass
class Req:
    id: str
    text: str
    constraint: object


# Symbol table
some_event             = Bool("some_event")
some_property          = Bool("some_property")
p_some_failure         = Real("p_some_failure")
lambda_some_failure    = Real("lambda_some_failure")
flight_duration_hours  = Real("flight_duration_hours")


UNIT_RELATIONS = [
    flight_duration_hours == 5,
    p_some_failure == lambda_some_failure * flight_duration_hours,
]


PSSA_REQUIREMENTS = [
    Req("X-1",
        "If some event occurs, then property holds.",
        Implies(some_event, some_property)),
    Req("X-2",
        "The probability of some failure shall not exceed 1.0E-05 per flight.",
        p_some_failure <= 1.0e-05),
]


SPEC_REQUIREMENTS = [
    Req("Y-1",
        "If some event occurs, then property holds.",
        Implies(some_event, some_property)),
]


ALT_PSSA_REQUIREMENTS = [
    Req("Z-1",
        "The failure rate of some failure shall not exceed 1.0E-05 per hour of flight.",
        lambda_some_failure <= 1.0e-05),
]


ENTAILMENT_PAIRS = [
    ("SPEC_REQUIREMENTS", "PSSA_REQUIREMENTS"),
]


EQUIVALENCE_MAP = [
    ("X-2", "Z-1"),
]
```

## Final instructions

Return the Python file only. Do not wrap it in markdown fences. Do not add commentary before or after. The first character of your response must be the opening triple-quote of the module docstring.
