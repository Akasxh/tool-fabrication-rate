# PAPER_PLAN v3.1 — SCALE @ ICML 2026
*v3 → v3.1: contribution #1 reframed for API-Bank precedent; Czapla date corrected; Engländer terminology corrected; Grok-as-deferred 6th model added; credit budget updated to ~$5,500 redeemed.*

**This file is canonical for the BASE plan.** Post-R1-review corrections live in `ADDENDUM_R1.md` — read both files together; ADDENDUM overrides any conflict. Track: Main 7p (confirmed). v3.md retained for diff trail. PAPER_PLAN.md (v1) and PAPER_PLAN_v2.md retained as snapshots.

---

## 0. WHAT CHANGED FROM v3

| # | Change | Driver |
|---|---|---|
| Δ1 | **Contribution #1 reframed** from "we name a new metric" to "we isolate registry-membership at the per-call denominator, disaggregating prior holistic measures." Cite API-Bank (Li et al., EMNLP 2023) and RelyToolBench (Cao et al., ICML 2025) as precedents in §2. | Phase-0 lit-sprint found API-Bank's "API Hallucination" metric is ~80% equivalent to TEHR. |
| Δ2 | **Czapla blog date corrected**: 2026-01-20 (URL slug confirms; title "The Unauthorized Tool Call Problem"). Was incorrectly stated as Feb 2026 in v3. | Lit-sprint output. |
| Δ3 | **Engländer paper framing corrected**: actual title "Agents Explore but Agents Ignore: LLMs Lack Environmental Curiosity"; framing is "environmental curiosity deficit," not "first-hypothesis anchoring" as v3 claimed. M1 backup plan must be re-described. | Phase-0 source-reading agent. |
| Δ4 | **Grok added as deferred 6th model**. Akash redeemed $2,500 xAI credits. Phase-1 spawns a Grok adapter agent in parallel; final inclusion decision deferred to Gate 2 (T+18:30). xAI API is OpenAI-compatible → adapter mostly mirrors OpenAIAdapter. | Akash credit availability + Czapla-vendor-coverage argument. |
| Δ5 | **Total redeemed credits ~$5,500** (OpenAI $2,500 + Anthropic $500 + xAI $2,500). Out-of-pocket budget: $0. Cost meter still enforced as a safety belt. | Akash credit redemption. |
| Δ6 | **§2 §2.4 anti-desk-reject defense updated**: "TEHR is API-Bank's API Hallucination renamed" answered by per-call denominator + cross-tier evaluation + targeted intervention. | Anticipating reviewer attack. |
| Δ7 | **G0.5 PASSED 2026-04-27**: MLX + `mlx-community/Qwen3-8B-4bit` (NOT `-Instruct-4bit`) ran 3/3 fixtures cleanly; ~27 tok/s; 5.4 GB RSS; verdict CORE. Local tier stays in. Adapter MUST pass `enable_thinking=False`. | MLX feasibility probe verdict. |
| Δ8 | **BFCL JSON-Schema normalization required**: BFCL writes `"type": "dict"` instead of `"type": "object"`; loader applies `_normalize_bfcl_schema` before yielding. All 3 adapters would reject otherwise. | Dataset acquisition agent discovery. |
| Δ9 | **τ-bench user simulator routed to Haiku 4.5** (not GPT-4o default). Saves paid spend; ~$3-5 against Anthropic credits. | Cost-routing decision. |
| Δ10 | **ICML 2026 author kit downloaded** to `paper/icml2026/`; `\usepackage{icml2026}` (no option) for blind review, `[preprint]` for arXiv, `[accepted]` for camera-ready. arXiv concurrent posting **allowed**. | SCALE-call-audit verdict. |
| Δ11 | **Mandatory LLM/agent usage disclosure section** required by SCALE call — must be added to paper before submit (does not count toward 7-page limit). | SCALE call audit. |

---

## 1. MISSION (unchanged)
Submit a Main Track 7-page paper to SCALE @ ICML 2026 introducing, quantifying, and recovering from the **Tool-Existence Hallucination** failure class in tool-using LLM agents.

---

## 2. THE PAPER

### 2.1 Working title (R2.5 rewrite — phenomenon-first, number-front)
*"Tool-Existence Hallucination in LLM Agents: A Per-Call Metric and a Training-Free Fix That Closes [Y]% of the Cost-Quality Gap"*

