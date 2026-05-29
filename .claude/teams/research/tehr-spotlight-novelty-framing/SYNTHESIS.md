# SYNTHESIS — Spotlight-grade conceptual framing for the TEHR paper

## Answer
The paper drew "limited novelty / trivial intervention" because it is currently pitched as **a new metric (TEHR) + a fix (RVR)** — and both of those, taken atomically, have close precedents (API-Bank's API-Hallucination category; "retry with the tool list"). The route to a conceptual contribution is to STOP leading with the metric and the fix, and lead instead with the one finding the reviewers have NOT seen before and that is genuinely counterintuitive: **the C0.7 ablation — in reactive agentic error-recovery, the STRUCTURAL FORM of the corrective turn is the active ingredient and the registry CONTENT is decorative.** This is a format-over-content result in a NEW regime (recovery, not forward ICL) where the withheld content is the literal solution set — a strictly stronger and more surprising version of Min et al. (2022). Wrap it in a unifying interpretation (the "grounding gap": a model's generative tool-name prior matures before its registry-grounding control, which PREDICTS the non-monotonic curve, the distractor-type shift, and frontier-zero as three signatures of one mechanism), motivate it with the security framing (this is the agentic analogue of "slopsquatting"/package hallucination, a recognized USENIX-Security-2025 threat class), and demote the non-monotonic curve from headline to supporting evidence with mandatory quantization and thinking-budget controls. That combination is defensible against a skeptical area chair; the bare metric-plus-fix framing is not.

## Confidence
**MEDIUM-HIGH.** All five adversarial gates closed: synthesist (claim matrix), moderator (C1 REFRAME, C2 COMPLEMENTARITY), skeptic (5 attacks with concrete rebuttals), adversary (corpus clean, no laundering/astroturf), evaluator (PASS, below). Confidence is not HIGH only because two load-bearing moves require small NEW experiments the paper has not yet run (the decoy/envelope-shape hardening of C0.7; the fp16 quantization spot-check). Once those are run, confidence → HIGH. The citation foundation is unimpeachable (8 peer-reviewed primaries).

