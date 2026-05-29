# moderator.md — debate on the load-bearing contradiction

## Debate C1: "Does a gap-led synthesis (H4) make the paper MAIN-TRACK DEFENSIBLE today, or is the ~20% a SCOPE verdict (H5) that only breadth-data fixes?"

Verdict types available: A_WINS, B_WINS, COMPLEMENTARITY, REFRAME, DEFER.
- **Position A (H4)**: the right framing materially raises main-track odds; the paper IS a conceptual contribution once the gap leads.
- **Position B (H5)**: framing is cosmetic against a structural scope deficit; two families + one benchmark + ~14-19 events = workshop regardless of framing.

### Round 1 — opening
- **A**: The current title/abstract bury the strongest result (the gap) under a workshop-survey "Who/How often/What fixes" triad. Reframing to lead with a per-call commercial-vs-open reliability gap, instrumented by a novel metric, closed by a deployable fix, and corroborated by independent contemporaneous work (HalluWorld 2605.19341, Spracklen USENIX'25) is NOT cosmetic — it changes the claimed contribution from "a metric+fix" (which drew "limited novelty") to "a capability-frontier finding with an instrument and a fix." That is a different paper to an AC.
- **B**: Personas 13/14/15 — written by the authors themselves to model a hostile main-track AC — ALL default-reject a two-family, one-benchmark result. Persona 14 verbatim: "two families and one benchmark reads as workshop scope... interesting but narrow is a reject." The team's own 6-persona panel scored even the best honest version at borderline, and PROGRESS.md concedes "main-track is a multi-day program." No sentence-level reframing answers "where is the second benchmark."

### Round 2 — rebuttal
- **A concedes**: B is right that framing alone does not clear the tool-eval-specialist's structural bar. The gap-led framing cannot manufacture a second benchmark.
- **B concedes**: A is right that framing is not cosmetic — the SAME data under H2 scored 14% and under bounded-honest scored 18%, a 4-point swing from framing alone (PROGRESS.md). So framing demonstrably moves the score by single-digit points; it is necessary. And B cannot claim the gap is unimportant — HalluWorld (arXiv:2605.19341) independently corroborates the open-vs-frontier shape 10 days before this session, and Spracklen et al. (arXiv:2406.10279, USENIX Security'25) anchors the open-vs-closed hallucination gap as a heavyweight precedent. The gap is real and externally witnessed; B's objection is to its single-benchmark GENERALITY, not its importance.
- **Both converge**: the disagreement was mis-posed as either/or. Framing sets the CEILING the data can reach; data sets WHERE in that ceiling-band the paper lands. H4 raises the ceiling from "workshop" to "main-track-plausible"; the 2nd-benchmark gap reproduction is what actually moves the paper UP to that ceiling.

### Round 3 — synthesis
The question "framing OR breadth" is the wrong question. The right question: **what is the maximal-defensibility FRAMING (so no reviewer-impact is left on the table), and what is the single DATA result that, under that framing, moves the paper from workshop+ to main-track-plausible?**

## VERDICT: REFRAME (→ COMPLEMENTARITY)
- **Framing**: adopt **H4** (gap-led synthesis). This is necessary and demonstrably worth single-digit score points; it is the defensible-today maximum and is robust to the pending decoy under-firing (empiricist robustness check).
- **Ceiling**: **H5 is the correct honest CEILING DIAGNOSIS** — framing is necessary but NOT sufficient; the binding constraint is breadth. The deliverable must state both, not pick one.
- **Highest-leverage data**: the **2nd benchmark with a non-zero base that reproduces the gap** (empiricist rank 1), because it simultaneously (a) discharges the tool-eval-specialist's structural reject, (b) tests external validity of the headline gap AND the fix, (c) is the team's own named ceiling-setter. The 2nd open family is rank 2 (cheaper, very likely to reproduce a non-zero rate per Spectral-Guardrails 2602.08082, discharges the Wei multi-family bar). The powered decoy is NOT a ceiling-setter (it rescues a supporting claim that already scored 14% as a lead).

## Secondary debate C2: "Lead the security/slopsquatting angle, or keep it as motivation?"
- Prior session's skeptic Attack 3 (REUSED): the paper has no exploit/collision measurement; leading security writes a check it can't cash. Empiricist: a collision probe is high-effort, scope-creep. **VERDICT: B_WINS (keep security as honest MOTIVATION, 1 paragraph, "we measure the rate, not exploitation")** — unless a collision probe is added, which is a stretch goal, not the main-track lever.

## Confidence
HIGH. The REFRAME dissolves a false dichotomy that the team itself has been oscillating on (PROGRESS.md shows the framing pivots). The actionable output — H4 framing + 2nd-benchmark-gap as the single lift — is concrete and survives both positions.
