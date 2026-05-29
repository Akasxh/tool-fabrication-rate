# librarian.md — tool-use / function-calling reliability frontier (2024-2026)

Sub-Q2. BUILDS ON Phase-0 `PHASE0/prior_art.md` (2026-04-27) — that file is REUSE (covers API-Bank, RelyToolBench/Cao, BFCL v4 hallucination metric, Gorilla, τ-bench, LLM-agent-hallucination survey 2509.18970). This file ADDS 2025-2026 freshness and pins citations precisely.

## Named baselines / current frontier (verified citations)

### 1. BFCL — "From Tool Use to Agentic" — VERIFIED (NEW vs Phase-0)
- Patil, Mao, Ji, Yan, Suresh, Stoica, Gonzalez. **ICML 2025** (proceedings.mlr.press/v267/patil25a.html; OpenReview 2GmDdhBdDk).
- V4 scoring: Overall = Agentic 40% + Multi-Turn 30% + Live 10% + Non-Live 10% + **Hallucination 10%**. Hallucination here = "model makes incorrect assumptions/guesses rather than calling necessary intermediate functions" + Relevance/Irrelevance F1. **CONFIRMS Phase-0 claim**: BFCL's "Hallucination" = relevance/over-triggering, NOT registry-membership. TEHR is orthogonal — favorable white space.

### 2. RelyToolBench / Relign — Cao et al. — VERIFIED
- "Reducing Tool Hallucination via Reliability Alignment," arXiv 2412.04141, **ICML 2025 poster** (icml.cc/virtual/2025/poster/45001). Two categories: Tool Selection Hallucination (incl. non-existent/irrelevant tools — bundled) + Tool Usage Hallucination. Metrics: Reliable Pass Rate, Benefit-cost Utility. Relign expands the action space with indecisive actions (defer / clarify). **Training/alignment-time**, aggregate metric — contrast to TEHR's per-call disaggregation + inference-time fix. Matches Phase-0.

### 3. ToolACE — VERIFIED
- Tool-use data-synthesis framework; fine-tuned models hit 91.41% on BFCL, with a dual-layer validator (rule + LLM discriminators) targeting hallucination/intent/output-consistency. Data/training-time approach. Cite as "training-data-side mitigation" contrast.

### 4. Instruction-Following Eval in Function Calling — VERIFIED (NEW)
- arXiv 2509.18420 (2025). Function-calling instruction-following eval. Cite as adjacent eval frontier.

### 5. On the Robustness of Agentic Function Calling — VERIFIED (NEW)
- arXiv 2504.00914 (April 2025). Robustness of agentic function calling. Adjacent robustness frontier.

### 6. Quotient AI literature review (industry survey) — REPORTED-NOT-VERIFIED (blog)
- blog.quotientai.co tool-calling-capabilities lit review. Useful for landscape orientation; do NOT cite as primary.

## White space TEHR can own (synthesized from above + Phase-0)
1. **Registry-membership at a per-call denominator** — API-Bank (per-task category), RelyToolBench (bundled into Tool Selection Hallucination), BFCL (relevance, not membership). NONE isolate the per-call registry-membership rate. (Phase-0 verdict, confirmed.)
2. **Inference-time, training-free recovery for membership violations** — Cao/ToolACE/Fission-GRPO are all training/data-time. RVR is message-level, black-box-deployable. White space.
3. **The C0.7 ablation regime** — no tool-use-reliability paper found that isolates "envelope FORM vs registry CONTENT" as the active ingredient of recovery. This is the cleanest unclaimed slice.
4. **Cross-tier scaling characterization of the membership-violation rate** — existing benchmarks report leaderboard aggregates, not a per-call rate AS A FUNCTION of intra-family scale. TEHR's curve is the unclaimed measurement object.

## Caveat to lead — combinatorial-not-atomic novelty
The frontier is dense and training-time-heavy. TEHR's defensible territory is the intersection {per-call membership rate} × {inference-time recovery} × {scaling characterization} × {format-not-content mechanism of the fix}. No single competitor occupies that cell — but each axis individually is occupied, so the paper's novelty is COMBINATORIAL/CONCEPTUAL, which is exactly why "limited methodological novelty" landed. The fix is to lead with the conceptual claim (format-not-content recovery + grounding-gap theory), not the metric.

## Confidence
HIGH on all named-baseline citations (BFCL, RelyToolBench, ToolACE, API-Bank via Phase-0 reuse, all peer-reviewed). HIGH that BFCL's hallucination metric measures relevance not registry-membership (verified V4 scoring + definition). Handoff: the white-space cell is combinatorial — synthesist should frame novelty as the intersection {per-call membership rate × inference-time recovery × scaling characterization × format-not-content mechanism}, because each individual axis is occupied and the atomic-metric framing is what drew "limited novelty."