Backup if §6 mechanism collapses: *"Registry-Visible Reprompting: A Training-Free Recovery for Tool-Hallucination Failures"*

### 2.2 One-sentence main result (R2.5 rewrite — phenomenon and number lead)
*LLM agents call tools that do not exist on [X]% of calls; a single-turn re-prompt that lists the registry (RVR) recovers [Y]% of these failures and closes [Z]% of the small-vs-frontier cost-quality gap, validated across 5 models spanning 3 capability tiers and 2 vendor families on BFCL-v4 and τ-bench at <2% token overhead.*

### 2.3 Four claimed contributions (CONTRIBUTION #1 REFRAMED — Δ1)
1. **Metric (disaggregation)**: We operationalize **TEHR** as a fine-grained, per-call metric isolating registry-membership violations. Prior work measures this failure mode at coarser granularity — API-Bank \citep{li2023apibank} categorizes name-mismatch as a *per-task error type* (61.4% rate); RelyToolBench \citep{cao2025reliability} bundles non-existent-tool errors with relevance and timing under "Tool Selection Hallucination" with aggregate reliability scoring. TEHR's contribution is **disaggregation**: a clean per-call denominator for the registry-membership-specific failure mode, enabling targeted intervention design (RVR) and per-tier comparison across model capability scales.
2. **Empirical characterization across 3 tiers**: TEHR baselines on 5–6 models (4 API + 1 local + optional Grok) × 2 benchmarks × 50 BFCL + 25 τ-bench tasks ≈ 750–900 main runs + 360–450 probe runs.
3. **RVR intervention**: training-free, registry-list-in-reprompt; primary test C1 vs C0.5 (naive retry) — isolates the *content* of the re-prompt as the active ingredient.
4. **Cost-quality-gap closure**: scaling-curve evidence that RVR's pass-rate gain grows with the small-vs-frontier capability gap, yielding a practical recommendation (use small-tier + RVR over frontier baseline at ~[Z]× lower cost).

### 2.4 Why this clears workshop-caliber novelty (UPDATED)
- **Industry pain documented (Czapla \citep{czapla2026}); academic precedent partial (API-Bank, RelyToolBench bundle this with other failure modes).** TEHR's contribution is the disaggregation, not the discovery.
- C1-vs-C0.5 design isolates the *content* of the re-prompt — not just "any retry."
- 3-tier scaling curve gives a *quantitative* efficiency claim, not a qualitative one.
- Local-tier inclusion (Qwen3-8B on M5) demonstrates feasibility on consumer hardware — directly addresses SCALE's "efficient agents" theme.

---

## 3. HARD CONSTRAINTS (UPDATED — Δ4, Δ5)

| Axis | Value |
|---|---|
| Workshop | SCALE @ ICML 2026 |
| Track | Main 7 pages |
| Deadline | 2026-04-28 AoE (~2026-04-29 12:00 UTC) — *verified by SCALE-call-audit agent* |
| Time budget | 36h wall-clock |
| **API cost ceiling** | **$0 paid (post $5,500 credits); ~$200-400 against credits** |
| **Orchestration cost** | **$0 — Claude Max plan** |
| **Local compute** | M5 32 GB unified memory; MLX runtime; Qwen3-8B-Instruct (~5-6 GB at 4-bit) |
| **Models** | **5 core + 1 deferred**: Sonnet 4.6, Haiku 4.5, GPT-4.1, GPT-4.1-mini, Qwen3-8B@MLX **+ Grok (deferred to G2)** |
| Benchmarks | BFCL v4 multi-turn (primary, N=50) + τ-bench retail (secondary, N=25) |
| Per-task cap | 120s wall-clock, 8 turns |
| Author | Solo unless co-author confirmed before T+0 |

### 3.1 Soft constraints (unchanged)
- No hardware/KV-cache framing.
- Cost-quality-gap framing is the load-bearing story.
- Statistical bar: paired McNemar mid-p; Holm-Bonferroni; TOST; bootstrap 95% CIs.

---

## 4. EXPERIMENTAL DESIGN (mostly unchanged from v3)

### 4.1 RVR (the intervention)
Pseudocode in `paper/sections/03_method.tex`. Pure function; at-most-one retry enforced by runner not by RVR itself.

### 4.2 Conditions
| Condition | Description |
|---|---|
| **C0** baseline | ReAct, framework default error on bad call |
| **C0.5** naive retry | "Previous failed, try again" — *no registry list* |
| **C1** RVR | Bad call → re-prompt with full registry list |

