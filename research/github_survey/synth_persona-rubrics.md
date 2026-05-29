# Synthesis: New Reviewer Personas to Harden the TEHR/RVR Paper for MAIN-TRACK ICML

**Author role:** persona-rubrics synthesist
**Date:** 2026-05-29
**Inputs:** verified `repo_*.md` (AI-Scientist, AI-Scientist-v2, CycleReviewer, AgentLaboratory, ToolBeHonest, reflexion, storm) + `discover_automated_peer_revie.md` + `discover_self_correction___re.md`
**Existing personas audited:** `paper-review-toolkit/personas/01..12` (hostile statistician, adversarial reviewer, MARG experiments/clarity/impact, workshop strategist, industry practitioner, open-source champion, brutally-honest AC, reproducibility skeptic, contamination researcher, 3-line skim).

---

## TL;DR

The existing 12 personas are strong on **statistics, clarity, reproducibility, contamination, and venue fit**. For a MAIN-TRACK ICML jump (depth + theory, not workshop breadth+audit), they have **four structural gaps**, each of which maps to a concrete prior-art source and a real reject vector for our specific paper (per-call TEHR on BFCL multi-turn; Anthropic 4.x = 0 events; Qwen3-4bit non-monotonic peak 1.87% @ 14B; RVR intervention):

1. **No persona owns construct validity / metric definition** — i.e. "is TEHR even measuring the thing you name, and is your taxonomy complete?" This is the single biggest main-track risk given a 0-event headline and one error category.
2. **No persona owns intervention/causal validity** — "does RVR actually *cause* the improvement, or is it a confounded re-prompt? Where is the ungrounded-reflection control?"
3. **No persona owns the area-chair calibration/scoring discipline** — the existing AC persona (09) is a holistic final-gate, not a rubric-anchored multi-criterion scorer with explicit Soundness/Contribution numbers and reviewer-bias modeling.
4. **No persona owns cross-family / generalization breadth** — "you have two families; main-track needs the result to hold across the model zoo and benchmark suite, not just BFCL."

Below are **4 new personas, ranked by leverage**, each with rubric, output format, license-clean provenance, and the specific objection it pre-empts. All are re-implementations of *patterns* from permissively cited prior art — no licensed code is copied (AI-Scientist/CycleReviewer licenses forbid vendoring; see provenance notes).

---

## RANK 1 (highest leverage) — Persona 13: Construct-Validity & Failure-Taxonomy Auditor

**Why it is #1:** Our headline is a *0-event* result for Anthropic 4.x and a single error category (tool-not-in-registry). The most likely main-track reject is not statistical — it is **"your metric is too narrow / your null is trivially achievable / your taxonomy is incomplete."** No current persona presses on whether TEHR is a valid, non-degenerate, complete construct. ToolBeHonest (the closest prior art) defines a **six-way error taxonomy** (`non_existent_tools`, `solvability_hallu`, `wrong_tools`, `correct`, `wrong_unsolvable_index`, `wrong_reasoning`) across MNT/PT/LFT scenarios — a reviewer who knows that work will ask why we measure only one of those six.

**Provenance / citations:**
- **ToolBeHonest** (EMNLP 2024, arXiv:2406.20015; MIT) — `repo_ToolBeHonest.md`. Source of the six-way failure-mode rubric and the per-sample-vs-per-call distinction. MIT, so we *could* vendor the taxonomy, but re-implementing the rubric prompt is cleaner.
- **FacTool** (Apache-2.0) and **SelfCheckGPT** (MIT) from `discover_self_correction___re.md` — anticipate "did you compare against a consistency/detector baseline for the hallucination signal itself?"

