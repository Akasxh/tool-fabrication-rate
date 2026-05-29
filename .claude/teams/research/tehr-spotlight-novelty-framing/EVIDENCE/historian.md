# historian.md — inverse/U-shaped scaling theory + format-vs-content prior art

Sub-Q1 (inverse/U-shaped scaling) and Sub-Q5 (format-not-content). All citations VERIFIED unless tagged.

## A. Inverse-scaling / U-shaped scaling canon

### A1. Inverse Scaling Prize — McKenzie et al. — VERIFIED
- **Title**: "Inverse Scaling: When Bigger Isn't Better"
- **Authors**: Ian R. McKenzie, Alexander Lyzhov, Michael Pieler, ... (large collab; "et al.")
- **arXiv**: 2306.09479. **Venue**: TMLR (Transactions on Machine Learning Research), 2023.
- **Core**: Public-contest collection of 11 datasets where larger LMs do WORSE. Four identified causes of inverse scaling:
  (i) **preference to repeat memorized sequences over following in-context instructions**;
  (ii) imitation of undesirable training-data patterns;
  (iii) **an easy DISTRACTOR task the model focuses on instead of the harder real task**;
  (iv) misleading few-shot demonstrations.
- **Relevance to TEHR**: cause (i) and (iii) are directly on-point. Tool-existence hallucination is plausibly the model preferring its memorized/prior tool-name distribution (i) over the in-context registry (in-context instructions). The distractor account (iii) is the engine of the U-shape story below.

### A2. "Inverse scaling can become U-shaped" — Wei et al. — VERIFIED (load-bearing)
- **Title**: "Inverse scaling can become U-shaped"
- **Authors**: Jason Wei, Najoung Kim, Yi Tay, Quoc V. Le.
- **arXiv**: 2211.02011 (submitted Nov 2022; v5 May 2023). **Venue**: EMNLP 2023 (main, aclanthology 2023.emnlp-main.963).
- **Core result**: Of the 11 Inverse Scaling Prize tasks, when scaled to PaLM-540B (5x more compute than the original ≤280B Gopher-scale eval): **6/11 became U-shaped, 4/11 stayed inverse, 1/11 turned positive.**
- **MECHANISM (the anchor for our distractor-shift)**: "U-shaped scaling tasks consist of a **true task and a distractor task**. Medium-sized models are good enough to perform the distractor task, which hurts performance; large models can **ignore the distractor task** and perform the true task. The ability to ignore the distractor is an emergent ability from scaling."
- **Model families used**: PaLM (8B/62B/540B), with comparison to Chinchilla and GPT-3 (multi-family) — VERIFIED via body fetch. **This is the reviewer-bar finding**: Wei et al. established U-shaped scaling using MULTIPLE distinct families AND a within-family ladder. A single-family curve (Qwen3 0.6B-32B) does NOT meet their evidentiary standard for "U-shaped scaling" as a fundamental phenomenon. A reviewer can legitimately say a single quantized family is "task/family-specific optimization, not a scaling law."

### A3. BIG-Bench / emergence U-shape backdrop — VERIFIED (named, lighter)
- "U-shaped and Inverted-U Scaling behind Emergent Abilities of LLMs," arXiv 2410.01692 (2024). Ties U-shaped sub-task curves to apparent emergence. Useful as a secondary citation that U/inverted-U scaling is an active, accepted research object, not a one-off.

## B. The reviewer-bar for an inverse/U-shape claim (answer to Sub-Q1)
To position the Qwen3 TEHR hump as a legitimate U-shaped-scaling instance, a skeptical AC will demand AT LEAST ONE of:
1. **A second model family showing the same hump** (Wei et al.'s standard was multi-family). This is the single strongest demand and the cheapest partial-discharge: even a coarse 3-point ladder in a second open family (e.g. Llama-3.2 1B/3B/8B or Gemma-3 1B/4B/12B) showing peak-then-drop converts N=1 → N=2.
2. **Disentanglement of the 4-bit quantization confound** (see adversary.md — package-hallucination work shows quantization itself produces non-monotonic hallucination-vs-size). The hump must be shown to survive at a fixed (or varied) quantization level, ideally with an fp16 point.
3. **A task-decomposition account in Wei et al.'s own terms** — i.e., name the "true task" (gate generation on the registry) and the "distractor task" (emit the most-plausible tool name from prior). The distractor-TYPE shift is exactly such a decomposition and is the paper's strongest theoretical move. This is what elevates the curve from "a wiggle" to "a Wei-style U-shape."

**Verdict**: single-family alone is NOT enough for a clean "U-shaped scaling" headline at main-track. It IS enough if (a) reframed as "a U-shaped *instance* whose mechanism we decompose" AND (b) one of the confound controls above is added. The distractor-shift is the asset that makes the framing Wei-compatible rather than a bare curve.

## C. Format-not-content prior art (Sub-Q5 — the C0.7 anchor)

### C1. Min et al. — VERIFIED (the canonical anchor)
- **Title**: "Rethinking the Role of Demonstrations: What Makes In-Context Learning Work?"
- **Authors**: Sewon Min, Xinxi Lyu, Ari Holtzman, Mikel Artetxe, Mike Lewis, Hannaneh Hajishirzi, Luke Zettlemoyer.
- **arXiv**: 2202.12837. **Venue**: EMNLP 2022 (2022.emnlp-main.759).
- **Core finding (verbatim-faithful)**: "randomly replacing labels in the demonstrations barely hurts performance ... over 12 different models." What DOES matter: (1) the **label space**, (2) the **distribution of input text**, (3) the **overall FORMAT of the sequence.**
- **Why it's the anchor for C0.7**: This is the foundational result that, in-context, the STRUCTURE/FORMAT of a signal can be the active ingredient while the informational CONTENT (correct labels) is nearly inert. The C0.7 finding ("structured error envelope WITHOUT the registry list already hits zero — envelope shape is the active ingredient, registry content is decorative") is the *recovery/error-correction analogue* of Min et al.'s ICL result. That analogy is the conceptual bridge: nobody has shown the format-over-content effect for **error-recovery scaffolding in tool-using agents**.

### C2. Mind Your Format — VERIFIED (supporting)
- **Title**: "Mind Your Format: Towards Consistent Evaluation of In-Context Learning Improvements," arXiv 2401.06766 (2024).
- 21 models (770M-70B), 4 datasets: "a poor choice of the template can reduce the strongest models to random-guess level"; best templates don't transfer across models even within a family. Supports "format is load-bearing and model-dependent."

### C3. Differentiation requirement for H2 (the format-not-content positioning)
The format-over-content theme is KNOWN (C1, C2) — so the paper CANNOT claim to discover it. The novel slice TEHR can own: **format-over-content for reactive error-recovery in agentic tool use, where the "content" being shown to be decorative is the literal correct answer set (the registry).** Min et al. randomized labels in *forward* demonstrations; C0.7 withholds the *correct tool list* in a *corrective* turn and recovery still completes. That is a stronger and more surprising version of the effect (the missing content is the literal solution), in a new regime (recovery, not prediction). This is defensible and citation-anchored.

## Confidence
HIGH on the citation anchors (Wei, McKenzie, Min, Mind-Your-Format all verified incl. body fetch on Wei). MEDIUM-HIGH on the reviewer-bar conclusion (single-family is below Wei's standard) — this is an inference from Wei's multi-family methodology, defensible but a judgment call. Handoff to synthesist: the distractor-shift is the asset that makes the U-shape Wei-compatible; the format-not-content claim must be differentiated as "recovery regime, missing content = literal solution."
