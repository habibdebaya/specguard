# Changelog

## v0.2.1 (2026-05-12)

### Encoding

- New module-level list `COMPOSITION_RELATIONS`, parallel to `UNIT_RELATIONS`, carrying the algebraic relations that govern how per-component failure probabilities compose into joint failure probabilities under the standard's own independence axioms. Two relations declared for the worked example: the product composition of the per-system hydraulic failure probabilities under the independence asserted in `E14-7`, and the catastrophic threshold cited in section E.3.11 paragraph 3 of ARP4754B Appendix E.
- New collection `AIRPLANE_CATASTROPHIC_OBJECTIVES` at the airplane layer, holding the safety objective for loss of deceleration capability cited in section E.3.11 paragraph 3.
- One new entailment pair declared, `(PSSA_REQUIREMENTS, AIRPLANE_CATASTROPHIC_OBJECTIVES)`. The same entailment machinery, now run under the extended axiom block, asks whether the per-component bounds entail the airplane-level catastrophic objective.

### New finding

- Finding 4, a compositional gap between the per-system hydraulic bounds in Table E14 of ARP4754B Appendix E and the catastrophic threshold cited in section E.3.11 paragraph 3. Each hydraulic system is bounded at 3.3E-05 per flight, and E14-7 asserts their independence. Under the composition axiom, the joint probability of simultaneous failure reaches 1.089E-09, which exceeds the 1.0E-09 threshold the standard itself cites for the "loss of deceleration capability" safety objective. Surfaced on the pair `(PSSA_REQUIREMENTS, AIRPLANE_CATASTROPHIC_OBJECTIVES)`, with witness state `p_loss_both_hyd_per_flight = 1.0041E-09` sitting in the gap. The architectural mitigation in the standard is the emergency accumulator (`PASA-SR-12`, `S18-ACFT-R-1551`), which breaks the failure chain regardless of the joint probability. The numerical bounds alone do not entail the budget.

### Solver

- `get_axioms` in `solve.py` now concatenates `COMPOSITION_RELATIONS` into the axiom set alongside `UNIT_RELATIONS`. The check functions themselves are unchanged. The compositional check is the existing entailment machinery run under a richer axiom block.

### Writeup

- Intro slide updated to reflect four real defects.
- New Finding 4 slide between Finding 3 and Implications.
- Implications slide extended to position Finding 4 as a compositional drift, structurally distinct from the restatement drifts of Findings 1 through 3.
- Approach section's Axioms subsection extended to describe the two-kind structure of the axiom block, unit relations and composition relations.

## v0.2 (2026-05-10)

### Encoding

- Page-by-page audit of the encoded requirements file against ARP4754B Appendix E. One transcription error corrected on `S18-ACFT-R-1100`, two derived requirements added (`S18-WBS-R-2976`, `S18-BSCU-R-0020`).
- Encoding scope expanded from two collections to ten, covering the airplane, Wheel Brake System, and Brake System Control Unit layers, together with three assumption catalogues drawn from Tables E2, E9, E10, and E23. Around 175 numbered requirements in total.
- New analysis-side collection at the airplane layer, `PASA_SAFETY_REQUIREMENTS`, drawn from Tables E5 and E6.
- New axiom block `UNIT_RELATIONS` carrying the per-flight to per-hour conversion derived from the five-hour average flight stated in section E.3.3.
- New entailment pair declared at the airplane layer, mirroring the existing pattern at the WBS and BSCU layers.
- Ten equivalence pairs declared, three of them spanning the AFHA and SFHA assumption catalogues.

### New findings

The bidirectional equivalence check is itself new in v0.2. Two findings emerge from it.

- Finding 2, a unit mismatch between Tables E14 and E28 of ARP4754B Appendix E. Two safety assumptions are restated as per-hour failure rates rather than per-flight probabilities, with no accompanying numeric adjustment. Under the five-hour flight axiom the per-hour formulations are five times weaker than the per-flight formulations. Surfaced on the pairs `(E14-4, E28-WBS-ASMP-4)` and `(E14-5, E28-WBS-ASMP-5)`, with witness state `p_loss_elec_bus_per_flight = 4.8828e-04` sitting in the gap between the two bounds.
- Finding 3, a strict-versus-non-strict drift between the AFHA and SFHA versions of the high-speed-overrun definition. Surfaced on the pair `(ASMP 3.2.2-1, SASP 1.1-6)`, with a witness state at the boundary where the two definitions disagree.

### Solver

- Solver is now fully data-driven. Collections are auto-discovered from the requirements module, and `ENTAILMENT_PAIRS` and `EQUIVALENCE_MAP` are read as data rather than hardcoded against named collections.
- New check family, bidirectional equivalence under the axiom block. Each declared pair is checked in both directions, with the failing direction's witness reported when the pair is not equivalent.
- Internal-consistency check now reports the minimal unsat core rather than a flat unsat result.

### LLM encoding pipeline

- `encode.py` script that takes a PDF of an aerospace standard and a section descriptor and produces a Z3-feedable Python file via Claude Opus 4.7.
- Three-pass prompt at `prompts/encode.md`. The first pass plans the symbol table, the second encodes each requirement against its verbatim English, the third cross-references the encoded constraints for restatement pairs.

### Report

- `report.py` renders the run output as a LaTeX document. Z3 expressions appear in proper logical notation rather than as Python source.
- Automatic compilation of the LaTeX to PDF via `pdflatex` in the same step.
- Conditional auto-copy of the appendix-E PDF report into `docs/reports/` so the website serves the latest version.

### Writeup

- Intro slide reframed to lead with the tool, with ARP4754B Appendix E introduced as the test bench. The PDF iframe of the generated report and an encoding excerpt sit on the right of the slide on desktop.
- Motivation slide gains an embedded slideshow showing the table of contents of ARP4754B across three pages.
- Approach slide expanded into a paper-style code walkthrough, with a new opening section, Encoding by LLM, that justifies the LLM-based encoding step on the basis of role separation between the LLM, the human reviewer, and the Z3 solver.
- Each finding slide gains two table screenshots from the standard, showing the offending rows in their original context.
- New Implications slide between Finding 3 and Closing.
- Theme switched from a blue gradient with sans-serif body to a flat off-white with a serif body and restrained borders.

### Project layout

- Encoded examples moved from `reqs.py` at the repository root into `examples/arp4754b_appendix_e.py`.
- New top-level directories: `pdfs/` for source standards, `reports/` for generated `.tex` and `.pdf` output, `prompts/` for the encoding prompt.
- Website assets organised into `docs/icons/`, `docs/figures/`, and `docs/reports/`, with `index.html` and `style.css` at the `docs/` root.
- README trimmed to a short description, a pointer to the writeup, and the run section. `CHANGELOG.md` introduced.

## v0.1 (2026-05-05)

- Two requirement collections in a single file `reqs.py` at the repository root. `PSSA_REQUIREMENTS` from Tables E12 to E14, `SPEC_REQUIREMENTS` from Table E19. Around thirty numbered requirements.
- Z3 solver in `solve.py` running three checks. PSSA internal consistency, SPEC internal consistency, and directional entailment of each PSSA requirement by the SPEC. Check pairs hardcoded by collection name.
- The entailment check surfaces a single defect, the asymmetric encoding of the HYD 1 Enable to Alt/Emer Ctrl paired conditional, where Table E13 specifies both directions but Table E19 propagates only the forward one.
- Static website at `docs/` with a brief writeup of the tool and the single finding.
