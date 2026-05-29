# τ-bench enablement report (second benchmark)

Goal: stand up τ-bench-retail as a second benchmark so the "BFCL-only" reviewer
criticism no longer holds. Status: **working end-to-end on the API path.** A
3-task Haiku smoke produces coherent multi-turn trajectories with valid tool
calls, zero tool-existence hallucinations (TEHR 0/24 pooled), and a live reward
oracle. All changes are additive and scoped to the τ-bench path; the BFCL/Qwen
path (which the running M5 queue depends on) is untouched and re-verified.

## What changed (diff summary)

Four files, all additive. `mlx_adapter.py` / `test_mlx_adapter.py` in the working
tree are **not** mine (pre-existing uncommitted queue work).

- **`harness/pyproject.toml`** — added `litellm==1.86.2` (τ-bench's `user.py`
  transitively imports it; we use it import-only — the GPT-4o user simulator is
  replaced by the existing Haiku patch). Installing litellm bumped
  `pydantic 2.9.0 -> 2.13.4`; pin updated to match. Full suite + BFCL/MLX import
  re-verified under the new pydantic (152 passed).

- **`harness/runner/executors.py`** (`make_tau_bench_executor`) —
  - Now calls `env.reset(task_index=...)` (was missing entirely; without it the
    env never loads the task DB or user instruction). Result observation +
    `info` captured on `executor.state["initial_observation"]` /
    `["reset_ok"]` / `["reset_error"]`; reset failures are recorded, never raised.
  - Added `_resolve_tau_env_class(fqn)`: the loader stubs the `…retail` package
    `__init__` (to dodge a litellm import at load time), so
    `MockRetailDomainEnv` is not an attribute of the package object. The
    resolver tries the package attribute, then falls back to the real
    `…retail.env` submodule. Defensively (re)installs the loader's namespace
    stubs.

- **`harness/runner/loop.py`** — all τ-bench-scoped (`if task.benchmark ==
  "tau_bench"`); BFCL branch byte-identical:
  - `respond` pseudo-tool (`RESPOND_ACTION_NAME`) added to the registry used for
    both rendering AND hallucination classification, so the agent can talk to
    the user simulator and `respond` is never miscounted as a fabrication.
  - `_to_canonical_inner` flattens the loader's OpenAI-wrapper schemas
    (`{type, function:{…}}`) to the canonical-inner shape (`{name, description,
    parameters}`) the adapters/classifier expect (BFCL already emits this; this
    is the single reconciliation point).
  - History seeded with a **system** prompt (the env's domain-policy `wiki` +
    an interaction protocol pointing the agent at the `respond` tool) and the
    env's initial observation (the user simulator's opening line).
  - **Plain-text → `respond` synthesis**: a τ-bench turn with no tool call IS a
    message to the user, so the assistant text is wrapped into a synthetic
    `respond(content=…)` call and stepped through the env (matches τ-bench's own
    `ToolCallingAgent` semantics). The env's reply is threaded back as the next
    user turn. This is what stopped the conversations from stalling on turn 1.

- **`harness/adapters/anthropic_adapter.py`** — extract a leading `system`-role
  message into the API's top-level `system=` kwarg. Additive and guarded: when
  no system message is present (the BFCL path) the request shape is identical to
  before. Needed because Anthropic takes `system` as a kwarg, not a message role.

## Smoke result (n=3, claude-haiku-4-5, τ-bench retail, C0)

| task | turns | tool-call status | TEHR | terminal | reward |
|------|-------|------------------|------|----------|--------|
| tau_retail_000 | 8 | all executed | 0/8 | max_turns | 0.0 |
| tau_retail_001 | 8 | all executed | 0/8 | max_turns | 0.0 |
| tau_retail_002 | 8 | all executed | 0/8 | max_turns | 0.0 |

- **Valid tool calls?** Yes. Every turn produced a parseable, in-registry tool
  call (real retail tools + `respond`). Pooled TEHR = **0/24** (zero
  tool-existence hallucinations — consistent with the Anthropic 4.x finding).
