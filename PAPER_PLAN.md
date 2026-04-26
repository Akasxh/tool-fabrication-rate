# PAPER_PLAN — SCALE @ ICML 2026 Submission

**Slug**: scale-icml-2026-paper-plan
**Author**: Akash (solo, unless co-author confirmed before T+0)
**Drafted**: 2026-04-27
**Status**: PRE-FLIGHT — ready for `/ultraplan` refinement

---

## 1. MISSION

Submit a Main Track 7-page paper to the **SCALE workshop @ ICML 2026** that introduces, quantifies, and fixes the **Tool-Existence Hallucination** failure class in tool-using LLM agents — a phenomenon documented in industry (Czapla / Answer.AI, Feb 2026) but **not yet addressed academically**. Deliver a paper whose one-sentence main result would make a senior researcher in agentic AI pause and say *"huh, that's actually interesting."*

---

## 2. THE PAPER

### 2.1 Working title
*"The Tool-Existence Hallucination: A 2-Line Intervention Recovers 70-90% of Wasted Retries Across Frontier Agents"*

### 2.2 One-sentence main result (load-bearing for novelty)
*Across 4 frontier models, the dominant retry-waste failure class of ReAct agents on standard benchmarks is calling tools that don't exist in the registry; a 2-line training-free inference-time intervention (registry-membership check + re-prompt) recovers 70–90% of wasted retries with <2% overhead and zero quality regression on baseline-passing tasks, and the failure rate correlates with tool-name lexical similarity in the registry.*

### 2.3 Four claimed contributions
1. **Naming + metric**: Tool-Existence Hallucination Rate (TEHR), the first metric to quantify this failure class.
2. **Empirical characterization**: TEHR baselines on 4 frontier models × 2 benchmarks × 100 tasks (1600 runs).
3. **Intervention**: A training-free, registry-only, inference-time fix with measured recovery rate, overhead, and no-regression guarantee.
4. **Mechanism + design rule**: Lexical-similarity correlation analysis → prescriptive guidance for tool-set design (maximize Levenshtein distance, avoid semantic clustering).

### 2.4 Why this clears NeurIPS-caliber novelty
- **Industry pain documented, academic gap open**: Czapla (Answer.AI, Feb 2026) names the phenomenon across Claude / Gemini / Grok / GPT; Empirical Bug Study (arXiv 2602.21806) confirms "API misuse" as top-3 root cause across 998 CrewAI+LangChain bugs. **No academic paper measures, names, or fixes it.**
- **Methodological precedent exists**: L-ICL (arXiv 2602.00276) is the L-ICL-shape paper for planners ("minimal intervention 0%→89%"); M2 is the analog for tool-using agents on a fresh failure class.
- **Mechanism is principled**: The intervention is a constrained-decoding analog deployed at the message level. Reviewers will recognize the formalism.
- **Theory hook**: Lexical-similarity → hallucination rate correlation lifts it above measurement.
- **Differentiation is clean**: Fission-GRPO (RL-trained, not training-free), AEGIS (safety not correctness), AutoTool (selection from large set, not membership). All distinguishable in one paragraph each.

---

## 3. HARD CONSTRAINTS

| Axis | Value |
|---|---|
| Workshop | SCALE @ ICML 2026 — "Scalable Learning and Optimization for Efficient Multimodal AI Agents" |
| Track | **Main 7 pages** (Benchmarking & Late-breaking off the table) |
| Deadline | 2026-04-28 AoE (~2026-04-29 12:00 UTC) |
| Time budget | **36 hours** wall-clock from T+0 (incl. ~12h sleep, ~24h work) |
| Format | ICML 2026 LaTeX, double-blind, 7 pages excl. references/appendix |
| Submission | OpenReview: https://openreview.net/group?id=ICML.cc/2026/Workshop/SCALE |
| Hardware | MacBook M5 + 32 GB unified memory (dev only) |
| API budget | $25-50 across Anthropic + OpenAI + Google + Together |
| Models | Claude 4.6 (Anthropic), GPT-4.1/o4 (OpenAI), Gemini 2.5 Pro (Google), Qwen3-72B (Together) |
| Benchmarks | BFCL v4 multi-turn (primary) + τ-bench retail (secondary) |
| Author | Solo unless co-author confirmed before T+0 |

