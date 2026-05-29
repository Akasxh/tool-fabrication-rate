# mechanism.md — induction heads / copying-vs-retrieval × scale (Sub-Q3)

Question: is there a mechanistic story for the distractor-shift (near-name = orthographic copy at small scale → synonym = semantic confusion at larger scale) that the literature supports, and would a small probe make this spotlight-worthy?

## Verified citations

### M1. Olsson et al. — Induction heads — VERIFIED (foundational)
- "In-context Learning and Induction Heads," Olsson, Elhage, et al. (Anthropic), arXiv 2209.11895 / transformer-circuits.pub 2022.
- Induction heads implement [A][B]...[A]→[B]: attend to the token that previously followed a matching prefix, **copy** it via the OV circuit. Form in a sharp **phase change** early in training, co-incident with an ICL jump. **This is the mechanism behind "near-name" / orthographic copying** — a prefix-match-and-copy operation. Small models have basic induction heads.

### M2. Ren et al. — Semantic induction heads — VERIFIED (the scale-shift anchor)
- "Identifying Semantic Induction Heads to Understand In-Context Learning," Ren, Guo, Yan, Liu, Zhang, Qiu, Lin. **ACL 2024 Findings** (2024.findings-acl.412), arXiv 2402.13055.
- Beyond orthographic copying: certain heads encode **semantic relations** (knowledge-graph head→tail, syntactic dependencies) — attending to a head token recalls and up-weights the *related* tail token. Their formation "correlates closely with the emergence of ICL ability."
- **This is the mechanism behind "synonym" distractors**: a richer, relation-following head substitutes a *semantically related* tool name. These are the kind of circuits that appear in larger/more-trained models.

### M3. Richer-mechanism-emerges-later literature — VERIFIED (supporting)
- "Beyond Induction Heads: In-Context Meta Learning Induces Multi-Phase Circuit Emergence," arXiv 2505.16694 (2025): multi-phase emergence — models first memorize, then evolve to infer the task; induction heads act as "inductive scaffold" for richer task-encoding (function-vector) heads that emerge later.
- "In-Context Learning Without Copying," arXiv 2511.05743 (2025): models keep abstract ICL even with weakened copying/induction heads — i.e. copying and semantic/abstract retrieval are separable mechanisms.
- "On the Emergence of Induction Heads for In-Context Learning," arXiv 2511.01033 (2025).
- "Temporal Dependencies in In-Context Learning: The Role of Induction Heads," arXiv 2604.01094 (April 2026, freshness-window).

## The mechanistic story (does the literature support it?)
**Partially, and plausibly — enough to motivate a probe, NOT enough to assert without one.**
The ordering {orthographic copy emerges first/smaller (M1) → semantic relation-following emerges later/larger (M2, M3)} is an established direction in the interpretability literature. Mapping it onto the distractor-TYPE shift (near-name at 1.7B → matched-random mid → synonym at 14B) is a *coherent and literature-consistent* hypothesis: as the family scales, the dominant failure migrates from low-level orthographic prefix-copy errors to higher-level semantic-substitution errors, tracking the maturation from basic to semantic induction circuits. The "matched-random" middle band (4B/8B) is consistent with a transitional regime where neither mechanism cleanly dominates.

## Would a small probe make this spotlight-worthy? (answer: YES, conditionally)
- **Prior art check**: "Internal Representations as Indicators of Hallucinations in Agent Tool Selection" (Healy et al., arXiv 2601.05214, Jan 2026) ALREADY probes internal representations for tool-selection hallucination. So a *generic* "can we detect tool hallucination from activations" probe is NO LONGER novel. (Could not extract their per-scale findings — PDF was slides; flag REPORTED-NOT-VERIFIED on their exact method, but the existence of the paper is VERIFIED and it constrains our novelty.)
- **The novel probe** is NOT "detect hallucination from activations." It is: **show that the distractor-type composition tracks an induction-head maturity signal across the Qwen3 ladder.** Concretely, on the open Qwen3 weights (available, not just MLX-quantized — interpretability needs fp16 + attention access), measure a basic-induction-head score (prefix-match-copy, à la Olsson) vs a semantic-induction-head score (relation-following, à la Ren) per model size, and correlate the basic→semantic crossover with the near-name→synonym distractor crossover. If the crossovers align, that is a genuine mechanistic explanation, not a correlation-fishing exercise.
- **Feasibility caveat**: this is the MOST expensive option. It needs fp16 Qwen3 weights with attention hooks (NOT the 4-bit MLX runtime used for the main study), and is a real interpretability mini-study. On M5 32GB, only the small members (0.6B-4B, maybe 8B) fit in fp16 with hooks; 14B/32B fp16 likely won't. That undercuts the probe precisely at the peak (14B). This is a serious feasibility problem for the FULL mechanistic claim and must be flagged to the lead.

## Recommendation to lead
The mechanism angle is the highest-ceiling, highest-cost option. A FULL induction-head probe is likely infeasible at the peak sizes on available hardware before deadline. A LIGHTER, defensible version: present the distractor-shift as a *literature-grounded mechanistic hypothesis* (cite M1/M2/M3), and run a cheap behavioral proxy (below) rather than activation probing. Reserve the full activation probe as future work — claiming it as the contribution risks an AC asking for the 14B/32B fp16 numbers we can't produce.
- **Cheap behavioral proxy** (fits the project): a controlled distractor-set probe — for each scale, present registries where the held-out correct tool has (a) an orthographic near-neighbor, (b) a semantic synonym, (c) a random matched name, and measure which distractor the model fabricates. This is a BEHAVIORAL test of the same hypothesis, needs only the existing MLX inference path, and directly substantiates the "distractor shift = mechanism shift" story without activation access. This is the minimum experiment for the mechanism framing.

## Confidence
MEDIUM-HIGH on the literature direction (orthographic-copy induction heads emerge earlier/smaller, semantic induction heads later/larger — Olsson + Ren + supporting 2025-26 work, all verified). MEDIUM on the mapping to the distractor-shift (literature-consistent hypothesis, not yet tested on Qwen3). LOW on full-activation-probe feasibility before deadline (14B/32B fp16 + hooks likely exceed M5 32GB). Handoff: recommend the behavioral distractor-set probe as the minimum experiment; reserve activation probing as future work; do NOT claim the activation mechanism as a contribution without the peak-size numbers.
