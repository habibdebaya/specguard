# specguard website silhouette

Five vertical slides, snap-scroll, mobile-first. Single-finger flick moves to the next slide. No nav, no header, no CTAs. Restrained typography, monospace-leaning. The artifact is the pitch.

---

## Slide 1. The premise

Frames the contradiction at the heart of the problem. Sets up everything that follows.

**Content**

Civil aviation runs on standards. Hundreds of pages of natural-language requirements that every aircraft system must comply with to fly.

Those standards are written by humans, reviewed by humans, and never formally verified.

If they contain logical defects, every system built to comply with them inherits the defect.

**Closing line**

*specguard takes one of those standards, encodes its requirements as formal constraints, and runs generic logical checks. It finds defects without being told where to look.*

**Visual**

Text only.

---

## Slide 2. The standard

Establishes the document being analyzed and stakes the relevance.

**Content**

ARP4754B is the SAE standard governing how civil aircraft systems are developed and certified.

Published 2023. Boeing, Airbus, and COMAC all certify their aircraft against it.

172 pages long. Most of it is process guidance. Appendix E is the worked example, the development of a fictional Wheel Brake System for an aircraft designated S18.

**Visual**

Text only.

---

## Slide 3. The slice

Narrows to the specific structure specguard analyzes. Introduces the dual structure that the entailment check operates on. This is the slide that carries the table screenshots.

**Content**

The S18 is a fictional aircraft. The whole appendix is a worked example, the standard's own demonstration of how its processes should be applied. The cleanest instance of safety-driven development the document contains.

Within it, two artifacts sit at the heart of the Wheel Brake System specification.

- The **safety analysis** lists thirteen obligations the system must satisfy. Tables E12, E13, E14.
- The **specification** is the binding contract. Table E19.

The contract is supposed to enforce every obligation the analysis identified. specguard checks whether it does.

**Visual**

Two screenshots side by side on desktop, stacked on mobile. Table E13 on one side and Table E19 on the other. Sized so the visual structure is visible without the rows being readable. The point is "two tables, two roles," not legibility.

---

## Slide 4. The defect

The substantive slide. Walks the finding through three layers, from the standard's own words, to the abstract logic, to what fails physically.

**Content**

**In the standard's own words.**

The analysis (Table E13) specifies two paired obligations.

> E13-6 says "When HYD 1 Enable output is enabled, Alt/Emer Ctrl output shall be disabled."
>
> E13-7 says "When HYD 1 Enable output is disabled, Alt/Emer Ctrl output shall be enabled."

Together, exactly one control path is active at any moment. Braking is always available.

The contract has only one such requirement, R-6109 in Table E19.

> "When HYD 1 Enable output is enabled, Alt/Emer Ctrl output shall be disabled."

Half of the obligation is missing.

**In abstract terms.**

The analysis says,

- If A, then not B.
- If not A, then B.

The contract says only,

- If A, then not B.

The contract is silent on the case where A is false.

**What that means physically.**

A system built strictly to the contract can be in this state.

- HYD 1 Enable OFF
- Alt/Emer Ctrl OFF

Both paths off. No braking command anywhere in the system.

The real-world consequence is loss of all braking at touchdown or during a rejected takeoff. The aircraft cannot decelerate before the runway ends.

The safety analysis explicitly forbids this state. The contract permits it.

The standard's own validation process did not catch this. specguard's entailment check finds it in milliseconds, and the witness state, the specific combination of inputs that breaks the safety claim, is constructed by Z3 from the constraints alone, with no human guidance about where to look.

**Visual**

Text only. Possibly a small inline truth-table or two-row diagram for the A and B framing if it helps land the abstraction.

---

## Slide 5. Implications

The closing. Why this matters at scale, what it argues for. Founder framing without sales language.

**Content**

Civil aircraft certification takes years. Compliance with standards like ARP4754B costs millions per program.

Yet the standards themselves contain logical defects that pass through human review.

Symbolic verification catches them mechanically. The encoding is one-time work. The checks run in seconds.

Every certified aircraft program would benefit from running its governing standards through this kind of pipeline before signing the contract.

**Closing line**

*The defect above was found by a tool that knows nothing about wheel brakes. It only knows the algebra.*

**Visual**

Text only.

---

## Aesthetic and behavioural notes

- One-finger vertical scroll, CSS scroll-snap. Each slide fills the viewport.
- Mobile-first. Test at iPhone width before desktop.
- Typography. One serif or clean sans for body, monospace for the requirement quotes and the abstract A and B logic. High contrast. Dark on light or the inverse, pick whichever lands cleaner.
- No headers, footers, navigation, CTA buttons, sign-up forms, or marketing copy.
- Each slide fits comfortably with around five to eight lines of body text plus a heading and the closing line.
- The two table screenshots on slide 3 are the only images in the entire site.
- Accessible. Real semantic HTML, readable without JavaScript if possible, keyboard navigable.
