# Synthesis: Benchmarks to ACTUALLY Run for Main-Track Breadth

**Author role:** paper-benchmarks-to-run synthesist
**Date:** 2026-05-29
**Inputs:** verified `repo_*.md` + `discover_*.md` survey files; harness code at
`harness/bench_loaders/*.py`, `harness/runner/loop.py`, `harness/runner/executors.py`,
`harness/types.py`, `harness/adapters/*.py`.

---

## TL;DR ranking (reviewer-impact × low-effort × permissive-license)

| Rank | Benchmark | Action | License | Effort | New axis it adds |
|------|-----------|--------|---------|--------|------------------|
| **1** | **BFCL single-turn + irrelevance/live (gorilla)** | run-as-benchmark (expand existing loader) | Apache-2.0 | **LOW** (data already vendored) | single-turn + abstention/irrelevance axis on the *same* substrate |
| **2** | **Seal-Tools (fairyshine)** | run-as-benchmark (new loader) | Apache-2.0 | LOW-MED | large/diverse synthetic registry, single-turn multi-call, in- vs out-of-domain generalization |
| **3** | **RestBench data (RestGPT, Yifan-Song793)** | include-parts → run-as-benchmark (data only) | MIT | MED | real-world REST/OpenAPI registry domain (vs synthetic Python tools) |
| 4 | StableToolBench query JSON | include-parts (TEHR-only loader) | Apache-2.0 (code) / ToolBench data research-use | MED | RapidAPI tool-schema diversity; but small per-query registries (median 4-7) |
| — | ToolSandbox (apple) | run-as-benchmark, LATER phase | NOASSERTION (Apple custom; no patent grant) | MED-HIGH | 3rd stateful multi-turn surface; GPT-only hardcoded user sim + no MLX serving = front-loaded cost/repro tax |
| — | inspect_ai / inspect_evals | cite + optional cross-check | MIT | MED-HIGH | recognized harness; but its BFCL port is state-based and gives **no** per-call TEHR; adopting it = second runtime |
| — | ToolBeHonest, NexusRaven, ToolBench, API-Bank, MetaTool, AgentBench, ToolEmu, AppWorld | cite-only | mixed | — | prior art / differentiation only |

**Why this ordering:** Every candidate's TEHR is computable from a single predicate already in
`loop.py:177` — `call.name not in registry`. TEHR is fully decoupled from task execution and from
any judge. So the *only* thing a new benchmark needs is (a) a loader that emits a `Task` with a
normalized OpenAI-shape `registry`, and (b) — if we want a pass/accuracy column too — an executor;
but for TEHR alone a **stub executor that returns `{"output": ...}` without a real backend is
sufficient.** This is why "single-turn, registry-only" benchmarks are dramatically cheaper than
stateful multi-turn ones (no env, no user simulator, no live API keys). Rank is dominated by:
already-vendored data > permissive license + clean schema > real keys/infra/non-standard license.

---

## Harness reality check (what "run a new benchmark" actually costs)

Confirmed by reading the code, not the spec:

1. **TEHR is execution-independent.** `loop.py` `_classify_turn` flags a hallucination purely on
   `call.name not in active_registry` (line 177); `tehr_num/tehr_denom` accumulate from the turn
   status (lines 288-296). No backend, no judge, no ground-truth needed for TEHR.
2. **A loader just yields `Task`** (`harness/types.py`): `{id, benchmark, registry, initial_prompt,
   turns_max, expected_outcome}`. `registry` must be canonical OpenAI shape
   `{name: {"name","description","parameters": <JSON-Schema>}}`. `bfcl.py` shows the exact pattern,
   including `_normalize_bfcl_schema` (rewrites `"type":"dict"`→`"object"`); a new loader needs the
   analogous one-function schema normalizer for its source format.
3. **Two small touch-points for a NEW benchmark name:**
   - `harness/types.py`: `BenchmarkName = Literal["bfcl","tau_bench"]` → add the new name.
   - `harness/runner/loop.py` + `executors.py`: benchmark-specific branches key on
     `task.benchmark == "bfcl"` / `"tau_bench"`. A single-turn registry-only benchmark wants a
     default branch: `turns_max=1`, a no-op/stub executor, and no env/user-sim. This is a few lines,
     not a rewrite.
4. **Adapters are reused unchanged.** Anthropic, OpenAI, and the in-process MLX adapter
   (`mlx_adapter.py`, default `mlx-community/Qwen3-8B-4bit`, bespoke `<tool_call>` regex parse) all
   consume `Task.registry`. Any new loader runs on the **same MLX + API matrix** with zero adapter
   work. This is the decisive advantage over ToolSandbox/StableToolBench, whose runtimes assume
   vLLM/OpenAI-compatible servers and (ToolSandbox) a hardcoded GPT user simulator — neither has an
   MLX path, and our MLX adapter is in-process, not an HTTP server.

