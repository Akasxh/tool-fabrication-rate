# PAPER_PLAN v2 — SCALE @ ICML 2026 Submission
*Refined through 10 critique passes against PAPER_PLAN.md (v1).*

**Slug**: scale-icml-2026-paper-plan
**Author**: Akash (solo, unless co-author confirmed before T+0)
**Drafted**: 2026-04-27
**Status**: REFINED — every change traceable to a numbered pass below.

---

## 0. WHAT CHANGED FROM v1 (executive summary)

| # | Change | Driver |
|---|---|---|
| C1 | **Title dropped "2-line" gimmick** → *"Registry-Visible Reprompting (RVR): Recovering Tool-Hallucination Failures Without Training"* | Pass 3 |
| C2 | **Added condition C0.5 (naive retry)** as primary comparator; intervention is now C1 vs C0.5, not C1 vs C0 | Passes 3, 5 |
| C3 | **Budget 5×: $30-45 → $200-300**; cut N from 100 → 50; dropped o4; capped turns at 8 | Pass 2 |
| C4 | **§6 lexical-similarity correlation REPLACED with a 360-run controlled probe** (near-name + synonym + random distractors) | Pass 6 |
| C5 | **Pre-write §2/§3/§4/§7-template/abstract-template in Phase 0** to make Phase 5 tractable | Pass 9 |
| C6 | **Gate 0 added** (30-min literature sprint to verify TEHR ≠ BFCL `incorrect_function_name`) | Pass 4 |
| C7 | **Pre-committed cut hierarchy** (no decisions invented under fatigue) + explicit MVP definition | Pass 10 |
| C8 | **Pre-registered statistical analysis upgraded**: paired McNemar + TOST for non-inferiority + Holm-Bonferroni; pooled-across-models headline | Pass 5 |
| C9 | **Operational hardening**: 120s per-task timeout, refusal as 4th outcome, per-10-task checkpoints, parser unit tests | Pass 8 |
| C10 | **Anonymization hardening**: JSONL scrub script, OpenReview-only repo (no GitHub), arXiv deferred to post-decision | Pass 7 |
| C11 | **Schedule realism**: 14h continuous block split, 2h decompression while main run dispatches, Sleep 2 = 6h | Pass 1 |

---

## 1. MISSION (unchanged)

Submit a Main Track 7-page paper to **SCALE @ ICML 2026** that introduces, quantifies, and recovers from the **Tool-Existence Hallucination** failure class in tool-using LLM agents — documented in industry (Czapla, Feb 2026) but not yet addressed academically.

---

## 2. THE PAPER

### 2.1 Working title (CHANGED — Pass 3)
*"Registry-Visible Reprompting: Recovering Tool-Hallucination Failures in Frontier Agents Without Training"*

Backup title (if §6 probe fails): *"Schema-Aware Recovery for Tool-Using Agents: A Multi-Model Empirical Study"*

### 2.2 One-sentence main result (CHANGED — Passes 3, 5)
*Across 4 frontier models on BFCL-v4 and τ-bench, Registry-Visible Reprompting (RVR) — a training-free inference-time fix that re-prompts the model with the registry list whenever it calls a non-existent tool — recovers a pooled [X]% (95% CI [L, H]) of hallucination-induced failures, beating naive retry by Δ[Y]pp (paired McNemar p<0.01) at <2% token overhead and within ±1pp non-inferior pass rate on baseline-passing tasks (TOST, margin 1pp).*

The headline is **pooled across models**, not per-model; per-model breakdowns appear with appropriate caveats (Pass 5).

### 2.3 Four claimed contributions (REWORDED — Passes 3, 4)
1. **Metric**: Tool-Existence Hallucination Rate (TEHR) — formalized cross-benchmark with per-call denominator. *If Gate 0 finds prior usage in BFCL/τ-bench, contribution becomes "we unify and quantify what was reported informally."*
2. **Empirical characterization**: TEHR baselines on 4 frontier models × 2 benchmarks × 50 tasks (~800 runs) + 360 controlled-probe runs.
3. **Intervention (RVR)**: training-free, registry-list-in-reprompt, with measured Δ over naive retry, overhead, and non-inferiority on baseline-passing tasks.
4. **Mechanism via controlled probe**: causal evidence that near-name and semantic-cousin distractors increase TEHR; prescriptive design rule for tool-set hygiene.

