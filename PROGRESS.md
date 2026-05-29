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

## Running log
- `2026-05-29` Branch + restore point created. Re-aggregation confirms headline. Phase A research dispatched.
- `2026-05-29` Phase A: paper-inventory + novelty-research returned. STRATEGY PIVOT: lead with C0.7 "format-not-content recovery" (novel mechanism-of-fix claim); demote curve to "predicted signature"; add C0.8 decoy-list experiment. Number bugs confirmed (8B denom 258/268/269; 2599 not reconstructable). Dispatched: compute audit, self-review digest, citation verification (3 high-risk concurrent-work cites must be verified before use).

