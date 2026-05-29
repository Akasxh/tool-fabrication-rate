# HARNESS_SPEC.md — Phase 1 Parallel-Build Contract

**Status**: Phase 0 architecture lock + post-G0.5 corrections + dataset-acquisition findings. Phase 1 agents implement against this spec without coordination.
**Owners**: A1 = Anthropic adapter agent · A2 = OpenAI adapter agent · A3 = MLX adapter agent · A4 = Bench loaders + runner + stats agent · M = Main thread integrates.

## 1. Directory Layout

```
harness/
├── HARNESS_SPEC.md                          (M) this file
├── pyproject.toml                           (M) deps: anthropic, openai, mlx-lm, scipy, numpy, statsmodels
├── README.md                                (M) one-page run instructions
├── __init__.py                              (M) empty
├── types.py                                 (M) shared dataclasses: Task, ProviderResponse, ToolCall, Action
├── registry.py                              (M) Registry = dict[str, ToolSchema]; helpers + _normalize_bfcl_schema
├── adapters/
│   ├── __init__.py                          (M) empty
│   ├── base.py                              (M) abstract ModelAdapter — defines the interface all 3 adapters honor
│   ├── anthropic_adapter.py                 (A1) Claude Sonnet 4.6 + Haiku 4.5 via anthropic SDK native tool-use
│   ├── openai_adapter.py                    (A2) GPT-4.1 + GPT-4.1-mini + (deferred xAI) via openai SDK tools= schema
│   └── mlx_adapter.py                       (A3) Qwen3-8B-4bit via mlx_lm.generate + Qwen3 chat template
├── bench_loaders/
│   ├── __init__.py                          (A4) empty
│   ├── bfcl.py                              (A4) load BFCL v4 multi-turn → Task iterator (applies _normalize_bfcl_schema)
│   └── tau_bench.py                         (A4) load τ-bench retail → Task iterator
├── intervention/
│   ├── __init__.py                          (M) empty
│   ├── rvr.py                               (M) RVR per §4.1 of v3
│   └── naive_retry.py                       (M) C0.5 baseline
├── runner/
│   ├── __init__.py                          (A4) empty
│   └── loop.py                              (A4) ReAct loop, condition dispatch, 120s/8-turn caps
├── trace_logger.py                          (A4) JSONL writer, redaction-ready
├── cost_meter.py                            (A4) token-cost tracker + 90% abort callback
├── stats/
│   ├── __init__.py                          (A4) empty + condition-key alias map (C0.5 ↔ C0_5)
│   ├── tehr.py                              (A4) TEHR + bootstrap CIs
│   ├── paired_mcnemar.py                    (A4) paired McNemar mid-p + Holm-Bonferroni
│   ├── tost.py                              (A4) TOST non-inferiority (margin 1pp)
│   └── probe_anova.py                       (A4) one-way ANOVA + Tukey HSD for §6 probe
└── tests/
    ├── __init__.py                          (M) empty
    ├── fixtures/                            (each adapter agent ships fixtures here)
    │   ├── anthropic_responses.json         (A1)
    │   ├── openai_responses.json            (A2)
    │   └── mlx_responses.json               (A3)
    ├── test_anthropic_adapter.py            (A1)
    ├── test_openai_adapter.py               (A2)
    ├── test_mlx_adapter.py                  (A3)
    └── test_runner_smoke.py                 (A4) end-to-end 1-task smoke per adapter
```

## 2. Module API Contracts

### `types.py` (M, ships first)

```python
from dataclasses import dataclass
from typing import Literal, Optional, Any
from enum import Enum

ToolCallStatus = Literal["executed","hallucinated","refused","timed_out","parse_fail"]

@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]

@dataclass(frozen=True)
class Task:
    id: str
    benchmark: Literal["bfcl","tau_bench"]
    registry: dict[str, dict]   # CANONICAL OpenAI shape; bfcl loader normalizes "dict"→"object"
    initial_prompt: str
    turns_max: int
    expected_outcome: dict      # for BFCL: includes subsequent_user_messages list

@dataclass(frozen=True)
class ProviderResponse:
    raw_text: str
    tool_calls: list[ToolCall]
    parse_ok: bool
    finish_reason: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    raw_provider_payload: Optional[dict] = None

class ActionKind(Enum):
    EXECUTE = "execute"
    RE_PROMPT = "re_prompt"
    ABORT = "abort"

@dataclass(frozen=True)
class Action:
    kind: ActionKind
    tool_call: Optional[ToolCall] = None
    feedback: Optional[str] = None
```