### 2.4 Why this clears workshop-caliber novelty
- Industry pain documented (Czapla), academic gap open.
- C1-vs-C0.5 design isolates the *content* of the re-prompt as the active ingredient — not just "any retry works."
- Controlled probe in §6 gives a **causal** mechanism claim, not a fragile correlation.
- Differentiation paragraph against L-ICL, Fission-GRPO, AEGIS, AutoTool pre-written in Phase 0.

---

## 3. HARD CONSTRAINTS

| Axis | Value (changed values **bold**) |
|---|---|
| Workshop | SCALE @ ICML 2026 |
| Track | Main 7 pages |
| Deadline | 2026-04-28 AoE (~2026-04-29 12:00 UTC) |
| Time budget | 36h wall-clock |
| Format | ICML 2026 LaTeX, double-blind |
| Submission | OpenReview (supplementary attachment for code; **no GitHub**) |
| Hardware | MacBook M5, 32 GB |
| **API budget** | **$200-300 (was $25-50)** — confirm credit balance T+0 |
| **Models** | **Claude Sonnet 4.6 + Haiku 4.5 (tier comparison), GPT-4.1 (no o4), Gemini 2.5 Pro, Qwen3-72B** |
| Benchmarks | BFCL v4 multi-turn (primary) + τ-bench retail (secondary) |
| **N per cell** | **50 tasks (was 100)** |
| **Per-task wall-clock cap** | **120s, max 8 turns** |
| Author | Solo unless co-author confirmed before T+0 |

### 3.1 Soft constraints / preferences
- No hardware/KV-cache/inference-systems framing.
- No audit/measurement-only framing.
- Total runs: **800 main + 360 probe + 200 pilot = ~1360** (was ~2000).
- Statistical bar: paired McNemar for recovery; TOST (margin 1pp) for non-inferiority; Holm-Bonferroni across 4 models; bootstrap 95% CIs throughout.

---

## 4. EXPERIMENTAL DESIGN

### 4.1 The intervention (RVR) — Pass 3 reframe

**Pseudocode (honestly ~7 lines, no "2-line" claim):**

```python
def rvr(agent_msg, registry):
    proposed_tool = parse_tool_call(agent_msg)
    if proposed_tool.name not in registry:
        feedback = (
            f"Tool '{proposed_tool.name}' is not in the registry.\n"
            f"Available tools: {sorted(registry.keys())}.\n"
            f"Choose one of these or explain why none apply."
        )
        return Action.RE_PROMPT(feedback)   # at most one retry
    return Action.EXECUTE(proposed_tool)
```

**Design choices defended in §3:**
- Registry list in re-prompt (vs "tool not found, retry"): isolated as the active ingredient by the C0.5 comparison.
- Max 1 retry: bounds compute, matches production retry budgets.
- Training-free: orthogonal to RL methods (Fission-GRPO).
- Constrained-decoding analog at the *message* level — same effect without logit access.

### 4.2 Conditions (CHANGED — added C0.5)

| Condition | Description | Purpose |
|---|---|---|
| **C0** baseline | ReAct with framework's default error on bad tool call | Establish TEHR |
| **C0.5** naive retry | On bad tool call, retry with original prompt + "previous tool call failed, try again" — **no registry list** | Active comparator: isolates whether *retry alone* explains gain |
| **C1** RVR | Bad tool call → re-prompt with full registry list | The intervention |

Primary comparison: **C1 vs C0.5** on the strict subset of C0-failed tasks containing a hallucinated tool call.

### 4.3 Metrics (CHANGED — Pass 5)

| Metric | Definition | Test |
|---|---|---|
| TEHR | (hallucinated tool calls) / (total tool calls), per model, per benchmark, under C0 | Bootstrap 95% CI |
| ΔPass (RVR vs naive) | Pass rate(C1) − Pass rate(C0.5) on hallucination-tagged C0-failed tasks | Paired McNemar (mid-p), Holm-Bonferroni across 4 models |
| Token overhead | Mean Δtokens(C1 − C0) per task | Reported, target <2% |
| Non-inferiority on C0-passing | Pass rate(C1) ≥ Pass rate(C0) − 1pp on C0-passing strict subset | TOST (margin 1pp) |
| Probe ΔTEHR (§6) | TEHR change from injecting near-name vs synonym vs random distractor | One-way ANOVA + post-hoc on the 3 distractor types |

### 4.4 Pre-registered analysis decisions (EXPANDED — Pass 5)

Locked before looking at full data. **11 items (was 7)**:

