# Synthesis: Reusable Harness Components

**Author:** harness-components synthesist · **Date:** 2026-05-29
**Scope:** Which surveyed repos have COMPONENTS (loaders, tool-call parsers, executors, eval scorers)
we can reuse to strengthen `harness/`, license-permitting. File-level pointers + ranked, actionable plan.

**Our harness today** (`/Users/cero/Desktop/PROJECTS/icml/harness/`):
- `bench_loaders/{bfcl.py, tau_bench.py}` → yield `Task(registry=<canonical OpenAI-shape>, ...)`; `_tau_user_simulator_haiku.py` swaps τ-bench's GPT-4o user sim for Haiku.
- `registry.py` → `_normalize_bfcl_schema` (Python-type → JSON-Schema 2020-12), `validate_registry`, `render_for_{anthropic,openai,mlx}`.
- `adapters/{anthropic,openai,mlx}_adapter.py` → in-process MLX via `mlx_lm.load`+`generate`, bespoke `<tool_call>{json}</tool_call>` regex parse; API adapters via native tool-use.
- `runner/{loop.py, executors.py, refusal.py}` → ReAct loop; `make_bfcl_executor` (stateful `getattr` dispatch) + `make_tau_bench_executor` (env `step/reset`).
- `intervention/{rvr.py, naive_retry.py, framework_default.py, decoy_list.py}` → pure `(parsed_calls, registry) -> Action`.
- `stats/` → TEHR + bootstrap CI, McNemar, TOST, ANOVA.

**Key architectural facts that gate reuse:**
1. TEHR is OURS to compute from the call trace ("emitted tool name ∉ registry?") regardless of harness. No surveyed repo computes it; nearest neighbors (BFCL `irrelevance_match`, deepeval `ToolCorrectnessMetric`, promptfoo `validateFunctionCall`) fold nonexistent-tool calls into generic correctness/relevance failures — that absorption IS our motivation.
2. Local tier is **in-process MLX** (not an HTTP server). Anything assuming vLLM/Ollama/OpenAI-server tool parsing is a swap, not a drop-in, and moves parsing off the code that produced our published MLX 4-bit TEHR numbers.
3. `harness/types.py` hardcodes `BenchmarkName = Literal["bfcl","tau_bench"]` and `Task.registry` = canonical OpenAI JSON-Schema. New benchmarks need this literal extended + a schema normalizer (the `_normalize_bfcl_schema` role).

---

## TIER 1 — Build now (high value, license-clean, low/medium effort)

### 1. BFCL `eval_checker` as an OFFICIAL accuracy scorer (ShishirPatil/gorilla, Apache-2.0)
**This is the single highest-value component reuse.** We already vendor the BFCL data at
`harness/data/bfcl_v4/repo/berkeley-function-call-leaderboard/`, and `runner/executors.py` already imports
its `func_source_code` classes. The unused prize is the **scoring layer**:
- `bfcl_eval/eval_checker/multi_turn_eval/` — official state-based multi-turn scorer (replays GT vs model calls, compares backend-object attributes).
- `bfcl_eval/eval_checker/ast_eval/` — AST-based single-turn correctness checker.
- `bfcl_eval/eval_checker/eval_runner.py` — orchestration.

**Why:** the predictable reviewer attack is "does RVR re-prompting hurt task accuracy?" The credible answer is the community-standard BFCL accuracy, not a homegrown number. Reporting BFCL accuracy *alongside* TEHR/RVR is the cost-quality-gap story with an external metric.
**Effort:** MEDIUM. The checker pulls a heavy/conflicting dep tail (`tree_sitter==0.21.3`, `faiss-cpu`, `sentence-transformers`, `qwen-agent`, `numpy==1.26.4`). **Isolate behind an optional extra or a subprocess** — do NOT put it in the core uv env. License: Apache-2.0, vendor-clean (retain NOTICE/attribution).
**Also low-hanging:** point our existing `bench_loaders/bfcl.py` at the **single-turn** AST categories (`simple`/`parallel`/`multiple`/`parallel_multiple`) + `irrelevance`/`live` — reuses our normalizer, adds a cheap single-turn TEHR axis. Effort LOW-MED.

