# synthesist.md — claim matrix + contradictions

## Claim matrix (load-bearing claims → support → tier)

| # | Claim | Support | Tier |
|---|---|---|---|
| K1 | U-shaped/inverse scaling is a real, respected phenomenon with a distractor-task mechanism | Wei 2211.02011 (EMNLP'23); McKenzie 2306.09479 (TMLR'23) | STRONG |
| K2 | Wei's U-shape standard used MULTIPLE families (PaLM+Chinchilla+GPT-3) → single-family is below bar | Wei body fetch | STRONG (inference) |
| K3 | In-context FORMAT/structure can be the active ingredient while CONTENT (correct labels) is near-inert | Min 2202.12837 (EMNLP'22) | STRONG |
| K4 | Orthographic-copy induction heads emerge earlier/smaller; semantic-relation heads later/larger | Olsson 2209.11895; Ren 2402.13055 (ACL'24); 2505.16694 | STRONG (direction); MEDIUM (mapping to distractor-shift) |
| K5 | "Model names a non-existent entity in a namespace" is a recognized high-stakes (security) failure class | Spracklen USENIX Sec'25; slopsquatting (Larson Apr'25) | STRONG |
| K6 | Open models hallucinate names far more than commercial (21.7% vs 5.2% pkgs) — parallels Claude-0 vs Qwen->0 | Spracklen USENIX'25 | STRONG |
| K7 | BFCL/RelyToolBench/API-Bank measure hallucination at coarser grain than per-call registry-membership | BFCL ICML'25; Cao 2412.04141; Phase-0 API-Bank | STRONG |
| K8 | 4-bit quantization itself can induce non-monotonic hallucination-vs-size | 2512.08213 (NCSU, Dec'25) | MEDIUM (direction); REPORTED-NOT-VERIFIED (numbers) |
| K9 | Non-monotonic function hallucination in Qwen agents already reported (CoT-budget axis) | 2604.02155 (Apr'26, single-author preprint) | REPORTED-NOT-VERIFIED |
| K10 | No prior work isolates "envelope FORM vs registry CONTENT" as the active ingredient of agentic error-recovery | librarian + historian negative search | MEDIUM (absence-of-evidence) |

## Contradictions / tensions surfaced (for moderator)

### C1 (LOAD-BEARING) — Is the single-family Qwen3 hump a legitimate "U-shaped scaling" instance, or is it (a) below Wei's multi-family bar and/or (b) a 4-bit-quantization×scale artifact?
- Pro-legitimacy: K1+K4 give a Wei-compatible distractor-decomposition mechanism; the distractor-TYPE shift is exactly the kind of structure Wei's account predicts.
- Anti-legitimacy: K2 (multi-family standard) + K8 (quantization confound) + K9 (concurrent CoT-budget account). AT-1 calls this the #1 threat.
- **This decides whether H1 (U-shaped headline) is viable as the LEAD or must be demoted.** → MODERATOR.

### C2 (LOAD-BEARING) — Is "format-not-content recovery" (C0.7) a genuine conceptual contribution or a restatement of Min et al. 2022?
- Pro-novelty: K3 is forward-prediction ICL with random LABELS; C0.7 is reactive RECOVERY withholding the literal SOLUTION SET (registry). Different regime, stronger effect.
- Anti-novelty: a skeptic could say "format-over-content is known; you applied it to a new task = incremental."
- **This decides whether H2 is a spotlight-grade hook or a related-work paragraph.** → MODERATOR.

### C3 (NON-load-bearing for now) — Mechanism framing payoff vs feasibility.
- mechanism.md: full activation probe is highest-ceiling but likely infeasible at peak sizes (14B/32B fp16 on M5). Behavioral distractor-probe is feasible. Not a contradiction between specialists; a cost/ceiling tradeoff for the lead. Skeptic should pressure-test whether the behavioral probe alone supports a mechanistic CLAIM or only a hypothesis.

## Citation anchors underpinning the matrix
Load-bearing primaries (all peer-reviewed unless noted): Wei et al. arXiv:2211.02011 (EMNLP'23); McKenzie et al. arXiv:2306.09479 (TMLR'23); Min et al. arXiv:2202.12837 (EMNLP'22); Olsson et al. arXiv:2209.11895 (2022); Ren et al. arXiv:2402.13055 (ACL'24 Findings); Spracklen et al. (USENIX Security'25); Patil et al. BFCL (ICML'25); Cao et al. arXiv:2412.04141 (ICML'25). Threats: arXiv:2512.08213 (quant confound, preprint); arXiv:2604.02155 (CoT-budget overlap, preprint).

## Synthesist's pre-moderator read
The four findings are NOT independent contributions; they cohere under ONE theory (H3 grounding-gap): a model's generative tool-name prior matures before its registry-grounding control, producing (a) the non-monotonic curve, (b) the distractor-type shift as the prior's internal structure surfaces, (c) frontier-zero as control fully catches up, and (d) RVR/C0.7 working because a structural re-entry cue re-engages grounding without needing new content. This unifying theory is what converts "four descriptive findings + a trivial fix" into a conceptual contribution. The moderator must resolve C1 and C2 to know whether the LEAD is the theory (H3), the security reframe (web-miner #1), or the format-not-content result (H2).

## Confidence
HIGH on the claim matrix tiers (K1-K7 are peer-reviewed primaries). MEDIUM on K10 (absence-of-evidence — the format-not-content-recovery slice appears unclaimed but absence is hard to prove). Handoff: C1 and C2 are both load-bearing → moderator (done); the unifying grounding-gap read is the synthesist's hypothesis, not a verdict — skeptic must test whether it over-claims.