### `adapters/base.py` (M)
Abstract `ModelAdapter` with `dispatch(messages, tools, max_tokens) → ProviderResponse`. Adapter must NOT raise on tool-parse failure — set `parse_ok=False` instead. Network/auth errors may raise; runner catches.

### `adapters/anthropic_adapter.py` (A1)
`AnthropicAdapter(model_id, api_key=None)`. `dispatch` uses `messages.create(tools=[...])`; maps `tool_use` content blocks to `ToolCall(name=block.name, arguments=block.input)`. Refusals classified by runner, not here. **Note**: Anthropic expects each tool's schema in `input_schema` field — the loader's normalized `"object"` (post-BFCL fix) flows through unchanged.

### `adapters/openai_adapter.py` (A2)
`OpenAIAdapter(model_id, api_key=None, base_url=None)`. `chat.completions.create(tools=[{"type":"function","function":{...}}],...)`. **Arguments arrive as JSON string — adapter must `json.loads` them; on JSONDecodeError set `parse_ok=False`.** `finish_reason="tool_calls"` → `"tool_use"`. The same class also serves xAI when constructed with `base_url="https://api.x.ai/v1"` (deferred to G2).

### `adapters/mlx_adapter.py` (A3)
**Repo: `mlx-community/Qwen3-8B-4bit`** (NOT `-Instruct-4bit`; that variant doesn't exist on HF). Renders via:
```python
prompt = tokenizer.apply_chat_template(
    messages, tools=tools,
    add_generation_prompt=True, tokenize=False,
    enable_thinking=False,        # CRITICAL: disable Qwen3 reasoning toggle
)
```
Runs `mlx_lm.generate`; parses Qwen3 tool-call envelope `<tool_call>{"name":..., "arguments":{...}}</tool_call>` via regex `<tool_call>\s*(\{.*?\})\s*</tool_call>` (DOTALL) + `json.loads`. `price_per_1k_*=0.0`. **Output shape MUST match Anthropic adapter exactly.** **Date hint**: prepend a system message *"Today's date is 2026-04-27."* — Qwen3 defaults relative dates to its training-cutoff year (2023), which corrupts BFCL/τ-bench scoring on date-dependent tasks.

### `bench_loaders/bfcl.py` (A4)
`load_bfcl(split="multi_turn_base", n=50, seed=0, data_dir=None) → Iterator[Task]`. Deterministic via `random.Random(seed).sample`. **CRITICAL: applies `registry.py:_normalize_bfcl_schema(schema)` to every task's tool definitions before yielding** — BFCL writes `"type": "dict"` instead of `"type": "object"` in JSON-Schema params, which all 3 adapters reject. **Also**: BFCL multi-turn `question` is `list[list[message]]` (one inner list per turn); loader stores `question[0]` as `Task.initial_prompt` and `question[1:]` as `Task.expected_outcome["subsequent_user_messages"]` (list of message lists), one batch per turn.

### `bench_loaders/tau_bench.py` (A4)
`load_tau_bench(domain="retail", n=25, seed=0, data_dir=None) → Iterator[Task]`. τ-bench has stateful tool env (`MockRetailDomainEnv`); `Task.expected_outcome` carries env config + reward sha256-hash oracle; loader does NOT instantiate, runner does. **τ-bench user simulator routing** (decision locked at §8.9): the default user simulator uses GPT-4o via litellm; we override to Claude **Haiku 4.5** to stay on credits.

### `registry.py` (M)
```python
def _normalize_bfcl_schema(d):
    """Recursively rewrites BFCL's `"type": "dict"` → `"type": "object"` so all 3
    adapters accept the schemas. Idempotent on already-normalized schemas."""
    if isinstance(d, dict):
        return {k: ("object" if k == "type" and v == "dict" else _normalize_bfcl_schema(v))
                for k, v in d.items()}
    if isinstance(d, list):
        return [_normalize_bfcl_schema(x) for x in d]
    return d
```

### `intervention/rvr.py` (M)
`rvr(parsed_calls, registry) → Action`. Pure function; if any name ∉ registry → `RE_PROMPT` with the registry list rendered. Empty `parsed_calls` → `EXECUTE(tool_call=None)` (model chose no tool).

### `intervention/naive_retry.py` (M)
C0.5 baseline. Feedback string locked: *"Your previous tool call failed. Please try again."* — no registry list.

### `runner/loop.py` (A4)
```python
def run_task(task, adapter, condition, logger, cost_meter, tool_executor,
             turn_timeout_s=120.0, max_turns=8) -> dict:
    """Returns {pass, tehr_num, tehr_denom, n_turns, terminal}."""
```
Per turn: dispatch → classify each tool call → if hallucinated, dispatch intervention by condition → at-most-one re-prompt → if executed, call `tool_executor` → log → cost_meter.add → check budget. Hard 120s wall + 8-turn caps. Single source of truth for `tool_call_status`. **For BFCL multi-turn**: between turns, append `task.expected_outcome["subsequent_user_messages"][turn_idx]` to the conversation as the next user input.

### `trace_logger.py` (A4)
```python
class TraceLogger:
    def __init__(self, out_path, redact_keys=None, persist_raw=False): ...
    def write(self, record): ...   # validates §3 schema, redacts, writes JSONL line, flushes
    def close(self): ...
```
Append-only; flush per write so kills don't lose data. `persist_raw=False` by default (drops `raw_provider_payload`); set `True` for debugging only.

### `cost_meter.py` (A4)
```python
class CostMeter:
    def __init__(self, budget_usd, on_threshold=None): ...   # fires once at 0.9*budget
    def add(self, tokens_in, tokens_out, price_in_per_1k, price_out_per_1k) -> float: ...
    def total(self) -> float: ...
    def over_budget(self) -> bool: ...
class BudgetAbort(RuntimeError): ...
```
Thread-safe via internal lock. MLX prices=0.0 → never trips threshold.

### `stats/tehr.py` (A4)
- `tehr(num_hallucinated, num_total) → float` (NaN if total==0).
- `tehr_bootstrap_ci(per_call_labels, n_resamples=10_000, alpha=0.05, seed=0) → (point, lo, hi)` percentile bootstrap on per-call labels.

### `stats/paired_mcnemar.py` (A4)
- `paired_mcnemar_midp(b, c) → p_value`. Mid-p formula: `0.5 * P(X = min(b,c) | Bin(b+c,0.5)) + P(X < min(b,c))`, doubled two-sided.
- `holm_bonferroni(pvalues, alpha=0.05) → list[bool]` (rejection booleans in original order).

### `stats/tost.py` (A4)
- `tost_paired_proportions(success_a, success_b, margin=0.01, alpha=0.05) → {p_lower, p_upper, non_inferior, mean_diff, ci_low, ci_high}`. Normal approx on pairwise differences.

### `stats/probe_anova.py` (A4)
- `oneway_anova_tukey(groups: dict[str, list[float]], alpha=0.05) → {f_stat, p_value, tukey: [{pair, diff, p_adj, reject}, ...]}`. Backed by `scipy.stats.f_oneway` + `statsmodels.stats.multicomp.pairwise_tukeyhsd`.

### `stats/__init__.py` (A4) — condition-key alias map
```python
CONDITION_LABEL_FOR_PAPER  = {"C0": "C0", "C0_5": "C0.5", "C1": "C1"}
CONDITION_LABEL_FOR_JSONL  = {v: k for k, v in CONDITION_LABEL_FOR_PAPER.items()}
```
Use `CONDITION_LABEL_FOR_PAPER[record["condition"]]` whenever results land in tables/figures.

## 3. JSONL Trace Schema

One JSON object per turn. Required fields:

| field | type | nullable | notes |
|---|---|---|---|
| `task_id` | str | no | |
| `model` | str | no | adapter.model_id (pinned dated alias preferred) |
| `benchmark` | str | no | `"bfcl"` or `"tau_bench"` |
| `condition` | str | no | `"C0"` / `"C0_5"` / `"C1"` (paper renders `C0.5` via stats alias map) |
| `turn_idx` | int | no | 0-based |
| `agent_message` | str | no | redacted |
| `parsed_tool_call` | object | yes | `{"name", "arguments"}` |
| `tool_call_status` | str | no | one of 5 statuses |
| `tool_response` | object | yes | benchmark-shaped |
| `intervention_event` | object | yes | `{"kind":"rvr_rejected"\|"naive_retry","feedback":str}` |
| `latency_ms` | int | no | |
| `tokens_in` | int | no | |
| `tokens_out` | int | no | |
| `cost_usd` | float | no | this turn only |
| `timestamp` | str | no | ISO-8601 UTC |
| `schema_version` | str | no | `"1.0"` |

Example record:
```json
{"task_id":"bfcl_mt_0042","model":"claude-sonnet-4-6","benchmark":"bfcl","condition":"C1","turn_idx":2,"agent_message":"I'll look up the weather using get_weather_v2.","parsed_tool_call":{"name":"get_weather_v2","arguments":{"city":"SF"}},"tool_call_status":"hallucinated","tool_response":null,"intervention_event":{"kind":"rvr_rejected","feedback":"Tool 'get_weather_v2' is not in the registry. Available tools: ['get_weather','book_flight']..."},"latency_ms":842,"tokens_in":1203,"tokens_out":74,"cost_usd":0.0042,"timestamp":"2026-04-27T14:33:11.420Z","schema_version":"1.0"}
```

## 4. Parser Unit-Test Spec

Each adapter ships fixtures in `tests/fixtures/<provider>_responses.json`. Adapter tests mock the SDK call.

### Anthropic (A1) — 4 fixtures
1. **clean_tool_call**: `ToolUseBlock(name="get_weather", input={"city":"SF"})`, `stop_reason="tool_use"` → executed.
2. **hallucinated_tool_call**: same shape, `name="get_weather_v2"` → adapter returns verbatim; runner classifies → hallucinated.
3. **refusal_text_only**: `TextBlock("I can't help with that.")`, `stop_reason="end_turn"` → tool_calls=[], parse_ok=True → refused (runner classifies via deny-list).
4. **parse_fail_malformed_input**: ToolUseBlock with `input` as string `"{not json"` → tool_calls=[], parse_ok=False → parse_fail.

### OpenAI (A2) — 4 fixtures
1. **clean_tool_call**: `tool_calls=[{function:{name:"get_weather",arguments:'{"city":"SF"}'}}]`, finish=`"tool_calls"` → executed.
2. **hallucinated_tool_call**: same with `name="lookup_weather_api"` → hallucinated.
3. **refusal_safety**: `message.refusal="I cannot..."`, no tool_calls → refused, finish=`"refusal"`.
4. **parse_fail_bad_json**: `arguments='{"city": '` truncated → tool_calls=[], parse_ok=False → parse_fail.

### MLX (A3) — 4 fixtures
1. **clean_tool_call**: `'<tool_call>{"name":"get_weather","arguments":{"city":"SF"}}</tool_call>'` → executed.
2. **hallucinated_tool_call**: `"name":"weather_lookup"` in same envelope → hallucinated.
3. **refusal_no_tool**: `"I'm sorry, I can't do that."`, no envelope → refused.
4. **parse_fail_malformed**: `'<tool_call>{"name":"x", "arguments": {oops}</tool_call>'` → regex matches but json.loads fails → parse_fail.

## 5. Integration Acceptance Criteria

1. Each adapter passes its 4 fixture unit tests (`pytest tests/test_*_adapter.py` green).
2. `runner/loop.py` runs 1 BFCL task end-to-end against each of 5 model configs (4 API + MLX), emitting valid JSONL per §3.
3. `intervention/rvr.py` correctly intercepts a hallucinated call → `Action.RE_PROMPT` with registry list rendered; one-retry cap enforced by runner (verified via fixture that hallucinates twice).
4. `cost_meter.py`: 10 synthetic calls produce hand-checked `total()` within 1e-9; threshold callback fires exactly once at 90%; `BudgetAbort` raised at 100%.
5. **Schema round-trip**: every JSONL line written during smoke run loads with `json.loads` and contains all 16 required fields; `schema_version=="1.0"`.
6. **Determinism**: re-running `load_bfcl(seed=0,n=10)` twice yields identical IDs in identical order; same for τ-bench loader.
7. **Stats sanity**: `paired_mcnemar_midp(b=10,c=2)` matches hand reference within 1e-6; `tehr_bootstrap_ci` 95% CI brackets point estimate on synthetic balanced sample; `tost_paired_proportions` returns `non_inferior=True` on identical inputs at margin=0.01.
8. **Redaction & no-leak**: trace_logger with deny-list including user email + API-key substrings → `grep -F` returns zero hits across all results JSONL; no adapter logs raw API keys.
9. **BFCL schema normalization**: passing a BFCL task through the loader → `task.registry` contains zero `"type": "dict"` strings (all rewritten to `"object"`); idempotent re-application is a no-op.
10. **MLX `enable_thinking=False`** verified by inspection: rendered prompt does not contain `<think>` tokens.

## 6. Open Questions Before Phase 1 Starts (HISTORICAL — see §8 for resolutions)

All questions resolved; see §8.

## 7. Architectural Concerns (flagged)

- **MLX shape contract** — verified at G0.5: regex parser works, repo is `mlx-community/Qwen3-8B-4bit` (not `-Instruct-4bit`), `enable_thinking=False` required.
- **Refusal detection is brittle** (deny-list). Will misclassify some refusals as `executed` (refusal+tool call) or `hallucinated` (refusal text containing fake tool name). Acceptable for v1; flagged.
- **`tool_executor` is the single biggest cross-cutting concern.** BFCL's executor is *stateful Python class instances per task* (dispatched via `getattr(instance, name)(**args)`); τ-bench's is the `MockRetailDomainEnv` (`step()`/`reset()` API). A4 implements two flavors with a common `Callable[[str, dict], dict]` interface; runner owns lifecycle (instantiate at task start, dispose at end). If τ-bench cut per v3.1 §6.3, only the BFCL flavor is needed.
- **120s timeout enforcement** in runner only. Adapters honor `dispatch` timeouts via SDK kwargs (Anthropic+OpenAI+xAI support; MLX doesn't — A3 uses `max_tokens` as proxy).
- **τ-bench user simulator** runs through Anthropic credits; cost meter must include simulator turns in the per-task tally.

## 8. Decisions Locked at T+00:00 (with G0.5 corrections)

These resolve §6's open questions; Phase-1 adapter agents implement against these.

### 8.1 Pinned model IDs (Q1 RESOLVED)

| Tier | Adapter | Production string | Dated alias (preferred) | $/1M in | $/1M out |
|---|---|---|---|---|---|
| Frontier | Anthropic | `claude-sonnet-4-6` | (rolling — query `/v1/models` at run-start; log to metadata) | $3.00 | $15.00 |
| Small    | Anthropic | `claude-haiku-4-5`  | `claude-haiku-4-5-20251001` | $1.00 | $5.00 |
| Frontier | OpenAI    | `gpt-4.1`           | `gpt-4.1-2025-04-14`        | $2.00 | $8.00 |
| Small    | OpenAI    | `gpt-4.1-mini`      | `gpt-4.1-mini-2025-04-14`   | $0.40 | $1.60 |
| Frontier (deferred to G2) | xAI | `grok-4`     | `grok-4-0709`               | $3.00 | $15.00 |
| Small    (deferred to G2) | xAI | `grok-4-fast`| (rolling)                    | $0.20 | $0.50 |
| Local    | MLX       | `mlx-community/Qwen3-8B-4bit` | (HF revision pinned at run-start) | $0    | $0    |

xAI uses the OpenAI SDK with `base_url="https://api.x.ai/v1"` — single adapter class, two providers.

### 8.2 Refusal deny-list (Q5 RESOLVED)

Frozen list, applied case-insensitively as a prefix match on the assistant text channel WHEN no tool call is present:

```python
REFUSAL_PHRASES: tuple[str, ...] = (
    "i can't",
    "i cannot",
    "i'm not able",
    "i won't",
)
```

Limitation: misclassifies the rare cases where the text channel contains both a refusal phrase and a tool call, or a refusal phrase from the user echoed back. Flagged in §7; acceptable for v1.

### 8.3 Raw provider payload retention (Q3 RESOLVED)

Default: drop `raw_provider_payload` before write. Set `TraceLogger(persist_raw=True)` only for adapter debugging — never for the main run.

### 8.4 τ-bench environment lifecycle (Q4 RESOLVED)

Runner owns the env lifecycle for the entire task: instantiate once at task start, pass `tool_executor` callable bound to the env, dispose at task end. No per-turn re-instantiation.

### 8.5 MLX HF repo (Q2 RESOLVED at G0.5, 2026-04-27)

Confirmed: **`mlx-community/Qwen3-8B-4bit`** (NOT `-Instruct-4bit` — the `-Instruct` suffix variant does not exist on HuggingFace; Qwen3 chat-tuned weights ship without the suffix). Throughput ~27 tok/s on M5/32GB; cold-load ~3.5 min; tokenizer chat template has full tools-aware Jinja with `<tool_call>{json}</tool_call>` envelope. **A3 MUST pass `enable_thinking=False` to `apply_chat_template`** — Qwen3's reasoning toggle defaults ON and injects `<think>...</think>` blocks that break the parser regex. Date-tolerant grading or a *"Today's date is 2026-04-27"* system-prompt hint required for downstream BFCL/τ-bench scoring (model defaults to training-cutoff year on relative dates).

### 8.6 SDK pinning (informational — for `pyproject.toml`)

```
anthropic>=0.96.0,<1.0.0
openai>=2.32.0,<3.0.0   # used for both OpenAI and xAI
mlx-lm>=0.31.0
scipy>=1.13.0
numpy>=1.26.0
statsmodels>=0.14.0
```

### 8.7 CostMeter abort thresholds (informational — per provider)

```
anthropic_meter = CostMeter(budget_usd=400.0)   # 80% of $500 credit
openai_meter    = CostMeter(budget_usd=2000.0)  # 80% of $2500 credit
xai_meter       = CostMeter(budget_usd=2000.0)  # 80% of $2500 credit
local_meter     = CostMeter(budget_usd=10.0)    # symbolic; MLX is $0
```

### 8.8 BFCL JSON-Schema normalization (NEW — discovered during dataset acquisition)

BFCL multi-turn task tool definitions use `"type": "dict"` instead of `"type": "object"` in JSON-Schema parameters. **All three target adapters reject this** (Anthropic `input_schema`, OpenAI `tools[*].function.parameters`, MLX/Qwen3 `apply_chat_template(tools=...)`). The `bench_loaders/bfcl.py` loader MUST apply `registry.py:_normalize_bfcl_schema` to every task before yielding so adapters see canonical OpenAI-shape registries. Helper is in `registry.py` (§2). Acceptance test in §5 item 9.

### 8.9 τ-bench user simulator routing (NEW — cost-routing decision)

τ-bench's default user simulator uses `gpt-4o` via litellm. To stay on YC credits and minimize paid spend, route the simulator to **Claude Haiku 4.5** via the Anthropic SDK. Estimated added cost: ~$3-5 against Anthropic credits (well within the $400 abort threshold). Loader patches `tau_bench/envs/retail/.../user_simulator.py` at load time (or via subclass) — exact patch point in `PHASE0/dataset_status.md` §4.3. The user-simulator turns are accumulated in the same `CostMeter` as the agent turns.

### 8.10 BFCL multi-turn staged user messages (NEW — runner contract)

BFCL multi-turn `question` is `list[list[message]]` — each inner list is one turn's incremental user message batch. The loader stores `question[0]` as `Task.initial_prompt` and `question[1:]` as `Task.expected_outcome["subsequent_user_messages"]`. **The runner MUST hand-feed these into the conversation between turns**: at the start of `turn_idx >= 1`, append `subsequent_user_messages[turn_idx - 1]` (a list of messages) to the conversation history before calling `adapter.dispatch`. Without this, multi-turn semantics collapse to single-turn and TEHR is biased.
