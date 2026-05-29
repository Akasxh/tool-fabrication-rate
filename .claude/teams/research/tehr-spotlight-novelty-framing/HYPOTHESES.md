# HYPOTHESES — competing conceptual framings (pre-investigation)

These are the framings the skeptic/moderator will later attack. Seeded before evidence.

## H1 — "U-shaped tool-reliability scaling" (the scaling-phenomenon framing)
The headline is the NON-MONOTONIC TEHR curve: an inverse-scaling hump that peaks mid-family (14B) then vanishes (32B). Position TEHR as a new, mechanistically-characterized instance of U-shaped scaling in a *novel domain* (tool registry grounding), with the distractor-type shift as the decomposition story (à la Wei et al.'s "U-shaped = distractor task + true task" account).
- **Strength**: rides a respected literature (Inverse Scaling Prize, Wei U-shaped). Phenomenon-first, surprising.
- **Risk**: single family = N=1. Reviewers may demand 2-3 families showing the hump. 4-bit quantization confound (is it scale or quantization artifact?). "0% at both ends" could be a measurement-floor artifact.

## H2 — "Format-not-content: the scaffolding/envelope-shape contribution" (the C0.7 framing)
The real conceptual contribution is the C0.7 ablation: a *structured error envelope with NO registry list* already recovers fully — so the active ingredient is the FORM of the corrective signal, not its informational content. This reframes RVR from "retry with a list" to a claim about how in-context corrective scaffolding works: agents need a structural re-entry cue, not new information. Connects to in-context format-effect / prompt-formatting literature.
- **Strength**: genuinely counterintuitive, defends against "just retry," is a *mechanism-of-the-fix* claim not a measurement.
- **Risk**: "format over content" is a known theme in prompt-sensitivity work — must differentiate. N of conditions is small; needs the ablation hardened (multiple envelope shapes, content-matched controls).

## H3 — "Grounding-gap / capability-control mismatch" (the conceptual-lens framing)
Frame tool-existence hallucination as a *grounding* failure: the model's generative prior over plausible tool names outruns its in-context grounding to the provided registry. The non-monotonicity is then predicted: as a model scales it acquires a richer tool-name prior (more plausible fabrications) before it acquires the meta-capability to gate generation on the registry. TEHR measures the grounding gap; RVR closes it by forcing re-grounding. This is a theory that PREDICTS the hump and the distractor shift.
- **Strength**: a theory with predictive content is what spotlights reward; unifies all four findings.
- **Risk**: speculative; needs a mechanistic probe (induction-head / retrieval) to not be hand-waving. Highest payoff, highest evidentiary burden.

## H4 — "Negative result for frontier safety + efficiency recommendation" (the practitioner framing)
De-emphasize novelty-of-mechanism; lean on the clean result that Claude 4.x has ZERO across 2599 calls while open small models don't, and that a free inference-time fix closes the gap. Position as a reliability/efficiency contribution (small+RVR ≈ frontier at fraction of cost). This is the current plan's framing.
- **Strength**: already built, defensible, real numbers.
- **Risk**: this IS what got "limited novelty / trivial intervention." It is the BACKUP, not the lead. Likely insufficient for spotlight alone.

## Prior lean (to be tested)
Most likely a COMBINATION wins: H2 (format-not-content) as the crisp conceptual hook + H3 (grounding-gap theory) as the framing that makes H1 (the curve) and the distractor shift cohere. H1 alone is too N=1-fragile for spotlight; H4 alone is the rejected status quo. The minimum-experiment question is which of H2/H3's evidentiary burdens is cheapest to discharge on M5+API.