### 2. RestBench data loader → `bench_loaders/restbench.py` (Yifan-Song793/RestGPT, MIT)
A new **tool-existence domain** (real REST APIs) beyond BFCL's synthetic Python tools. Reuse **data + specs only**, never the agent code (it hard-wires dead `text-davinci-003` + pre-0.1 langchain).
- `datasets/tmdb.json` (100 tasks), `datasets/spotify.json` (57) — each `{"query", "solution":[ordered REST calls]}`.
- `specs/tmdb_oas.json` (OpenAPI 3.0.0, 54 ops), `specs/spotify_oas.json` (40 ops) — frozen registry, no live keys needed.

**Plan:** loader normalizes OpenAPI operations → our OpenAI-shape `registry` (analogous to `_normalize_bfcl_schema`); carry the gold path in `expected_outcome`; **stub execution** (TEHR only needs emitted call names vs registry). MIT — vendor data with attribution.
**Effort:** MEDIUM (OpenAPI→registry normalizer is the work). Adds a larger, OpenAPI-typed registry distribution that could surface new Qwen3 non-monotonic behavior.

### 3. Seal-Tools loader → `bench_loaders/seal_tools.py` (fairyshine/Seal-Tools, Apache-2.0)
Single-turn, large-registry breadth axis. Files (`master` branch):
- `tool.jsonl` (4076 tool specs, typed `parameters`+`required`), `test_in_domain.jsonl` (700), `test_out_domain.jsonl` (654, unseen tools — generalization).
- Verified: **0/3732 gold calls missing from the registry** → any emitted name ∉ `tool.jsonl` is an unambiguous existence-hallucination. Clean TEHR ground truth.

**Plan:** loader maps `{"type":"str",...}`+`required` → OpenAI schema (normalizer role); one `Task` per test row. **Do NOT vendor their `LLM_Evaluation/calculate.py`** (uses `eval()`, Python-3.10 `match`, intermingled with unrelated NLP). Reimplement their API-F1/Param-F1 in a few lines if we want comparable numbers.
**Effort:** MEDIUM. Note: single-*turn* but multi-*call* (71% in-domain / 86% out-domain rows need >1 call) — infra-simpler than BFCL multi-turn, not "easy."

### 4. τ-bench airline domain (sierra-research/tau-bench, MIT) — already 90% done
τ-bench is **already vendored and fully wired** (`bench_loaders/tau_bench.py`, `_tau_user_simulator_haiku.py`, `runner/executors.py::make_tau_bench_executor`). The airline modules are present in the vendored tree (`tau_bench/envs/airline/`); the loader currently hardcodes retail + `MockRetailDomainEnv`. Adding airline = a module-path swap + new loader path + new test. **Effort: LOW.** Cheapest breadth win on the multi-turn axis. (Disclose: Haiku user-sim ≠ GPT-4o, so not leaderboard-comparable.)

---

## TIER 2 — Build as baseline/intervention arms (medium effort, strong paper value)

### 5. Constrained-decoding intervention on MLX tier (dottxt-ai/outlines, Apache-2.0)
The strongest cost-quality-gap contrast to RVR: force the tool-NAME slot to `Literal[registry names]` so local-tier TEHR is **structurally 0**, then measure what it costs (task accuracy, args correctness, error displacement to wrong-but-valid tools).
- `outlines.from_mlxlm(*mlx_lm.load(...))` unpacks the exact `(model, tokenizer)` our `mlx_adapter.py::_ensure_loaded` produces (line ~114).
- Build the constraint from `registry.py::render_for_mlx` / tool-name set.
- Keep it **additive**: a new `ConstrainedMLXAdapter`, do NOT touch the Qwen3 path.

