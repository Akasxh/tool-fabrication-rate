# Prior Art Audit: TEHR Novelty
*Source: Phase-0 lit sprint, 2026-04-27.*

## Verdict
**PARTIAL — phenomenon is well-documented; a near-equivalent metric exists in API-Bank (EMNLP 2023). Novelty claim must be reframed from "we name a new metric" to "we isolate registry-membership violations as a fine-grained metric, disaggregating prior holistic measures."**

## Evidence (key precedents only)

### 1. API-Bank (Li et al., EMNLP 2023) — **closest precedent**
- **arXiv 2304.08244** / aclanthology.org/2023.emnlp-main.187
- Defines **"API Hallucination"** as one of six error categories: *"the API name in the ground truth does not match the name in the prediction"* (61.4% error rate in some models).
- This is ~80% overlap with TEHR. The remaining 20% is the *denominator*: API-Bank reports it as an error category; TEHR reports it as a per-call rate over total tool calls.
- **Implication for our paper:** must cite as the direct precedent. Cannot claim TEHR is a "new" metric.

### 2. RelyToolBench / Reducing Tool Hallucination via Reliability Alignment (Cao et al., ICML 2025)
- **arXiv 2412.04141**
- Formalizes two categories: **Tool Selection Hallucination** (which includes "tool type errors: irrelevant or non-existent tools") and Tool Usage Hallucination (format/content).
- Aggregate metrics: Reliable Pass Rate, Benefit-cost Utility — penalize across both, not isolated per-failure-mode.
- **Implication:** the *non-existent-tool* category is named here but bundled with relevance errors.

### 3. BFCL V4 (Berkeley Function Calling Leaderboard)
- gorilla.cs.berkeley.edu/leaderboard.html
- Has a **"Hallucination" metric (10% of overall score)** — but it measures *relevance* (model invokes a tool when none should be), **not registry-membership**.
- **Implication:** orthogonal to TEHR; favorable for our positioning — BFCL doesn't measure what we measure.

### 4. Gorilla (Patil et al., NeurIPS 2023)
- arXiv 2305.15334
- Identifies "wrong API" / "Hallucinate!" as failure modes; doesn't formalize them as a per-call rate.
- **Implication:** foundational anchor; cite for problem framing, not metric.

### 5. τ-bench (Sierra, June 2024)
- arXiv 2406.12045
- Has `used_wrong_tool` and `used_wrong_tool_argument` fault categories — broader than TEHR.
- **Implication:** cite as a benchmark we evaluate on; not a metric precedent.

### 6. Czapla / Answer.AI blog (date correction)
- URL: `answer.ai/posts/2026-01-20-toolcalling.html`
- **Actual date: 2026-01-20 (January), not February as v3 plan currently states.** Update PAPER_PLAN_v3.md.
- Direct quote: *"When developers provide LLMs with a namespace containing many functions but restrict tool specifications to only a few, the model can still invoke unauthorized functions."*
- Concrete example: *"Claude attempted to call `read_secret()` despite only being granted access to `read_url()`."*

### 7. LLM Agents Hallucination Survey (arXiv 2509.18970)
- Taxonomy survey; identifies tool-use hallucination as a category, doesn't formalize a per-call rate.

## Reframed contribution #1 (replaces v3 §2.3 item 1)

> **Metric**: We operationalize the **Tool-Existence Hallucination Rate (TEHR)** as a fine-grained, per-call metric isolating registry-membership violations. Prior work measures this failure mode at coarser granularity: API-Bank (Li et al., 2023) treats name-mismatch as a categorical error type but does not report a per-call rate; RelyToolBench (Cao et al., 2025) bundles non-existent-tool errors with relevance violations under "Tool Selection Hallucination." TEHR's contribution is **disaggregation**: it gives a clean denominator for the registry-membership-specific failure mode, enabling targeted intervention design (RVR) and per-tier comparison across model capability scales.

## Differentiation paragraph for §2 Related Work (~120 words)

> Tool-call hallucinations have been measured under several aggregations. API-Bank \citep{li2023apibank} introduced "API Hallucination" as a ground-truth-vs-prediction name-mismatch category, reporting per-task error rates up to 61.4\%. RelyToolBench \citep{cao2025reliability} formalizes Tool Selection Hallucination — which includes non-existent-tool invocations alongside relevance and timing errors — and proposes aggregate reliability scores. BFCL v4's hallucination metric \citep{bfclv4} captures a different failure: invocations when no tool is appropriate. Our metric, the Tool-Existence Hallucination Rate (TEHR), isolates the registry-membership dimension at the per-tool-call denominator, separating it from relevance errors, argument errors, and timing errors. This isolation is what enables our intervention (Registry-Visible Reprompting, §3) to be evaluated against a clean ablation: C1 vs.\ a naive-retry baseline (C0.5) on the strict subset of hallucination-tagged tool calls.

## Action items propagating to PAPER_PLAN_v3
1. Update §2.3 contribution #1 wording (use the reframed claim above).
2. Update §2 Related Work to cite API-Bank, RelyToolBench, BFCL v4 hallucination metric explicitly.
3. Fix Czapla date: 2026-**01-20** (was incorrectly stated as Feb 2026).
4. Reviewer-attack defense (§8.2): "TEHR is API-Bank's API Hallucination renamed" → answered by per-call denominator + cross-tier evaluation + targeted intervention.
