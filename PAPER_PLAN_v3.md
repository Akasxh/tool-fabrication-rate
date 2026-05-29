# PAPER_PLAN v3 — SCALE @ ICML 2026
*Refined v2 → v3 with: M5 local tier, Max-plan orchestration, parallel-agent execution architecture, cost-quality-gap headline.*

---

## 0. WHAT CHANGED FROM v2

| # | Change | Driver |
|---|---|---|
| Δ1 | **Model set: 5 models, 3 tiers, 2 vendor families + 1 open-source** (Sonnet 4.6, Haiku 4.5, GPT-4.1, GPT-4.1-mini, Qwen3-8B@MLX). Drop Gemini + Together-cloud Qwen3-72B. | Cost-quality story; SCALE alignment |
| Δ2 | **Headline reframed**: from "RVR recovers X% of failures" to **"RVR closes the cost-quality gap across capability tiers"** — Δ$-per-success becomes a primary metric. | SCALE workshop fit |
| Δ3 | **Cost architecture explicit**: Max-plan funds all orchestration agents (free); YC credits fund only model-as-subject API runs; M5 funds Tier-3 entirely. | Pass user constraint: "as low as possible" |
| Δ4 | **Parallel-agent execution plan added (§13)**: per-phase parallelization map with reviewer-merge pattern. | User request |
| Δ5 | **Local-tier harness component added** (MLX adapter for Qwen3-8B). Optional → core if MLX tool-calling format is reliable; falls back to API-only-4-models if not. | M5 hardware available |
| Δ6 | **§6 mechanism extended**: 3-tier scaling curve (RVR effect vs base capability) becomes a 5th figure. | Capability-scaling claim |

---

## 1. MISSION (unchanged)
Submit a Main Track 7-page paper to SCALE @ ICML 2026 introducing, quantifying, and recovering from the **Tool-Existence Hallucination** failure class in tool-using LLM agents.

---

## 2. THE PAPER

### 2.1 Working title
*"Registry-Visible Reprompting: Closing the Cost-Quality Gap in Tool-Using Agents Without Training"*

Backup if §6 scaling-curve fails: *"Registry-Visible Reprompting: A Training-Free Recovery for Tool-Hallucination Failures"*

### 2.2 One-sentence main result
*Across 5 models spanning 3 capability tiers and 2 vendor families plus an open-source 8B local model, Registry-Visible Reprompting (RVR) — a training-free re-prompt with the tool registry — recovers a pooled [X]% (95% CI [L, H]) of hallucination-induced failures, closing [Y]% of the cost-quality gap between small-tier and frontier-tier models on BFCL-v4 and τ-bench at <2% token overhead and ~[Z]× lower cost-per-success than the frontier baseline.*

### 2.3 Four claimed contributions
1. **Metric**: Tool-Existence Hallucination Rate (TEHR), formalized cross-benchmark, cross-tier, with per-call denominator. *(If Gate 0 finds prior usage, contribution becomes "we unify and quantify across tiers what was reported informally.")*
2. **Empirical characterization across 3 tiers**: TEHR baselines on 5 models (4 API + 1 local) × 2 benchmarks × 50 tasks ≈ 750 main runs + 360 probe runs.
3. **RVR intervention**: training-free, registry-list-in-reprompt; primary test C1 vs C0.5 (naive retry) — isolates the *content* of the re-prompt as the active ingredient.
4. **Cost-quality-gap closure**: scaling-curve evidence that RVR's pass-rate gain grows with the small-vs-frontier capability gap, yielding a practical recommendation (use small-tier + RVR over frontier baseline at ~[Z]× lower cost).

### 2.4 Why this clears workshop-caliber novelty
- Industry pain documented (Czapla); academic gap open.
- C1-vs-C0.5 design isolates the *content* of the re-prompt — not just "any retry."
- 3-tier scaling curve gives a *quantitative* efficiency claim, not a qualitative one — "RVR closes [Y]% of the gap" is concrete.
- Local-tier inclusion (Qwen3-8B on M5) demonstrates feasibility on consumer hardware — directly addresses SCALE's "efficient agents" theme.

---

## 3. HARD CONSTRAINTS

