# Cross-family MLX tool-call parsing — fix report

Scope: `harness/adapters/mlx_adapter.py` (+ additive tests in
`harness/tests/test_mlx_adapter.py`). All changes are additive; the Qwen3
path is byte-for-byte preserved. No MLX inference was run (M5 queue holds the
GPU). Verified by `pytest harness/tests` (all green, 8 new cases) and the
import smoke-check `import harness.runner.loop, harness.adapters.mlx_adapter`.

## Root cause

The adapter only recognized Qwen's `<tool_call>{json}</tool_call>` envelope and
read `obj["arguments"]`. Non-Qwen families emit different envelopes and/or the
`parameters` key, so they produced **0 parsed tool calls** — confirmed directly
from saved C0 traces (e.g.
`results/llama_3_1_8B_C0_1777362827/.../...synonym.jsonl` shows
`agent_message = {"name":"mkdir","parameters":{"dir_name":"Projects"}}` with
`parsed_tool_call: null`).

## Diff summary

1. **Shared key-aliasing** — new `_coerce_call(obj)` accepts `arguments`
   (Qwen3/Mistral) **or** `parameters` (Llama-3.1) as the argument key. Missing
   `name` → `parse_ok=False`, identical to the legacy Qwen behavior.
2. **Family-tiered `_parse_tool_calls`** (first match wins; Qwen checked first
   so its behavior is unchanged):
   - **Tier 1 — Qwen3**: `<tool_call>{json}</tool_call>` (unchanged regex/logic).
   - **Tier 2 — Mistral**: `[TOOL_CALLS][ {...}, ... ]` JSON array
     (`_MISTRAL_TOOL_CALLS_RE`), decoded as a list.
   - **Tier 3 — Llama-3.1**: `<|python_tag|>{json}` **or** a bare top-level
     `{"name":..,"parameters":..}` object/array. Bare JSON is only treated as a
     call when every element is a dict carrying a `name` key (incidental JSON
     like `{"result":42}` is left as content).
3. **`<think>...</think>` stripping** before the bare/array detectors so a
   reasoning-distill's trailing envelope is still recoverable. No-op on the
   Qwen3 path (it runs with `enable_thinking=False`, so no `<think>` present).
4. **`_strip_envelopes`** now removes all recognized envelopes (Qwen,
   Mistral, python_tag, `<think>`, and a standalone bare-JSON call) from the
   text channel, mirroring the parser's family coverage.
5. **`enable_thinking=False` is now Qwen3-gated** (`"qwen3" in model_id.lower()`).
   Other families' templates don't accept the kwarg; previously it was passed
   to every model. The default adapter id is still Qwen3, so existing tests that
   assert the kwarg remain green.

## Which families WILL now parse

Determined from each model's bundled chat template (read from the HF cache, no
inference) + saved raw outputs under `results/`:

| Family | Template supports `tools=` | Emission format | Status |
|---|---|---|---|
| **Llama-3.1-8B-Instruct** | yes (`python_tag`) | bare `{"name":..,"parameters":..}` (confirmed in C0 traces) | **WILL parse** via alias + bare-JSON/python_tag tier |
| **Mistral-7B-Instruct-v0.3** | yes (`[TOOL_CALLS]`) | `[TOOL_CALLS][{...}]` with `arguments` (confirmed in bundled `tool_use` template) | **WILL parse** via Tier 2 |
| **DeepSeek-R1-Distill-Qwen-7B** | **no** `tools` slot; template has `tool_call` + `<think>` | reasoning prose, no tool envelope when no tool slot | **PARTIAL / unreliable** — parser now strips `<think>` and would catch a `<tool_call>` envelope if emitted, but the template has no slot to inject the tool registry, so the model rarely/never emits a structured call. Treat results as a lower bound; not a clean tool-calling baseline. |

Note on Mistral/Phi/DeepSeek saved C0 traces: the *prior* run emitted Markdown
prose (and DeepSeek emitted pure `<think>` reasoning) rather than structured
calls. For Llama the format was correct and only the parser failed — so Llama is
the one family the fix definitively recovers from existing data. Mistral's
`[TOOL_CALLS]` handling is in place for when it does emit the format; a fresh
run is needed to measure how often it triggers.

## Which are structurally impossible

Confirmed from the chat templates (no `tools`, no `tool_call`, no envelope
tokens — there is no template path to either inject the registry or emit a
parseable call):

- **Phi-3.5-mini-instruct** — template has no `tools`, no `tool_call`. Saved C0
  traces are pure prose ("I'm unable to perform actions directly..."). No code
  change can fix this; it has no tool-calling format.
- **gemma-2-9b-it** — same: no `tools`, no `tool_call`, no envelope tokens.

These should be reported as "no tool template" and excluded from the
cross-family TEHR comparison (or footnoted as structurally incapable).

## Ready-to-queue command list

Run only after the M5 queue (`scripts/run_queue.sh`) finishes — these contend
for GPU memory. Pattern mirrors `run_cell` in `run_queue.sh` (BFCL multi-turn
base, 4 distractor types, `--remove-target`). `run_probe.py` accepts the local
MLX repo ids directly via `--models`.

```bash
ROOT=/Users/cero/Desktop/PROJECTS/icml
PY="$ROOT/harness/.venv/bin/python"

# Llama-3.1-8B — definitively recovered by the fix (clean JSON tool calls)
PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py \
  --models mlx-community/Llama-3.1-8B-Instruct-4bit \
  --distractor-types near_name,synonym,matched_random,unrelated \
  --n 25 --condition C0 --remove-target \
  --run-id xf_llama31_8B_C0_$(date +%s)

# Mistral-7B-Instruct-v0.3 — [TOOL_CALLS] now parsed when emitted
PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py \
  --models mlx-community/Mistral-7B-Instruct-v0.3-4bit \
  --distractor-types near_name,synonym,matched_random,unrelated \
  --n 25 --condition C0 --remove-target \
  --run-id xf_mistral_7B_C0_$(date +%s)

# DeepSeek-R1-Distill-Qwen-7B — partial; report as lower bound only
PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py \
  --models mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit \
  --distractor-types near_name,synonym,matched_random,unrelated \
  --n 25 --condition C0 --remove-target \
  --run-id xf_deepseek_7B_C0_$(date +%s)

# (Optional) C1 intervention arm for the two parseable families
for M in Llama-3.1-8B-Instruct-4bit Mistral-7B-Instruct-v0.3-4bit; do
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py \
    --models "mlx-community/$M" \
    --distractor-types near_name,synonym,matched_random,unrelated \
    --n 25 --condition C1 --remove-target \
    --run-id "xf_${M%%-Instruct*}_C1_$(date +%s)"
done
```

Skip Phi-3.5-mini and gemma-2-9b: structurally incapable of tool calls (no
template path). Re-running them only re-confirms 0 parseable calls.
