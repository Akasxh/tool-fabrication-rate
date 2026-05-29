# QUESTION — TEHR spotlight-novelty framing

## Raw prompt (verbatim)
> Research task: find the strongest CONCEPTUAL/NOVELTY framing to elevate a careful-but-descriptive empirical paper into main-track-spotlight territory. All three workshop reviewers (even the positive ones) flagged "limited methodological novelty" and "trivial intervention." I need a defensible, citation-backed positioning that adds a genuine conceptual contribution.
>
> Findings (real, reproduced from raw data):
> - Per-call metric TEHR: fraction of agent tool calls naming a tool NOT in the provided registry.
> - Claude 4.x (Opus 4.7, Sonnet 4/4.5/4.6, Haiku 4.5): 0 tool-existence hallucinations across ~2599 calls.
> - Qwen3 (0.6B→32B, 4-bit MLX) NON-MONOTONIC: 0% (0.6B) → 0.95% (1.7B) → 1.33% (4B) → 1.46% (8B) → 1.87% PEAK (14B) → 0% (32B).
> - Peak-distractor-type shift: dominant error distractor changes with scale — near-name (1.7B) → matched-random (4B/8B) → synonym (14B).
> - Intervention RVR (Registry-Visible Reprompting): on tool-not-found, re-prompt once with structured envelope listing available tools. Removes all fabrications. Ablation: structured error envelope WITHOUT registry list (C0.7) already hits zero — "envelope shape is the active ingredient, registry content is decorative."
>
> Cover: (1) inverse/U-shaped scaling lit; (2) 2024-2026 tool-use hallucination/reliability frontier + named baselines + white space; (3) mechanism angle (induction heads/copying/in-context retrieval × scale → distractor shift); (4) creative/contrarian angle from recent X/GitHub/blogs; (5) recommendation — strongest positioning + backup, each with one-sentence thesis, 2-3 anchor citations, MINIMUM additional experiment.

## Assumed interpretation (LABELED — proceeding without asking)
The paper (SCALE @ ICML 2026, project SCALE) currently positions TEHR as a measurement + training-free fix. Workshop reviewers accept the empirics but reject the *novelty*: the metric is near-equivalent to API-Bank's "API Hallucination" (already known in Phase-0 audit) and RVR is "just retry with a list." The user wants a CONCEPTUAL reframe — a genuine intellectual contribution — that survives a skeptical ICML area chair, not cosmetic relabeling. The C0.7 ablation ("envelope shape, not registry content, is the active ingredient") is a NEW finding not yet in the plan and is potentially the strongest conceptual hook. The deliverable is positioning + anchor citations + the minimum experiment to make each credible.

## Sub-questions
1. **Inverse/U-shaped scaling theory.** Exact citations (authors, year, venue, arxiv id) for: Inverse Scaling Prize (McKenzie et al.), "Inverse scaling can become U-shaped" (Wei et al.), BIG-Bench emergence/U-shaped, grokking-adjacent non-monotonicity. Can a single-family (Qwen3) TEHR hump be legitimately framed as a new U-shaped-scaling instance in the tool-use domain? What would a reviewer demand (multiple families? a mechanism? a task-decomposition account)?
2. **2024-2026 tool-use hallucination/reliability frontier.** Named baselines (BFCL/Gorilla, ToolBench, API-Bank, MetaTool, RestGPT, τ-bench, ToolACE, RelyToolBench, constrained decoding for tool calls, Fission-GRPO-likes). What's measured vs not. Where is the white space TEHR can own? (Build on existing Phase-0 audit; ADD 2025-2026 freshness.)
3. **Mechanism angle.** Literature linking induction heads / copying / in-context retrieval to scale that supports/refutes a mechanistic story for the distractor-shift (near-name=orthographic copy at small scale → synonym=semantic confusion at larger scale). Olsson et al. 2022 induction heads; ICL-vs-memorization scaling. Could a small mechanistic probe make this spotlight-worthy? What probe?
4. **Creative/contrarian angle.** Recent (2025-2026) X/Twitter, GitHub, blog discussion of: tool-existence/registry/function-name hallucination, non-monotonic capability scaling, quantization × hallucination. 3-5 genuinely novel differentiating framings, concrete.
5. **The C0.7 ablation as the conceptual core.** Is "structured error envelope shape, not its information content, drives recovery" a known result anywhere (format-vs-content, scaffolding, in-context format effects)? This may be the real contribution. Anchor or refute.
6. **14-day freshness sweep (BINDING).** What shipped/was published in the last ~14 days (mid-May 2026) on tool-use reliability, scaling phenomena, or agent self-correction that the April Phase-0 audit could not have seen?
7. **Recommendation.** Strongest positioning + backup. Each: one-sentence thesis, 2-3 anchor citations, MINIMUM additional experiment to convince a skeptical AC.

## Acceptance criteria
- Every load-bearing citation has author/year/venue/arxiv-id and is verifiability-tagged (VERIFIED / REPORTED-NOT-VERIFIED / UNVERIFIABLE).
- At least one positioning thesis that an area chair could not dismiss as "API-Bank renamed" or "just retry."
- The minimum-additional-experiment for the top recommendation is concrete and feasible on the project's compute (M5 32GB MLX + API credits).
- Inverse-scaling framing question answered with the explicit reviewer-bar (how many families / what mechanism).
- Creative angles are concrete and differentiated, not generic.

## Known constraints
- Deadline pressure: SCALE ICML 2026 (workshop already reviewed; user is reaching for a stronger venue/track or rebuttal). Camera-ready / resubmit economics matter.
- Compute: M5 32GB MLX (Qwen3 family already runnable), API credits (~$5K across vendors).
- The empirics are FIXED (reproduced from raw data) — we are reframing, not re-running the core study. New experiments must be small and targeted.
- Phase-0 prior-art audit (2026-04-27) already exists; REUSE it, ADD freshness.