**Rubric (what it checks):**
- Is TEHR operationally defined so the unit (per-call) cannot be gamed by trajectory length? Is the denominator (calls? executed calls? attempted calls?) stated and stable?
- Is the **0-event headline degenerate?** Could Anthropic 4.x score 0 simply because constrained decoding / API tool-schema enforcement makes an out-of-registry call structurally impossible? If so, TEHR measures the harness, not the model. (This is the killer objection — force a disclosure paragraph.)
- Taxonomy completeness vs ToolBeHonest's six categories: we measure `non_existent_tools` only. Where are wrong-tool, wrong-argument, solvability-hallucination calls in our trajectories? Are they folded into "correct" and inflating the 0?
- Is there a measured **floor/ceiling**: a positive control (a model or prompt that *does* hallucinate tools) so the metric is shown to be sensitive, not just zero everywhere it matters?
- Construct vs label noise: who adjudicates "tool not in registry" — exact string match, normalized name, or semantic? Mis-normalization could hide or invent events.

**Output format:**
```
CLAIM | CONSTRUCT-THREAT | IS-METRIC-DEGENERATE(Y/N) | FIX
```
End with: (a) Construct validity: VALID / NARROW-BUT-HONEST / DEGENERATE; (b) the single taxonomy category whose omission a reviewer will weaponize; (c) the one positive-control experiment that proves TEHR is sensitive (not trivially 0).
**Word limit:** 500.

---

## RANK 2 — Persona 14: Intervention / Causal-Ablation Reviewer (RVR skeptic)

**Why it is #2:** RVR is our method contribution; main-track reviewers reject methods whose gains are **confounded by the act of re-prompting rather than by the registry content**. The existing MARG-experiments persona (03) checks experimental design generically, but no persona owns the specific causal question: *is it the registry injection, or just a second attempt, that fixes the call?* The self-correction literature gives us the exact controls reviewers will demand.

**Provenance / citations:**
- **Reflexion** (NeurIPS 2023, arXiv:2303.11366; MIT) — `repo_reflexion.md`. The canonical ungrounded self-reflection method; the survey already recommends an in-harness "Reflexion-style" baseline (~0.5 day) that swaps registry feedback for a free-text reflection prompt. This persona makes that control *mandatory*.
- **CRITIC** (ICLR 2024, "tool-interactive critiquing"; MIT, microsoft/ProphetNet) and **Self-Refine** (Apache-2.0) from `discover_self_correction___re.md` — RVR = tool-interactive critiquing specialized to tool-existence; Self-Refine = intrinsic correction that *should not* fix tool-existence errors. These are the contrast arms.

**Rubric:**
- Ablation matrix: (a) no intervention, (b) bare retry / re-prompt with *no* registry, (c) Reflexion-style free-text self-reflection retry, (d) RVR (registry injection). Without arms (b) and (c), the gain is confounded.
- Is the improvement reported as a **paired** delta per call/trajectory, with the same seed and decoding, so it isn't a re-sampling artifact?
- Does RVR ever *introduce* new failures (fixes the tool-existence call but derails the downstream task)? Report pass-rate / task-success alongside TEHR — the "pass-rate failure" killing objection from persona 02.
- Cost/latency of the extra turn: is the RVR win worth the second call, and is that trade reported honestly (industry-practitioner concern, persona 07, but here quantified)?
- Does RVR fire only on events it defines (circularity, persona 02)? Show it on independently-labeled bad calls, not just self-detected ones.

**Output format:**
```
ARM | PRESENT(Y/N) | WHAT-IT-ISOLATES | GAP-IF-MISSING
```
End with: (a) Causal claim: SUPPORTED / CONFOUNDED / UNTESTED; (b) the single missing control arm most likely to flip a borderline vote; (c) one-sentence honest statement of what RVR's gain is *net of* a bare retry.
**Word limit:** 500.

---

## RANK 3 — Persona 15: Rubric-Anchored Area Chair (calibrated multi-criterion scorer)

**Why it is #3:** Our existing AC (09) is a holistic "one remaining issue" gate. Main-track ICML reviewers and ACs score against an **explicit multi-dimensional rubric** (Soundness / Presentation / Contribution 1-4, Overall 1-10, Confidence 1-5, Accept/Reject) and are subject to **leniency/harshness bias**. We have no persona that produces those calibrated numbers or that deliberately runs a positive-vs-negative reviewer prior to stress the score's stability. This is the most direct, battle-tested transfer from the automated-review repos.