1. TEHR computed on tool calls, not tasks — denominator clarity.
2. Recovery requires the C1-passing trace to contain a membership-rejection event.
3. Quality regression measured on strict C0-passing subset, with **TOST non-inferiority** (margin 1pp), not bare two-tailed.
4. **N=50** tasks per benchmark per model (was 100); pre-committed.
5. 2 prompt templates per benchmark — robustness check.
6. τ-bench secondary; BFCL primary.
7. Recovery test is **paired McNemar (mid-p) for C1 vs C0.5**, not C1 vs zero.
8. **Holm-Bonferroni** correction across 4 per-model tests.
9. **Headline pooled across models**; per-model breakdowns directional.
10. **Power target**: ΔPass ≥ 20pp at 80% power. If hallucination events per cell <30, headline drops to "exploratory."
11. **System failures (timeout/refusal) excluded** from TEHR num+denom; reported separately as a robustness footnote.

### 4.5 Compute + cost budget (REVISED — Pass 2)

| Phase | Runs | Cost | Wall-clock |
|---|---|---|---|
| Pre-flight smoke test | 20 | <$2 | 15 min |
| Pilot (Gate 2 input) | 200 (4 × 25 × 2) | $20-40 | 1.5 h |
| Main run (Gate 3 input) | 800 (4 × 2 × 50 × 2) | $100-180 | 3 h |
| **§6 controlled probe** | **360 (30 × 4 × 3)** | **$30-50** | **45 min** |
| Re-runs / API failure recovery | up to 200 | up to $30 | 0.5 h budgeted |
| **Total** | **~1580** | **$180-300** | **5.75 h** |

**Pre-commit at T+0**: confirm credit balance ≥$300 across providers. Instrument the harness with a **token-cost meter that aborts at 90% of budget**.

---

## 5. 36-HOUR EXECUTION PLAN (RESHAPED — Passes 1, 9)

Cumulative T+H format. **Wall-clock vs task-clock noted.** Total: ~24h work + 12h sleep across 36h.

### Phase 0 — Pre-flight + Pre-writing (T+00:00 → T+05:00)

| T+ | Task | Deliverable |
|---|---|---|
| 00:00-00:30 | **Gate 0**: 30-min literature sprint. Grep BFCL/τ-bench/ToolBench/Gorilla papers for `function_name`, `hallucinat`, `existence`, `unknown_tool`. Write `prior_art.md` | Decision: contribution #1 wording |
| 00:30-01:30 | Verify 4 API keys; confirm $300 credit; install deps; smoke-test 1 call/provider | All 4 respond; budget confirmed |
| 01:30-02:30 | Pull 20 BFCL + 10 τ-bench samples; manually inspect for unprompted hallucinations across 4 models | ≥1 hallucination observed → Gate 1 dry-run green |
| 02:30-03:30 | Clone ICML 2026 LaTeX template; **pre-write §3 Method + §4 Setup + §7 limitations template + abstract template** (blanks for numbers) | Skeleton compiles to 4-page placeholder PDF |
| 03:30-04:30 | Read & note: Czapla, L-ICL (2602.00276), Empirical Bug Study (2602.21806), Engländer (2604.17609); **pre-write §2 Related Work (5 paragraphs)** | `related_work.tex` drafted |
| 04:30-05:00 | Sign off on **pre-committed cut hierarchy** (§6.3 below); commit it; do not re-litigate | Cut-hierarchy locked |

**Sleep 1**: T+05:00 → T+13:00 (8h, non-negotiable).

### Phase 1 — Day 1: Gate 1 + Harness (T+13:00 → T+15:30)

| T+ | Task | Deliverable |
|---|---|---|
| 13:00-13:45 | **GATE 1**: 4 models × 5 probes (20 calls) — does any framework intercept at API level vs let hallucinations through? | M2 GO / M1 PIVOT |
| 13:45-15:00 | Build `bench_tool_hallucination.py`: BFCL+τ-bench loaders, dispatch, **120s per-task timeout**, **refusal detection**, **per-10-task checkpoint**, token-cost meter, **parser unit tests** for each provider | End-to-end 1-task run on each provider |
| 15:00-15:30 | Build `rvr.py` (intervention) + `naive_retry.py` (C0.5) | C0/C0.5/C1 each run 1 task end-to-end |

### Phase 2 — Day 1: Pilot + Gate 2 (T+15:30 → T+18:30)

| T+ | Task | Deliverable |
|---|---|---|
| 15:30-17:30 | Pilot: 4 models × 25 tasks × 2 conditions (BFCL only, C0+C1, skip C0.5 for pilot) = 200 runs. Live dashboard on per-provider success rate | Pilot CSV |
| 17:30-18:30 | **GATE 2**: TEHR ≥5% on ≥2 of 4 models? Decision: scale-up / soft-claim / pivot to M1 | Decision logged |

