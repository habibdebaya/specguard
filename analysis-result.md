# specguard review (ARP4754B Appendix E)

## 1. Faithfulness summary

High-level: the encoding is **mostly faithful** to the Appendix E content I could verify from the provided PDF parse (especially Tables E2, E10, E12-E14, E19, E22-E24, E28 and section E.3.11 text). The four headline findings are reproducible, but I found several fidelity issues that matter for a strict "verbatim + ID-faithful" claim.

- I verified the key source anchors against the PDF text:
  - Five-hour average flight: section E.3.3, page 108.
  - AFHA/SFHA wording split: Table E2 (page 112) vs Table E10 (page 128).
  - WBS PSSA rows used in findings: Tables E13/E14 (page 137).
  - WBS spec propagation: Table E19 (pages 142-144).
  - BSCU tables: E22/E23/E24 (pages 150-151).
  - WBS-level assumptions rewrite: Table E28 (pages 157-158).
  - Catastrophic threshold text: section E.3.11 paragraph 3 (page 119).

- Specific fidelity defects:
  - `examples/arp4754b_appendix_e.py:349` has a transcription typo for `S18-WBS-R-0046`: encoded text says "when **the** commanded by the flight crew"; Table E19 says "when commanded by the flight crew" (page 142).
  - Non-verbatim/fabricated IDs are used in several places:
    - `examples/arp4754b_appendix_e.py:579` and `examples/arp4754b_appendix_e.py:583` use `E23-1`/`E23-2`, but Table E23 rows are unnumbered assumptions (page 150).
    - `examples/arp4754b_appendix_e.py:289`-`examples/arp4754b_appendix_e.py:315` use `E28-WBS-ASMP-*`; Table E28 labels are `WBS PSSA ASMP 1..7` (pages 157-158).
    - `examples/arp4754b_appendix_e.py:954` uses `E.3.11-3`, which is a constructed paragraph reference, not a table requirement ID (page 119 narrative).

- Scope/completeness note:
  - For the major encoded tables in the declared scope, I did not find a clear missing numbered row in the main WBS/BSCU/Airplane requirement sets; coverage is broad and generally consistent with Table E19, Table E24, etc.

## 2. Correctness summary

- Solver logic is largely correct:
  - Entailment implementation is the standard unsat check of `(entailer ∧ axioms ∧ ¬target)` in `solve.py:136`-`solve.py:147`.
  - Equivalence runs both directions in `solve.py:163`-`solve.py:183`.
  - Witness reporting via free vars is reasonable, but only prints vars from the target formula (`solve.py:118`-`solve.py:121`).

- Axioms:
  - `UNIT_RELATIONS` is sound with respect to the cited source: `flight_duration_hours == 5` matches E.3.3 (page 108) and conversion equations are dimensionally valid.
  - `COMPOSITION_RELATIONS` is reasonable if interpreted as probabilistic independence composition: `p_joint = p1 * p2` plus threshold `1.0e-09` from E.3.11 (page 119).

- Findings verification (reproduced by running `.venv/bin/python solve.py`):
  - Finding 1: confirmed (`E13-7` entailment failure), witness `hyd1_enable_on=False, alt_emer_ctrl_on=False`.
  - Finding 2: confirmed (`E14-4`/`E14-5` vs `E28-WBS-ASMP-4`/`-5` non-equivalence), witness around `4.8828e-04` in per-flight gap.
  - Finding 3: confirmed (`ASMP 3.2.2-1` vs `SASP 1.1-6` strict/non-strict mismatch), boundary witness at equality.
  - Finding 4: confirmed (`E.3.11-3` fails from PSSA assumptions under composition), witness `p_loss_both_hyd_per_flight=1.0041e-09 > 1.0e-09`; arithmetic check `3.3e-5 * 3.3e-5 = 1.089e-9` holds.

- Important discrepancy with writeup:
  - Current solver run also reports extra failures in `SPEC_REQUIREMENTS -> PSSA_REQUIREMENTS` (`E14-3`, `E14-4`, `E14-5`) not discussed as headline findings. This is visible in current runtime output and indicates either scope drift or narrative drift.