### 3.1 Soft constraints / preferences
- **No** hardware/KV-cache/inference-systems framing — explicitly rejected by Akash.
- **No** "audit/measurement-only" framing — must have a method or surprising claim.
- Total runs ≈ 1600 (4 models × 2 benchmarks × 100 tasks × 2 conditions). Pilot pre-run ≈ 200 (4 × 25 × 2).
- Statistical bar: 95% CIs on TEHR per model; Cohen's d on intervention recovery; correlation r with bootstrap CI for lexical-similarity claim.

---

## 4. EXPERIMENTAL DESIGN

### 4.1 The intervention (the method contribution)

**Pseudocode (≈10 lines, the "2-line" framing is the conceptual core, the rest is plumbing):**

```python
def intervention(agent_msg, registry):
    proposed_tool = parse_tool_call(agent_msg)
    if proposed_tool.name not in registry:        # the membership check
        feedback = f"Tool '{proposed_tool.name}' is not in the registry. " \
                   f"Available tools: {sorted(registry.keys())}. " \
                   f"Choose one of these or explain why none apply."
        return Action.RE_PROMPT(feedback)         # one retry, with registry list
    return Action.EXECUTE(proposed_tool)
```

**Design choices to defend in §3 of the paper:**
- Why the registry list is included in the re-prompt (vs. "tool not found, retry" alone): exploits the model's autoregressive prior over the *correct* tool name once it's in context.
- Why max 1 retry (not unbounded): bounds compute overhead; matches frontier-API retry budgets in production.
- Why training-free: orthogonal to RL approaches (Fission-GRPO); deployable today on closed APIs.
- Constrained-decoding analog framing: at the message level, the intervention restricts the *next* tool call's name to the registry — same effect as token-level constrained decoding without needing logit access.

### 4.2 Conditions

| Condition | Description |
|---|---|
| **C0 baseline** | Agent runs ReAct loop with no membership check; failures count as task failure or wasted retry per benchmark scoring |
| **C1 intervention** | Same agent, but every tool call passes through `intervention()`; max 1 re-prompt per hallucinated tool call |

### 4.3 Metrics

| Metric | Definition | Where reported |
|---|---|---|
| **TEHR** | Tool-Existence Hallucination Rate = (hallucinated tool calls) / (total tool calls) per model under C0 | §4 baseline table |
| **Recovery rate** | Fraction of C0-failed tasks that pass under C1 *due to* the membership check (not coincidental) | §5 main table |
| **Compute overhead** | Mean extra tokens per task, C1 vs C0 | §5 overhead column |
| **Quality regression** | Pass rate on C0-passing tasks under C1 (must be ≥99% to claim "no regression") | §5 regression column |
| **Lexical similarity correlation** | Pearson r between mean pairwise Levenshtein distance of registry tool names and TEHR per task, with bootstrap 95% CI | §6 mechanism analysis |
| **Per-model breakdown** | All of the above, split by model | §5 + appendix |

### 4.4 Pre-registered analysis decisions (lock these BEFORE looking at full data)

These 7 fixes from skeptic-v3 are baked into the harness to prevent reviewer attacks:

1. **TEHR is computed on tool calls, not on tasks** — denominator clarity.
2. **"Recovery" requires the C1-passing trace to contain a membership-rejection event** — prevents conflating with random variance.
3. **Quality regression measured on the strict subset of C0-passing tasks** — not on the whole set.
4. **N=100 tasks per benchmark per model with 95% CIs** — sample size pre-committed.
5. **2 prompt templates per benchmark** — robustness to prompt phrasing; report both.
6. **τ-bench used as secondary** — generalization claim across benchmark distributions.
7. **One-tailed test on recovery rate vs zero**, two-tailed on regression — directionally honest.

### 4.5 Compute + cost budget

| Phase | Runs | Cost | Wall-clock |
|---|---|---|---|
| Pre-flight smoke test | 20 | <$1 | 15 min |
| Pilot (Gate 2 input) | 200 (4 × 25 × 2) | ~$5 | 1.5 h |
| Main run (Gate 3 input) | 1600 (4 × 2 × 100 × 2) | $25-35 | 3 h |
| Re-runs / API failure recovery | up to 200 | up to $5 | 0.5 h budgeted |
| **Total** | **~2000** | **$30-45** | **5 h** |

