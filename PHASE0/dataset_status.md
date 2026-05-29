# Dataset Status — Phase 0 / Acquisition + Schema Audit

**Owner**: Phase-0 dataset-acquisition agent
**Date**: 2026-04-27
**Consumers**: Phase-1 agents A1 (Anthropic adapter), A2 (OpenAI adapter), A3 (MLX adapter), A4 (bench loaders + runner)
**Spec it must satisfy**: `harness/HARNESS_SPEC.md` §2 — `bench_loaders/bfcl.py`, `bench_loaders/tau_bench.py`, and the `Task` dataclass in `types.py`.

Status summary: **BOTH benchmarks acquired successfully**. Clones are pinned. Schemas are audited. Phase-1 loader agents (A4) and adapter agents (A1/A2/A3) have all the information they need below.

---

## 1. Acquisition

| Benchmark | Source | Path | Commit (pinned) | License |
|---|---|---|---|---|
| BFCL v4 (multi-turn) | `https://github.com/ShishirPatil/gorilla.git` (sparse-checkout `berkeley-function-call-leaderboard/`) | `/Users/cero/Desktop/PROJECTS/icml/harness/data/bfcl_v4/repo` | `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8` | Apache 2.0 |
| τ-bench (retail) | `https://github.com/sierra-research/tau-bench.git` (full clone, depth 1) | `/Users/cero/Desktop/PROJECTS/icml/harness/data/tau_bench_retail` | `59a200c6d575d595120f1cb70fea53cef0632f6b` | MIT (© 2024 Sierra) |

**Disk footprint** (`du -sh`):
- BFCL v4 clone: 57 MB (sparse-checkout filtered out model-result dumps)
- τ-bench clone: 65 MB
- **Total**: 122 MB — well under the 1 GB budget.

Re-pinning command for reproducibility:
```bash
cd harness/data/bfcl_v4/repo  && git checkout 6ea5797
cd harness/data/tau_bench_retail && git checkout 59a200c
```

License files:
- `harness/data/bfcl_v4/repo/LICENSE`  (Apache 2.0, root)
- `harness/data/tau_bench_retail/LICENSE` (MIT)

Attribution to include in the paper / artifact appendix:
> BFCL: Patil et al., Berkeley Function-Calling Leaderboard, Apache-2.0.
> τ-bench: Yao et al. (Sierra Research), MIT.

---

## 2. Directory Layout (what's where)

```
harness/data/
├── bfcl_v4/
│   └── repo/                                                  # sparse-checkout
│       └── berkeley-function-call-leaderboard/
│           ├── LICENSE                                        (Apache 2.0)
│           ├── bfcl_eval/
│           │   ├── data/
│           │   │   ├── BFCL_v4_multi_turn_base.json           (200 tasks, JSONL)
│           │   │   ├── BFCL_v4_multi_turn_long_context.json   (200, JSONL)
│           │   │   ├── BFCL_v4_multi_turn_miss_func.json      (200, JSONL)
│           │   │   ├── BFCL_v4_multi_turn_miss_param.json     (200, JSONL)
│           │   │   ├── multi_turn_func_doc/                   (12 *.json, JSONL of tool schemas, keyed by class)
│           │   │   └── possible_answer/
│           │   │       └── BFCL_v4_multi_turn_base.json       (200, ground-truth call lists)
│           │   ├── eval_checker/multi_turn_eval/
│           │   │   ├── multi_turn_utils.py                    (executor: execute_multi_turn_func_call)
│           │   │   ├── multi_turn_checker.py                  (oracle scorer)
│           │   │   └── func_source_code/                      (Python class implementations — the stateful tools)
│           │   └── constants/executable_backend_config.py     (CLASS_FILE_PATH_MAPPING, STATELESS_CLASSES)
└── tau_bench_retail/
    ├── LICENSE                                                (MIT)
    ├── tau_bench/
    │   ├── envs/
    │   │   ├── base.py                                        (Env: reset/step/calculate_reward)
    │   │   ├── user.py                                        (UserStrategy: HUMAN/LLM/REACT/VERIFY/REFLECTION)
    │   │   ├── tool.py                                        (Tool ABC)
    │   │   └── retail/
    │   │       ├── env.py                                     (MockRetailDomainEnv)
    │   │       ├── tasks_test.py                              (115 Task literals)
    │   │       ├── tasks_dev.py                               (20)
    │   │       ├── tasks_train.py                             (500)
    │   │       ├── tools/                                     (16 *.py, each a Tool subclass with get_info())
    │   │       ├── data/                                      (orders.json, products.json, users.json)
    │   │       ├── rules.py
    │   │       └── wiki.py
    │   ├── types.py                                           (Action, Task, EnvResponse, RewardResult, ...)
    │   └── agents/                                            (reference agents — we ignore)
```

