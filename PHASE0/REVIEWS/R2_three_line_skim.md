# Three-Line Skim Reviewer — Round 2

## Persona
Workshop reviewer with 12 papers in 2 weeks; reads abstract + first paragraph + main table caption, and rejects anything that hasn't sold itself by line 3.

## The 3-line test
- **Title: FAIL** — three abstract phrases ("Registry-Visible Reprompting", "Cost-Quality Gap", "Without Training") and zero concrete failure mode. (a) what: opaque jargon; (b) why I care: unstated; (c) headline claim: missing.
- **Abstract one-sentence: FAIL** — v3.1 §2.2 is 67 words, four nested clauses, three bracketed placeholders, and buries the phenomenon in a subordinate. A tired reviewer bounces at "spanning 3 capability tiers and 2–3 vendor families plus an open-source 8B local model" before reaching the number.
- **First paragraph (proxy): FAIL as sketched** — v3.1 §8.1 says lead with Czapla; Czapla is a blog post; that cedes ground. ADDENDUM E.1 already corrected this (lead with API-Bank's 61.4%) — §8.1 is stale.
- **§5 table caption (proxy): FAIL until drafted** — no caption exists; the table forces the reviewer to compute gap-closure mentally.
- **Contributions list: PARTIAL FAIL** — ADDENDUM B.4 collapses 4→3, but #1 ("Benchmark + Metric + Mechanism") packs three nouns into one bullet — two claims stapled together. #1 and #3 also overlap on "3-tier" framing.

## Where I bounce as a tired reviewer
The title's "Registry-Visible Reprompting" is a term-of-art I have to decode before knowing what failure it fixes. Then §2.2 opens with model-counting ("5–6 models spanning 3 capability tiers and 2–3 vendor families plus an open-source 8B local model") — that's setup, not result. By the time I reach "[X]% (95% CI [L, H])" I've spent my attention budget on the apparatus, not the finding. I want the number in clause one.

## Suggested rewrites that pass the 3-line test
- **Title**: *"Tool-Existence Hallucination in LLM Agents: A Per-Call Metric and a Training-Free Fix That Closes [Y]% of the Cost-Quality Gap."* (Phenomenon, contribution, headline — in that order.)
- **One-sentence main result**: *"LLM agents call tools that do not exist on [X]% of calls; a single-turn re-prompt that lists the registry (RVR) recovers [Y]% of these failures and closes [Z]% of the small-vs-frontier cost-quality gap, validated across 5 models on BFCL-v4 and τ-bench at <2% token overhead."*
- **First-paragraph hook (5 sentences)**: *"Tool registries are the typed substrate through which multimodal agents reach vision, code, audio, and external systems — and current LLM agents routinely call tools that aren't in them. API-Bank \citep{li2023apibank} measured a 61.4% per-task name-mismatch rate on a 2023 benchmark; we show the failure persists in 2026 frontier models on multi-turn registries (Czapla \citep{czapla2026}), and that prior metrics bundle it with unrelated errors. We disaggregate the failure as Tool-Existence Hallucination Rate (TEHR), a per-call metric. We then show that a training-free intervention — Registry-Visible Reprompting (RVR) — recovers [X]% of hallucination-induced failures and closes [Y]% of the small-vs-frontier cost-quality gap on BFCL-v4 and τ-bench. The remainder of the paper formalizes TEHR (§3), characterizes RVR's mechanism via a controlled distractor probe (§6), and reports the 5-model × 2-benchmark × 4-condition main result (§5)."*
- **§5 table caption (3 sentences)**: *"Main result: pooled across 4 API models and 2 benchmarks, RVR (C₁) recovers [X]% of C₀-failed-with-hallucination tasks vs. framework-default error feedback (C₀.₇), paired McNemar mid-p < [P]. The right-most column reports gap-closure ratio: (small+RVR − small+C₀)/(frontier+C₀ − small+C₀). Token overhead <2%; cost-per-success [Z]× lower than the frontier baseline."*

## Top-3 sentence-level fixes
1. Move the headline number to clause 1 of the abstract; move the model/tier counting to clause 3. (Currently inverted.)
2. Rename the title to lead with "Tool-Existence Hallucination" — it is the phenomenon; "Registry-Visible Reprompting" is the fix. Reviewers index on phenomena.
3. Split contribution #1 into "metric" and "mechanism probe." Bundling them ("Benchmark + Metric + Mechanism") reads as padding; separating shows two distinct empirical artifacts.

## Verdict
**NEEDS-EDITS** — paper has the goods (clean phenomenon, training-free fix, quantitative gap-closure claim, 5-model coverage), but the current title and §2.2 sentence bury all three in apparatus-talk. Twenty minutes on the title + abstract one-liner converts this from a skim-reject to a skim-keep.
