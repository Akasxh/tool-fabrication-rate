# What's Missing Audit

Auditor persona: meticulous; benchmarks paper against ICML 2026 reproducibility checklist + SCALE workshop expectations + reviewer-Q&A patterns. Categories below use [PRESENT | PARTIAL | MISSING] with severity tags.

## Category-by-category checklist

### 1. Figures and tables
- Tables: PRESENT (Tab. regime, Tab. probe, Tab. probe-mech). All-zero rows but well-formed.
- Figures: MISSING (BLOCKER-tier for ICML norms; MAJOR for workshop). Zero figures in entire submission.
- Decomposition trace diagram (§5.3 `pwd→ls→cd→mkdir→mv` chain): MISSING (MAJOR — single most reviewer-friendly artifact in the paper, currently buried in prose).
- Distractor-probe schematic (target-removed + 4 arms): MISSING (MAJOR).
- Cost-vs-N curve / dollar accounting: MISSING (MINOR).
- Per-tier visualization: MISSING (MINOR — but redundant given table coverage).

### 2. Reproducibility (ICML 2026 checklist)
- Code release statement: PRESENT in §1 contributions; PARTIAL — no anonymized URL/commit hash in submission body; only "anonymized supplementary archive" referenced.
- Data pinning: PRESENT (BFCL @ `6ea5797`, Apache-2.0).
- Random seeds: PARTIAL — manifest *will record* "all random seeds" but the *values* are not stated in paper, nor whether seeds matter at temp=0 (they don't for sampling, but do for task ordering / probe injection RNG).
- Compute environment: PARTIAL — Python deps listed (`anthropic==0.97.0`, `mlx-lm==0.31.3`, etc.) but Python version, OS string, hardware (Apple Silicon model), MLX precision (4-bit? 8-bit?) not stated in body.
- Model snapshot resolution: PRESENT (rolling alias resolved at run-start via `models.list`).
- Hyperparameters: PRESENT (temp=0, top_p omitted with API justification, turn cap=8, wall-clock cap=120s).
- Statistical test specs: PRESENT (paired McNemar mid-p, TOST 5pp, Holm-Bonferroni, BCa cluster-bootstrap, Friedman+Nemenyi).
- Multiple-comparison correction: PRESENT (Holm-Bonferroni across three primary tests).
- All baselines cited: PRESENT (C0, C0.5, C0.7 with langchain_toolnotfound2025 anchor).
- Compute resources: PARTIAL — $21.61 spent and per-cell breakdown exist in `headline_numbers.md` but body says "$22 USD" without wall-clock total. The "~3h wall-clock" figure from the audit prompt is NOT in the paper. (MINOR.)
- N=15 per probe arm rationale: MISSING (MAJOR — pre-reg said N=100 probe; actual was N=15, this discrepancy is unexplained in §4 or §5).

### 3. Limitations / Threats to validity
- Sample-size limits: PARTIAL — §7 acknowledges "exploratory where N<30" via cell flags but never reports a *power* calculation for the headline TEHR=0 result. (MAJOR.)
- Vendor scope: PRESENT (§7.2 explicitly forgoes Gemini/Llama/Mistral/DeepSeek).
- BFCL-vs-production gap: PRESENT (§7.7 ambient-function risk).
- Statistical underpowering of headline null: PARTIAL — §6 reports post-hoc power <0.20 *for the mechanism Friedman test* but the headline "TEHR=0/1571" has NO confidence interval / rule-of-three upper bound stated. (BLOCKER — see top-10 #1.)
- Distractor-probe limitations: PRESENT (§7.3 hallucination taxonomy).
- Decomposition-vs-fabrication confound: MISSING (MAJOR — the agent's decomposition behavior may itself reduce the regime where TEHR is even *measurable*, making TEHR a possibly miscalibrated metric for modern models. The paper notes decomposition empirically but doesn't acknowledge that decomposition makes the metric self-suppressing).
- Model-tier mismatch with claim: PARTIAL — abstract claims "two Anthropic capability tiers" but Tab. regime shows Sonnet-only on regime tests; Haiku appears only in probe. (MAJOR — internal inconsistency.)
- Pre-reg-vs-actual delta: MISSING (BLOCKER — §4 pre-registers N=100 probe, N=100 main run; §5 reports N=15 probe and N=33-40 main run. No "deviation log" reconciling pre-registration with execution).

### 4. Expected reviewer questions not pre-empted
- "Why didn't you replicate MetaTool's 25% number?" PARTIAL — §1 mentions the 25% figure but doesn't put it in a comparison table. (MAJOR.)
- "Why is N=15 enough?" MISSING (BLOCKER).
- "What does TEHR=0/15 mean — exactly zero or below detection threshold?" MISSING (BLOCKER — rule of three: 0/N gives 95% CI upper bound of 3/N; for N=1571, upper bound is ~0.19%. This single number would transform the paper's claim.).
- "What would TEHR look like on weaker open-source models?" PARTIAL — §4.1 mentions Qwen3-8B "where applicable" but Qwen results are absent from Tab. regime. (MAJOR — discrepancy with §8 LLM disclosure which claims five models evaluated, vs. paper body which reports two.)
- "Upper bound on TEHR given 0 events?" MISSING (BLOCKER — rule of three).
- "Why scope only Anthropic when the title implies broader?" PARTIAL — §7.2 acknowledges; title still doesn't qualify. (MINOR.)
- "Is C0.7 the right baseline?" PARTIAL — §3.3 motivates C0.7 against `langchain_toolnotfound2025` but no empirical evidence that real-world frameworks emit that exact JSON shape. (MINOR.)
- "Does decomposition itself count as a recovery from a near-hallucination, and if so, why isn't it in the metric?" MISSING (MAJOR).

### 5. Comparison with prior work
- Bibliography: 23 entries; 5 marked TODO-verify (`bugstudy2026`, `licl2026`, `fissiongrpo2026`, `englander2026` arXiv IDs; whole bib has TODO header). MAJOR — must be resolved before submission.
- Direct numerical comparisons: MISSING (MAJOR). Paper text says "MetaTool reports 25%" but no side-by-side table comparing API-Bank's 61.4%, MetaTool's 25%, RelyToolBench's TSH%, and our 0.0%. This would be the paper's strongest visual.
- L-ICL 59→89% comparison: numerical claim made in §2 but not in any table.

### 6. Visualizations
- Decomposition trace as sequence diagram: MISSING (HIGH-LEVERAGE quick win).
- Cost-vs-N curve: MISSING (LOW-VALUE for this paper).
- Per-tier comparison plot: MISSING (LOW-VALUE — table suffices for 2 tiers).
- TEHR-bar chart with rule-of-three CIs: MISSING (HIGH-LEVERAGE).
- Prior-work comparison bar chart (61.4% / 25% / our 0%): MISSING (HIGHEST-LEVERAGE).

### 7. Ethical / Safety
- Safety section: PRESENT (§7.7 ambient-function risk).
- IRB / human-subjects: not applicable; no statement needed.
- Dataset license: PRESENT (Apache-2.0 BFCL).
- Dual-use / red-team disclosure: MISSING (MINOR — workshop accepts without).
- Model-card consultation: MISSING (MINOR — Anthropic Sonnet/Haiku model cards not cited).

### 8. Submission mechanics
- Page limit: PARTIAL — main.tex uses standard `article` class with 1in margins, *not* the ICML 2026 style. Word count under standard format is unknown until styled. (MAJOR — current main.tex line 2 says "Switch to icml2026 once SCALE-call-audit confirms style files." Not done.)
- Anonymization: PRESENT (per earlier R2 audit; Author=Anonymous).
- LLM/agent-disclosure section: PRESENT (§8).
- arXiv concurrent posting: handled per audit; no opt-in/opt-out language in paper.
- Appendix referenced but absent: MAJOR — §3.2 ("ablate $k\in\{0,1,2,3\}$ ... in the appendix"), §7.4 ("sketch the trade-off in the appendix"), §7.5 ("wall-clock distribution ... in the appendix"). Three forward-references to a non-existent appendix.

---

## Top-10 missing items, ranked by reviewer-impact

1. **[BLOCKER]** No rule-of-three upper bound on TEHR=0/1571. — Add one sentence: "By the rule of three, the 95% upper bound on TEHR is 3/1571 ≈ 0.19%." This is the single most defensible quantitative statement available and its absence will cost the paper credibility with statistical reviewers.
2. **[BLOCKER]** Pre-registration vs. actual execution mismatch (N=100 → N=15 probe; 5-model claim → 2-model body). — Add a "Deviations from pre-registration" subsection in §4 explaining the credit-budget reduction and explicitly de-listing GPT-4.1/4.1-mini/Qwen from the body claims (§8 still lists 5 models — internal contradiction).
3. **[BLOCKER]** Paper does not compile under ICML 2026 style file. — Replace `\documentclass[11pt]{article}` with `\usepackage{icml2026}` and verify page count.
4. **[MAJOR]** Three forward-references to a nonexistent appendix (§3.2, §7.4, §7.5). — Either add a one-page appendix or strike the references.
5. **[MAJOR]** Zero figures. — Add at minimum a prior-work comparison bar chart (61.4% API-Bank / 25% MetaTool / 0% ours) — single most reviewer-impactful artifact.
6. **[MAJOR]** Bib entries with `TODO: verify arXiv ID` (5 entries). — Either verify the IDs or remove the citations and rewrite affected paragraphs.
7. **[MAJOR]** Headline claim ("two Anthropic capability tiers") contradicted by Tab. regime (Sonnet only). — Either rerun Haiku on regime splits ($1-2 spend) or rewrite the claim as "Sonnet on regime + Sonnet/Haiku on probe."
8. **[MAJOR]** No direct numerical comparison table vs. prior tool-hallucination metrics. — Add a 4-row comparison table (API-Bank 61.4% / MetaTool 25% / RelyToolBench TSH / ours 0.0%, with model-vintage and benchmark columns).
9. **[MAJOR]** Decomposition-as-confound for TEHR not acknowledged. — Add one paragraph in §7 noting that decomposition behavior depresses the denominator-relevant regime, making TEHR's headline number conservative-by-construction in modern models.
10. **[MINOR]** Hardware/Python-version/MLX-precision not in body. — Add a one-line "Compute environment" callout in §4.5.

## Quick-win additions (each <30 min)

- Insert rule-of-three CI sentence (top-10 #1) — 5 min.
- Strike or stub the three appendix references (top-10 #4) — 10 min.
- Fix the §8 LLM-disclosure claim of "five models" to match §5's two — 5 min.
- Add Python/OS/hardware single-line block to §4.5 — 10 min.
- Resolve five `TODO: verify` arXiv IDs in `refs.bib` (search arxiv.org) — 30 min total.

## High-leverage additions (1–3 hours)

- Comparison-with-prior-work table (top-10 #8). — 1 hour.
- Decomposition-trace sequence diagram (TikZ or PNG) of `bfcl_multi_turn_miss_func_24` — 1.5 hours.
- TEHR bar chart with rule-of-three error bars across the six regime cells — 1 hour.
- Pre-registration deviation log subsection in §4 (top-10 #2) — 1 hour.
- Switch to ICML 2026 style file and recompile, fix any page-count overflow (top-10 #3) — 2 hours.

## OK-to-skip-for-workshop, defer to camera-ready

- Cost-vs-N curve.
- p99 latency distribution figure.
- Multi-vendor extension (OpenAI, Gemini, xAI).
- Enterprise-scale registry stress test (≥100 tools).
- Hierarchical-RVR variant.
- Multimodal extension (vision-tool registries).
- Red-team / dual-use disclosure expansion.
- Anthropic model-card citation.

---

## Total count

- Items expected (canonical ICML reproducibility + SCALE expectations + reviewer-anticipation): ~38
- Items PRESENT: 18
- Items PARTIAL: 11
- Items MISSING: 9
- Coverage ratio: 47% fully present, 76% at least partial.

The submission is workshop-tier defensible with the five quick wins (~1 hour total) and three high-leverage additions (~5 hours total). Without the rule-of-three CI and the pre-registration deviation log, the paper is exposed to predictable BLOCKER-grade reviewer attacks.