| Axis | Value |
|---|---|
| Workshop | SCALE @ ICML 2026 |
| Track | Main 7 pages |
| Deadline | 2026-04-28 AoE |
| Time budget | 36h wall-clock |
| **API cost ceiling** | **$30 paid (post-credits); ~$200-300 against credits** |
| **Orchestration cost** | **$0 — Claude Max plan funds all agent work** |
| **Local compute** | **M5 32 GB unified memory; MLX runtime; Qwen3-8B-Instruct (~5-6 GB at 4-bit)** |
| Models | 5: Sonnet 4.6, Haiku 4.5, GPT-4.1, GPT-4.1-mini, Qwen3-8B@MLX |
| Benchmarks | BFCL v4 multi-turn (primary) + τ-bench retail (secondary) |
| N per cell | 50 (BFCL), 25 (τ-bench) |
| Per-task cap | 120s wall-clock, 8 turns |
| Author | Solo unless co-author confirmed before T+0 |

### 3.1 Soft constraints
- No hardware/KV-cache/inference-systems framing.
- Cost-quality-gap framing is the load-bearing story.
- Statistical bar: paired McNemar w/ mid-p; Holm-Bonferroni across per-tier tests; TOST for non-inferiority; bootstrap 95% CIs.

---

## 4. EXPERIMENTAL DESIGN

### 4.1 RVR (the intervention)
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

### 4.2 Conditions

| Condition | Description |
|---|---|
| **C0** baseline | ReAct, framework default error on bad call |
| **C0.5** naive retry | On bad call: retry with original prompt + "previous failed, try again" — *no registry list* |
| **C1** RVR | Bad call → re-prompt with full registry list |

Primary test: C1 vs C0.5 (paired) on the strict subset of C0-failed-with-hallucination tasks.

### 4.3 Metrics
- **TEHR** per (model, benchmark, condition).
- **ΔPass(C1−C0.5)** — paired McNemar mid-p, Holm-Bonferroni across per-tier tests.
- **Token overhead** C1 vs C0.
- **Non-inferiority** on C0-passing strict subset, TOST margin 1pp.
- **Cost-per-success** = (input + output cost per task) / (pass rate). Reported per (model, condition).
- **Gap-closure ratio** = [PassRate(small + C1) − PassRate(small + C0)] / [PassRate(frontier + C0) − PassRate(small + C0)]. **The headline number.**
- **Probe ΔTEHR** (§6) by distractor type (near-name, synonym, random) × tier.

### 4.4 Pre-registered analysis decisions (locked at T+05:00)
1. TEHR on tool calls, not tasks.
2. Recovery requires a membership-rejection event in the C1 trace.
3. Non-inferiority via TOST (margin 1pp), not bare two-tailed.
4. N=50 BFCL + 25 τ-bench per (model × condition), pre-committed.
5. 2 prompt templates per benchmark.
6. τ-bench secondary; BFCL primary.
7. Recovery test = paired McNemar (mid-p) for C1 vs C0.5.
8. Holm-Bonferroni across per-tier tests.
9. Headline pooled across tiers for primary; per-model breakdowns directional.
10. Power target: ΔPass ≥ 20pp at 80% power; if hallucination events per cell <30, headline downgrades to "exploratory."
11. System failures (timeout/refusal/parse-fail) excluded from TEHR num+denom; reported as a robustness footnote.
12. **Local-tier (Qwen3-8B) results validated separately** — do not pool with API tiers in primary headline; report as a "feasibility" panel.

### 4.5 Compute + cost budget

| Phase | Runs | Cost (paid) | Wall-clock |
|---|---|---|---|
| Smoke test | 25 | <$2 | 15 min |
| Pilot | 200 (4 API × 25 × 2 cond) | $20-30 | 1.5 h |
| Main run (API) | 600 (4 API × (50+25) × 2 cond) | **$60-110 (against credits → ~$0)** | 2 h |
| Main run (M5/Qwen3) | 150 (1 model × (50+25) × 2 cond) | **$0** | 1.5 h (slower local) |
| §6 probe | 360 (30 × (4 API + 1 local) × 3 distractors → 450) | $40-60 → **~$0 with credits** | 50 min |
| Buffer / re-runs | 200 | $20 | 0.5 h |
| **Total** | **~1625** | **$0-30 paid, ~$120-200 against credits** | **~6 h compute** |

**Hard pre-commit at T+0**: confirm Anthropic credit ≥ $200, OpenAI credit ≥ $100. If either short, drop that vendor's small tier first.

---