**Real cost (under-stated in survey):** `MLXLM.generate` returns a bare `str` — no token counts, no finish_reason. The new adapter must re-derive `tokens_in/out` (`tokenizer.encode`) + the `length` finish heuristic + keep our `_parse_tool_calls`. Budget the **token-accounting glue**, not the license.
**Critical asymmetry (must-cite framing):** outlines' Anthropic backend RAISES on any `output_type` (it does NOT delegate to server-side JSON mode). So constrained decoding is **structurally unavailable** for our API 4.x tier — which is exactly the argument for black-box RVR. Do NOT claim outlines constrains the Anthropic tier.
Import as a dep (Apache-2.0), don't vendor.

### 6. Reflexion-style ungrounded-reflection baseline (noahshinn/reflexion, MIT) — clean-room
RVR is single-step registry-*grounded* reflection; Reflexion is multi-trial free-text reflection. A head-to-head (grounded vs ungrounded self-reflection on TEHR) sharpens novelty.
**Plan:** a new sibling in `intervention/` mirroring `rvr.py`'s pure signature `(parsed_calls, registry) -> Action`, returning `Action(kind=RE_PROMPT, feedback=<self-reflection prompt>)` with NO registry list. ~25 lines, clean-room (their repo is non-installable, OpenAI-locked, per-task-duplicated — do NOT vendor). Borrow the prompt structure from `alfworld_runs/generate_reflections.py::_generate_reflection_query`.
**Effort:** <1 hour. High paper value.

### 7. lm-format-enforcer as a SECOND hard-constraint baseline (noamgat/lm-format-enforcer, MIT) — OPTIONAL
Same role as outlines (logit-mask tool-name → TEHR=0 on local), via a documented regex/choice constraint `(toolA|toolB|...)` or JSON-Schema enum. MLX is NOT a supported backend → needs a custom logits-processor adapter (it exposes a backend-agnostic `CharacterLevelParser`/prefix-allowed-tokens interface). Only worth it if we want a second constrained-decoding data point; otherwise outlines alone suffices. API models excluded by design (README: "can not be used with OpenAI ChatGPT and similar"). MIT, vendorable.

---

## TIER 3 — Mine assets / borrow patterns (no harness code reuse)

### 8. ToolEmu JSON assets for a TEHR distractor stress-test (ryoungj/ToolEmu, Apache-2.0)
Do NOT run its runner (coupled to a *removed* langchain API + `anthropic==0.3.6`, no local backend). DO vendor the **assets**: `assets/all_toolkits.json` (verified **38 toolkits / 330 tools**, survey/paper say 36/311) + `assets/all_cases.json` (144 cases). Use as a large tool-spec corpus to mine **decoy/distractor tool names** for a registry-pressure TEHR stress test (feeds `intervention/decoy_list.py`-style experiments). Apache-2.0, attribute. Ignore the stray MIT classifier in `setup.py`.

### 9. ToolACE-2-8B as a MODEL baseline (Team-ACE, Apache-2.0 data + Llama-3.1 weights)
No code/repo to reuse (HF org, no GitHub). But our **vendored BFCL already registers a ModelConfig for `Team-ACE/ToolACE-2-8B`** (`bfcl_eval/constants/model_config.py`, `LlamaHandler`), so running it as an extra open 8B FC family through our BFCL loader is **lower-effort than expected**. MLX 4-bit convert is routine (LlamaForCausalLM). **Caveat to elevate:** it was trained on BFCL-adjacent synthetic data → near-zero BFCL TEHR is partly in-distribution; frame as "in-distribution FC specialist," cross-check on tau-bench (OOD) before any apples-to-apples row vs Qwen3/Anthropic. Weights = Llama-3.1 Community License → run inference only, never relicense/vendor weights.