**Provenance / citations (richest cluster):**
- **AI-Scientist / AI-Scientist-v2** (`repo_AI-Scientist.md`, `repo_AI-Scientist-v2.md`) — `perform_review.py` / `perform_llm_review.py`: the exact NeurIPS rubric (Soundness/Presentation/Contribution 1-4, Overall 1-10, Confidence 1-5, binary decision), `num_reviews_ensemble` averaging, `num_reflections` self-refine, `reviewer_system_prompt_pos`/`_neg` biased personas, and `get_meta_review` AC aggregation. **License: NOASSERTION (RAIL-derivative, non-OSI). DO NOT vendor — re-implement the rubric/scale/reflection pattern from scratch.** (Sec 3.3 propagates use-restrictions; Sec 3.2(e) would attach a machine-generated disclaimer to our manuscript.)
- **CycleReviewer / DeepReviewer** (ICLR 2025, arXiv:2411.00816; `repo_CycleReviewer.md`) — per-criterion ratings -> `avg_rating` -> binary `paper_decision`, multi-perspective + self-verification. **License: NOASSERTION (CycleResearcher License, non-commercial, registration-gated, China jurisdiction). Hardest no-vendor of the set — cite only, re-implement the rubric shape.**
- **microsoft/LLM-Rubric** (ACL 2024; MIT) from `discover_automated_peer_revie.md` — calibrated multi-dimensional rubric: produce a distribution per rubric question + a calibration network, rather than a raw scalar. The principled upgrade for *calibration*. MIT = safe to adapt directly.
- **AgentLaboratory** (MIT; `repo_AgentLaboratory.md`) — `ReviewersAgent` 3-persona ensemble (harsh-but-fair / impact / novelty) + `get_score()` NeurIPS 1-10 rubric; MIT, so directly copyable, but cleaner to re-implement.

**Rubric (this persona *emits scores*, not just prose):**
- Score the paper on Soundness (1-4), Presentation (1-4), Contribution (1-4), Overall (1-10), Confidence (1-5), Decision (Accept/Weak-Accept/Weak-Reject/Reject) — main-track scale.
- Run the score **twice** under a lenient prior and a harsh prior (pos/neg system prompt); report the spread. If Accept under lenient but Reject under harsh, the paper is borderline and the gap names the load-bearing weakness.
- Calibrate, don't just average: state per-criterion the *evidence in the paper* that pins the score, and flag any criterion scored on vibes (LLM-Rubric calibration idea).
- Meta-review aggregation: reconcile against the verdicts of personas 13/14/16 and the existing 01/02/10/11; identify the one criterion where personas disagree most.

**Output format:**
```
CRITERION | SCORE(lenient) | SCORE(harsh) | PINNING-EVIDENCE | RISK
```
End with: (a) Overall (1-10) + Decision under each prior; (b) the criterion with the widest lenient-harsh spread (the real battleground); (c) the single change that raises the *harsh* Overall by ≥1 point.
**Word limit:** 500.

---

## RANK 4 — Persona 16: Generalization / Cross-Family Breadth Reviewer (main-track depth gate)

**Why it is #4 (but mandatory for MAIN-TRACK):** A workshop accepts a two-family audit; a main-track ICML paper is expected to show the phenomenon **generalizes across the model zoo and benchmark suite**. The workshop-strategist persona (06) *advocates* for breadth-as-fit; this persona is the adversary who says "two families and one benchmark is a workshop result." It directly drives the breadth expansion the project already plans (more benchmarks/baselines/families via `harness/bench_loaders/*.py`).