---

## 5. 36-HOUR EXECUTION PLAN

Cumulative *task hours* (T+H format). Total: 24h of work, 12h of sleep/breaks, scheduled across 36h wall-clock.

### Phase 0 — Pre-flight (T+00:00 → T+04:00, tonight)

| T+ | Task | Deliverable |
|---|---|---|
| 00:00 - 01:00 | Verify 4 API keys (Anthropic / OpenAI / Google / Together); `pip install bfcl-eval==2025.12.17 anthropic openai google-genai together pandas matplotlib scikit-learn python-Levenshtein scipy`; smoke-test 1 call per provider | All 4 providers respond |
| 01:00 - 02:00 | Pull 20 sample BFCL multi-turn tasks + 10 τ-bench retail tasks; manually inspect ≥5 traces per model from API for whether tool-name hallucinations occur unprompted (early Gate 1 dry run) | At least 1 hallucinated tool name observed across sample → green light for Gate 1 |
| 02:00 - 03:00 | Clone ICML 2026 LaTeX template; create `paper.tex` skeleton with all 7 section headers + abstract placeholder; init anonymous reproduction repo (separate GitHub account or anonymous OpenReview attachment) | Skeleton compiles to 1-page placeholder PDF |
| 03:00 - 04:00 | Read end-to-end: Czapla (Answer.AI), L-ICL (arXiv 2602.00276), Empirical Bug Study (arXiv 2602.21806), Engländer "Agents Ignore" (arXiv 2604.17609 — needed if M1 pivot triggers) | Notes file with key quotes for Related Work |

**Sleep 1**: T+04:00 → T+12:00 (8h). Non-negotiable — Day 1 is the marathon.

### Phase 1 — Day 1: Gate 1 + Setup (T+12:00 → T+15:00)

| T+ | Task | Deliverable |
|---|---|---|
| 12:00 - 13:00 | **GATE 1 — Formal framework verification.** For each of 4 models, send a prompt with a small registry (3 tools) and a task that nudges toward an out-of-registry name; observe whether the API rejects, the framework catches it, or the hallucination flows through. Repeat 5x per model (20 calls total) | Decision: M2 GO / M1 PIVOT |
| 13:00 - 14:30 | Build `bench_tool_hallucination.py`: BFCL + τ-bench loaders, model dispatch (4 providers), trace logging, TEHR computation | Runs 1 task end-to-end on each model |
| 14:30 - 15:00 | Build `intervention.py`: registry membership check, re-prompt format, 1-retry limit, overhead instrumentation | Runs 1 task end-to-end with C1 |

### Phase 2 — Day 1: Pilot + Gate 2 (T+15:00 → T+18:00)

| T+ | Task | Deliverable |
|---|---|---|
| 15:00 - 17:00 | Pilot run: 4 models × 25 tasks × 2 conditions = 200 runs, BFCL only. Monitor for API failures, throttle errors, parsing bugs | Pilot CSV with TEHR + recovery columns |
| 17:00 - 18:00 | **GATE 2 — Pilot TEHR check.** TEHR ≥5% across at least 2 of 4 models? If yes → green light main run. If 1/4 only → flag for paper framing. If 0/4 → pivot to M1 | Decision: scale-up / pivot |

### Phase 3 — Day 1: Main Run + Gate 3 (T+18:00 → T+22:00)

| T+ | Task | Deliverable |
|---|---|---|
| 18:00 - 21:00 | Main run: 4 × 2 × 100 × 2 = 1600 runs. Run BFCL and τ-bench in parallel where API rate limits allow. Log all traces to JSONL | Full results CSV |
| 21:00 - 21:30 | **GATE 3 — Recovery rate check.** Recovery ≥50% on at least 2 of 4 models? If yes → headline holds. If 30-50% → soften claim to "30-50% recovery, characterization paper". If <30% → emergency reframe to "characterization-only, no intervention claim" or pivot to M1 | Decision: claim strength |
| 21:30 - 22:00 | Quality regression check on C0-passing subset. Must be ≥99% to claim "no regression" | Regression statistic computed |

### Phase 4 — Day 1: Analysis + Plots + Abstract (T+22:00 → T+26:00)