## 5. 36-HOUR EXECUTION PLAN (with parallel-agent annotations)

Notation: `[A×N]` means N parallel agents; `[seq]` means sequential by Akash + main thread.

### Phase 0 — Pre-flight + Pre-writing (T+00:00 → T+05:00)

| T+ | Task | Mode |
|---|---|---|
| 00:00-00:15 | Confirm credit balances; create skeleton repo + LaTeX template | seq |
| 00:15-02:00 | **Launch 5 parallel agents** (Max-funded, free): Gate-0 lit sprint / Czapla+4 papers reading & §2 draft / §3 Method draft / §4 Setup draft / Harness architecture spec | **[A×5]** |
| 02:00-03:00 | Reviewer agent verifies each output; main thread integrates | [A×1 review + seq integrate] |
| 03:00-04:00 | MLX feasibility probe: install MLX, load Qwen3-8B 4-bit, run 5 BFCL tasks via tool-calling template; **decide CORE vs DROP for local tier** | seq |
| 04:00-05:00 | Lock pre-registered decisions; sign off on cut hierarchy; commit Phase 0 outputs | seq |

**Sleep 1**: T+05:00 → T+13:00 (8h).

### Phase 1 — Day 1: Gate 1 + Harness build (T+13:00 → T+15:30)

| T+ | Task | Mode |
|---|---|---|
| 13:00-13:30 | **Gate 1**: 5 models × 5 probe calls (25 calls) — verify hallucinations flow through | seq |
| 13:30-15:00 | **Launch 4 parallel adapter-build agents**: Anthropic adapter / OpenAI adapter / MLX adapter / BFCL+τ-bench loader | **[A×4]** |
| 15:00-15:30 | **Reviewer agent** runs parser unit tests on each; integrate; run 1 end-to-end task per provider | [A×1 review + seq] |

### Phase 2 — Day 1: Pilot + Gate 2 (T+15:30 → T+18:30)

| T+ | Task | Mode |
|---|---|---|
| 15:30-17:30 | Pilot dispatch: 200 runs, BFCL only, C0+C1 only. Live cost-meter dashboard | seq dispatch + monitor |
| 17:30-18:30 | **Gate 2**: TEHR ≥5% on ≥2 tiers? Decision logged | seq |

### Phase 3 — Day 1: Main Run + §6 Probe + Gate 3 (T+18:30 → T+22:30)

| T+ | Task | Mode |
|---|---|---|
| 18:30-21:30 | **Main run dispatched** (API tiers, ~2h wall-clock); **M5/Qwen3 dispatched in parallel** (1.5h wall-clock); **decompression block T+18:30-20:00** for Akash while runs execute | dispatch + monitor |
| 21:30-22:00 | §6 probe dispatched (50 min, parallel across providers) | dispatch |
| 22:00-22:30 | **Gate 3**: pooled ΔPass(C1−C0.5) ≥20pp? Gap-closure ratio ≥0.5? Non-inferiority TOST passes? | seq |

### Phase 4 — Day 1: Analysis + Plots + Numbers (T+22:30 → T+26:30)

| T+ | Task | Mode |
|---|---|---|
| 22:30-23:30 | **Launch 3 parallel stats agents**: TEHR+CIs / paired McNemar+Holm / TOST+probe ANOVA | **[A×3]** |
| 23:30-00:30 | **Launch 4 parallel plot agents**: TEHR bars / ΔPass bars / cost-per-success scatter / 3-tier scaling curve | **[A×4]** |
| 00:30-01:30 | Fill abstract template with numbers; fill §1 intro outline | seq |
| 01:30-02:30 | Buffer | seq |

**Sleep 2**: T+26:30 → T+32:30 (6h).

### Phase 5 — Day 2: Writing Marathon (T+32:30 → T+35:30)

§2/§3/§4/§7-template/abstract were drafted in Phase 0. Phase 5 = §1 + §5 + §6 only.

| T+ | Task | Mode |
|---|---|---|
| 32:30-32:45 | Probe figure (or skip) | seq |
| 32:45-33:45 | **§1 Introduction** (1p) — Akash writes; **parallel agent drafts an alt version** for cherry-picking phrases | seq + [A×1] |
| 33:45-34:45 | **§5 Results** (1.25p) — Akash writes from §5-template + numbers | seq |
| 34:45-35:15 | **§6 Mechanism** (0.5p) — probe + scaling curve + design rule | seq |
| 35:15-35:30 | Fill §7 placeholders | seq |