Primary test: C1 vs C0.5 (paired) on the strict subset of C0-failed-with-hallucination tasks.

### 4.3 Metrics
- TEHR per (model, benchmark, condition).
- ΔPass(C1−C0.5) — paired McNemar mid-p, Holm-Bonferroni across per-tier tests.
- Token overhead C1 vs C0.
- Non-inferiority on C0-passing strict subset, TOST margin 1pp.
- Cost-per-success per (model, condition).
- **Gap-closure ratio** = [PassRate(small + C1) − PassRate(small + C0)] / [PassRate(frontier + C0) − PassRate(small + C0)]. **Headline.**
- Probe ΔTEHR (§6) by distractor type (near-name, synonym, random) × tier.

### 4.4 Pre-registered analysis decisions (unchanged from v3.4 — 12 items locked at T+05:00)

### 4.5 Compute + cost budget (UPDATED)

| Phase | Runs | Cost (paid) | Wall-clock |
|---|---|---|---|
| Smoke test | 25 | <$0 (credits) | 15 min |
| Pilot | 200 (4 API × 25 × 2 cond) | $0 (credits) | 1.5 h |
| Main run (API) | 600 (4 API × (50+25) × 2 cond) | $0 (credits, ~$60-110 against $5500 reserve) | 2 h |
| Main run (M5/Qwen3) | 150 (1 model × (50+25) × 2 cond) | $0 | 1.5 h |
| §6 probe | 360-450 (30 × 4-5 × 3 distractors) | $0 (credits, ~$40-60) | 50 min |
| **Optional: Grok** | **150-200** | **$0 (xAI credits)** | **1 h** |
| Buffer / re-runs | 200 | $0 (credits) | 0.5 h |
| **Total** | **~1700-2000** | **$0 paid; ~$150-250 against credits** | **~6.5 h compute** |

Cost meter still active as safety belt — abort threshold = 90% of credit ceiling per provider, set conservatively at $400 per provider.

---

## 5. 36-HOUR EXECUTION PLAN (mostly unchanged; Phase 0 progress noted)

### Phase 0 STATUS (in progress)
- ✓ Gate 0 lit sprint complete (verdict: PARTIAL precedent; reframe applied above)
- ✓ §2/§3/§4 pre-drafts complete (in `paper/sections/`)
- ✓ Harness spec complete (`harness/HARNESS_SPEC.md`)
- ⧖ MLX feasibility probe (Gate 0.5) — running
- ⧖ Reviewer pass over Phase-0 outputs — running
- ⧖ Dataset acquisition (BFCL + τ-bench) — running
- ⧖ Model ID pinning + credit smoke test — running
- ⧖ SCALE call audit — running

### Phase 1 (T+13:00 → T+15:30) — UPDATED for Grok
- Spawn 5 parallel adapter agents: Anthropic / OpenAI / **xAI (deferred)** / MLX / BFCL+τ-bench loader.
- Reviewer agent verifies parser unit tests on each.
- xAI adapter built but only activated at Gate 2.

### Phase 2-6 (unchanged from v3)
See v3 §5 for Phase 2 (Pilot+G2), Phase 3 (Main+G3), Phase 4 (Analysis), Phase 5 (Writing), Phase 6 (Polish+Submit).

---

## 6. HARD GATES (UPDATED)

