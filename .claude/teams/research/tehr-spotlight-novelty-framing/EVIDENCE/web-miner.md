# web-miner.md — creative/contrarian angles + 14-day freshness sweep (Sub-Q4, Sub-Q6)

## A. Production / community evidence that TEHR is a real, named, in-the-wild failure (VERIFIED via GitHub issues + security press)

### A1. "Slopsquatting" — package/name hallucination as a SECURITY threat — VERIFIED
- Term for: attackers register names that LLMs **confidently hallucinate**, then wait for install. Security-press framing (aikido.dev). Anchored academically by:
- **"We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs"** — Spracklen, Wijewickrama, Sakib, Maiti, Viswanath, Jadliwala. **USENIX Security 2025** (usenix.org/conference/usenixsecurity25/presentation/spracklen). VERIFIED.
  - 16 LLMs, 576,000 code samples, 2 languages. **Avg hallucinated-package rate: ≥5.2% commercial, 21.7% open-source.** 205,474 unique hallucinated names. Of hallucinated names: 51% pure fabrications, 38% conflations (e.g. `express-mongoose`), 13% typo-variants. **Commercial < open-source** hallucination — directly parallels the paper's Claude-4.x(0%) vs Qwen-open(>0%) split.
- **Why this matters for positioning**: tool-existence hallucination is the *agentic-tool* sibling of package hallucination. The security framing ("a hallucinated name that resolves against an ambient function = unauthorized capability" — cf. Czapla's `read_secret()` example in Phase-0) gives TEHR a HIGH-STAKES motivation that the current efficiency framing lacks. Slopsquatting is the proven, citable, scary version of "model names a thing not in the provided namespace."

### A2. Production reproductions of TEHR in 2026 (VERIFIED GitHub issues)
- **google-gemini/gemini-cli #25952**: MCP tool-call hallucination — model emits snake_case tool names instead of registered hyphenated names → "tool not found." Real 2026 bug. (Orthographic/near-name distractor, in the wild.)
- **google/adk-python #4173**: agent invokes hallucinated tool (`readLine`) instead of proper validation. Real 2026 bug.
- **cuttalo/depscope-hallucinations-dataset**: daily-updated public corpus of LLM-hallucinated package names from production AI-coding-agent traffic, 19 ecosystems (CC-BY-NC-SA). As of May 2026 a related corpus had 161 entries / 18 ecosystems. Community is actively cataloguing exactly this failure.

## B. 14-day freshness sweep (mid-May 2026) — papers the April Phase-0 audit could NOT have seen

### B1. THREAT/OPPORTUNITY — "Brief Is Better" — VERIFIED
- Xuan Qi, "Brief Is Better: Non-Monotonic Chain-of-Thought Budget Effects in Function-Calling Language Agents," arXiv **2604.02155** (April 2026).
- Finds NON-MONOTONIC function-calling behavior: brief reasoning (~32 tok) +45% relative vs extended (~256 tok) which degrades below baseline; long CoT yields **18% hallucinated functions, 28% wrong selection** on Qwen2.5-1.5B (+ Phi-3 referenced).
- **THREAT**: this is recent prior art on *non-monotonic function hallucination in Qwen-family agents* — a reviewer WILL surface it. It pre-empts a naive "we are first to show non-monotonic function hallucination."
- **OPPORTUNITY / confound**: it ties hallucination to **CoT/reasoning-token budget**, and Qwen3 has a thinking mode. Per PAPER_PLAN v3.1 Δ7, the MLX adapter passes `enable_thinking=False`. So the paper can DIFFERENTIATE: our non-monotonic curve is over MODEL SCALE at a FIXED (disabled) thinking budget, isolating scale from CoT-length. This both distinguishes from 2604.02155 AND defends against the "it's just a reasoning-budget artifact" attack — BUT ONLY IF the paper explicitly reports thinking was disabled and ideally adds a thinking-on/off sensitivity check.

### B2. "Internal Representations as Indicators of Hallucinations in Agent Tool Selection" — VERIFIED existence
- Healy, Srinivasan, Madathil, Wu. arXiv **2601.05214** (Jan 2026). Probes internal reps for tool-selection hallucination. Constrains the mechanism-probe novelty (see mechanism.md M-priorart). Could not extract per-scale method (PDF = slides); REPORTED-NOT-VERIFIED on specifics.

### B3. Adjacent recent non-monotonic / hallucination work — VERIFIED existence
- "LLMs as Noisy Channels: A Shannon Perspective on Model Capacity and Scaling Laws," arXiv 2605.23901 (May 2026): formalizes a monotonic→U-shaped transition when SNR is insufficient. Possible *theoretical* framing for why a grounding signal (registry) below a capacity threshold yields U-shaped failure. Speculative; cite cautiously.
- "Hallucinations Live in Variance," arXiv 2601.07058 (Jan 2026): non-monotone stability vs sparsity.
- "Neural Diversity Regularizes Hallucinations in Small Language Models," arXiv 2510.20690: U-shaped hallucination vs neural diversity.
- "Secure or Suspect? ... Package Hallucinations ... Quantized LLMs," arXiv 2512.08213 (Dec 2025) — the quantization confound, see adversary.md.

## C. 3-5 concrete creative/contrarian framings (Sub-Q4 deliverable)

1. **"Slopsquatting for agents: tool-existence hallucination is a supply-chain attack surface."** Reframe TEHR from efficiency to SECURITY. Anchor: Spracklen USENIX'25 + Czapla `read_secret()` + gemini-cli #25952. A hallucinated tool name that resolves against an ambient/MCP function = unauthorized capability execution. This is the highest-impact reframe and the most spotlight-friendly (security ACs care). Minimum experiment: a "collision probe" — measure how often fabricated tool names collide with a plausible adjacent namespace (e.g. a superset registry), i.e. exploitability rate.

2. **"Format-not-content recovery" (the C0.7 contribution).** The counterintuitive, mechanism-of-the-fix claim: a structured error envelope with NO registry content recovers as well as one with it. Differentiates from "just retry." Anchor: Min et al. 2022. This is the crispest defense against "trivial intervention."

3. **"Capability-control inversion / grounding gap."** The non-monotonicity is PREDICTED by a theory: generative tool-name prior matures before registry-grounding control. Mid-scale models have a rich enough prior to fabricate plausibly but not enough control to gate on the registry; the largest model re-acquires control. Anchor: Wei U-shaped (distractor) + McKenzie cause (i) "repeat memorized over in-context."

4. **"Disabled-thinking isolates scale from reasoning-budget."** Contrarian methodological flex against 2604.02155: by holding thinking OFF, the curve is a pure scale phenomenon, not a CoT-length artifact — a cleaner non-monotonic-scaling datapoint than the concurrent work.

5. **"The frontier-zero result is the headline, not the fix."** Claude 4.x = 0/2599 across five models is a striking, clean negative-space result (frontier alignment has effectively SOLVED registry grounding) while open models 0.6-32B have NOT, non-monotonically. The contribution is the *capability-frontier map* of when this failure exists at all. Pairs naturally with #1 (security): the failure is concentrated exactly in the open/self-hosted models people deploy for cost/privacy.

## Provenance note
GitHub issues and security blogs are LOWER-tier than papers; they establish the phenomenon is real-in-the-wild (motivation), NOT quantitative claims. USENIX'25 and the arXiv papers are the load-bearing citations. Adversary audits the corpus next.

## Confidence
HIGH on USENIX'25 numbers, slopsquatting attribution (Seth Larson Apr-2025, verified), and the existence of all freshness-window papers. HIGH on the "Brief Is Better" overlap as a real threat that must be cited-and-distinguished. MEDIUM on the security reframe being spotlight-decisive (compelling but the paper's data is reliability/efficiency, not an attack demonstration — would need a collision/exploitability probe). Handoff: framing #1 (security/slopsquatting-for-agents) and #2 (format-not-content) are the two strongest; #4 (thinking-disabled) is a mandatory defensive note regardless of headline.
