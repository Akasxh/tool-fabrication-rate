# 🛰️ Spotlight Push — Live Progress

**Goal:** SCALE camera-ready + main-track-spotlight-grade revision. Full autonomous.
**Branch:** `camera-ready-spotlight` (restore point: commit `b6ca532`)
**Started:** 2026-05-29

> This file is the live dashboard. It updates continuously. Phases run partly in parallel
> (long M5 compute in background while writing/research proceed).

---

## Headline status (ground truth, re-aggregated from raw traces)

C0 non-monotonic curve **reproduces the submitted paper exactly**:

| model | C0 TEHR | events |
|---|---|---|
| Qwen3-0.6B | 0.00% | 0/75 |
| Qwen3-1.7B | 0.95% | 2/210 |
| Qwen3-4B | 1.33% | 3/226 |
| Qwen3-8B | 1.46% | 9/615 |
| **Qwen3-14B** | **1.87%** ← peak | 5/268 |
| Qwen3-32B | 0.00% | 0/224 |

Anthropic: 0 events across all 5 versions. Qwen2.5-7B: 6.10% (28/459). Total signal ≈ 19 Qwen3 C0 events → **thin; N-expansion is the #1 priority.**

---

## Phase tracker

- [x] **A — Ground truth** — re-aggregation ✅; paper inventory ⏳; novelty research ⏳; compute audit ⏳
- [~] **B — Long compute (M5, sequential)** — QUEUE LAUNCHED (`scripts/run_queue.sh`, bg). Live status: `results/_queue/STATUS.tsv`
  - [~] B-decoy **C0.8 decoy condition** — implemented (`harness/intervention/decoy_list.py`), 33 tests pass, smoke OK. 8B running FIRST (gates primary framing).
  - [~] B1 N-expansion (14B n=50, 32B n=50, 8B n=50) — queued
  - [~] B3 C-ladder full 5-cond {C0,C0_5,C0_7,C0_8,C1} on 8B/14B/4B — queued
  - [~] B2 Quantization confound (8B 4/8bit/bf16 + 14B-8bit) — downloads running concurrently; 14B-bf16 excluded (OOM)
  - [ ] B4 Downstream utility (task-success Δ, abstention, latency) from traces — analysis, no run
  - [ ] B7 Cross-family parsing fix (Llama high-value; Phi/gemma structurally can't tool-call → drop honestly)
  - [ ] B5 tau-bench 2nd benchmark — needs env.reset/respond wiring + litellm (riskier)
  - [ ] B6 Contamination / paraphrase probe — stretch
- [ ] **C — Writing** — correctness fixes, reframing, inverse-scaling positioning, de-anon + acks
- [ ] **D — Integrate** new numbers + figures
- [ ] **E — Adversarial gate** — 12-persona toolkit, rounds to convergence, evaluator PASS
- [ ] **F — Polish** — PDF, poster/spotlight assets

---

## Open questions / risks
- 32B "collapse" may be underpowered (0/224, UB only). N-expansion resolves.
- Peak-distractor shift rests on 2/3/5 events. May not survive expansion. Follow the data.
- Cross-family claim currently rests on Qwen2.5-7B alone. Fix parsing or scope honestly.

## LIVE AGENTS / JOBS (max-parallel push)
- **M5 experiment queue** (sequential, GPU-bound) — Qwen3 decoy/curve/ladder/quant. ~critical path.
- **forge-lead** (bg agent) — building reusable `paper-spotlight` SKILL so this pipeline is one command next time.
- **11-agent workflow** `tehr-spotlight-fanout` (bg) — parallel queue-safe work → `paper/_staging/`:
  tau-bench enablement · cross-family parser · stats-with-CIs · coverage matrix · prior-art table ·
  security motivation · BOTH abstract variants (primary+backup) · citation audit of existing 2026 cites ·
  main-track persona pre-review · §3.3/§6 redraft · integration synthesis.
- **Decoy trigger** armed — fires the moment 8B C0.8 lands (~1h) → framing locked.
- Downloads ✅ done early · tectonic ✅ ready.

## What's running right now (autonomous)
- **M5 experiment queue** (`scripts/run_queue.sh`, bg) — sequential, ~30h. Cell 1 = 8B C0.8 decoy (the framing gate). Live: `results/_queue/STATUS.tsv`, `queue.log`. Re-aggregates after every cell.
- **Quant-variant downloads** (`scripts/dl_quant.sh`, bg) — 8B-8bit/bf16 + 14B-8bit. Live: `results/_queue/download.log`.
- **tectonic** (LaTeX engine) installing — needed to compile the camera-ready after the rewrite.
- **Milestone trigger** armed — fires when the 8B decoy result lands (~2h), at which point the primary-vs-backup framing is decided and the reframe begins.

## Done this session
- Branch + restore point; full paper inventory; novelty/positioning research; compute audit; prior-self-review digest.
- Re-aggregation confirms headline curve reproduces exactly.
- C0.8 decoy condition implemented + tested + smoke-passed (the spotlight experiment).
- Downstream-utility analyzer written; preliminary 8B run shows C1/RVR Δpass −2.0pp vs C0.7 +1.3pp (strengthens "ship C0.7").
- 7 citations verified (incl. 3 concurrent works fetched from arXiv directly) + added; concurrent-work positioning written into Related Work; Xu et al. differentiation sharpened; stale comment removed.
- Committed as a reversible checkpoint.

## Gated on compute (next, in order)
1. **Decoy verdict** (~2h) → lock primary ("format-not-content, proven") or backup ("grounding-gap") framing.
2. N-expansion lands → recompute + lock ALL headline numbers; reconcile denominators; CP bounds on every 0% cell.
3. Quant confound lands → upgrade limitations "cannot disentangle" → "ran a control."
4. Full reframe: abstract/intro/§5.4/§6, trim §3.3, coverage matrix, downstream-utility paragraph.
5. Deferred code (post-Qwen-queue, to protect it): tau-bench 2nd benchmark, cross-family parser.
6. Adversarial review gate (12 personas) → evaluator PASS → PDF + poster.

## ⚖️ MAIN-TRACK VERDICT (4-persona adversarial pre-review, main-track bar)
**As-is: clear workshop ACCEPT, but main-track ~18% (WEAK_REJECT).** Two gates, both must clear:
- **Gate #1 — break the vendor/quantization confound.** Quant axis: bf16 8B run (queued, weights ready) ✅ mine to do. Vendor axis: a **non-Anthropic frontier API probe** (GPT/Gemini) — is the 0% an *Anthropic* or a *frontier* property? **← BLOCKED: no OpenAI/Gemini key.** Highest-leverage single experiment per all 4 personas.
- **Gate #2 — multiply event count** (whole headline rests on ~19 events). N≥100/cell on non-zero tiers → `run_queue2.sh` chained (14B + 8B C0, + 8B C0_7/C0_8/C1 so "registry is decorative" rests on >0 events).
- Plus: prove RVR changes *behavior* not just gates execution (post-reprompt re-fabrication analysis — free from C1 traces); reframe limitations so RVR ≠ "replaceable by allow-listing" (the decoy/format-not-content result IS this rebuttal); reconcile 268/269 + canonical number table (#5).
- Honest: even with all gates cleared, personas put it at *borderline-accept*, not safe. Main-track is a multi-day program; 1 day gets the workshop camera-ready excellent + the confound/event work well underway.

## NEEDS USER INPUT
- **OpenAI or Gemini API key** → unblocks the #1 main-track experiment (frontier vendor counterfactual). `run_queue2.sh` auto-runs it the moment a key is in `.env.local`.
- De-anonymization: author name(s) + affiliation (switch to `\usepackage[accepted]{icml2026}`).
- Acknowledgments wording.

## 🎯 DECOY VERDICT (LOCKED) — Variant A confirmed
Qwen3-8B C0.8 (decoy/wrong-list envelope) = **0/410, all 4 arms zero** — matches C0.7 (0/253, no list) and C1 (0/258, real list). **Registry content is decorative; envelope format drives recovery.** Paper rewritten to lead with this (Variant A). Deployable wrinkle: decoy/structured envelope Δpass **+2.7pp** vs full-RVR **−2.0pp** → ship the envelope, skip leaking the registry.

## 🟢 PAPER IN HAND (safe fallback, tagged `workshop-ready-honest`)
`paper/main_workshop_ready.pdf` — honest, bounded-claims version. Builds clean, body 7pp, refs p8, 0 undefined. Always submittable.

## ⚠️ Key lesson (panel-driven course-correct)
The aggressive "format-not-content" reframe OVERCLAIMED (equivalence from 3 zero-event arms) and a 6-persona panel scored it DOWN (~14% vs 18% baseline). Walked it back to bounded honest claims ("no detectable content effect, CI [−1.5,+1.4]pp; absence of evidence ≠ equivalence"), reverted the premature quant claim, killed an unbacked number, reconciled denominators (Anthropic 0/2578, OpenAI 0/2117). Honesty scores higher than loud claims.

## Two-track plan (user-directed)
- **Track 1 — ready-in-hand honest workshop paper:** DONE + tagged. Confirmation re-review running (did it recover to ≥18%?).
- **Track 2 — main-track push (fold in as experiments land, keep fallback safe):**
  - A1 powered decoy ablation on hot 14B cell (events under the ablation) — chained, the key gate.
  - bf16 quant control + A2 reflection — lean queue.
  - Frontier: 5 OpenAI models done (all 0%); gpt-5 pending.
  - A2-gate (2nd non-zero benchmark, tau-bench) — hardest; sets the ~borderline main-track ceiling.

## Running log
- `2026-05-29` Branch + restore point created. Re-aggregation confirms headline. Phase A research dispatched.
- `2026-05-29` Phase A: paper-inventory + novelty-research returned. STRATEGY PIVOT: lead with C0.7 "format-not-content recovery" (novel mechanism-of-fix claim); demote curve to "predicted signature"; add C0.8 decoy-list experiment. Number bugs confirmed (8B denom 258/268/269; 2599 not reconstructable). Dispatched: compute audit, self-review digest, citation verification (3 high-risk concurrent-work cites must be verified before use).