| Gate | T+ | PASS | PIVOT |
|---|---|---|---|
| **G0** | 00:30 | TEHR not already a named metric, OR defendable as "disaggregation" | **PASSED with reframe (API-Bank precedent → contribution #1 reworded)** |
| **G0.5** | 04:00 | MLX + Qwen3-8B successfully runs ≥3/5 BFCL-style tasks with valid tool-calling format | Drop local tier; revert to API-only model lineup |
| **G1** | 13:30 | Hallucinations flow through API on ≥2 of 5 models | Pivot to M1 (Engländer-adjacent controlled-evidence design) |
| **G2** | 18:30 | Pilot TEHR ≥5% on ≥2 tiers AND **decision: Grok in/out** | Pivot to M1; reserve xAI credits |
| **G3** | 22:30 | ΔPass(C1−C0.5) ≥20pp pooled AND gap-closure ratio ≥0.5 AND non-inferiority TOST passes | Soft-claim or characterization |

### 6.1 Backup M1 — UPDATED framing (Δ3)
First-Hypothesis Anchoring renamed to **"Registry-Aware Self-Correction Probe."** Differentiation from Engländer \citep{englander2026}: their "environmental curiosity deficit" shows agents under-exploit information present in the environment; M1 measures whether agents acknowledge a contradicting tool result and revise. Different failure class, different intervention. Mandatory differentiation paragraph in abstract + §1 + §2 if M1 triggers.

### 6.2 Hard abort (unchanged from v3)

### 6.3 Pre-committed cut hierarchy (UPDATED with Grok-out option)

| Trigger | Cut order |
|---|---|
| T+04:00 MLX fails | Drop local tier; reframe headline to "4-model 2-tier" |
| T+18:30 cost overrun (against credits, not paid) | Drop Grok if it was added; drop Haiku (smallest cost-saving on Anthropic side); N: 50→30; drop τ-bench |
| T+18:30 Grok adapter has issues | Skip Grok; main run is 5 models |
| T+21:30 main run unfinished | (1) Drop τ-bench partial; (2) Drop one API model (Haiku first if both Anthropic up); (3) Skip C0.5 (last resort) |
| T+22:30 ΔPass <20pp | Headline → characterization; drop probe; reframe title |
| T+33:45 behind on §5 | Per-model breakdowns → appendix; §6 → 1-paragraph teaser; §7 → 0.25p |
| T+35:30 PDF >7p | Compress §2 to 0.5p; probe details → appendix |

### 6.4 Minimum Viable Paper (unchanged)
§1 + §3 + §5 (2 tiers × 1 benchmark × C0+C1) + §7. ~4 pages.

---

## 7. RISK REGISTER (additions only — see v2/v3 for R1-R21)

| # | Risk | Like. | Imp. | Mitigation |
|---|---|---|---|---|
| **R22** | **API-Bank precedent narrows novelty more than expected; reviewer says "this is API-Bank renamed"** | Med | High | §2 cites API-Bank explicitly; emphasizes per-call denominator + cross-tier + paired intervention; differentiation paragraph pre-written |
| **R23** | **Grok adapter has non-trivial xAI quirks** (refusals, rate limits, response shape) | Med | Low | Phase-1 adapter agent does it in parallel; if blocked, Grok dropped at G2 with no story impact |
| **R24** | **Czapla blog date-of-record vs URL-slug discrepancy** (URL says 01-20, some sources say 02-18) | Low | Low | SCALE-call-audit agent or related-work-notes agent verifies; cite URL not date |

---

## 8. WRITING STRUCTURE (unchanged from v3)

§2 Related Work draft now requires API-Bank + RelyToolBench citations added — flagged for reviewer pass.

---

## 9. SUBMISSION CHECKLIST (additions to v2/v3)

- [ ] Anthropic credits redeemed and balance confirmed
- [ ] OpenAI credits redeemed and balance confirmed
- [ ] xAI credits redeemed (held in reserve until G2)
- [ ] Cursor credits **NOT** redeemed for this paper (saved for personal IDE use)
- [ ] §2 cites API-Bank \citep{li2023apibank} and RelyToolBench \citep{cao2025reliability}
- [ ] Czapla date in all docs is 2026-01-20
- [ ] Engländer paper cited under "environmental curiosity deficit" framing, not "first-hypothesis anchoring"

---

## 10. WHAT "DONE" LOOKS LIKE (unchanged)

OpenReview confirmation at T+35:55 ± 5min. Title §2.1, Main track, 7-page PDF + appendix + supplementary zip. **Paid cost = $0.**

---

## 11. OPEN QUESTIONS — STATUS

| v3 Q | v3.1 Resolution |
|---|---|
| Q1: Credits redeemed? | **YES** — $5,500 across OpenAI/Anthropic/xAI; Cursor skipped |
| Q2: MLX feasibility? | **Pending Gate 0.5 (T+04:00)** |
| Q3: Solo vs co-author? | **Solo** |
| Q4: arXiv concurrent posting? | **Pending SCALE-call-audit agent** |
| Q5 (v3.1 NEW): Grok inclusion? | **Adapter built in parallel; activated at Gate 2 if pilot has headroom** |

---

## 12. WORKSPACE STRUCTURE (unchanged from v3)

---

## 13. PARALLEL-AGENT EXECUTION PLAN (unchanged from v3)

---

**Predecessors**: PAPER_PLAN.md (v1), PAPER_PLAN_v2.md (v2), PAPER_PLAN_v3.md (v3). v3.1 is canonical.