**Budget arithmetic for ~1 day:** the cost driver is API tokens for the closed models × #tasks ×
#families. Single-turn benchmarks are ~1 dispatch/task (no multi-turn loop, `turns_max=1`), so a
150-300 task slice across the API families is a few dollars and minutes of wall-clock; the MLX arm
is local/free (M5 32GB) but slower. All three top picks fit comfortably in a day **combined**.

---

## #1 — BFCL single-turn + irrelevance/live  (ShishirPatil/gorilla, Apache-2.0)

**Why #1: the data is ALREADY VENDORED and the loader already exists.** Verified on disk:
`harness/data/bfcl_v4/repo/.../bfcl_eval/data/` contains 20 `BFCL_v4_*.json` task files, including
the single-turn ones we do **not** yet load: `BFCL_v4_simple_python.json`,
`..._simple_java.json`, `..._simple_javascript.json`, `BFCL_v4_multiple.json`,
`BFCL_v4_parallel.json`, `BFCL_v4_parallel_multiple.json`, plus the abstention-axis files
`BFCL_v4_irrelevance.json`, `BFCL_v4_live_irrelevance.json`, `BFCL_v4_live_relevance.json`, and the
live splits `BFCL_v4_live_simple/multiple/parallel/parallel_multiple.json`. Apache-2.0, no new
download, no new license exposure (gorilla LICENSE verified Apache-2.0 in survey, 12,876 stars).

**Integration sketch:**
- **Loader:** extend `harness/bench_loaders/bfcl.py`, NOT a new file. The single-turn task files use
  the same tool-doc + `_normalize_bfcl_schema` machinery; the registry comes from each task's
  declared functions instead of `involved_classes`. Add a `load_bfcl_single_turn(split, n, seed)`
  (or generalize `load_bfcl`) for the simple/parallel/multiple splits. The hard part the existing
  loader already solved: schema normalization.
- **# tasks:** start with a deterministic n=100-150 sample from `simple_python`, `multiple`,
  `parallel`, `parallel_multiple` (single-tool→multi-tool gradient) + the full `irrelevance` /
  `live_irrelevance` sets (these are small and are the abstention axis).
- **Executor:** stub (`turns_max=1`, return `{"output": "ok"}`). TEHR needs only the call name vs
  registry; for an optional accuracy column reuse the upstream AST checker later (survey flags its
  dep tail — isolate; not needed day-1).
- **Est. cost:** ~$1-3 of API tokens across Anthropic 4.x + OpenAI + (free) MLX Qwen3 4-bit, single
  dispatch per task. Sub-hour wall-clock for the API arm.
- **Reviewer objection it kills:** *"Your headline (Anthropic 4.x = 0 TEHR; Qwen3 4-bit
  non-monotonic peak 1.87% at 14B) is a single-setting artifact of BFCL multi-turn. Does it hold
  outside multi-turn?"* Adding single-turn simple/parallel/multiple on the **same tool substrate**
  isolates the multi-turn variable: if the 0-vs-non-monotonic pattern persists single-turn, it is a
  model property, not a multi-turn-loop artifact. The `irrelevance`/`relevance` splits separately
  rebut *"TEHR is just over-calling / a relevance-detection artifact"* — BFCL's irrelevance metric
  (no-call-on-irrelevant-query) is the closest prior metric and is **adjacent but distinct** from
  TEHR (see inspect_ai survey); reporting both shows TEHR is not subsumed by abstention.

---

## #2 — Seal-Tools  (fairyshine/Seal-Tools, Apache-2.0)

**Why #2: cleanest new-family fit, fully permissive, TEHR provably sound on it.** Verified twice
adversarially: 4076-tool registry (`tool.jsonl`), `test_in_domain`=700, `test_out_domain`=654 rows;
**0/1795 in-domain and 0/1937 out-domain gold calls are missing from the registry** — so any
predicted name absent from `tool.jsonl` is an unambiguous existence-hallucination. Apache-2.0
confirmed from decoded LICENSE body (57 stars; small but that does not matter — we run the data, not
adopt the project).

**Integration sketch:**
- **Loader:** new `harness/bench_loaders/seal_tools.py`, mirroring `bfcl.py`. Two pieces of work:
  (1) a schema normalizer mapping Seal-Tools `{"type":"str","description":...}` + `required` →
  OpenAI function-tool JSON-Schema (same role as `_normalize_bfcl_schema`); (2) build `registry`
  from `tool.jsonl` (or a per-query candidate subset — decide presentation; see note). Emit one
  `Task` per row of `test_in_domain` / `test_out_domain`, `turns_max=1`, gold `calling` list into
  `expected_outcome`.