| T+ | Task | Deliverable |
|---|---|---|
| 22:00 - 23:00 | Statistical analysis: bootstrap 95% CIs on TEHR per model; Cohen's d on recovery; one-tailed test on recovery vs zero | `stats.csv` |
| 23:00 - 00:00 | Lexical similarity correlation: compute mean pairwise Levenshtein distance per task's tool registry; correlate with task-level hallucination count; bootstrap CI on r | Correlation result + scatter plot |
| 00:00 - 01:00 | Generate 4 main figures: (1) TEHR baseline bar chart per model, (2) recovery rate per model, (3) overhead vs benefit scatter, (4) lexical-similarity scatter with regression line | 4 PDFs ready for embedding |
| 01:00 - 02:00 | Draft abstract (250 words, 5 sentences max) + intro outline. Write while results are fresh | `abstract.tex` + `intro_outline.md` |

**Sleep 2**: T+26:00 → T+31:00 (5h). Compressed — Day 2 needs energy.

### Phase 5 — Day 2: Writing Marathon (T+31:00 → T+35:00)

| T+ | Task | Deliverable |
|---|---|---|
| 31:00 - 32:00 | §1 Introduction (≈1 page): hook with Czapla quote → academic gap → contributions list (4 from §2.3 above) → roadmap | Draft §1 |
| 32:00 - 32:45 | §2 Related Work (≈0.75 page): 5 paragraphs on (a) tool-using agents, (b) agent failure analysis, (c) constrained decoding, (d) self-correction in agents, (e) intervention papers (L-ICL anchor, Fission-GRPO contrast, AEGIS contrast, AutoTool contrast) | Draft §2 |
| 32:45 - 33:30 | §3 Method (≈0.75 page): TEHR definition + intervention pseudocode + design choices + lexical-similarity feature | Draft §3 |
| 33:30 - 34:00 | §4 Experimental Setup (≈0.5 page): models, benchmarks, prompts, conditions, pre-registered analysis decisions (the 7 from §4.4 above) | Draft §4 |
| 34:00 - 34:45 | §5 Results (≈1.25 pages): TEHR baseline table + recovery rate table + overhead + regression + per-model breakdown + Figures 1-3 | Draft §5 — load-bearing |
| 34:45 - 35:00 | §6 Mechanism Analysis (≈0.5 page): lexical-similarity correlation + Figure 4 + design rule | Draft §6 |

### Phase 6 — Day 2: Polish + Submit (T+35:00 → T+36:00)

| T+ | Task | Deliverable |
|---|---|---|
| 35:00 - 35:15 | §7 Discussion + Limitations + Conclusion (≈0.5 page): single-organization, 4-model coverage limit, Levenshtein-as-proxy limit, future work | Draft §7 |
| 35:15 - 35:30 | LaTeX compile, fix overflow, ensure 7-page bound. Add anonymized appendix with full per-task tables + 7 pre-registered decisions explicit | PDF ≤7 pages excl. refs/appendix |
| 35:30 - 35:45 | Anonymize: remove author names, acknowledgments, GitHub URL → anonymous OpenReview-attachment URL; double-check via `pdfinfo` and grep for "akash" / IIT / vLLM | De-anonymization risk = nil |
| 35:45 - 35:55 | Push anonymous reproduction repo (code + data CSVs); link from paper as anonymous URL | Repo accessible |
| 35:55 - 36:00 | OpenReview submit; verify title, abstract, PDF, supplementary all uploaded; screenshot confirmation | Submission confirmation email |

---

## 6. HARD GATES (3) + DECISION TABLE

| Gate | T+ | Trigger to PASS | Trigger to PIVOT | Pivot target |
|---|---|---|---|---|
| **G1** | 13:00 | ≥1 hallucinated tool name flows through API in pilot probe across at least 2 of 4 models | All 4 frameworks intercept at API level | **M1 (anchoring)** — same toolchain, controlled-evidence study |
| **G2** | 18:00 | TEHR ≥5% in pilot on ≥2 of 4 models | TEHR <5% across all 4 in pilot | **M1 (anchoring)** — phenomenon too rare to anchor a paper |
| **G3** | 21:30 | Recovery ≥50% on ≥2 of 4 models | Recovery 30-50% → characterization-only framing; <30% → pivot or abort | M1 if abort; otherwise reframe |

### 6.1 Backup plan (M1 — First-Hypothesis Anchoring on Agent Trajectories)