### Phase 3 — Day 1: Main Run + Decompression + Gate 3 (T+18:30 → T+22:30)

| T+ | Task | Deliverable |
|---|---|---|
| 18:30-21:30 | **Main run dispatched** (3h wall-clock): 800 runs across 3 conditions (C0, C0.5, C1). **Decompression block T+18:30-20:30** while main run executes — eat, walk, prep figure templates. T+20:30-21:30 monitor & spot-fix | Full results CSV + checkpoints |
| 21:30-22:00 | **§6 probe run dispatched** (45 min): 360 runs (30 tasks × 4 models × 3 distractor types) | Probe CSV |
| 22:00-22:30 | **GATE 3**: ΔPass(C1 − C0.5) ≥20pp on ≥2 of 4 models pooled? + non-inferiority TOST passes? | Decision: headline / soft / cut |

### Phase 4 — Day 1: Analysis + Plots + Numbers (T+22:30 → T+26:30)

| T+ | Task | Deliverable |
|---|---|---|
| 22:30-23:30 | Stats: bootstrap CIs on TEHR, paired McNemar with Holm-Bonferroni on ΔPass, TOST on non-inferiority, ANOVA on probe | `stats.json` |
| 23:30-00:30 | **Generate 4 figures**: (1) TEHR baseline bars, (2) ΔPass(C1−C0.5) bars with CIs, (3) overhead vs benefit scatter, (4) probe ΔTEHR by distractor type | 4 PDFs |
| 00:30-01:30 | **Fill in abstract template** with numbers; **fill in §1 intro outline** | `abstract.tex` final, intro outline |
| 01:30-02:30 | Buffer / catch-up | — |

**Sleep 2**: T+26:30 → T+32:30 (**6h, was 5h** — Pass 1).

### Phase 5 — Day 2: Writing Marathon (T+32:30 → T+35:30)

Reduced scope because §2/§3/§4/§7-template were drafted in Phase 0.

| T+ | Task | Deliverable |
|---|---|---|
| 32:30-32:45 | Lexical-similarity scatter (or skip if probe-only § 6) | Optional figure |
| 32:45-33:45 | **§1 Introduction** (1p): hook with Czapla → academic gap → 4 contributions → roadmap | §1 |
| 33:45-34:45 | **§5 Results** (1.25p): main table + recovery + overhead + non-inferiority + per-model breakdown | §5 — load-bearing |
| 34:45-35:15 | **§6 Mechanism (probe)** (0.5p): 3-distractor results + design rule | §6 |
| 35:15-35:30 | **Fill §7 placeholders** with which-cuts-applied + final limitations | §7 |

### Phase 6 — Day 2: Polish + Submit (T+35:30 → T+36:00)

| T+ | Task | Deliverable |
|---|---|---|
| 35:30-35:40 | LaTeX compile, fix overflow to 7p; appendix has full per-model + 11 pre-registered decisions | PDF ≤7p |
| 35:40-35:50 | **Anonymize + scrub**: `pdfinfo`, `pdftotext | head`, JSONL deny-list grep, supplementary zip | Zero leaks |
| 35:50-35:55 | OpenReview submit (no GitHub): paper PDF + supplementary zip | Confirmation |
| 35:55-36:00 | Screenshot, commit local repo, exhale | Done |

---

## 6. HARD GATES + DECISION TABLE

| Gate | T+ | PASS | PIVOT |
|---|---|---|---|
| **G0** | 00:30 | TEHR not already a named metric, OR can be defended as "unified cross-benchmark" | Reword contribution #1; do not claim novelty |
| **G1** | 13:45 | ≥1 hallucinated tool name flows through API on ≥2 of 4 models | Pivot to M1 (anchoring) |
| **G2** | 18:30 | TEHR ≥5% on ≥2 of 4 models in pilot | Pivot to M1 |
| **G3** | 22:30 | ΔPass(C1−C0.5) ≥20pp on pooled-models AND non-inferiority TOST passes | Soft-claim or characterization-only |

### 6.1 Backup plan M1 (unchanged from v1)
First-Hypothesis Anchoring on Agent Trajectories with mandatory differentiation vs Engländer (2604.17609).

### 6.2 Hard abort threshold (unchanged)
If both M2 and M1 null by T+22:00: option A = M3 prefix-predictability classifier on collected traces; option B = honest abort, target NeurIPS ENLSP.