- **Registry presentation decision (load-bearing):** presenting all 4076 tools per call is the
  large-registry stress regime (good for TEHR pressure, but big prompts/cost). Presenting a
  per-query candidate set is cheaper and matches BFCL's small-registry regime. **Recommend running
  both as an ablation** — this directly answers "does registry size drive TEHR?", a question
  StableToolBench could NOT answer (its per-query registries are only median 4-7).
- **# tasks:** n=150 from each of in-domain and out-domain (300 total) for the headline; the
  in/out-domain split is a free **generalization axis** (out-domain tools/fields unseen at the
  benchmark's train time; 86% of out-domain rows are multi-tool).
- **Executor:** stub. `responses` are spec-only `API_call_N` placeholders (no executable backend) —
  fine, TEHR only inspects emitted names. Optionally reimplement Seal-Tools' API-F1/Param-F1 (a few
  lines; do NOT vendor their `calculate.py`: uses `eval()`, `match/case`, intermixed NLP tasks) to
  report a conventional accuracy column comparable to their NLPCC-2024 paper numbers.
- **Est. cost:** per-query-candidate-set variant ~$2-5 (300 single dispatches × families); the
  all-4076-tools variant is larger-prompt — cap n and run on a subset of families if budget tight.
- **Reviewer objection it kills:** *"BFCL has tiny per-task tool sets; your TEHR finding may be an
  artifact of small registries and a single tool distribution."* Seal-Tools provides (a) a genuinely
  large, schema-diverse synthetic tool universe (4076 tools across many fields), letting us test the
  registry-size hypothesis directly, and (b) an unseen-domain generalization split. It is also a
  *single-turn multi-call* setting — complementary to BFCL multi-turn — so it broadens both the
  registry-scale and the turn-structure axes at once. This is the strongest "more families" win that
  is also cheap and unencumbered.

---

## #3 — RestBench (Yifan-Song793/RestGPT, data only — MIT)

**Why #3: a real-world REST/OpenAPI domain, MIT-clean, but smaller and slightly more loader work.**
Verified: `datasets/tmdb.json`=100 tasks, `datasets/spotify.json`=57 (157 total), each
`{"query","solution":[ordered REST calls]}`; `specs/tmdb_oas.json`=OpenAPI 3.0.0 with 54 operations,
`specs/spotify_oas.json`=OpenAPI 3.0.3 with 40 operations. MIT confirmed from decoded LICENSE; safe
to vendor data + specs with attribution. **Do NOT run the agent** — `run.py` hardwires the retired
`text-davinci-003` and pre-0.1 langchain, no MLX/Anthropic path, needs live TMDB/Spotify OAuth keys.
We use **frozen specs only**, so live-endpoint drift is a non-issue.

**Integration sketch:**
- **Loader:** new `harness/bench_loaders/restbench.py`. Main work = **OpenAPI→registry normalizer**:
  enumerate operations from the two `*_oas.json` specs into the canonical registry (tool name =
  `METHOD path`, e.g. `GET /search/person`; parameters from the OpenAPI `parameters`/`requestBody`
  schema). Emit one `Task` per `datasets/*.json` row, `turns_max=1`, gold `solution` path into
  `expected_outcome`. No live keys (stub executor) — TEHR only needs name-existence.
- **# tasks:** all 157 (100 TMDB + 57 Spotify); small enough to run fully.
- **Est. cost:** trivial (~$1, 157 single dispatches × families).
- **Effort note:** MED — slightly more than Seal-Tools because OpenAPI specs are richer to parse
  than flat tool JSONL, and the `METHOD path` naming convention must match how the model is prompted
  to emit calls (define the tool-name convention in the registry and instructions consistently).
- **Reviewer objection it kills:** *"All your tools are synthetic Python-style functions (BFCL) or
  one retail domain (tau-bench). Does tool-existence hallucination matter for real, production-style
  API surfaces?"* RestBench is human-annotated over **real REST APIs with bounded OpenAPI registries**
  (54 / 40 endpoints) — a distinct, externally-recognizable domain. It also lets us contrast our
  *reactive* RVR (re-inject registry after a bad call) against RestGPT's *up-front* API-Selector
  module as prior art, sharpening the RVR novelty claim.

---

## Explicitly DEPRIORITIZED (and why), so the plan is honest

- **ToolSandbox (apple, NOASSERTION):** highest scientific adjacency (3rd stateful multi-turn
  surface, minefield/insufficient-info taxonomy = external grounding for TEHR) BUT the worst
  effort/repro profile for *our* stack: the user simulator is **hardcoded GPT-only**
  (`openai_api_user.py`, mandatory OpenAI spend every run + proprietary version drift in the eval
  loop), there is **no MLX serving path** (our `mlx_adapter.py` is in-process, not HTTP; vLLM can't
  load MLX 4-bit weights), and a new Qwen3 agent role would be needed. Non-standard Apple license
  (no patent grant) → cite + run-externally only, never vendor. **Do as a later-phase breadth item,
  not a 1-day win.** Cite as prior art regardless.