### 10. StableToolBench TEHR-only loader (THUNLP-MT/StableToolBench, Apache-2.0) — DEFERRED
`solvable_queries/test_instruction/*.json` are self-contained per-query registries (`api_list` + `relevant APIs` + `query`). A TEHR-only loader is feasible and needs NEITHER the virtual API server NOR the GPT-4 judge. **But** drop the "large registry → higher TEHR" rationale: measured per-query registries are SMALL (median 4-7, max 13), comparable to/smaller than BFCL. Full SoPR/SoWR is Linux/CUDA-bound with 2023 dep pins — not vendorable. Lower priority than Tier-1 loaders (Seal-Tools/RestBench give more distinct distributions for the same effort).

### 11. Reviewer-persona / paper-revision rubric patterns (no harness code)
For the paper-revision skill + reviewer personas (separate from the harness):
- **promptfoo** (MIT) `llm-rubric`/`g-eval`/`model-graded-closedqa` — borrow the *shape* (rubric text → JSON {score, reason}) for personas; YAML test-matrix (persona × section) for a reproducible revision gate. Reimplement in Python; do not vendor TS.
- **ToolEmu** `toolemu/prompts/text/{safety_evaluator,helpfulness_evaluator,adversarial_simulator}.md` — score-then-justify rubric + adversary-persona templates.
- **deepeval** (Apache-2.0) G-Eval/DAG decomposition — graph-structured judging pattern for persona rubrics.
- **Reflexion** bounded-memory ("last-N rounds") + corrective-plan prompt for a paper-revision reflection loop.

---

## CITE-ONLY (no usable component) — for completeness
- **API-Bank** (MIT root, **Apache-2.0 in `api-bank/` subdir** — do NOT treat as MIT; survey conflated them): free-text `[Api(...)]` DSL, implicit per-turn registries, heavy retrieval deps. Loader is 3-5 days, not 1-2. Cite + differentiate; loader is a stretch, not a quick win.
- **ToolBench / MetaTool / ToolBeHonest / AgentBench / AppWorld / NexusRaven**: cite-as-prior-art; no component cleanly fits our JSON-Schema `Task`/registry + in-process-MLX pipeline.
- **inspect_ai / lm-eval-harness / helm / openai-evals / langgraph / autogen / crewAI / dspy / letta / smolagents / guidance / instructor / jsonformer**: alternative *runtimes/frameworks*, not droppable components for our metric. `inspect_ai` (MIT) is the one worth noting as a citable BFCL+tau2 harness whose `multi_turn_match` scorer is state-based and (confirmed) does NOT surface a per-call existence signal — reinforces our TEHR-gap positioning. Adopting it would mean replacing our runner; not recommended given our harness is built.

---

## Recommended build order (concrete)
1. **τ-bench airline** (LOW; multi-turn breadth; infra mostly done).
2. **BFCL single-turn categories** via existing loader (LOW-MED; reuses normalizer).
3. **BFCL `eval_checker` as isolated optional accuracy scorer** (MED; pre-empts the "RVR hurts accuracy?" reviewer attack with the community metric).
4. **`bench_loaders/restbench.py`** (MED; real-REST tool-existence domain, MIT data).
5. **`bench_loaders/seal_tools.py`** (MED; single-turn large-registry / OOD generalization axis).
6. **Outlines `ConstrainedMLXAdapter` baseline** (MED; structural-TEHR=0 cost-quality contrast vs RVR; budget token-accounting glue).
7. **Reflexion-style intervention** (<1h; grounded-vs-ungrounded reflection head-to-head).
8. **ToolEmu assets** for a decoy/distractor registry-pressure stress test (LOW; vendor JSON only).

**License posture:** every Tier-1/Tier-2 item is MIT or Apache-2.0 — vendorable with attribution/NOTICE; no copyleft anywhere. ToolSandbox (NOASSERTION Apple Sample Code) and Tool EmuLab weights (Llama-3.1) are the only non-standard terms, both handled by run-external / inference-only and NOT vendoring source. Add a root LICENSE to our repo before any artifact release (currently absent).