- **A reward?** Yes — the reward oracle ran (terminal `calculate_reward`);
  reward was 0.0 because all 3 hit the **8-turn cap** before completing. The
  trajectories are genuinely coherent: e.g. task 001 authenticates
  (`respond` → `find_user_id_by_name_zip` → `get_user_details` →
  `get_order_details`), negotiates an address change with the user simulator,
  and gets explicit confirmation — it simply ran out of turns before the final
  `modify_user_address` mutation. τ-bench retail tasks routinely need ~12–15
  turns; the 8-turn cap is the only reason reward is 0.
- **Spend:** agent $0.176 + user-sim $0.015 = **$0.191 total** (budget $5; never
  approached the abort).
- Trace: `paper/_staging/tau_smoke_trace.jsonl`. Driver:
  `paper/_staging/_tau_smoke.py`.

## Remaining blockers / notes

1. **Turn cap is the binding constraint.** The loader sets `turns_max=8` and
   `run_task` caps at `min(max_turns, turns_max)`. To get non-trivial pass
   rates, raise the τ-bench turn budget to ~15–20. Cleanest knob: bump
   `turns_max` in `load_tau_bench_retail` (or thread a per-benchmark cap through
   the CLI). This is a config change, not a wiring fix.
2. **User-sim cost is not on the agent CostMeter.** The Haiku user simulator's
   spend is tracked by the env (`env.user.get_total_cost()`), separate from the
   agent-side CostMeter the CLI budgets against. For a fuller run, sum both when
   reporting τ-bench cost (the smoke driver already does).
3. **CLI executor builds a fresh Anthropic client** for the user sim
   (`make_tau_bench_executor(task)` with no `anthropic_client=`), so it relies on
   `ANTHROPIC_API_KEY` in the env. Fine, just slightly wasteful vs. reusing the
   agent adapter's client (the smoke driver reuses it via `adapter._client`).
4. **No reward yet observed == nothing proven about pass rate.** The smoke
   proves the *plumbing* (reset, tool dispatch, user-sim turn, reward oracle),
   not task success. A fuller cell with a higher turn cap is needed before any
   τ-bench numbers go in the paper.
5. litellm emits harmless `botocore` warnings at import (no boto installed);
   cosmetic, grep them out.

## Verification

- `harness/.venv/bin/python -m pytest harness/tests` → **152 passed, 1 warning**.
- `python -c "import harness.runner.loop, harness.adapters.mlx_adapter"` → OK.
- `scripts/run_probe.py` (the running queue's entry point) imports cleanly under
  the bumped deps — the Qwen/BFCL path is intact.
- CLI dry-run for the τ-bench cell plans correctly.

## Copy-paste command for a fuller τ-bench cell later

Source the key first; the user simulator needs `ANTHROPIC_API_KEY`.

```bash
cd /Users/cero/Desktop/PROJECTS/icml
set -a; . ./.env.local; set +a

# Recommended FIRST: raise the τ-bench turn cap so tasks can actually finish.
# Edit harness/bench_loaders/tau_bench.py -> load_tau_bench_retail: turns_max=20

# Option A — via the CLI (single cell: Haiku, τ-bench, C0, n=15):
PYTHONPATH=. harness/.venv/bin/python -m harness.runner.cli \
  --models claude-haiku-4-5 \
  --benchmark tau_bench \
  --conditions C0 \
  --n 15 \
  --output results/tau_haiku_c0 \
  --run-id tau_haiku_c0_$(date +%s)

# Option B — the standalone smoke driver, bigger n (honours the $5 abort via
# CostMeter; raise TAU_SMOKE_N):
TAU_SMOKE_N=15 PYTHONPATH=. harness/.venv/bin/python paper/_staging/_tau_smoke.py
```

Do NOT run this concurrently with heavy MLX/Qwen work — it is API-only (Haiku
agent + Haiku user sim) so it won't contend for M5 memory, but keep an eye on
Anthropic spend for larger n.