---

## 3. BFCL v4 Schema Audit (3 sample tasks)

Each line of `BFCL_v4_multi_turn_base.json` is a JSON record with these keys:

| field | type | example |
|---|---|---|
| `id` | str | `"multi_turn_base_0"` |
| `question` | `list[list[{role,content}]]` | one outer list per turn; inner list usually 1 user message |
| `initial_config` | `dict[class_name → dict]` | per-class init kwargs for stateful instances |
| `path` | `list[str]` | hint of expected `Class.method` invocations (NOT used for scoring) |
| `involved_classes` | `list[str]` | which Python tool-classes the task instantiates |
| `excluded_function` | `list[str]` | functions to remove from the registry for this task |

**`function` field is `[]` in multi-turn** — tools are NOT inlined. The registry must be built by:
1. Read `involved_classes` from the task.
2. For each class, look up `MULTI_TURN_FUNC_DOC_FILE_MAPPING[cls]` in `bfcl_eval/constants/executable_backend_config.py` to get the JSONL file under `data/multi_turn_func_doc/`.
3. Concatenate tool entries; drop any whose `name` is in `excluded_function`.

Tool entries (one per JSONL line in `multi_turn_func_doc/*.json`):

```json
{
  "name": "cat",
  "description": "Display the contents of a file...",
  "parameters": {
    "type": "dict",                             // <-- BFCL writes "dict", not "object"
    "properties": { "file_name": { "type": "string", "description": "..." } },
    "required": ["file_name"]
  },
  "response": { "type": "dict", "properties": { "file_content": {"type":"string"} } }   // ignore
}
```

**Multi-turn task counts** (all JSONL, 200 tasks each):
- `multi_turn_base`: 200
- `multi_turn_long_context`: 200
- `multi_turn_miss_func`: 200  (registry intentionally omits a needed tool — relevant to RVR if we extend)
- `multi_turn_miss_param`: 200

Default split for our `n=50` BFCL sample: **`multi_turn_base`** (matches `HARNESS_SPEC.md` §2 default `split="multi_turn_base"`).

### 3.1 BFCL ground-truth oracle (`possible_answer/BFCL_v4_multi_turn_base.json`)

```json
{
  "id": "multi_turn_base_0",
  "ground_truth": [
    ["cd(folder='document')", "mkdir(dir_name='temp')", "mv(source='final_report.pdf', destination='temp')"],
    ["cd(folder='temp')", "grep(file_name='final_report.pdf', pattern='budget analysis')"],
    ...
  ]
}
```

`ground_truth: list[list[str]]`. Outer index = user-question turn. Each inner string is a **Python source-call expression** (NOT a JSON dict of args). Scoring compares **resulting class state** (deep state hash) after the model's calls vs. after ground-truth calls — see `multi_turn_checker.py`. So the reference is *trajectory-equivalent state*, not literal call match.

### 3.2 BFCL Tool-Executor Lifecycle — **STATEFUL per-task**

From `bfcl_eval/eval_checker/multi_turn_eval/multi_turn_utils.py::execute_multi_turn_func_call`:

```python
class_method_name_mapping = {}
for class_name in involved_classes:
    instance_name = f"{model_name}_{test_entry_id}_{class_name}_instance"
    if instance_name not in globals():
        module = importlib.import_module(CLASS_FILE_PATH_MAPPING[class_name])
        class_instance = getattr(module, class_name)()
        if class_name not in STATELESS_CLASSES:
            class_instance._load_scenario(copy.deepcopy(initial_config[class_name]), ...)
        globals()[instance_name] = class_instance
```

- Instance keyed by `(model_name, task_id, class_name)`, cached in `globals()`.
- Persists across turns within a task; each turn re-uses the same instance.
- `STATELESS_CLASSES = ["MathAPI"]` is the only stateless one.
- Calls are evaluated via Python `eval()` after rewriting `cat(...)` → `<instance>.cat(...)`.