### Phase 6 — Day 2: Polish + Submit (T+35:30 → T+36:00)

| T+ | Task | Mode |
|---|---|---|
| 35:30-35:35 | Compile, fix overflow | seq |
| 35:35-35:45 | **Reviewer agent**: anonymization scan (deny-list grep, pdfinfo, pdftotext head, JSONL scrub verify) | [A×1] |
| 35:45-35:50 | OpenReview submit (PDF + supplementary zip; no GitHub) | seq |
| 35:50-36:00 | Confirm, screenshot, commit | seq |

---

## 6. HARD GATES

| Gate | T+ | PASS | PIVOT |
|---|---|---|---|
| **G0** | 00:30 | TEHR not already a named metric in BFCL/τ-bench, OR defendable as "unified across tiers" | Reword contribution #1 |
| **G0.5** | 04:00 | MLX + Qwen3-8B successfully runs ≥3/5 BFCL tasks with valid tool-calling format | Drop local tier; revert to 4-API model lineup |
| **G1** | 13:30 | Hallucinations flow through API on ≥2 of 5 models | Pivot to M1 |
| **G2** | 18:30 | Pilot TEHR ≥5% on ≥2 tiers | Pivot to M1 |
| **G3** | 22:30 | ΔPass(C1−C0.5) ≥20pp pooled AND gap-closure ratio ≥0.5 AND non-inferiority TOST passes | Soft-claim or characterization |

### 6.1 Backup M1 (unchanged from v1)
First-Hypothesis Anchoring. If triggered, scope shrinks to API-only 4 models.

### 6.2 Hard abort (unchanged)
Both M2 and M1 null → option A (M3 prefix-predictability classifier on collected traces) or option B (honest abort, target NeurIPS ENLSP).

### 6.3 Pre-committed cut hierarchy

| Trigger | Cut order |
|---|---|
| T+04:00 MLX fails | (1) Drop local tier; (2) Reframe headline to "4-model 2-tier" |
| T+18:30 cost overrun | (1) Drop GPT-4.1-mini (smallest cost-saving); (2) N: 50→30; (3) Drop τ-bench |
| T+21:30 main run unfinished | (1) Drop τ-bench partial; (2) Drop one API model (Haiku first if both Anthropic up); (3) Skip C0.5 (last resort) |
| T+22:30 ΔPass <20pp | (1) Headline → characterization; (2) Drop probe; (3) Reframe title |
| T+33:45 behind on §5 | (1) Per-model breakdowns → appendix; (2) §6 → 1-paragraph teaser; (3) §7 → 0.25p |
| T+35:30 PDF >7p | (1) Compress §2 to 0.5p; (2) Probe details → appendix |

### 6.4 Minimum Viable Paper
§1 + §3 + §5 (2 tiers × 1 benchmark × C0+C1) + §7. ~4 pages. Floor; below this triggers honest abort.

---

## 7. RISK REGISTER (additions only — see v2 for R1-R17)

| # | Risk | Like. | Imp. | Mitigation |
|---|---|---|---|---|
| **R18** | **MLX tool-calling on Qwen3-8B unreliable** | Med | Med | Gate 0.5 catches at T+04:00; drop local tier per cut hierarchy |
| **R19** | **3-tier story doesn't compose: small tiers fail at *parsing* not *existence*** | Med | High | Pilot will surface this; reframe to "2-tier API-only with optional local" |
| **R20** | **MLX runs slower than budgeted (1.5h estimate too tight)** | Med | Med | Run M5 in parallel with API runs; ≤30 min over budget = OK; >30 min = drop probe runs on local |
| **R21** | **Parallel agent outputs diverge in style/content** | Med | Low | Reviewer agent enforces style guide; main-thread final integration pass |

---

## 8. WRITING STRUCTURE — 7-PAGE LAYOUT (unchanged from v2)

§2/§3/§4/§7-template + abstract drafted in Phase 0; §1/§5/§6 in Phase 5.

---

## 9. SUBMISSION CHECKLIST (additions to v2)

- [ ] **MLX local-tier results clearly labeled "consumer hardware" with hardware spec footnoted**
- [ ] **Cost-per-success table shows YC-credit vs paid cost separately for transparency**
- [ ] **Scaling-curve figure (3 tiers) caption states "tier-comparison only; not a controlled scaling law"**