**Provenance / citations:**
- The **recommendation table** itself: this persona forces us to actually exploit the `run-as-benchmark` verdicts — **tau-bench (MIT), ToolSandbox (NOASSERTION but runnable), StableToolBench (Apache-2.0), Seal-Tools (Apache-2.0), RestGPT (MIT), inspect_ai (MIT)** — rather than only BFCL. And to use `cite-only` items (**API-Bank, MetaTool, AppWorld, AgentBench**) as the prior-art breadth the related-work needs.
- **ToolBeHonest** (MIT) as a *second, differently-defined* hallucination number for cross-benchmark triangulation (cite as anchor: GPT-4o 37.0, Gemini-1.5-Pro 45.3 *do* fabricate tools — contrast our Anthropic 4.x = 0).
- **MARG-reviewer** (Apache-2.0) / **AgentReview** (Apache-2.0) from `discover_automated_peer_revie.md` — multi-agent, specialized-perspective review scaffolds; the *pattern* justification for having a dedicated generalization persona at all.

**Rubric:**
- Family coverage: Anthropic 4.x and Qwen3 only? Where are Llama/Mistral/GPT/Gemini/DeepSeek tool-callers? Is the non-monotonic Qwen curve a Qwen artifact or a general scaling phenomenon? (The 14B-peak claim is fragile if it is one family.)
- Benchmark coverage: BFCL multi-turn only, or also tau-bench / ToolSandbox / Seal-Tools? A second benchmark that reproduces the 0-vs-nonzero split is the strongest single main-track upgrade.
- Is the **non-monotonic peak (1.87% @ 14B)** robust to seed/benchmark, or could it vanish under a second eval? Demand a CI on the peak and a replication on at least one other benchmark.
- External validity: does TEHR=0 for Anthropic 4.x survive a *harder* registry (more distractor tools, near-miss tool names) — i.e. is the null robust or just easy?
- Are the `run-as-benchmark` repos that are already license-clear (tau-bench, ToolSandbox, Seal-Tools, StableToolBench, RestGPT) actually run, or only cited?

**Output format:**
```
AXIS (family/benchmark/scale) | CURRENT-COVERAGE | MAIN-TRACK-EXPECTATION | DOABLE-ADD (repo+license)
```
End with: (a) Breadth verdict: MAIN-TRACK / WORKSHOP-ONLY; (b) the single additional family OR benchmark that most converts this from workshop to main-track; (c) whether the Qwen 14B peak is safe to headline.
**Word limit:** 500.

---

## Coverage map (new personas vs existing 12)

| Gap | Covered before? | New persona |
|---|---|---|
| Metric construct validity / taxonomy completeness / degenerate-null | No (01 is stats only) | **13** |
| Intervention causal isolation (RVR vs bare retry vs reflection) | Partial (03 generic) | **14** |
| Calibrated multi-criterion scoring + reviewer-bias spread | No (09 is holistic gate) | **15** |
| Cross-family / cross-benchmark generalization (main-track depth) | No (06 advocates fit) | **16** |

## Sequencing for the paper-revision skill (parallel-then-merge, per project pattern)

- **Parallel block A (run together):** 13 (construct), 14 (causal), 16 (breadth) — independent attack surfaces, no shared state.
- **Sequential gate:** 15 (rubric-anchored AC) runs *after* A, consuming 13/14/16 outputs plus the existing 01/02/10/11, and emits the calibrated lenient/harsh scores + meta-reconciliation. This mirrors AI-Scientist's `get_meta_review` and CycleReviewer's avg-rating->decision aggregation, re-implemented clean.

## License hygiene (one place, explicit)

- **Re-implement, do NOT vendor:** AI-Scientist / AI-Scientist-v2 (NOASSERTION, RAIL-derivative, manuscript-disclaimer + downstream-propagation) and CycleReviewer (NOASSERTION, non-commercial, registration-gated). Rubric *shapes/scales* are not copyrightable; their source files are.
- **Safe to adapt directly (permissive):** ToolBeHonest (MIT), Reflexion (MIT), Self-Refine (Apache-2.0), CRITIC (MIT), FacTool (Apache-2.0), SelfCheckGPT (MIT), AgentLaboratory (MIT), STORM/Co-STORM (MIT), microsoft/LLM-Rubric (MIT), MARG-reviewer (Apache-2.0), AgentReview (Apache-2.0).
- **ReviewGrounder** (`discover_automated_peer_revie.md`) is the closest analogue to RVR's tool-grounded re-prompt but has **no LICENSE file** — design reference only, do not vendor.