If G1 or G2 trips:
- Same toolchain, same models, same benchmarks.
- Controlled-evidence design: take agent's turn-1 hypothesis, return tool result that contradicts it; measure (a) acknowledgment, (b) revision, (c) action.
- 2 interventions: enumerate-alternatives + acknowledge-contradiction.
- 200 controlled tasks × 4 models × 3 conditions = 2400 runs; ~$30-40; 2.5-3h compute.
- **Mandatory differentiation paragraph in abstract + §1 + §2** vs Engländer "Agents Explore but Agents Ignore" (arXiv 2604.17609, Apr 19 2026).
- M1 fits 36h budget with the same Phase structure.

### 6.2 Hard abort threshold

If by T+22:00 BOTH M2 (TEHR baseline + recovery rate) AND M1 (controlled-evidence pilot) show null effects:
- **Option A**: Pivot to M3 (prefix predictability) using the 1600 traces already collected — train a 50M-param classifier on first 2 turns. Tight on time but feasible.
- **Option B**: Honest abort — submit at NeurIPS ENLSP 2026 or next workshop with proper experimental scale. **DO NOT** ship a thin paper to meet a deadline.

---

## 7. RISK REGISTER

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Frameworks already enforce membership at API level (M2 phenomenon doesn't exist in 2026) | Low | Critical | Gate 1 catches at T+13:00; pivot to M1 |
| R2 | Czapla post followed by an academic paper before SCALE review concludes (mid-June scoop) | Low-Medium | High | Submit early; cite Czapla + Empirical Bug Study as motivation; emphasize TEHR + lexical-similarity novelty layer beyond pure phenomenon naming |
| R3 | TEHR <5% across all models — phenomenon too rare | Medium | Critical | Gate 2; pivot to M1 |
| R4 | Recovery <50% — intervention claim too soft | Medium | High | Gate 3; reframe to characterization-only or pivot |
| R5 | Lexical-similarity correlation fails (r < 0.3 with wide CI) | Medium | Medium | Drop §6 mechanism claim; reframe as "future work" — paper still stands on §3-5 |
| R6 | API rate limits / throttling delays main run | Medium | Medium | 0.5h re-run budget; stagger providers; have Together-only fallback (Qwen3 + GPT only) ready |
| R7 | Provider outage during main run | Low-Medium | High | Run BFCL and τ-bench staggered; checkpoint after each model; resume from checkpoint |
| R8 | Writing compression — 7 pages of Main-track quality in 4h is tight | High | High | Phase 4 (Day 1 evening) drafts abstract + §1 outline before sleep; Phase 5 is execution not invention |
| R9 | De-anonymization slip (mention of vLLM / IIT Patna / Akash / GitHub handle) | Medium | Critical | Phase 6 dedicated grep + pdfinfo check; ask Claude to scan PDF before submit |
| R10 | OpenReview submission fails at deadline (system overload, file format) | Low-Medium | Critical | 5min slack between submit attempt and deadline; have PDF + supplementary pre-uploaded as draft |
| R11 | Akash falls behind schedule by Phase 3 (T+22:00) | Medium | High | If TEHR + recovery already passing at T+19:00, freeze claims, lock the data, prioritize writing over more analysis |
| R12 | Co-author appears mid-flight expecting collaboration | Low | Medium | Decide solo before T+0; if co-author confirmed, re-allocate writing in Phase 5 |

---

## 8. WRITING STRUCTURE — 7-PAGE LAYOUT

| § | Title | Pages | Load-bearing for |
|---|---|---|---|
| Abstract | (250w) | — | Reviewer first read; click factor |
| §1 | Introduction | 1.0 | Novelty positioning |
| §2 | Related Work | 0.75 | Differentiation from L-ICL / Fission-GRPO / AEGIS / Engländer / Czapla |
| §3 | Method | 0.75 | TEHR definition + intervention pseudocode + design rationale |
| §4 | Experimental Setup | 0.5 | Pre-registered decisions + reproducibility |
| §5 | Results | 1.25 | **The paper's spine — main table + recovery + regression** |
| §6 | Mechanism Analysis | 0.5 | Lexical-similarity correlation = the "theory hook" |
| §7 | Discussion + Limitations + Conclusion | 0.5 | Honest scope + future work |
| **Total** | | **5.25 + 0.5 figures + 0.5 abstract+title+meta = 7p** | |
| Appendix | Per-model tables, full protocol, all prompts, 7 pre-registered decisions | unlimited | Reproducibility |

### 8.1 Section-by-section load-bearing claims

- **Abstract**: must contain the one-sentence main result (§2.2) + 4 contributions (§2.3) + clean differentiation phrase ("L-ICL-shape result for tool-using agents on a phenomenon documented industrially but not academically").
- **§1**: hook with Czapla quote → "but no academic paper has measured, named, or fixed it" → 4 contributions enumerated → roadmap.
- **§5**: main table is `(model, TEHR_C0, recovery_C1, overhead, regression)` × 4 rows. Reviewer skim path = abstract + §5 main table. If §5 main table doesn't sell the paper, nothing else matters.
- **§6**: lexical-similarity scatter is the figure that distinguishes "measurement paper" from "characterization-with-mechanism paper." Cannot cut.

### 8.2 Anti-desk-reject defense moves (baked into draft)

- "Trivial intervention" attack → §3 design rationale + §6 mechanism + §5 multi-model recovery breadth answer it.
- "Frameworks already validate" attack → §1 cites Gate 1 verification + Czapla + Empirical Bug Study.
- "70-90% range too wide" attack → §5 reports per-model point estimates with 95% CIs; the range is across-model.
- "Where's the methodological contribution" attack → TEHR metric + intervention + lexical-similarity rule, all in §3 + §6.

---

## 9. SUBMISSION CHECKLIST

- [ ] PDF compiled, ≤7 pages excl. refs/appendix
- [ ] All 4 figures embedded with captions
- [ ] Main table in §5 complete with 95% CIs
- [ ] Anonymized: no "Akash", "IIT Patna", "vLLM", "CERN GSoC", real GitHub handle
- [ ] `pdfinfo paper.pdf` shows no author metadata
- [ ] Anonymous repo URL works in incognito
- [ ] Anonymous repo contains: code, prompts, raw CSV, plots, README
- [ ] Abstract on OpenReview matches paper abstract verbatim
- [ ] Title matches paper title
- [ ] Track selected: Main
- [ ] Supplementary file uploaded (appendix PDF or zip)
- [ ] Submitted ≥10 min before AoE deadline (timezone safety)
- [ ] Confirmation email screenshot saved

---

## 10. WHAT "DONE" LOOKS LIKE

A confirmation email from OpenReview at T+35:55 ± 5min, with:
- Paper title matching §2.1
- Track: Main
- 7-page PDF + appendix + anonymous repo
- All 4 contributions in §2.3 supported by experimental evidence in §5+§6
- All 7 pre-registered analysis decisions met
- Zero de-anonymization slips
- Backup plan (M1) untouched (means M2 path held)

If the M1 backup was triggered: same checklist with M1's title and intervention.

---

## 11. OPEN QUESTIONS FOR `/ultraplan` TO RESOLVE

1. Does Phase 0 pre-flight (4h tonight) leave enough buffer if API setup hits unexpected friction?
2. Should sleep 1 (8h) be cut to 6h to add 2h to Phase 4 (Day 1 analysis + abstract drafting)?
3. Is the §5 1.25-page allocation enough for 4 models × 2 benchmarks × 4 metrics, or should §5 be 1.5p at the cost of §2?
4. Should τ-bench be dropped if the main run runs over 3.5h, in favor of more BFCL N?
5. Is M3 (prefix predictability) a viable T+22:00 emergency pivot using already-collected traces, or is the hour budget too thin?
6. Should we pre-write a 1-paragraph "blame-Czapla" defense in case of late-breaking academic preemption (Risk R2)?
7. Is the lexical-similarity feature operationalized correctly (mean pairwise Levenshtein on tool name strings? token-level edit distance? embedding cosine?) — pin down before harness build.
8. What's the right CI presentation: 95% bootstrap on TEHR per model, or pooled across models? Reviewer expectation matters.

---

**Workspace**: `/home/akash/.claude/teams/research/scale-icml-2026-paper-plan/`
**Companion files**: SYNTHESIS_v3.md (canonical research synthesis), EVIDENCE/*.md (specialist outputs), v1+v2 retired in same directory.