---

## 10. WHAT "DONE" LOOKS LIKE
OpenReview confirmation at T+35:55 ± 5min with: title §2.1, Main track, 7-page PDF + appendix + supplementary zip, all 4 contributions supported, all 12 pre-registered decisions met, zero anonymization leaks, **paid cost ≤ $30**.

---

## 11. OPEN QUESTIONS FOR T+0 SIGN-OFF

1. **Credits redeemed?** Anthropic ≥$200 + OpenAI ≥$100 confirmed at console — yes/no.
2. **MLX feasibility verdict?** Decided at G0.5 (T+04:00) — local tier in or out.
3. **Solo vs co-author?** If co-author exists, Phase 5 writing parallelism doubles.
4. **arXiv concurrent posting?** SCALE call read in Phase 0 — defer or post.

---

## 12. WORKSPACE STRUCTURE

```
/Users/cero/Desktop/PROJECTS/icml/
├── PAPER_PLAN.md          # v1 (retained)
├── PAPER_PLAN_v2.md       # v2 (retained)
├── PAPER_PLAN_v3.md       # this file (canonical)
├── PHASE0/
│   ├── prior_art.md       # Gate 0 lit sprint output
│   ├── related_work_notes.md
│   └── mlx_feasibility.md # Gate 0.5 result
├── paper/
│   ├── main.tex           # ICML 2026 template
│   └── sections/
│       ├── 02_related_work.tex   # pre-written Phase 0
│       ├── 03_method.tex          # pre-written Phase 0
│       ├── 04_setup.tex           # pre-written Phase 0
│       ├── 07_limitations.tex     # template Phase 0
│       └── (01, 05, 06 written Phase 5)
├── harness/
│   ├── HARNESS_SPEC.md    # architecture (Phase 0)
│   ├── adapters/          # per-provider (Phase 1)
│   ├── bench_loaders/
│   ├── intervention/      # rvr.py, naive_retry.py
│   ├── stats/
│   └── trace_logger/
├── results/               # JSONL traces
└── figures/               # 4-5 PDFs
```

---

## 13. PARALLEL-AGENT EXECUTION PLAN (NEW)

### 13.1 Agent roles

| Role | Subagent type | When used | Cost |
|---|---|---|---|
| **Lit-explorer** | Explore (very thorough) | Phase 0 Gate-0 | Max plan |
| **Section-writer** | general-purpose | Phase 0, Phase 5 | Max plan |
| **Adapter-builder** | general-purpose | Phase 1 | Max plan |
| **Stats-builder** | general-purpose | Phase 4 | Max plan |
| **Plot-builder** | general-purpose | Phase 4 | Max plan |
| **Architect** | Plan | Phase 0, Phase 1 entry | Max plan |
| **Reviewer** | superpowers:code-reviewer | After every parallel batch | Max plan |

### 13.2 Reviewer-merge pattern
1. Spawn N independent agents on disjoint files / subtasks.
2. Each writes to its designated file path with a defined output spec.
3. **Reviewer agent** reads all N outputs + the spec; runs unit tests where applicable; produces a verdict file `REVIEW_<batch>.md` listing pass/fail/diffs-requested.
4. Main thread (Akash + me) integrates only the passing outputs; failed outputs get one re-spawn with feedback, then escalate.

### 13.3 Phase-level parallelism budget

| Phase | # parallel agents | Speedup vs sequential | Why |
|---|---|---|---|
| 0 | 5 + 1 reviewer | ~3× | All independent docs |
| 1 | 4 + 1 reviewer | ~2.5× | Per-provider adapters disjoint |
| 4 | 3 stats + 4 plots + 1 reviewer | ~3× | Disjoint analyses |
| 5 | 2 (alt-draft for cherry-pick) | ~1.2× | Limited — single-author voice required |

### 13.4 Hard rules
- **No agent makes a Gate decision.** Akash + main thread only.
- **No agent calls a paid API.** All paid API calls are dispatched by the harness Akash runs, not by spawned agents.
- **Every agent output gets reviewed before integration** — no merge-on-trust.
- **Background-mode default**: agents run in background so main thread stays responsive to Akash.

---

**Predecessors**: PAPER_PLAN.md (v1), PAPER_PLAN_v2.md (v2). v3 is canonical.
