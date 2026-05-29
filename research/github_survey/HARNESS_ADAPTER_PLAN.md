# Harness Adapter Plan — adding new benchmark loaders to `harness/bench_loaders/`

**Author role:** harness-adapter planner · **Date:** 2026-05-29
**Status:** PLAN ONLY — no harness file is edited here. The harness is busy; this is a
spec another worker (or a later session) executes against `harness/`.

**Inputs read (verified against on-disk code, not spec):**
- `research/github_survey/synth_paper-benchmarks-to-run.md` (ranking #1 BFCL single-turn, #2 Seal-Tools, #3 RestBench)
- `research/github_survey/synth_harness-components.md` (same ordering from the components angle)
- `harness/bench_loaders/{bfcl.py, tau_bench.py}`, `harness/types.py`, `harness/registry.py`,
  `harness/runner/{loop.py, executors.py, cli.py}`, `harness/tests/test_bfcl_loader.py`
- On-disk data audit (see "Data reality check" below)

---

## Data reality check (what is actually on disk RIGHT NOW)

| Pick | Survey rank | Data on disk? | Consequence |
|------|-------------|---------------|-------------|
| **BFCL single-turn + irrelevance/live** | #1 | **YES** — vendored | Buildable today, **zero new download**. |
| Seal-Tools | #2 | **NO** — only `research/github_survey/repo_Seal-Tools.md` | Needs a vendoring step first; planned but gated. |
| RestBench | #3 | **NO** — not present | Needs a vendoring step first; planned but gated. |

Confirmed present under
`harness/data/bfcl_v4/repo/berkeley-function-call-leaderboard/bfcl_eval/data/`:
`BFCL_v4_simple_python.json`, `..._simple_java.json`, `..._simple_javascript.json`,
`BFCL_v4_multiple.json`, `BFCL_v4_parallel.json`, `BFCL_v4_parallel_multiple.json`,
`BFCL_v4_irrelevance.json`, `BFCL_v4_live_irrelevance.json`, `BFCL_v4_live_relevance.json`,
plus `BFCL_v4_live_{simple,multiple,parallel,parallel_multiple}.json` and
`possible_answer/` files for everything **except** the irrelevance/relevance splits
(verified: `possible_answer/BFCL_v4_irrelevance.json` does **not** exist — by design;
those splits have no gold call).

**Decision:** Top-recommended loader to add now = **BFCL single-turn (the #1 pick)**,
implemented as an **extension of the existing `bfcl.py`** (the synth explicitly says
"extend `bfcl.py`, NOT a new file"). Seal-Tools and RestBench are specced below as
the next two new files but are **blocked on a data-vendoring step** and should not be
started until their data lands under `harness/data/`.

---

## Record-shape audit (single-turn BFCL) — the load-bearing difference from multi-turn

A single-turn record (`head -1 BFCL_v4_simple_python.json`) has **only three keys** and
the registry is carried **inline** on the record, not assembled from `involved_classes`:

```
KEYS:  ['id', 'question', 'function']
id:    "simple_python_0"
question: [[{"role":"user","content":"Find the area of a triangle ..."}]]   # same nested shape as multi-turn question[0]
function: [ {"name":"calculate_triangle_area","description":"...",
             "parameters":{"type":"dict","properties":{...},"required":[...]}} ]   # list of tool schemas
```

Implications for the loader (each verified against `bfcl.py`/`registry.py`):
1. **No `involved_classes`, no tool-doc files, no `_load_tool_docs`/`_build_registry`.**
   The registry is `record["function"]` — a list of tool schemas — keyed by `name`.
2. **Same normalizer reused unchanged.** Each function dict has `"type":"dict"`;
   `harness.registry._normalize_bfcl_schema` already rewrites that to `"object"`
   (and `float→number`, etc.), idempotently. This is the same one-function normalizer
   `bfcl.py` already imports — **no new normalizer needed for BFCL single-turn.**
3. **`question` is the same nested list-of-message-lists**, so `_extract_initial_prompt`
   (already in `bfcl.py`) can be reused verbatim.
4. **`multiple` and `parallel*` carry >1 function**; `simple_*` carry exactly 1. The
   registry build must iterate the whole `function` list (`multiple_0` has 2 functions,
   `parallel*` similar). A duplicate-name guard mirroring the existing
   `_build_registry` collision `UserWarning` is appropriate.
5. **Irrelevance/relevance/live-irrelevance have no `possible_answer`.** `expected_outcome`
   must tolerate a missing ground truth (`None`), exactly as the runner already tolerates
   `ground_truth=None` for multi-turn (it's metadata; TEHR never reads it).
6. **`id` is `simple_python_0`, `multiple_3`, `irrelevance_12`, `live_irrelevance_4`, …**
   The new Tasks keep the existing `f"bfcl_{task_id}"` id scheme, so they stay in the
   `bfcl` benchmark namespace and require **no new `BenchmarkName` literal**.

---

## PART A — BFCL single-turn (#1): extend `harness/bench_loaders/bfcl.py` (DO NOW)

### A.1 New module-level constants (add alongside `_VALID_SPLITS`)

```
_VALID_SINGLE_TURN_SPLITS = (
    "simple_python", "simple_java", "simple_javascript",
    "multiple", "parallel", "parallel_multiple",
    "irrelevance", "live_irrelevance", "live_relevance",
    "live_simple", "live_multiple", "live_parallel", "live_parallel_multiple",
)
_SINGLE_TURN_TURNS_MAX = 1          # single dispatch per task
# splits that legitimately have no gold call (abstention axis) → ground_truth stays None
_NO_GOLD_SPLITS = frozenset({"irrelevance", "live_irrelevance", "live_relevance"})
```

File path per split: `data_dir / "bfcl_eval" / "data" / f"BFCL_v4_{split}.json"`
(reuses `_resolve_data_dir`, `DEFAULT_DATA_DIR`, `_read_jsonl` already in the file).

### A.2 New function `load_bfcl_single_turn(...)` (sibling of `load_bfcl`)

Signature mirrors `load_bfcl` exactly so the CLI wiring is uniform:

```
def load_bfcl_single_turn(
    split: str = "simple_python",
    n: int = 100,
    seed: int = 0,
    data_dir: str | Path | None = None,
) -> Iterator[Task]:
```

Body (mirrors `load_bfcl`'s structure; reuses its helpers):
1. Validate `split in _VALID_SINGLE_TURN_SPLITS`, else `ValueError` (same idiom as the
   existing multi-turn validation).
2. Resolve `task_path`; `FileNotFoundError` if absent (same as `load_bfcl`).
3. `raw_tasks = _read_jsonl(task_path)`.
4. Optional gold: `ground_truth_map = _load_ground_truth_single_turn(root, split)` — a
   thin variant of the existing `_load_ground_truth` that reads
   `possible_answer/BFCL_v4_{split}.json` **and returns `{}` for `_NO_GOLD_SPLITS`** (the
   file does not exist there; `_load_ground_truth` already returns `{}` on a missing file,
   so this can simply call the existing `_load_ground_truth` and rely on that fallback —
   no new function strictly required).
5. Deterministic sampling identical to `load_bfcl`:
   `rng = Random(seed); chosen_idx = sorted(rng.sample(range(len(raw_tasks)), min(n, len(raw_tasks))))`.
6. For each chosen record build the **registry from `rec["function"]`**:

```
def _registry_from_function_list(functions, task_id):
    registry = {}
    for fn in functions:
        normalized = _normalize_bfcl_schema(dict(fn))   # rewrites type:dict -> object
        name = normalized["name"]
        if name in registry:
            warnings.warn(f"BFCL single-turn task {task_id!r}: duplicate tool name "
                          f"{name!r}; later wins.", stacklevel=2)
        registry[name] = normalized
    return registry
```
   (Mirror of `_build_registry`'s normalize+collision-guard, minus the class/file plumbing.)

7. `initial_prompt = _extract_initial_prompt(rec.get("question", []))` (reuse as-is).
8. Emit Task:

```
Task(
    id=f"bfcl_{rec['id']}",                 # e.g. "bfcl_simple_python_0"
    benchmark=_BENCHMARK,                    # "bfcl" — NO new literal
    registry=registry,
    initial_prompt=initial_prompt,
    turns_max=_SINGLE_TURN_TURNS_MAX,        # 1
    expected_outcome={
        "ground_truth": ground_truth_map.get(rec["id"]),   # None for irrelevance splits
        "subsequent_user_messages": [],                    # single-turn: empty
        "initial_config": {},
        "involved_classes": [],                            # none; signals stub-executor path
        "single_turn_split": split,                        # provenance for the analysis layer
    },
)
```

**Why `subsequent_user_messages: []` + `involved_classes: []` matters:** the runner's
existing BFCL branch (`loop.py:243`) calls `_append_user_turn(history, subsequent, turn_idx)`
which is a **no-op when `subsequent` is empty**, and the loop body already breaks after a
no-call turn for Anthropic (`loop.py:389`). With `turns_max=1` the loop runs exactly one
dispatch, classifies it (`call.name not in active_registry` at `loop.py:177` — the TEHR
predicate), logs it, and exits. **No `loop.py` edit is required for single-turn BFCL** —
this is the decisive cheapness of staying inside the `bfcl` benchmark name.

### A.3 Executor for single-turn BFCL — the ONE touch-point outside the loader

`make_bfcl_executor` (`executors.py:57`) builds a `method_owner` map from
`involved_classes`. With `involved_classes == []` the map is empty, so **every call returns
`{"error": "AttributeError: <name>", "type": "AttributeError"}`**. For TEHR that is
harmless (TEHR is computed *before* the executor runs, on the name-vs-registry predicate at
`loop.py:177`), but it would mark `pass=False` for every single-turn task via
`saw_executor_error` (`loop.py:299, 413`). Since single-turn BFCL is a **TEHR-only**
measurement (no stateful backend exists for these splits), the correct executor is a
**stub** that returns `{"output": "ok"}`.

Recommended wiring (the only edit needed beyond the loader): in
`harness/runner/cli.py::_make_executor` (currently lines 171-175), branch on
`task.expected_outcome.get("involved_classes")`:

```
def _make_executor(task):
    from harness.runner.executors import (
        make_bfcl_executor, make_tau_bench_executor, make_stub_executor,
    )
    if task.benchmark == "tau_bench":
        return make_tau_bench_executor(task)
    if task.benchmark == "bfcl" and not (task.expected_outcome or {}).get("involved_classes"):
        return make_stub_executor(task)      # single-turn: no stateful backend
    return make_bfcl_executor(task)
```

And add `make_stub_executor` to `executors.py` (≈6 lines, mirrors the factory contract
`Callable[[str, dict], dict]`):

```
def make_stub_executor(task: Task) -> Callable[[str, dict], dict]:
    """No-op executor for registry-only / single-turn benchmarks. TEHR is computed
    from the name-vs-registry predicate before this runs; success keeps pass=True."""
    def executor(name: str, args: dict) -> dict:
        return {"output": "ok"}
    return executor
```

This stub is **reused verbatim by Seal-Tools and RestBench** (Parts B/C), so it is shared
infrastructure, not BFCL-specific.

### A.4 CLI exposure (optional, low effort)

`cli.py::_load_tasks` (lines 162-169) currently only knows `load_bfcl` for `bench=="bfcl"`,
keyed on `args.bfcl_split`. To run single-turn from the CLI, extend the `bfcl` branch to
dispatch to `load_bfcl_single_turn` when `args.bfcl_split` is one of
`_VALID_SINGLE_TURN_SPLITS`, and add those values to the `--bfcl-split` `choices` list
(cli.py:80-84). This is a CLI-ergonomics edit, not required for the smoke test (the smoke
test imports the loader directly).

### A.5 Test (mirror `tests/test_bfcl_loader.py`)

Add `tests/test_bfcl_single_turn_loader.py` mirroring the existing fixture style: write a
2-record synthetic `BFCL_v4_simple_python.json` (each with inline `function` carrying a
`"type":"dict"` block) under `tmp_path/bfcl_eval/data/`, then assert:
- IDs prefixed `bfcl_`, `turns_max == 1`, `benchmark == "bfcl"`.
- No surviving `"type":"dict"` anywhere in `registry` (run `validate_registry`).
- Deterministic order for a fixed seed.
- `irrelevance` split with no `possible_answer` file → `ground_truth is None`, no raise.
- Happy-path: `load_bfcl_single_turn("simple_python", n=3)` against real on-disk data.

---

## PART B — Seal-Tools (#2): new `harness/bench_loaders/seal_tools.py` (GATED on vendoring)

**Blocker:** data is not on disk. Pre-req step (separate from this loader work): vendor
`fairyshine/Seal-Tools` (Apache-2.0) data-only into `harness/data/seal_tools/`:
`tool.jsonl` (4076 tool specs), `test_in_domain.jsonl` (700), `test_out_domain.jsonl` (654).
Do **not** vendor `LLM_Evaluation/calculate.py` (uses `eval()` / `match`). Add a NOTICE entry.

### B.1 New `BenchmarkName` literal — REQUIRED here

`harness/types.py:31` is `BenchmarkName = Literal["bfcl", "tau_bench"]`. Add `"seal_tools"`:
```
BenchmarkName = Literal["bfcl", "tau_bench", "seal_tools"]
```

### B.2 Schema normalizer (the real work — analogous to `_normalize_bfcl_schema`)

Seal-Tools params look like `{"<param>": {"type":"str","description":...}}` plus a
top-level `required` list, **not** JSON-Schema. Add a loader-local
`_seal_to_openai_schema(tool_record) -> dict` that emits canonical-inner shape:
```
{
  "name": rec["name"],
  "description": rec.get("description", ""),
  "parameters": {
      "type": "object",
      "properties": { p: {"type": _SEAL_TYPE_REMAP.get(t, "string"), "description": d}
                      for p,(t,d) in rec["parameters"].items() },
      "required": list(rec.get("required", [])),
  },
}
```
with `_SEAL_TYPE_REMAP = {"str":"string","int":"integer","float":"number","bool":"boolean",
"list":"array","dict":"object"}`. Run output through `validate_registry` in the test.

### B.3 `load_seal_tools(split, n, seed, registry_mode, data_dir)`

- `split ∈ {"in_domain","out_domain"}` → reads the matching `test_*.jsonl`.
- `registry_mode ∈ {"full","candidate"}` (the load-bearing ablation the synth flags):
  `"full"` → registry = all 4076 tools from `tool.jsonl` (large-registry stress regime);
  `"candidate"` → registry = only the tools referenced by that row's gold `calling` list
  (BFCL-like small-registry regime). **Run both as an ablation** (answers "does registry
  size drive TEHR?").
- Emit one Task per row: `id=f"seal_{split}_{i}"`, `benchmark="seal_tools"`, `turns_max=1`,
  `registry` per `registry_mode`, `initial_prompt=row["query"]`,
  `expected_outcome={"gold_calls": row["calling"], "split": split, "registry_mode": registry_mode}`.
- **Executor:** `make_stub_executor` (Part A.3) — `responses` are spec-only `API_call_N`
  placeholders; TEHR only inspects emitted names.

### B.4 Runner/CLI touch-points

- `loop.py`: `seal_tools` falls into the **`else` branch** of the benchmark dispatch
  (`loop.py:231` — `active_registry = task.registry`, plain `[{"role":"user",...}]` history).
  With `turns_max=1` it behaves exactly like single-turn BFCL. **No `loop.py` edit needed**
  beyond what already handles the generic single-turn case — confirm the non-Anthropic break
  conditions (`loop.py:389-403` are scoped to `bfcl`/`tau_bench`; a `seal_tools` no-call turn
  on Anthropic would not hit the `loop.py:389` break, but with `turns_max=1` the `for` loop
  ends anyway, so it is safe). If any adapter raises on an assistant-tail dispatch, that only
  matters for `turns_max>1`; single-turn is unaffected.
- `cli.py`: add `seal_tools` to `_load_tasks`, to the `--benchmark` `choices`, and route its
  executor to `make_stub_executor` in `_make_executor`.

---

## PART C — RestBench (#3): new `harness/bench_loaders/restbench.py` (GATED on vendoring)

**Blocker:** data not on disk. Pre-req: vendor `Yifan-Song793/RestGPT` (MIT) **data + specs
only** into `harness/data/restbench/`: `datasets/tmdb.json` (100), `datasets/spotify.json`
(57), `specs/tmdb_oas.json`, `specs/spotify_oas.json`. Do **not** vendor `run.py`
(dead `text-davinci-003` + pre-0.1 langchain). NOTICE entry.

### C.1 `BenchmarkName` literal: add `"restbench"`.

### C.2 OpenAPI→registry normalizer (the work)

Add loader-local `_oas_to_registry(oas_spec) -> dict`: enumerate every
`paths[<path>][<method>]` operation into a canonical-inner tool where:
- **tool name = `"<METHOD> <path>"`** e.g. `"GET /search/person"` (define this convention
  once and make the agent instructions match it; the registry name is the existence key).
- `description` = operation `summary`/`description`.
- `parameters` = `{"type":"object","properties": …, "required": […]}` assembled from the
  OpenAPI `parameters` array (query/path) + `requestBody` schema. Map OpenAPI types directly
  (they are already JSON-Schema 2020-12-compatible); pass any `$ref`-resolved sub-schemas
  through unchanged. Run through `validate_registry`.

### C.3 `load_restbench(domain, n, seed, data_dir)`

- `domain ∈ {"tmdb","spotify"}` (or `"all"` → both, 157 tasks total).
- registry = `_oas_to_registry` of the matching `*_oas.json` (bounded: 54 TMDB / 40 Spotify ops).
- One Task per `datasets/*.json` row: `id=f"rest_{domain}_{i}"`, `benchmark="restbench"`,
  `turns_max=1`, `initial_prompt=row["query"]`,
  `expected_outcome={"gold_solution": row["solution"], "domain": domain}`.
- **Executor:** `make_stub_executor`. No live TMDB/Spotify keys (frozen specs only → no
  endpoint drift).

### C.4 Runner/CLI: same as Seal-Tools (`else` branch in `loop.py`, single-turn; add to
`cli.py` `_load_tasks` + `_make_executor` stub route + `--benchmark` choices).

---

## Summary of touch-points (so the executor knows the blast radius)

| File | BFCL single-turn (#1, DO NOW) | Seal-Tools (#2, gated) | RestBench (#3, gated) |
|------|------------------------------|------------------------|-----------------------|
| `bench_loaders/bfcl.py` | **extend** (new `load_bfcl_single_turn` + helpers) | — | — |
| `bench_loaders/seal_tools.py` | — | **new file** | — |
| `bench_loaders/restbench.py` | — | — | **new file** |
| `types.py` `BenchmarkName` | no change (stays `bfcl`) | **+`"seal_tools"`** | **+`"restbench"`** |
| `runner/executors.py` | **add `make_stub_executor`** (shared) | reuse stub | reuse stub |
| `runner/loop.py` | **no edit** (turns_max=1 in existing bfcl branch) | no edit (else branch) | no edit (else branch) |
| `runner/cli.py` | extend `_load_tasks`/`_make_executor`/`--bfcl-split` choices | add bench wiring | add bench wiring |
| `data/` | none (vendored) | **vendor seal_tools/** first | **vendor restbench/** first |
| `tests/` | `test_bfcl_single_turn_loader.py` | `test_seal_tools_loader.py` | `test_restbench_loader.py` |

**Key invariant exploited everywhere:** TEHR is computed at `loop.py:177`
(`call.name not in active_registry`) **before** the executor runs and independent of any
gold answer or judge. So every new benchmark needs only (a) a loader emitting a Task with a
normalized canonical-inner `registry`, and (b) a stub executor. `turns_max=1` keeps all
three on a single dispatch per task.

---

## Exact Task / registry mapping (canonical-inner shape, per `registry.py`)

Every loader must emit `Task.registry` as `dict[name, {"name","description","parameters"}]`
where `parameters` is JSON-Schema 2020-12 (`"type":"object"` with `"properties"`), i.e. the
shape `validate_registry` enforces and `render_for_{anthropic,openai,mlx}` consume unchanged.

| Source field | → `registry` entry | Normalizer |
|--------------|--------------------|-----------|
| BFCL single-turn `record["function"][k]` | `{name, description, parameters}` keyed by `name` | `_normalize_bfcl_schema` (existing; `dict→object`) |
| Seal-Tools `tool.jsonl` row | same | new `_seal_to_openai_schema` (`str→string`, etc.) |
| RestBench OAS operation | name=`"<METHOD> <path>"` | new `_oas_to_registry` (OAS types already JSON-Schema) |

`initial_prompt`: BFCL → `_extract_initial_prompt(question)`; Seal-Tools → `row["query"]`;
RestBench → `row["query"]`.
`turns_max`: **1** for all three.
`expected_outcome`: carries provenance + gold (may be `None`/`[]`); **never read by TEHR**.

---

## Smoke command (verifies the #1 loader end-to-end, NO API spend)

Run from the harness package root (`/Users/cero/Desktop/PROJECTS/icml/harness`) using its
own venv. This loads real on-disk single-turn data, normalizes it, validates the registry,
and confirms the TEHR predicate is wired — without constructing any model adapter or
dispatching a single API call:

```bash
cd /Users/cero/Desktop/PROJECTS/icml/harness && .venv/bin/python -c "
from harness.bench_loaders.bfcl import load_bfcl_single_turn
from harness.registry import validate_registry
tasks = list(load_bfcl_single_turn(split='simple_python', n=5, seed=0))
assert tasks, 'no tasks loaded'
for t in tasks:
    assert t.id.startswith('bfcl_'), t.id
    assert t.benchmark == 'bfcl'
    assert t.turns_max == 1, t.turns_max
    validate_registry(t.registry)          # raises if any type:dict survived
    assert t.registry, t.id                # non-empty registry
print('OK', len(tasks), 'single-turn tasks; sample id=', tasks[0].id,
      'n_tools=', len(tasks[0].registry))
# abstention split: no gold, must not raise, ground_truth is None
irr = list(load_bfcl_single_turn(split='irrelevance', n=3, seed=0))
assert all(t.expected_outcome['ground_truth'] is None for t in irr)
print('OK irrelevance', len(irr), 'tasks, ground_truth=None as expected')
"
```

Expected output (shape):
```
OK 5 single-turn tasks; sample id= bfcl_simple_python_<k> n_tools= 1
OK irrelevance 3 tasks, ground_truth=None as expected
```

Then the unit test: `cd /Users/cero/Desktop/PROJECTS/icml/harness && .venv/bin/python -m pytest tests/test_bfcl_single_turn_loader.py -q`.

For Seal-Tools / RestBench, the analogous smoke command is identical with
`load_seal_tools(split='in_domain', n=5)` / `load_restbench(domain='tmdb', n=5)` once their
data is vendored under `harness/data/` — each followed by `validate_registry(t.registry)`
and a `turns_max == 1` assertion.

---

## Execution order (mirrors the synth's 1-day plan, gated by data availability)

1. **BFCL single-turn (#1) — buildable now.** Extend `bfcl.py` (`load_bfcl_single_turn`),
   add `make_stub_executor`, wire `cli._make_executor`, add the test. Run the smoke command.
   Kills the "multi-turn artifact" + "abstention artifact" reviewer objections on the same
   tool substrate, zero new data.
2. **Vendor Seal-Tools data → write `seal_tools.py` (#2).** Adds the large-registry +
   in/out-domain generalization axis; run both `registry_mode` variants.
3. **Vendor RestBench data → write `restbench.py` (#3).** Adds the real REST/OpenAPI domain.

All three run on the existing MLX + API adapter matrix with no adapter changes, single
dispatch per task (`turns_max=1`), and the shared stub executor.