- **StableToolBench (THUNLP-MT, Apache-2.0):** TEHR-only loader over
  `solvable_queries/test_instruction/*.json` is feasible and the code license is clean, BUT (a)
  per-query registries are small (measured median 4-7, max 13 — comparable to / smaller than BFCL,
  so it does NOT add the large-registry regime the original survey claimed; Seal-Tools does that
  better), (b) the full SoPR/SoWR pipeline is Linux/CUDA + 2023 dep pins + GPT-4 judge (won't run on
  M5), and (c) the underlying ToolBench API data is gated/research-use. Net: a *fourth* TEHR-only
  benchmark if time remains, behind Seal-Tools and RestBench which give cleaner new axes per unit
  effort. Cite for the stability-vs-existence differentiation.
- **inspect_ai / inspect_evals (MIT):** strong as a *citation* and an optional external-validity
  cross-check (recognized AISI harness; its BFCL+tau2 ports exist). But its multi-turn scorer is
  **state-based and surfaces no per-call TEHR** (an out-of-registry call returns an internal
  "Method not found" string and silently degrades the state match) — so it gives us TEHR for nothing
  and adopting it means standing up a second runtime + revalidating MLX tool-call parsing. Use to
  cite and (optionally) cross-check that our API-family accuracy matches a recognized harness; do not
  reroute the pipeline through it for the 1-day breadth push.
- **ToolBeHonest (MIT):** closest *named* prior art for tool-existence hallucination
  (`non_existent_tools` error category; GPT-4o 37.0 / Gemini-1.5-Pro 45.3 anchors showing
  frontier-2024 models DO fabricate tools — a sharp contrast to our Anthropic-4.x = 0). But it is a
  **per-sample static reasoning diagnostic**, not per-call live execution; running it yields a
  differently-defined number to reconcile. **cite-only as the key differentiation + baseline anchor**;
  reuse its six-way error taxonomy as a reviewer-persona rubric, not as a benchmark we run.
- **NexusRaven (CC-BY-NC-4.0 DATA):** single-turn, dead 2023 langchain, NonCommercial data → never
  vendor/run; cite as light prior art for the forced-choice-over-registry framing and as a
  reviewer-persona/ablation seed ("is TEHR an artifact of registry presentation?").
- **ToolBench, API-Bank, MetaTool, AgentBench, ToolEmu, AppWorld, ToolACE:** cite-only per the
  recommendation table; none beats picks 1-3 on effort × new-axis × license for a 1-day budget.

---

## Concrete 1-day execution order

1. **Morning (LOW effort, biggest certainty):** extend `bfcl.py` for single-turn + irrelevance/live
   splits (data already on disk). Add a default single-turn branch in `loop.py`/`executors.py`
   (`turns_max=1`, stub executor) + the new name(s) in `BenchmarkName`. Run n≈150 single-turn +
   full irrelevance across Anthropic 4.x + OpenAI + MLX Qwen3 4-bit. **This alone kills the
   "multi-turn artifact" and "abstention artifact" objections.**
2. **Midday (LOW-MED):** write `seal_tools.py` (schema normalizer + registry-presence). Run
   in-domain + out-domain, both registry-presentation variants on a capped n. **Kills the
   "small-registry / single-distribution artifact" objection + adds a generalization axis.**
3. **Afternoon (MED):** write `restbench.py` (OpenAPI→registry). Run all 157 TMDB+Spotify tasks.
   **Kills the "synthetic-tools-only / not real APIs" objection** and sets up the RVR-vs-API-Selector
   prior-art contrast.
4. **Cross-cutting:** report per-call TEHR for every family on every new split; rerun RVR
   intervention on each so the intervention claim generalizes beyond BFCL multi-turn. Add NOTICE/
   attribution entries for gorilla (Apache-2.0), Seal-Tools (Apache-2.0), RestGPT (MIT). Add a root
   LICENSE to our repo before any artifact release (currently absent per ToolSandbox survey note).

**One-line thesis for the paper's breadth section:** BFCL single-turn (same substrate, removes the
multi-turn variable) + Seal-Tools (large diverse registry + in/out-domain generalization) + RestBench
(real REST/OpenAPI domain) turn a single-setting result into a 4-benchmark, 3-domain,
multiple-turn-structure characterization of tool-existence hallucination — all permissively licensed,
all on our existing MLX + API harness, all within a day.
