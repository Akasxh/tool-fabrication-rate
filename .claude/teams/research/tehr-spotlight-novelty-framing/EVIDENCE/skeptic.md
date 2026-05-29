# skeptic.md — red-team of the leading positioning

Sources stress-tested: Min et al. arXiv:2202.12837 (format-not-content lineage); Ren et al. arXiv:2402.13055 (induction-head maturation prediction); Spracklen USENIX Security'25 (security wrapper).

Target: the recommendation forming from moderator — LEAD with the grounding-gap theory (H3) unifying the four findings, hardened format-not-content recovery (H2) as the crisp mechanism-of-the-fix, security/slopsquatting as motivation. Attacking the reasoning, not the corpus.

## Attack 1 — The grounding-gap "theory" is a post-hoc narrative, not a theory (it predicts nothing new).
A theory earns spotlight by PREDICTING something not used to build it. "Prior matures before control" was reverse-engineered from the curve it claims to explain. An AC will ask: what NOVEL prediction does it make that you then confirmed?
- **Rebuttal that survives**: the theory DOES make a falsifiable, not-yet-used prediction: **the distractor-type shift order** (orthographic→random→semantic) is predicted by the induction-head maturation literature (K4) INDEPENDENTLY of the TEHR curve. If you show the distractor order tracks an independent induction-head-maturity measurement, that is a confirmed prediction. Also: the theory predicts RVR's gain should be LARGEST where the grounding gap is widest (mid-scale peak) and ~zero at both ends — a quantitative, falsifiable cross-tier prediction the existing data can test.
- **Verdict**: theory is salvageable ONLY if at least one of these predictions is explicitly pre-stated and tested. Otherwise demote "theory" to "interpretation." This is the single biggest spotlight risk.

## Attack 2 — Format-not-content may be an artifact of an easy benchmark.
If the held-out tool is recoverable from the conversation context alone, then OF COURSE the registry content is decorative — the model already knows the answer from context, so any structural nudge suffices. The C0.7 result might say more about BFCL/τ-bench task easiness than about a deep recovery mechanism.
- **Rebuttal needed**: report, on the C0.7-recovered subset, how often the correct tool name appeared earlier in the context. If it usually did, the claim weakens to "structural re-entry suffices when the answer is recoverable from context" — still interesting but narrower. The content-matched decoy control (moderator's hardening) directly addresses this: if a WRONG tool list in the envelope still recovers, content is genuinely inert.
- **Verdict**: claim must be scoped to what the data supports; the decoy control is non-optional.

## Attack 3 — The security wrapper writes a check the paper can't cash.
"Slopsquatting for agents" is evocative but the paper has NO exploit, NO collision measurement, NO demonstration that a hallucinated tool name resolves against a real ambient function. CzC borrows USENIX's gravitas without doing USENIX's work. A security-minded AC will see through a motivation-only security framing.
- **Rebuttal**: either (a) keep security as MOTIVATION only (1 paragraph, honestly scoped: "this is the agentic analogue of package hallucination [USENIX'25]; we measure the rate, we do not demonstrate exploitation"), or (b) add a small collision/exploitability probe (how often does a fabricated name match a plausible superset-registry entry). Option (a) is honest and cheap; (b) is stronger but more work. Do NOT lead the TITLE with security unless (b) is done.

## Attack 4 — "Frontier-zero" may not survive the next model or a harder benchmark.
0/2599 on Claude 4.x is on TWO benchmarks (BFCL+τ-bench) with a particular registry-presentation format. It is a claim about THESE benchmarks, not about Claude in general. A harder adversarial registry (many near-name distractors) might break it.
- **Rebuttal**: scope the claim ("zero on BFCL-v4 + τ-bench under standard registry presentation"), report the Clopper-Pearson upper bound (~0.14%), and ideally include a small adversarial-registry stress probe to show the frontier-zero is robust (or to honestly report where it breaks — which would itself be a finding).

## Attack 5 — Is any of this actually SPOTLIGHT, or just a solid main-track paper?
Spotlight needs a "huh, I didn't expect that" that generalizes. Ranking the candidates by surprise-that-generalizes:
1. **Format-not-content recovery inversion** (hardened) — most likely to generalize ("your error-recovery scaffolds are solving the wrong variable") and is directly actionable for anyone building agents. HIGHEST spotlight potential.
2. **Grounding-gap theory with a confirmed prediction** — high ceiling, high risk (Attack 1).
3. **Frontier-zero capability map + security framing** — striking but more "useful benchmark result" than "conceptual leap."
- **Verdict**: the format-not-content inversion is the safest spotlight bet because its hardening (decoy control + 2 envelope shapes) is cheap and the claim is crisp and counterintuitive. The grounding-gap theory is the higher-ceiling bet but requires the predictive test to not be hand-waving.

## Surviving recommendation after skepticism
LEAD: format-not-content recovery inversion (H2 hardened) as the conceptual contribution — crisp, counterintuitive, cheap to harden, anchored to Min'22. FRAME the four findings under the grounding-gap interpretation, and elevate it to "theory" ONLY if the RVR-gain-tracks-the-gap prediction (which existing data can test) is pre-stated and confirmed. USE security as honest motivation. The non-monotonic curve is supporting evidence with mandatory quantization + thinking controls, NOT the headline.

## Confidence
HIGH that Attacks 1-3 are the exact attacks a real ICML AC will mount; each has a concrete, mostly-cheap rebuttal. Handoff to evaluator/lead: the minimum experiment set is now well-defined (decoy/envelope-shape ablation; fp16 spot-check; RVR-gain-vs-gap test; Clopper-Pearson CIs) and all fit the project's compute except full activation probing.