## 3. Bugs found

- **Transcription bug (verbatim mismatch)**
  - File: `examples/arp4754b_appendix_e.py:349`
  - Issue: `S18-WBS-R-0046` has "when the commanded..." (extra "the").
  - Fix: replace with exact Table E19 wording.

- **ID-faithfulness bug (constructed IDs for unnumbered rows)**
  - Files: `examples/arp4754b_appendix_e.py:579`, `examples/arp4754b_appendix_e.py:583`, `examples/arp4754b_appendix_e.py:289`, `examples/arp4754b_appendix_e.py:954`
  - Issue: IDs are not always verbatim from source numbering scheme.
  - Fix: keep a separate stable internal key field (e.g., `key`) and reserve `id` for source-verbatim identifiers only.

- **Unsat-core implementation does not match claimed behavior**
  - File: `solve.py:123`-`solve.py:133`; claim in `CHANGELOG.md:48`
  - Issue: code returns `s.unsat_core()` over tracked requirements only; this is not guaranteed minimal and excludes axiom-origin conflicts.
  - Fix: either (a) correct the changelog wording, or (b) implement core minimization plus optional tracked axioms.

- **Potentially misleading consistency report when axioms conflict**
  - File: `solve.py:125`-`solve.py:133`
  - Issue: axioms are untracked, so inconsistency caused by axioms can return `unsat` with empty core.
  - Fix: track axioms too (e.g., `ax_*`) and separate requirement-core vs axiom-core in reporting.

- **Production-safety bug: duplicate-ID check uses `assert`**
  - File: `solve.py:251`
  - Issue: `assert` can be disabled with `python -O`.
  - Fix: replace with explicit runtime check and raised exception.

- **Report generation hides PDF compile failures**
  - File: `report.py:235`-`report.py:252`
  - Issue: `pdflatex` stderr/stdout is swallowed and cleaned up, making debugging hard.
  - Fix: on non-zero return code, print/store logs and skip cleanup of `.log` for diagnostics.

## 4. Improvements (ranked by impact)

1. Add a **source-coverage validator** that checks each encoded table row against extracted PDF table rows (ID + verbatim text hash + diff report).
2. Enforce **schema-level faithfulness**: split `source_id` (verbatim), `internal_id` (stable key), and optional `source_loc` (page/table/row).
3. Add CI tests for solver invariants:
   - entailment correctness on toy models,
   - equivalence two-direction checks,
   - witness formatting edge cases (`None`, rationals, scientific notation),
   - unsat-core behavior with conflicting axioms.
4. Explicitly model probability domain constraints (`0 <= p <= 1`, `0 <= lambda`) to avoid non-physical witnesses.
5. Separate collections by role (`REQUIREMENTS`, `ASSUMPTIONS`, `OBJECTIVES`) and gate entailment pairs by role to avoid narrative/runtime drift.
6. Strengthen prompt (`prompts/encode.md`) with hard requirements:
   - "Do not invent IDs for unnumbered rows; use generated `internal_id` only."
   - "Emit page/table citation per Req."
   - "Emit machine-checkable CSV appendix for all source rows encoded/skipped."
7. Tighten writeup consistency checks so published findings always match current run artifacts (auto-generated findings section from solver JSON output).

## 5. Open questions

- Should unnumbered assumption rows (e.g., Table E23) be represented as `Req` at all, or as a separate `Assumption` type?
- Is the intended contract that `id` must be source-verbatim, or are normalized IDs acceptable if mapped?
- For "independence" rows, do you want propositional independence (`Not(And(...))` style) or probabilistic/statistical independence only?
- Are the extra current entailment failures (`E14-3/4/5`) expected and intentionally out-of-scope, or should the narrative be updated to include/explain them?
- Do you want strict reproducibility artifacts checked into git (solver JSON + generated report) for each tagged release?
