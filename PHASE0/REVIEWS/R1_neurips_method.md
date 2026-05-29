# R1 — NeurIPS Method Review

**Reviewer**: NeurIPS-style methods reviewer (cold, ablation-first)
**Target**: PAPER_PLAN_v3.1 + `paper/sections/03_method.tex`, `paper/sections/04_setup.tex`, `harness/HARNESS_SPEC.md`
**Date**: 2026-04-27

---

## Verdict

**Weak Reject (5/10) — borderline; conditional on adding ≥3 missing ablations and fixing the underpowered TOST.** The intervention is plausible and the per-call disaggregation argument (`prior_art.md` §1) is defensible. But the design has one ablation arm (C0.5), no comparator to framework-level error feedback, no registry-structure ablations, and a non-inferiority test mathematically incapable of supporting its claim at planned N. The §6 probe presents as causal but only manipulates one variable per cell, confounding lexical similarity with registry-size +1. Workshop-tier evidence dressed in NeurIPS-tier language.

---

## Top-5 Issues

1. **C0.5 is the only ablation, and it is the weakest possible one.** `03_method.tex` L42 and `intervention/naive_retry.py` (HARNESS_SPEC §2) define C0.5 as the literal string *"Your previous tool call failed. Please try again."* — no system-message restatement, no framework error wrapping, no schema echo. C1 vs. C0.5 conflates four factors: registry-list content, structured echo, tool-name salience, retry intent. Required: a C0.7 arm that wraps the framework error in agent-readable feedback (closer to LangChain default) and a C0.8 arm that re-states tools via system message without rejecting the call.

2. **Underpowered non-inferiority TOST.** `04_setup.tex` L22 / pre-reg item 3: TOST margin = 1pp on the C0-passing strict subset. With BFCL N=50 and τ-bench N=25, and pass rates ~50–70%, the strict subset yields ~25–35 paired observations. At α=0.05, 1pp non-inferiority needs hundreds of paired trials. The TOST is essentially guaranteed inconclusive. Either widen the margin to 5pp pre-registered, or replace with a paired CI on Δ and a "no decrease >Xpp" framing.

3. **Gap-closure ratio is a ratio of two noisy differences, no variance treatment.** `04_setup.tex` and PAPER_PLAN §4.3 designate `[PassRate(small+C1)−PassRate(small+C0)] / [PassRate(frontier+C0)−PassRate(small+C0)]` as the **headline**. Both numerator and denominator are small differences; the ratio is heavy-tailed and can flip sign for small denominators. There is no plan to bootstrap the *ratio* — `harness/stats/tehr.py` bootstraps per-call labels only. Headline must ship with paired bootstrap CI on the ratio plus pre-specified handling for denominators near zero.

4. **Multiple-comparisons correction scoped too narrowly.** Pre-reg item 8: Holm–Bonferroni "across per-tier tests." With 5 models × 2 benchmarks × 3 conditions × ≥4 metrics, the family is much larger than 4. FWER not actually controlled. Either widen Holm or pre-declare confirmatory vs. exploratory.

5. **§6 mechanism probe is correlational dressed as causal.** `03_method.tex` L47: near-name distractors are defined by Levenshtein distance; the probe injects ONE distractor per task. ΔTEHR conflates (a) lexical similarity, (b) registry-size +1, (c) the specific lemma chosen. The "random" arm is not length-, arity-, or position-matched. The "causal — not merely correlational" claim is overstated.

---

## Specific Concerns

- **No comparison to LangChain-style framework error feedback** (the realistic deployed baseline). C0 surfaces "the framework's default error string" — dataset-dependent and degenerate (BFCL: silent reject). Add C0.7 as above.
- **No registry-ordering ablation.** RVR renders `sorted(registry.keys())` (L25). Sorting is arbitrary. Pre-register: alphabetical vs. random vs. relevance-ranked.
- **No registry-length ablation.** BFCL classes have 2–22 tools (`dataset_status.md` §3.3); the claim should weaken at |R|≥50 where echo length competes with task tokens.
- **No retries=k ablation.** §3.2(ii) cites "production retry budgets" with no source. k∈{1,2,3} is a one-line change.
- **No description-verbosity ablation.** Feedback is names-only (L23). Names+description vs. full-schema isolates whether names are the active ingredient.
- **No system-vs-user position ablation.** `intervention/rvr.py` is silent on role placement; this changes the effect.
- **Per-cell N too small for per-tier claims.** N=50 × 2 × strict-subset filter → likely 10–25 paired hallucination events per (model, condition). McNemar mid-p with b+c<10 is unstable; pre-reg item 10's ≥30 threshold will likely fail and force "exploratory" framing — at which point the headline collapses.
- **No head-to-head against Fission-GRPO or any RL-trained baseline on the same BFCL split.** §3.3 claims orthogonality but reports no numbers. A footnote is not a comparison.
- **τ-bench user simulator routed to Haiku 4.5** (HARNESS_SPEC §8.9): confounds reward across conditions if simulator behaves differently on hallucinated trajectories. Pre-register: same simulator, same seed, all conditions, fixed temperature.
- **Refusal deny-list is 4 phrases** (HARNESS_SPEC §8.2). Misclassification rate is an unreported confound for TEHR's denominator. Need a held-out audit.

---

## Required Changes

1. **Add C0.7 (framework-style structured error)** between C0 and C0.5. Locks "is RVR better than what people deploy?"
2. **Add registry-ordering ablation** (≥3 levels) on one tier × one benchmark, even N=20.
3. **Add registry-length ablation**: bin BFCL tasks by |R|; report ΔPass per bin.
4. **Replace TOST 1pp** with margin 5pp pre-registered or paired bootstrap CI with "no clinically meaningful decrease" framing.
5. **Bootstrap CI on the gap-closure ratio** with denominator-near-zero policy.
6. **Restate FWER scope.** Widen Holm to the full family or label confirmatory vs. exploratory.
7. **Reframe §6 as correlational** unless §6 adds a length+arity+position-matched random-distractor control.

---

## Strongest Contribution

The disaggregation argument (`prior_art.md` §1; PAPER_PLAN §2.3 Δ1) — separating registry-membership violations from relevance/argument errors at a per-call denominator — is genuinely useful and well-supported against API-Bank and RelyToolBench. A real, if minor, methodological improvement.

## Most Damaging Weakness

A single ablation arm (C0.5) cannot support a four-claim contribution package. RVR may work; the design as written cannot tell us *why*, *how robustly*, or *against what realistic baseline*. Without C0.7 plus one registry-structure ablation, this is a press-release with confidence intervals.

## Verdict Justification

Phenomenon real, engineering competent, disaggregation defensible. But two of four headline claims (gap-closure, no-quality-regression) ride on metrics that are either underpowered (TOST) or have unaddressed variance (gap-closure ratio). I would champion this after the seven required changes; as currently planned, NeurIPS reject, SCALE weak-reject.

---

## Top-3 Missing Ablations

1. **C0.7 — framework-style error feedback** between C0 and C0.5. Without it, RVR is only proven better than a stripped-down toy baseline.
2. **Registry-length × ordering ablation** (small/medium/large × alphabetical/random/relevance-ranked). Without it, the headline is silently confined to ~10-tool registries.
3. **Length-, arity-, and position-matched random-distractor control in §6.** Without it, "near-name distractors cause TEHR" is correlational masquerading as causal.