**Implication for our runner**: A4's `tool_executor` for BFCL must:
1. At task start: instantiate the involved classes per `initial_config`, store on the per-task scratchpad (NOT globals — adapt to a dict on the runner).
2. Per turn: when the model emits a tool call `{name, arguments}`, dispatch to `getattr(instance, name)(**arguments)`.
3. At task end: optionally invoke BFCL's checker against `ground_truth` for `pass` boolean; or use a state-hash check.

The good news: **our `ToolCall` carries `arguments` as a dict already**. We do NOT need to parse Python-source-call strings *during the run* — those strings only matter to the offline scorer at end-of-task. The runner's executor just calls `getattr(instance, name)(**arguments)`.

### 3.3 Tools for stateful classes are *Python source files* — not data

`bfcl_eval/eval_checker/multi_turn_eval/func_source_code/{gorilla_file_system,trading_bot,...}.py` are real classes with `_load_scenario`, getters, setters. To execute calls, A4 must `pip install` BFCL eval as a package, OR import these files directly via `sys.path` injection. The cleanest path: add `/Users/cero/Desktop/PROJECTS/icml/harness/data/bfcl_v4/repo/berkeley-function-call-leaderboard` to `sys.path` in `bench_loaders/bfcl.py`, then `from bfcl_eval.eval_checker.multi_turn_eval.func_source_code import gorilla_file_system`. **Phase-1 A4 must not vendor or fork these files** — license is Apache-2.0 so it's allowed, but it bloats the harness and breaks update tracking.

| `multi_turn_func_doc/*.json` | tool count | source-class file |
|---|---|---|
| gorilla_file_system.json | 18 | `func_source_code/gorilla_file_system.py` |
| math_api.json | 17 | `math_api.py` (stateless) |
| memory_kv.json | 15 | `memory_kv.py` |
| memory_rec_sum.json | 5 | `memory_rec_sum.py` |
| memory_vector.json | 12 | `memory_vector.py` |
| message_api.json | 10 | `message_api.py` |
| posting_api.json | 14 | `posting_api.py` |
| ticket_api.json | 9 | `ticket_api.py` |
| trading_bot.json | 20 | `trading_bot.py` |
| travel_booking.json | 18 | `travel_booking.py` |
| vehicle_control.json | 22 | `vehicle_control.py` |
| web_search.json | 2 | `web_search.py` |

---

## 4. τ-bench Retail Schema Audit (3 sample tasks)

Tasks live in **Python source** (`tau_bench/envs/retail/tasks_test.py`), not JSON. Each is a `tau_bench.types.Task` Pydantic model:

```python
class Task(BaseModel):
    user_id: str           # e.g. "yusuf_rossi_9620"
    actions: List[Action]  # ground-truth tool-call sequence
    instruction: str       # the system-of-record description; user simulator paraphrases this
    outputs: List[str]     # optional substrings that must appear in the agent's final reply
```

`Action` = `{name: str, kwargs: dict}`.

**Three sample tasks** from `tasks_test.py` (slots 0, 1, 2):

| # | user_id | instruction snippet | actions count | outputs |
|---|---|---|---|---|
| 0 | `yusuf_rossi_9620` | exchange mech keyboard + thermostat | 5 | `[]` |
| 1 | `yusuf_rossi_9620` | exchange thermostat only (fallback rule) | 5 | `[]` |
| 2 | `yusuf_rossi_9620` | count tshirt options + return 3 items | 12 | `["10"]` |

**Task counts** (retail domain):
- `tasks_test.py` (TASKS_TEST): **115**  ← canonical evaluation split
- `tasks_dev.py`: 20
- `tasks_train.py`: 500

Default split for our `n=25` τ-bench sample: **TASKS_TEST**.

### 4.1 τ-bench tool schema — already OpenAI-canonical

Each tool inherits `tau_bench.envs.tool.Tool` and defines:
```python
class GetOrderDetails(Tool):
    @staticmethod
    def invoke(data, order_id) -> str:  # mutates `data`, returns str
        ...
    @staticmethod
    def get_info() -> dict:
        return {
            "type": "function",
            "function": {
                "name": "get_order_details",
                "description": "...",
                "parameters": {
                    "type": "object",                # <-- "object", not "dict" — ALREADY OPENAI-shaped
                    "properties": {"order_id": {"type":"string","description":"..."}},
                    "required": ["order_id"]
                }
            }
        }
```

