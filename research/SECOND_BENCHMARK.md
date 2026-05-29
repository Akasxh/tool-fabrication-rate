# Second-benchmark TFR probe: tau-bench (Sierra retail)

**Goal.** Reproduce the distractor-based Tool-Fabrication-Rate (TFR) probe on a
SECOND, genuinely different benchmark with a non-zero base — the binding
main-track constraint named by the hostile reviewer panel ("a 2nd benchmark with
a non-zero base that reproduces the gap").

## Benchmark chosen: tau-bench retail (PREFERRED option)

We used **tau-bench** (Sierra retail domain), not BFCL single-turn. Rationale:

- It is a **genuinely different benchmark family** (Sierra retail/airline, real
  multi-turn user-simulator interaction) — exactly what reviewers want, vs. the
  weaker BFCL-single-turn fallback which is the same family as our primary
  result.
- It was **already wired**: `harness/bench_loaders/tau_bench.py` loads the
  retail tasks, and `harness/runner/loop.py` + `harness/runner/executors.py`
  already support `benchmark=="tau_bench"` with the `respond` pseudo-tool, the
  Haiku user simulator, and env-step execution.
- The probe methodology is benchmark-agnostic: it needs Tasks with a tool
  `registry`; tau-bench Tasks carry one (16 retail tools).

## What was changed (ADDITIVE only)

All edits are in `scripts/run_probe.py`. No harness module was modified, so the
running MLX queue (`run_mt2.sh`, which re-imports harness code) is unaffected.
The existing BFCL `multi_turn_base` probe path is unchanged (defaults preserved).

1. **`inject()` made shape-aware.** Added `_inner_schema()` helper. BFCL emits
   canonical-inner tool schemas (`{name, description, parameters}`); tau-bench
   emits the OpenAI wrapper (`{type:"function", function:{...}}`). The distractor
   description-length / arity are now read from the inner view in both cases, so
   `matched_random` distractors still match the real tools' average shape. The
   injected distractor is always canonical-inner; the runner's existing
   `_tau_augmented_registry()` flattens the whole registry to canonical-inner
   before hallucination classification, so mixing shapes is safe.

2. **`--benchmark {bfcl,tau_bench}` flag** (default `bfcl`). With `tau_bench`,
   `main()` loads tasks via `load_tau_bench_retail(...)` and builds executors via
   `make_tau_bench_executor` instead of `make_bfcl_executor`. Added
   `--tau-split {test,dev,train}` (default `test`, 115 tasks).

3. **Cell key generalized.** Was hardcoded `anthropic_{model}_{bfcl_split}_...`;
   now `{model_slug}_{split_label}_{condition}_{dtype}` where `model_slug`
   replaces `/` (so MLX repo ids are filesystem-safe) and `split_label` is e.g.
   `tau_test`. Provider-agnostic.

The probe semantics are identical across benchmarks: `inject()` adds ONE
synthetic distractor and (with `--remove-target`) removes the real target tool;
TFR = fraction of model turns that name a tool **absent from the registry**
(`tool_call_status == "hallucinated"` in `harness/runner/loop.py`). The synthetic
distractor names are not in any training corpus, so memorization cuts against
fabrication.

## Smoke (n=3, near_name, C0, --remove-target) — END TO END

| Model | Provider | Benchmark | TFR (num/denom) | pass | spend |
|---|---|---|---|---|---|
| claude-haiku-4-5 | Anthropic API | tau-bench retail (test) | **0/23 = 0.000** | 0/3 | $0.165 |
| mlx-community/Qwen3-8B-4bit | local MLX | tau-bench retail (test) | **0/8 = 0.000** | 0/3 | $0.00 (user-sim was free/cached) |

The commercial model (Haiku) fabricates at the **measurement floor (0.000)**, as
expected. Qwen3-8B also showed 0 fabrications on this tiny smoke — **but the
denominator is only 8 tool calls** (the three retail tasks converged in 2–3
turns each). At the ~1–2% open-weight fabrication rate measured on BFCL, 8 calls
is far too few to surface a single fabrication (expected ≈0.1 events). **The
smoke proves the PIPELINE works end-to-end on both API and local MLX; it does
NOT — and is not sized to — measure the gap.** The full grid below uses n=25 and
the full distractor-type set to give an adequate denominator (~hundreds of calls
per model), which is what reproduces the commercial-floor vs open-weight gap.

All logged turns were `executed` against real retail tools (`respond`,
`get_order_details`, `find_user_id_by_name_zip`, `get_user_details`, `think`) —
the multi-turn user-simulator conversation threads correctly and the
distractor/removed-target injection runs cleanly on a genuinely different 2nd
benchmark. The Qwen3-8B cell ran under heavy GPU contention from the live
`run_mt2.sh` queue (one turn every 1–2 min); a dedicated grid run with the queue
idle will be far faster.

Run artifacts:
- `results/smoke_tau_haiku/claude-haiku-4-5_tau_test_C0_near_name.jsonl`
- `results/smoke_tau_qwen8b/mlx-community_Qwen3-8B-4bit_tau_test_C0_near_name.jsonl`

> NOTE: tau-bench's user simulator is Haiku (API) even when the agent is a local
> MLX model — this is inherent to tau-bench and costs only the user-sim tokens.

## pytest

`harness/.venv/bin/python -m pytest harness/tests -q` → **all green** after the
edits (run_probe.py is not imported by the harness package; the change is
strictly additive to a script).

## Copy-paste: full 2nd-benchmark probe (commercial-vs-open gap)

Run from repo root. `set -a; . ./.env.local; set +a` loads Anthropic + OpenAI
keys. Use `--n 25` (or more) and the full distractor-type set for the paper grid.
`--remove-target` is the gap-eliciting condition (real tool removed, near-name
lure left in place).

```bash
cd /Users/cero/Desktop/PROJECTS/icml
set -a; . ./.env.local; set +a
PY=harness/.venv/bin/python
RUN=tau_probe_$(date +%s)
DT=near_name,synonym,matched_random,unrelated

# --- API models (no M5 contention; run anytime) ---
for M in claude-sonnet-4-6 claude-haiku-4-5 gpt-4.1 gpt-4o; do
  PYTHONPATH=. "$PY" scripts/run_probe.py \
    --benchmark tau_bench --tau-split test \
    --models "$M" --distractor-types "$DT" \
    --n 25 --condition C0 --remove-target \
    --run-id "$RUN" --output results
done

# --- Open-weight MLX models (M5; serialize to avoid GPU thrash; the MLX
#     queue run_mt2.sh must be idle first) ---
for M in mlx-community/Qwen3-1.7B-4bit mlx-community/Qwen3-4B-4bit \
         mlx-community/Qwen3-8B-4bit mlx-community/Qwen3-14B-4bit; do
  PYTHONPATH=. "$PY" scripts/run_probe.py \
    --benchmark tau_bench --tau-split test \
    --models "$M" --distractor-types "$DT" \
    --n 25 --condition C0 --remove-target \
    --run-id "$RUN" --output results
done

# --- aggregate ---
PYTHONPATH=. "$PY" scripts/analyze_run.py results/"$RUN"
```

All cells write into one `results/$RUN/` directory; `analyze_run.py` aggregates
per-model TFR across cells and flags the commercial-floor vs open-weight gap.

## Blockers / caveats

- **None blocking.** The probe runs end-to-end on tau-bench.
- tau-bench user simulator = Haiku (API): every cell (even MLX agents) incurs a
  small Anthropic user-sim cost (~$0.05/task at n=3 for Haiku-agent; lower for
  MLX-agent which only pays user-sim tokens). Watch spend at n=25 across 8
  models (~ a few dollars total; user-sim dominates).
- MLX cells contend with the running `run_mt2.sh` queue for the M5 GPU — run them
  after that queue drains, or expect slow wall-clock.
