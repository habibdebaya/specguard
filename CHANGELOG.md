# Changelog

## v0.2 (2026-05-10)

### Encoding

- Page-by-page audit of the encoded requirements file against ARP4754B Appendix E. One transcription error corrected on `S18-ACFT-R-1100`, two derived requirements added (`S18-WBS-R-2976`, `S18-BSCU-R-0020`).
- Encoding scope expanded from two collections to ten, covering the airplane, Wheel Brake System, and Brake System Control Unit layers, together with three assumption catalogues drawn from Tables E2, E9, E10, and E23. Around 175 numbered requirements in total.
- New analysis-side collection at the airplane layer, `PASA_SAFETY_REQUIREMENTS`, drawn from Tables E5 and E6.
- New axiom block `UNIT_RELATIONS` carrying the per-flight to per-hour conversion derived from the five-hour average flight stated in section E.3.3.
- New entailment pair declared at the airplane layer, mirroring the existing pattern at the WBS and BSCU layers.
- Ten equivalence pairs declared, three of them spanning the AFHA and SFHA assumption catalogues.

### New finding

- Finding 3, a strict-versus-non-strict drift between the AFHA and SFHA versions of the high-speed-overrun definition. Surfaced by the bidirectional equivalence check on the pair `(ASMP 3.2.2-1, SASP 1.1-6)`, with a witness state at the boundary where the two definitions disagree.

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

## v0.1 (2026-05-05)

- Two requirement collections in a single file `reqs.py` at the repository root. `PSSA_REQUIREMENTS` from Tables E12 to E14, `SPEC_REQUIREMENTS` from Table E19. Around thirty numbered requirements.
- Z3 solver in `solve.py` running three checks. PSSA internal consistency, SPEC internal consistency, and directional entailment of each PSSA requirement by the SPEC. Check pairs hardcoded by collection name.
- The entailment check surfaces a single defect, the asymmetric encoding of the HYD 1 Enable to Alt/Emer Ctrl paired conditional, where Table E13 specifies both directions but Table E19 propagates only the forward one.
- Static website at `docs/` with a brief writeup of the tool and the single finding.