The 16 retail tools (`tau_bench/envs/retail/tools/__init__.py::ALL_TOOLS`):
`Calculate, CancelPendingOrder, ExchangeDeliveredOrderItems, FindUserIdByEmail, FindUserIdByNameZip, GetOrderDetails, GetProductDetails, GetUserDetails, ListAllProductTypes, ModifyPendingOrderAddress, ModifyPendingOrderItems, ModifyPendingOrderPayment, ModifyUserAddress, ReturnDeliveredOrderItems, Think, TransferToHumanAgents`.

### 4.2 τ-bench Tool-Executor Lifecycle — **stateful Env per task**

From `tau_bench/envs/base.py`:
- `Env.__init__` builds `self.data = data_load_func()` (deep copy of orders/products/users JSON).
- `env.reset(task_index)` re-loads data and selects task `i`.
- `env.step(action)` mutates `self.data` and returns `EnvResponse(observation, reward, done, info)`.
- Termination: when the model invokes `transfer_to_human_agents` (a tool in `terminate_tools`) OR the user simulator emits `###STOP###`.
- Reward is computed at `done=True` by `calculate_reward()`: re-runs the ground-truth `task.actions` against a *fresh* copy of data and compares **data-state SHA-256 hashes**. Output checks (substring match in any `respond` action's content) are `AND`-ed.

**Implication for our runner**: A4 must:
1. Per task: `env = MockRetailDomainEnv(user_strategy="llm", user_model=??, task_split="test", task_index=i)`.
2. Loop: send the user's first message (from `env.reset()` — the simulator-paraphrased instruction), the model emits a tool call, A4 maps it to `Action(name=..., kwargs=...)`, calls `env.step(action)`, feeds `observation` back to the model.
3. Read `pass` from the final `EnvResponse.reward` (1.0 = pass, 0.0 = fail).

### 4.3 τ-bench User-Simulator caveat — **THIS IS A PAID-API DEPENDENCY**

The default `user_strategy="llm"` instantiates an `LLMUserSimulationEnv` that calls `litellm.completion(model=..., custom_llm_provider=...)` with a hard-coded default `user_model="gpt-4o"`. **Each τ-bench task makes 2-N OpenAI calls just for the user simulator**, in addition to the calls our agent-under-test makes. Three options for Phase 1:

1. **Set `user_model="gpt-4.1-mini"` and `user_provider="openai"`** — accept the cost; budget it.
2. **Set `user_strategy="react"` with same cheap model** — slightly more reliable simulator.
3. **Replace user with a deterministic stub** that replays `task.instruction` verbatim and `###STOP###` after N turns — *not* canonical τ-bench; not paper-claim defensible.

**Recommendation for Phase 1**: option 1 with `gpt-4.1-mini`; estimate ~$0.01-0.03 per task × 25 tasks × 3 conditions × 5 model configs ≈ $11-12 sim cost. Add to `cost_meter.py` budget plan. **A4 must surface this in `bench_loaders/tau_bench.py` config** so the runner knows to expect simulator API calls.

---

## 5. `Task` Dataclass Mapping Tables

`Task` from `harness/types.py`:

```python
@dataclass(frozen=True)
class Task:
    id: str
    benchmark: Literal["bfcl","tau_bench"]
    registry: dict[str, dict]
    initial_prompt: str
    turns_max: int
    expected_outcome: dict
```

### 5.1 BFCL → Task mapping

| `Task.field` | source | conversion |
|---|---|---|
| `id` | `record["id"]` (e.g. `"multi_turn_base_0"`) | prefix optional: `f"bfcl_{record['id']}"` for trace clarity |
| `benchmark` | constant | `"bfcl"` |
| `registry` | union of `multi_turn_func_doc/<cls>.json` for each `cls in record["involved_classes"]`, minus names in `record["excluded_function"]` | Build `{tool_name: tool_schema_dict}`; **convert `"type":"dict"` → `"type":"object"`** in `parameters`; drop `"response"` field. |
| `initial_prompt` | `record["question"][0][0]["content"]` | First user message of turn 0. **Note**: subsequent turns' messages live at `record["question"][i][0]["content"]` and are revealed turn-by-turn during the rollout — runner must feed them when the model finishes turn `i` and we move to turn `i+1`. |
| `turns_max` | `len(record["question"])` (typical 4-5) | Cap at HARNESS_SPEC default `8`; `min(len(question), 8)`. |
| `expected_outcome` | `{"ground_truth": possible_answer[id]["ground_truth"], "initial_config": record["initial_config"], "involved_classes": record["involved_classes"]}` | The runner / scorer needs `initial_config` + `involved_classes` to instantiate the per-task tool executor. The `ground_truth` is consumed by the BFCL checker post-hoc. |

### 5.2 τ-bench retail → Task mapping

| `Task.field` | source | conversion |
|---|---|---|
| `id` | `f"tau_retail_{task_index}"` | (no native string ID; use index in TASKS_TEST) |
| `benchmark` | constant | `"tau_bench"` |
| `registry` | `[Tool.get_info() for Tool in ALL_TOOLS]` re-keyed `{name: schema}` | Already OpenAI-shape — for Anthropic adapter, peel `entry["function"]` and rename `parameters` → `input_schema`. |
| `initial_prompt` | `env.reset(task_index).observation` | Returned by user simulator on reset; **NOT** `task.instruction` directly. Note this means the loader CAN'T pre-populate this without an Env instance + a paid API call — the loader should leave `initial_prompt=""` and have the runner fetch it post-`reset()`, OR load with `user_strategy="human"` for testing. **Recommendation**: A4 sets `Task.initial_prompt=task.instruction` (the canonical scripted version) for offline reproducibility and lets the runner replace with `env.reset()` output at execution time. |
| `turns_max` | spec default `8` | τ-bench has no per-task turn cap; HARNESS_SPEC §2 fixes 8. |
| `expected_outcome` | `{"task_index": i, "user_id": task.user_id, "instruction": task.instruction, "actions": [a.model_dump() for a in task.actions], "outputs": task.outputs}` | The runner's tool_executor uses `task_index` to call `MockRetailDomainEnv(task_index=i)`; the env itself is the oracle. `actions` and `outputs` are stored for offline analysis only; runner uses live `EnvResponse.reward`. |

---

## 6. Schema-Conversion Notes for the 3 Adapters

**A1 — AnthropicAdapter (`adapters/anthropic_adapter.py`)**

Anthropic tool schema:
```python
{"name": "get_weather", "description": "...", "input_schema": {"type":"object", "properties":{...}, "required":[...]}}
```
- Strip the OpenAI `{"type":"function","function":{...}}` wrapper if present (τ-bench tools have it; BFCL tools don't).
- Rename `parameters` → `input_schema`.
- **BFCL-specific**: replace `"type":"dict"` with `"type":"object"` recursively in `input_schema`.
- Drop the BFCL `response` field — Anthropic ignores it.

**A2 — OpenAIAdapter (`adapters/openai_adapter.py`)**

OpenAI tool schema:
```python
{"type":"function","function":{"name":"...","description":"...","parameters":{"type":"object",...}}}
```
- τ-bench: pass through verbatim (it's already this shape).
- BFCL: wrap `{"type":"function", "function": entry}` and again **replace `"dict"` → `"object"`** in `parameters`.

**A3 — MLXAdapter (`adapters/mlx_adapter.py`)**

Qwen3 chat template's `tools=` slot wants OpenAI-shaped tool dicts (same as A2). Render with:
```python
prompt = tokenizer.apply_chat_template(messages, tools=tool_list, add_generation_prompt=True)
```
where `tool_list` is the OpenAI-shaped list. So **MLX adapter converts tools the same way A2 does**: BFCL → wrap+rename `"dict"`→`"object"`; τ-bench → passthrough.

### 6.1 The single most important conversion gotcha

**BFCL writes `"type": "dict"` instead of `"type": "object"` in JSON-Schema. Every adapter that emits JSON-Schema-conformant tool definitions (Anthropic `input_schema`, OpenAI `function.parameters`, Qwen3 chat-template `tools=`) must rewrite this recursively before dispatch. Failing to do so causes silent tool-rejection on Anthropic and OpenAI (the SDK 400s with "invalid schema") and causes Qwen3 to render malformed tool prompts.**

A4's `bench_loaders/bfcl.py` should normalize the schema **once** at load time so all three adapters can treat the `Task.registry` as already-canonical OpenAI-shape with `"object"`. Recommended helper signature:

```python
def _normalize_bfcl_schema(s: dict) -> dict:
    if isinstance(s, dict):
        if s.get("type") == "dict":
            s = {**s, "type": "object"}
        return {k: _normalize_bfcl_schema(v) for k, v in s.items()}
    if isinstance(s, list):
        return [_normalize_bfcl_schema(x) for x in s]
    return s
```

---

## 7. Tool-Executor Lifecycle Summary (HARNESS_SPEC §7)

| Aspect | BFCL multi-turn | τ-bench retail |
|---|---|---|
| State scope | per-task | per-task |
| Implementation | Python class instances (e.g. `GorillaFileSystem`) instantiated from `initial_config` | `MockRetailDomainEnv` wrapping `data = {orders, products, users}` |
| Per-turn or per-task? | **per-task** instance, calls dispatched per turn | **per-task** Env, `step()` called per turn |
| Reset between turns | NO — state must persist | NO — state must persist |
| Reset between tasks | YES — fresh instances | YES — `env.reset(task_index)` reloads data |
| Tool call dispatch | `getattr(instance, call.name)(**call.arguments)` | `env.step(Action(name=call.name, kwargs=call.arguments))` |
| Done/termination signal | none from tool side; runner caps at `turns_max` | `EnvResponse.done` (set when `transfer_to_human_agents` called or user emits `###STOP###`) |
| Pass/fail oracle | post-task: `multi_turn_checker.py` compares state hash to ground-truth-replay state hash | live: `EnvResponse.reward` ∈ {0.0, 1.0} on `done=True` |

A4 implements **two `tool_executor` callables** with the same `(call: ToolCall) → str | dict` signature, but very different setup/teardown lifecycles. Recommend a thin `ToolExecutor` protocol with `setup(task) → state`, `step(state, call) → result`, `teardown(state) → pass_bool`.

---

## 8. Gotchas / Edge Cases for A4 (and adapter agents)

1. **BFCL `"type":"dict"`**: see §6.1. THE conversion bug to avoid.
2. **BFCL multi-turn `question` is staged**: `record["question"]` is `list[list[message]]`, one outer list per user turn. The agent gets `question[0][0]["content"]` first; after it finishes, the runner injects `question[1][0]["content"]` as the next user turn. Loader must put `question[1:]` somewhere in `Task.expected_outcome` (e.g. `{"subsequent_user_messages": [...]}`) or the runner can't hand-feed them.
3. **BFCL `excluded_function` is per-task**: registry must be filtered per task — DO NOT cache a global registry per class.
4. **BFCL `function` field is empty in multi-turn** but non-empty in single-turn (`BFCL_v4_simple_python.json` etc., out-of-scope here). If we ever extend, branch on `record.get("function")`.
5. **τ-bench `task.outputs` may be empty** (most retail tasks). When non-empty, the agent's final `respond` must contain each substring (case-insensitive, comma-stripped — see `base.py::calculate_reward`). Runner must capture the agent's plain-text turns as candidate `respond` actions or auto-emit `respond(content=last_message)` at end-of-task.
6. **τ-bench user simulator costs money** (§4.3). Must be in cost_meter budget.
7. **τ-bench `transfer_to_human_agents` is a terminate tool** but is also the canonical "I give up" signal — agents legitimately use it. Don't classify it as `refused`. The `terminate_tools=["transfer_to_human_agents"]` list is the source of truth.
8. **τ-bench `Think` tool** is a no-op designed to give the model a thinking-step token budget — its `invoke` just returns "". Treat normally; it counts against tool-call budget.
9. **BFCL `STATELESS_CLASSES = ["MathAPI"]`** — singleton allowed; everything else needs deep-copied init.
10. **BFCL `MULTI_TURN_FUNC_DOC_FILE_MAPPING`** values point to JSONL filenames in `multi_turn_func_doc/`. The loader must `import` from `bfcl_eval.constants.executable_backend_config` (or vendor the dict — pick the former; less drift).
11. **Refusal deny-list in HARNESS_SPEC §6.5** — beware τ-bench task #1's instruction "If there is no keyboard..." starts with "If" but contains "I'd rather only" which has "I'd" — substring match must be **prefix or whole-word**, not substring. (Already in spec as "case-insensitive prefix match" — confirmed safe.)

---

## 9. Phase-1 Adapter Agent Prerequisites

### A1 — Anthropic adapter agent
- Read §6 for `parameters → input_schema` rename.
- Be defensive against BFCL `"type":"dict"` even if A4 normalizes (defense-in-depth via a single helper).
- For fixtures, mirror the 4 cases in HARNESS_SPEC §4 — no extra dataset knowledge needed; tool calls are independent of which dataset they came from at adapter level.

### A2 — OpenAI adapter agent
- Same. Tools come in OpenAI shape from A4's loader; passthrough.
- The `arguments` field is **JSON-string** in OpenAI's response — `json.loads`; on `JSONDecodeError`, set `parse_ok=False`. (HARNESS_SPEC §2 already mandates this.)

### A3 — MLX adapter agent
- Tools are OpenAI shape; `apply_chat_template(..., tools=tools, add_generation_prompt=True)`.
- Verify `mlx-community/Qwen3-8B-Instruct-4bit` has tool-call template support (HARNESS_SPEC §6.2 G0.5 probe).
- Output regex: `<tool_call>\s*({.*?})\s*</tool_call>` on a multi-line `re.DOTALL` flag; `json.loads` the captured group; on failure → `parse_ok=False` per spec §4 fixture #4.

### A4 — bench loaders + runner agent
- Implement `_normalize_bfcl_schema` (§6.1) and apply at load time.
- BFCL loader: import from `bfcl_eval.constants.executable_backend_config`; assemble registry from `multi_turn_func_doc/`; carry `initial_config` and `involved_classes` in `Task.expected_outcome` so runner can stand up the executor. Stage subsequent user messages in `expected_outcome["subsequent_user_messages"]`.
- τ-bench loader: build registry from `[t.get_info() for t in ALL_TOOLS]`; carry `task_index` in `expected_outcome` so runner can `MockRetailDomainEnv(task_index=...)`.
- Runner: implement two `tool_executor` factories (BFCL stateful-classes vs. τ-bench Env). The protocol is: `executor = make_executor(task); for call in agent: result = executor.step(call); ...; pass_ = executor.teardown()`.
- Determinism: `random.Random(seed).sample(all_tasks, n)` for the loader's task selection. Confirmed both task sources are deterministic-indexable (BFCL JSONL line order is stable; τ-bench `TASKS_TEST` is a Python list literal).

---

## 10. Open Questions / Decisions Needed from M (the maintainer)

1. **τ-bench user-simulator model**: lock to `gpt-4.1-mini` via `user_model="gpt-4.1-mini"`, `user_provider="openai"`? Cost ~$11-12 across the full sweep. Alternative: cut τ-bench from ICML run (HARNESS_SPEC §6.3 already flags a kill-switch).
2. **BFCL split selection**: Phase 1 default `multi_turn_base` only? Or include `multi_turn_miss_func` (which is *exactly* the hallucination-induction setup we want — registry deliberately omits a needed tool, very on-thesis for SCALE)?
3. **Task ID prefix in trace logs**: `bfcl_multi_turn_base_0042` vs. raw `multi_turn_base_0042`? The trace `benchmark` field disambiguates already, so raw is fine.
4. **τ-bench reward coarseness**: τ-bench reward is binary {0,1} per task — fine for our pass-rate metric, but TEHR (per-call hallucination rate) is fully orthogonal and benchmark-agnostic, so no impact.

---

## 11. Status — Ready for Phase 1

- [x] BFCL v4 cloned + audited (200 multi_turn_base tasks, schema understood, executor lifecycle documented)
- [x] τ-bench retail cloned + audited (115 test tasks, OpenAI-shape tools, Env API documented)
- [x] License compliance verified (Apache 2.0 + MIT)
- [x] Disk under budget (122 MB / 1 GB)
- [x] Conversion gotchas catalogued (the `"dict"`→`"object"` is the big one)
- [x] Tool-executor lifecycle clarified for both benchmarks (per-task stateful, dispatch per turn)
- [x] Adapter prerequisites enumerated per agent

**Phase 1 can start.** A4 owns the loader implementation; A1/A2/A3 can implement adapters in parallel using fixture-only tests without needing the loaders.