### 6.3 Pre-committed cut hierarchy (NEW — Pass 10)

Sign off at T+05:00. Do not re-litigate under fatigue.

| Trigger | Cut order |
|---|---|
| T+18:30 cost overrun | (1) Drop Haiku tier; (2) N: 50→30; (3) Drop τ-bench |
| T+21:30 main run unfinished | (1) Drop τ-bench partials; (2) Drop one model (Qwen3 first); (3) Skip C0.5 (kills primary test — last resort) |
| T+22:30 ΔPass <20pp | (1) Headline becomes "characterization with intervention"; (2) Drop probe; (3) Reframe title to backup |
| T+26:30 figures incomplete | (1) §6 fig → table; (2) Overhead fig → text; (3) Use soft-claim abstract |
| T+33:45 behind on §5 | (1) Per-model breakdowns → appendix; (2) §6 → 1-paragraph teaser; (3) §7 → 0.25p |
| T+35:30 PDF >7p | (1) Compress §2 to 0.5p; (2) Probe details → appendix; (3) Inline citations |

### 6.4 Minimum Viable Paper (NEW — Pass 10)

**MVP = §1 + §3 + §5 (3 models × 1 benchmark × C0+C1) + §7.**
4 sections, ~4 pages, no §6 mechanism, no τ-bench, no probe. Ugly but submittable. **This is the floor; anything below this triggers honest abort (no submission), not "ship something."**

---

## 7. RISK REGISTER (EXPANDED)

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Frameworks intercept hallucinations at API level | Low | Critical | Gate 1 |
| R2 | Czapla → academic preempt before SCALE review | Low-Med | High | Submit early; pre-write differentiation paragraph |
| R3 | TEHR <5% across all models | Med | Critical | Gate 2; pivot M1 |
| R4 | ΔPass(C1−C0.5) <20pp | Med | High | Gate 3; soft-claim or characterization |
| R5 | Probe ΔTEHR null | Med | Med | Drop §6 to teaser; paper still stands on §3-5 |
| R6 | API rate limits / throttling | Med | Med | 0.5h buffer; per-provider live dashboard; staggered dispatch |
| R7 | Provider mid-run outage | Low-Med | High | Per-10-task checkpoints; resume on crash |
| R8 | Writing compression unrealistic | High → **Med** | High | **Pass 9 mitigation: pre-write §2/§3/§4/§7-template/abstract in Phase 0** |
| R9 | De-anonymization leak | Med | Critical | **Pass 7: JSONL scrub script, OpenReview-only repo, deny-list grep, pdftotext head** |
| R10 | OpenReview submit fails at deadline | Low-Med | Critical | 5min slack; pre-uploaded draft |
| R11 | Akash falls behind by T+22:00 | Med | High | **Pass 10: cut hierarchy pre-committed** |
| R12 | Co-author appears mid-flight | Low | Med | Decide solo before T+0 |
| **R13 NEW** | **Budget overrun (5× cost)** | **Med** | **Critical** | **Pass 2: $300 ceiling, token-cost meter, abort at 90%** |
| **R14 NEW** | **Per-task hang eats run budget** | **Med** | **Med** | **Pass 8: 120s timeout, refusal/system_failure as 4th outcome** |
| **R15 NEW** | **TEHR is BFCL `incorrect_function_name` in disguise** | **Med** | **High** | **Pass 4: Gate 0 literature sprint; reword contribution if needed** |
| **R16 NEW** | **N=50 + low TEHR → underpowered headline** | **Med** | **High** | **Pass 5: pooled-across-models headline; per-model is directional** |
| **R17 NEW** | **Statistical critique** (multiple comparisons, wrong test for non-inferiority) | **Med** | **Med** | **Pass 5: Holm-Bonferroni, TOST, paired McNemar with mid-p** |

---

## 8. WRITING STRUCTURE (UPDATED)

| § | Title | Pages | Drafted in |
|---|---|---|---|
| Abstract | (250w) | — | Phase 0 (template) → Phase 4 (numbers) |
| §1 | Introduction | 1.0 | Phase 5 |
| §2 | Related Work | 0.75 | **Phase 0** (results-independent) |
| §3 | Method (TEHR + RVR + design) | 0.75 | **Phase 0** (results-independent) |
| §4 | Experimental Setup | 0.5 | **Phase 0** (results-independent) |
| §5 | Results | 1.25 | Phase 5 (numbers from Phase 4) |
| §6 | Mechanism (controlled probe) | 0.5 | Phase 5 |
| §7 | Discussion + Limitations | 0.5 | **Phase 0 template** → Phase 5 fill-in |
| Appendix | per-model tables, 11 pre-reg decisions, prompts | unlimited | Phase 6 |