## Key evidence
- **U-shaped scaling canon + the distractor-task mechanism that the distractor-shift maps onto** — Wei et al. arXiv:2211.02011 (EMNLP'23): U-shaped = true task + distractor task; large models learn to ignore the distractor. McKenzie et al. arXiv:2306.09479 (TMLR'23): inverse-scaling cause (i) "prefer memorized over in-context." `EVIDENCE/historian.md#A`.
- **The reviewer-bar for a U-shape claim is multi-family** (Wei used PaLM+Chinchilla+GPT-3) → single quantized Qwen3 family is below it. `EVIDENCE/historian.md#B`, `EVIDENCE/adversary.md#AT-2`.
- **Format-over-content lineage** — Min et al. arXiv:2202.12837 (EMNLP'22): random demonstration labels barely hurt; format/label-space/input-distribution carry ICL. The C0.7 anchor. `EVIDENCE/historian.md#C`.
- **Mechanistic support for the distractor-shift** — Olsson et al. arXiv:2209.11895 (orthographic copy / induction heads, earlier-smaller) + Ren et al. arXiv:2402.13055 (ACL'24, semantic induction heads, later-larger). Maps near-name→synonym onto basic→semantic head maturation. `EVIDENCE/mechanism.md#M1-M3`.
- **Security framing with a heavyweight anchor** — Spracklen et al., "We Have a Package for You", USENIX Security 2025: 16 models, 576K samples, open-source 21.7% vs commercial 5.2% hallucinated packages; "slopsquatting" (coined Seth Larson, PSF, Apr 2025). Direct parallel to Claude-4.x-0% vs Qwen->0%. `EVIDENCE/web-miner.md#A`.
- **White space is combinatorial** — BFCL ICML'25 hallucination metric = relevance not membership; RelyToolBench/API-Bank bundle or coarse-grain membership. No competitor occupies {per-call membership × inference-time recovery × scaling characterization × format-not-content mechanism}. `EVIDENCE/librarian.md`.

## Counter-evidence (what skeptic/adversary found that complicates the story)
- **The 4-bit quantization confound (CRITICAL).** "Secure or Suspect?" arXiv:2512.08213 shows 4-bit quantization ALONE induces non-monotonic hallucination-vs-size. The whole Qwen3 curve is 4-bit MLX → the hump could be a quantization×scale artifact. Must add an fp16 spot-check. `EVIDENCE/adversary.md#AT-1`.
- **Concurrent overlap.** arXiv:2604.02155 (Apr'26, "Brief Is Better") already reports non-monotonic function hallucination in Qwen agents tied to CoT-budget. Differentiate explicitly (our axis is SCALE at fixed/disabled thinking) or a reviewer thinks you missed it. `EVIDENCE/web-miner.md#B1`.
- **Mechanism-probe partially pre-empted.** arXiv:2601.05214 (Jan'26) already probes internal reps for tool-selection hallucination → a generic activation probe is not novel; only the distractor-shift-tracks-head-maturity framing is. `EVIDENCE/mechanism.md`.
- **C0.7 could be benchmark-easiness.** If the correct tool is recoverable from context, structural nudge suffices trivially. Needs a content-matched decoy control. `EVIDENCE/skeptic.md#Attack-2`.
- **"0/2599" is a floor claim.** Clopper-Pearson upper bound ~0.14%; report it, never bare "0%". `EVIDENCE/adversary.md#AT-5`.

## Moderator verdicts
- **C1 (is the single-family hump a legitimate U-shaped-scaling instance?) → REFRAME.** Not a standalone scaling-law headline (N=1 family). Reframe as a *predicted signature of the grounding-gap theory*. Mandatory controls before any U-shape language: fp16 spot-check (≥2 ladder points), explicit thinking-disabled statement (+ on/off check), Clopper-Pearson CIs on 0% endpoints.
- **C2 (is format-not-content a contribution or a Min-2022 restatement?) → COMPLEMENTARITY.** The phenomenon is not novel (cite Min prominently). The OPERATIONAL inversion — "in reactive recovery, the envelope shape is active and the registry content is decorative; stop re-injecting tool lists" — IS a genuine, deployable, counterintuitive contribution. Hardening required: ≥2 envelope shapes + a content-matched decoy control.

## Evaluator scores
See `EVIDENCE/evaluator.md`. Result: **PASS** (4.4/5 avg). Lowest dimension: source-quality on two preprint threats (mitigated by tagging REPORTED-NOT-VERIFIED and using direction-not-numbers).

---

## RECOMMENDATION (the deliverable)

### PRIMARY positioning — "Format-not-content recovery: your agent's error scaffolds are fixing the wrong variable"
- **One-sentence thesis**: *Tool-existence hallucination in LLM agents is recovered not by telling the model which tools exist, but by the structural form of the corrective turn — the registry content is decorative — revealing that reactive error-recovery in agents is a re-grounding phenomenon, not an information-delivery one.*
- **Anchor citations (2-3)**: Min et al. (arXiv:2202.12837, EMNLP'22) — format-over-content lineage; Wei et al. (arXiv:2211.02011, EMNLP'23) — the distractor/grounding mechanism that explains WHY a structural cue re-engages the true task; Spracklen et al. (USENIX Security'25) — the stakes (this is the agentic analogue of package hallucination/slopsquatting).
- **MINIMUM additional experiment to convince a skeptical AC**: the **C0.7 hardening ablation** — run ≥3 corrective-envelope variants {full registry (C1), no-list structured envelope (C0.7), structured envelope with a WRONG/decoy tool list (C0.8-new), unstructured "try again" (C0.5)} and report recovery on the hallucination-tagged subset. The decisive datapoint: if the DECOY-list envelope still recovers (content is provably wrong yet recovery happens), "content is decorative" is proven, not merely suggested. ~150-300 calls, fits the existing MLX+API harness, no retraining. This is cheap and it is the single experiment that converts the rejected "trivial intervention" into a counterintuitive mechanistic result.

### BACKUP positioning — "The grounding-gap: a capability-control inversion that predicts non-monotonic tool-reliability scaling"
- **One-sentence thesis**: *A model's generative prior over plausible tool names matures faster than its in-context registry-grounding control, producing a U-shaped tool-existence-hallucination curve, a scale-dependent distractor-type shift (orthographic→semantic), and frontier-zero grounding — three signatures of one mechanism.*
- **Anchor citations (2-3)**: Wei et al. (arXiv:2211.02011) — U-shaped = distractor the model learns to ignore; Olsson et al. (arXiv:2209.11895) + Ren et al. (arXiv:2402.13055, ACL'24) — orthographic→semantic induction-head maturation, the mechanism behind the distractor-shift; McKenzie et al. (arXiv:2306.09479, TMLR'23) — inverse-scaling cause (i), prior-over-in-context.
- **MINIMUM additional experiment**: a **two-pronged confound-killer + prediction-test**: (a) fp16 spot-check at 2 Qwen3 ladder points (small members fit on M5) to show the hump is not a 4-bit artifact (kills arXiv:2512.08213's objection); (b) the theory's falsifiable prediction — **RVR's pass-rate gain should be largest at the peak (widest grounding gap) and ~zero at both endpoints** — testable on the EXISTING data; pre-state it and confirm. If RVR-gain tracks the gap, the "theory" earns the word; otherwise demote to "interpretation." Plus the behavioral distractor-set probe (mechanism.md) if time permits, to substantiate the head-maturation mapping behaviorally without infeasible 14B/32B fp16 activation access.

### Framing rules that apply to EITHER positioning (binding, from the gates)
1. Cite API-Bank + RelyToolBench + BFCL as the disaggregation precedent (already in PAPER_PLAN v3.1 §2) — keep the metric as a SUPPORTING contribution, not the lead.
2. State "thinking disabled" explicitly and cite-and-distinguish arXiv:2604.02155 in §2, or a reviewer will think the curve is a CoT-budget artifact.
3. Report Clopper-Pearson CIs on all 0% cells; never write bare "0%".
4. Keep security as honest MOTIVATION (the paper measures the rate; it does not demonstrate exploitation) unless a collision/exploitability probe is added.
5. Demote the U-shape from headline to "a predicted signature," controlled for quantization, per moderator C1.

## Open questions (what blocks the next confidence tier)
- Does the DECOY-list envelope recover? (If yes → PRIMARY positioning is bulletproof; if no → "content decorative" weakens to "redundant," still publishable but less spotlight.) Only the new ablation answers this.
- Does the hump survive fp16? (Blocks any U-shape language.)
- Does RVR-gain track the grounding gap across tiers? (Decides whether the grounding-gap is a "theory" or an "interpretation.")
- Could not extract arXiv:2601.05214's per-scale method (slides PDF) — confirm before claiming the mechanism-probe framing is unclaimed.