**Phase 5 net new prose: §1 + §5 + §6 = 2.75 pages in 3h** — feasible.

### 8.1 Anti-desk-reject defense moves
- "Trivial intervention" → §3 design rationale + §6 causal probe + C1-vs-C0.5 isolation answer it.
- "BFCL already does this" → Gate 0 result + §2 unification framing.
- "Statistically underpowered" → pooled headline + Holm-Bonferroni + power-target footnote (Pass 5).
- "70-90% range too wide" → no longer claimed; replaced with pooled CI.
- "Where's the methodological contribution" → TEHR cross-benchmark formalization + RVR isolation design + controlled probe.

---

## 9. SUBMISSION CHECKLIST (EXPANDED — Pass 7)

- [ ] PDF compiled, ≤7 pages excl. refs/appendix
- [ ] All 4 figures embedded with captions
- [ ] Main table in §5 with bootstrap CIs + Holm-Bonferroni p-values
- [ ] Anonymized: no "Akash", "IIT Patna", "vLLM", "CERN GSoC", real GitHub handle
- [ ] **`pdfinfo paper.pdf` shows no metadata**
- [ ] **`pdftotext paper.pdf - | head -50` clean**
- [ ] **JSONL scrub script ran on all traces; deny-list grep returns 0**
- [ ] **OpenReview supplementary zip uploaded; no GitHub repo linked**
- [ ] **arXiv preprint deferred until decision (per SCALE policy check in Phase 0)**
- [ ] Abstract on OpenReview matches paper abstract verbatim
- [ ] Title matches paper title
- [ ] Track selected: Main
- [ ] Submitted ≥10 min before AoE deadline
- [ ] Confirmation email screenshot saved

---

## 10. WHAT "DONE" LOOKS LIKE

OpenReview confirmation at T+35:55 ± 5min with:
- Title: §2.1
- Track: Main
- 7-page PDF + appendix + supplementary zip
- All 4 contributions in §2.3 supported by §5+§6
- All 11 pre-registered decisions met
- Zero anonymization leaks
- Cost ≤ $300

If MVP-only (Pass 10): same checklist, soft-claim title, characterization paper.

---

## 11. OPEN QUESTIONS — RESOLVED BY THE 10 PASSES

| v1 Q | v2 Resolution |
|---|---|
| Q1: Phase 0 4h enough? | **NO**, expanded to 5h with pre-writing (Pass 9) |
| Q2: Cut Sleep 1 to 6h? | **NO**, keep 8h; pre-writing solves the writing-time crunch (Pass 1, 9) |
| Q3: §5 1.25p enough? | **YES**, with per-model breakdowns to appendix per cut hierarchy (Pass 10) |
| Q4: Drop τ-bench under load? | **YES**, in cut hierarchy at T+18:30 cost trigger or T+21:30 time trigger (Pass 10) |
| Q5: M3 viable as T+22:00 emergency? | **YES** for honest abort fallback only (option A, kept) |
| Q6: Pre-write Czapla-defense? | **YES**, in §2 Related Work paragraph drafted Phase 0 (Pass 4, 9) |
| Q7: Lexical similarity operationalization? | **DROPPED**; replaced with controlled probe (3 distractor types: near-name, synonym, random) — causal not correlational (Pass 6) |
| Q8: CI presentation? | **Pooled-across-models headline + per-model directional + Holm-Bonferroni** (Pass 5) |

---

## 12. NEW OPEN QUESTIONS (raised by v2)

1. **Credit-balance check at T+0**: do we actually have $300 across providers? If not, cut N to 30 and accept underpowered headline.
2. **Co-author**: a single confirmed co-author who can run the writing pass while Akash runs experiments doubles throughput. **This is the highest-leverage decision in the next 2 hours.**
3. **SCALE arXiv policy**: read the call carefully in Phase 0 for concurrent-arXiv rules.
4. **Probe distractor design**: how exactly are "near-name" distractors generated? — propose: 1 char-swap, 1 prefix-extension, 1 suffix-extension per task; "synonym" via embedding cos-sim ≥0.7 on tool-description. Specify before harness build.

---

**Workspace**: `/Users/cero/Desktop/PROJECTS/icml/`
**Predecessor**: `PAPER_PLAN.md` (v1, retained for diff).
