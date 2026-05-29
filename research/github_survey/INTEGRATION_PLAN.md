# INTEGRATION PLAN — SCALE / TEHR / RVR, Main-Track ICML 2026

**Owner approval doc.** Synthesizes the six `synth_*.md` files into one ranked, actionable plan.
Deadline 2026-04-28 AoE. Stack: in-process MLX (M5 32GB, free local) + Anthropic/OpenAI API.
Headline to defend: per-call **TEHR** on BFCL multi-turn; Anthropic 4.x = 0 events; Qwen3 4-bit
non-monotonic curve peaking 1.87% @ 14B; **RVR** = re-prompt with the tool registry on a bad call.

**Sources:** `synth_paper-benchmarks-to-run.md`, `synth_paper-baselines-and-priorart.md`,
`synth_license-risk-audit.md`, `synth_harness-components.md`, `synth_persona-rubrics.md`,
`synth_skill-enhancements.md` (all in `research/github_survey/`).

---

## P0 — BLOCKERS (do before any vendoring; ~30 min)

1. **Add a root `LICENSE`** to our repo (Apache-2.0 recommended — patent grant, max inbound
   compatibility). Without it the MIT/Apache notice-retention obligations we inherit are incoherent.
2. **Add `NOTICE` / `THIRD_PARTY_LICENSES`** listing every vendored repo + license. Mandatory for
   Apache-2.0, good practice for MIT.

These gate every "vendor data" step below. Cost: trivial. Risk of skipping: artifact release is
legally undefined.

---

## (a) BENCHMARKS TO RUN — ranked for main-track breadth

Decisive harness fact (verified in all three technical synths): **TEHR is execution-independent** —
`loop.py:177` flags a hallucination purely on `call.name not in active_registry`. So a new benchmark
needs only (i) a loader that yields a `Task` with a canonical OpenAI-shape `registry`, and (ii) a
**stub executor** (`turns_max=1`, return `{"output":"ok"}`). No env, no judge, no live keys for TEHR.
Two touch-points per new name: extend `BenchmarkName` literal in `harness/types.py`; add a default
single-turn branch in `loop.py`/`executors.py`. Adapters (Anthropic/OpenAI/MLX) are reused unchanged.

| Rank | Benchmark | Action | License | Effort | Cost (API+free MLX) | Reviewer objection it kills |
|------|-----------|--------|---------|--------|---------------------|------------------------------|
| **1** | **BFCL single-turn + irrelevance/live** (gorilla) | extend existing `bfcl.py` | Apache-2.0 | **LOW** (data already on disk) | ~$1-3, sub-hour | "multi-turn artifact" + "abstention artifact" |
| **2** | **Seal-Tools** (fairyshine) | new `seal_tools.py` | Apache-2.0 | LOW-MED | ~$2-5 | "small-registry / single-distribution artifact" + adds in/out-domain generalization axis |
| **3** | **RestBench** (RestGPT data only) | new `restbench.py` | MIT | MED | ~$1 (157 tasks) | "synthetic tools only / not real APIs" |
| 3.5 | **tau-bench AIRLINE** (already vendored) | loader path swap | MIT | **LOW** | ~$1-2 | cheapest multi-turn breadth win; 2nd domain on stateful axis |

**Recommended set for the paper: pick #1 + #2 + #3** (turns one setting into a 4-benchmark,
3-domain, multiple-turn-structure characterization). Add **tau-bench airline** as a near-free bonus
multi-turn domain since it is ~90% wired already.

### Concrete commands / effort

**#1 BFCL single-turn + irrelevance/live (LOW — half-morning):**
- Data already on disk: `harness/data/bfcl_v4/repo/.../bfcl_eval/data/BFCL_v4_*.json` (simple_python/
  java/javascript, multiple, parallel, parallel_multiple, irrelevance, live_irrelevance,
  live_relevance, live_*). No download.
- Extend `harness/bench_loaders/bfcl.py` with `load_bfcl_single_turn(split, n, seed)` reusing the
  existing `_normalize_bfcl_schema`; registry comes from each task's declared functions.
- Add a default single-turn branch (`turns_max=1`, stub executor) in `loop.py`/`executors.py`.
- Run n≈100-150 deterministic sample from simple/multiple/parallel/parallel_multiple (single→multi-
  tool gradient) + **full** irrelevance / live_irrelevance sets, across Anthropic 4.x + OpenAI + MLX
  Qwen3 4-bit. Report TEHR + BFCL `irrelevance_match` side-by-side (shows TEHR ≠ abstention).

**#2 Seal-Tools (LOW-MED — midday):**
- New `harness/bench_loaders/seal_tools.py` mirroring `bfcl.py`. Two pieces of work: (i) schema
  normalizer `{"type":"str",...}`+`required` → OpenAI JSON-Schema; (ii) build `registry` from
  `tool.jsonl` (4076 tools). Verified: 0/3732 gold calls are missing from the registry → any emitted
  name ∉ `tool.jsonl` is an unambiguous existence-hallucination.
- One `Task` per row of `test_in_domain` (700) / `test_out_domain` (654, unseen tools), `turns_max=1`.
- **Run BOTH registry presentations as an ablation** (full 4076-tool registry vs per-query candidate
  set) — this directly answers "does registry size drive TEHR?", which StableToolBench cannot (its
  per-query registries are median 4-7).
- n=150 each from in-domain + out-domain (300 total) for the headline. Do NOT vendor their
  `calculate.py` (uses `eval()`); reimplement API-F1/Param-F1 in a few lines if an accuracy column
  is wanted.

**#3 RestBench (MED — afternoon):**
- New `harness/bench_loaders/restbench.py`. Main work = OpenAPI→registry normalizer: enumerate ops
  from `specs/tmdb_oas.json` (54 ops) + `specs/spotify_oas.json` (40 ops); tool name = `METHOD path`
  (e.g. `GET /search/person`); params from OpenAPI `parameters`/`requestBody`.
- One `Task` per row of `datasets/tmdb.json` (100) + `datasets/spotify.json` (57) = all 157.
  `turns_max=1`, gold `solution` path into `expected_outcome`, **stub executor** (frozen specs, no
  live TMDB/Spotify keys). Do NOT run their agent (hardwired retired `text-davinci-003`).

**tau-bench airline (LOW — bonus):** loader currently hardcodes retail + `MockRetailDomainEnv`;
airline modules already vendored at `tau_bench/envs/airline/`. Add airline as a module-path swap +
loader path + test. Disclose: Haiku user-sim ≠ GPT-4o (not leaderboard-comparable).

**Cross-cutting:** rerun the **RVR intervention on every new split** so the intervention claim
generalizes beyond BFCL multi-turn.

---

## (b) BASELINES TO ADD — the RVR ablation ladder + constrained-decoding upper bound

Framing fact: RVR's *mechanism* already ships default-on in LangGraph/smolagents/pydantic-ai/
instructor. **Novelty is not the intervention** — it is (1) measuring the per-call TEHR these
guardrails silently absorb, (2) quantifying RVR recovery across families, (3) the black-box-API vs
white-box-decode-time asymmetry. The baselines must build that ablation ladder.

Implemented as sibling pure functions in `harness/intervention/` — signature
`(parsed_calls, registry) -> Action`. `rvr.py`, `naive_retry.py`, `decoy_list.py`,
`framework_default.py` already exist.

**Ablation ladder (the headline table):**
No-intervention → **A1** generic reask (no registry) → **A2** Reflexion-style ungrounded reflection
→ **A3** Self-Refine-style intrinsic refine → **RVR** (grounded reask) → **A5** constrained decoding
(structural upper bound, local-MLX only). This single ladder answers every "is RVR just X?" question.

| # | Baseline arm | Effort | License | Notes |
|---|--------------|--------|---------|-------|
| A1 | Generic reask ("invalid, try again", no registry) | trivial — exists as `naive_retry.py` | MIT (instructor pattern) | isolates retry vs registry-grounding |
| A2 | Reflexion-style ungrounded self-reflection retry | **<1 hr**, ~25-line sibling | MIT (Reflexion) clean-room | grounded vs ungrounded reflection head-to-head. Borrow prompt shape from `alfworld_runs/generate_reflections.py`; do NOT vendor (repo is OpenAI-locked, non-installable) |
| A3 | Self-Refine-style intrinsic refine (no external feedback) | low | Apache-2.0 (Self-Refine) | predicted to NOT fix tool-existence → motivates grounding |
| A4 | Decoy/distractor-registry robustness arm | exists (`decoy_list.py`) | n/a | inject near-miss names; seed decoys from ToolEmu `assets/all_toolkits.json` (38 toolkits/330 tools, Apache-2.0, vendor JSON only) |
| **A5** | **Constrained decoding (Outlines)** — local-MLX/Qwen3 ONLY | MED (budget token-accounting glue) | Apache-2.0 | **Primary** decode-time engine. `outlines.from_mlxlm(*mlx_lm.load(...))` wraps the exact objects `mlx_adapter.py::_ensure_loaded` produces. Force tool-name slot to `Literal[registry]` → TEHR=0 by construction. **CRITICAL:** outlines `from_anthropic` *raises* on any `output_type` → structurally unavailable on API tier. Never claim it constrains Anthropic; that asymmetry IS the argument for black-box RVR. Import as dep, do NOT vendor. |

**A5 real cost (under-stated elsewhere):** `MLXLM.generate` returns a bare `str` — no token counts,
no finish_reason. New `ConstrainedMLXAdapter` must re-derive `tokens_in/out` (`tokenizer.encode`) +
`length` finish heuristic + keep `_parse_tool_calls`. Budget the glue, not the license. Keep additive
— do NOT touch the Qwen3 path that produced our published numbers.

**Optional second decode-time engine:** lm-format-enforcer (MIT) — needs a custom MLX
logits-processor adapter (no MLX backend). Only for a 2nd data point; otherwise Outlines suffices.

**Optional model baseline:** ToolACE-2-8B (Llama-3.1 Community weights, inference-only) — BFCL
already ships a `ModelConfig` (`LlamaHandler`) for it, so low plumbing. Frame as "in-distribution FC
specialist" (trained on BFCL-adjacent data → near-zero BFCL TEHR partly in-distribution); cross-check
on tau-bench (OOD) before any apples-to-apples row vs Qwen3/Anthropic. Never relicense weights.

**Optional benchmark-as-baseline:** **When2Call** (NVIDIA, Apache-2.0) — closest published analog to
our axis (4-way MCQ incl. tool-doesn't-exist; ships DPO-style negative data). Strongly consider
running as a breadth+positioning add.

**Accuracy scorer (pre-empts "does RVR hurt accuracy?"):** vendor BFCL `eval_checker` (Apache-2.0,
already on disk) as an **isolated optional extra / subprocess** — it pulls a heavy conflicting dep
tail (`tree_sitter==0.21.3`, `faiss-cpu`, `sentence-transformers`, `qwen-agent`, `numpy==1.26.4`); do
NOT put in the core uv env. Reporting community-standard BFCL accuracy alongside TEHR is the
cost-quality-gap story with an external metric.

---

## (c) PRIOR-ART CITATIONS TO ADD to refs.bib

Already present (do not re-add): `bfcl2024`, `bfclv4_2025`, `taubench2024`, `outlines2023`,
`reflexion2023`, `gou2024critic` (CRITIC), `toolbehonest2024`, `stableTOOLbench2024`,
`huang2024metatool`, `li2023apibank`, `appworld2024`, `langchain_toolnotfound2025`, `jsonmode2024`,
`openaitools2024`, `anthropictools2024`, `selfdebug2023`, `reactagent2023`.

**NEW keys to add** (grouped; all verified permissive or cite-only-safe):

*Measurement / tool-hallucination (closest constructs — highest priority):*
- `nvidia2025when2call` — When2Call (NAACL 2025; NVIDIA/When2Call; Apache-2.0). Closest analog; +run.
- `mirage2025` — mirage-bench (arXiv:2507.21017; sunblaze-ucb; Apache-2.0). Unified agentic-
  hallucination taxonomy; frames TEHR as one instance.

*Self-correction / reflection family (position RVR as grounded reflection):*
- `madaan2023selfrefine` — Self-Refine (Apache-2.0). Baseline A3 + intrinsic-vs-grounded contrast.
- `zou2024textgrad` — TextGrad (zou-group/textgrad; MIT). Recent textual-gradient revision.
- `gou2024tora` — ToRA (microsoft/ToRA; MIT). Tool-integrated reasoning w/ execution-feedback.
- `chern2023factool` — FacTool (Apache-2.0). Pre-empts "vs factuality/consistency detector?".
- `manakul2023selfcheckgpt` — SelfCheckGPT (MIT). Consistency-based hallucination detection.

*Constrained / guided decoding family ("why not just constrain decoding?"):*
- `willard2023outlines` — if the existing `outlines2023` key is the blog/library, add the paper
  (Willard & Louf, arXiv:2307.09702); else reuse existing key.
- `microsoft2023guidance` — guidance (MIT, 21k★).
- `gat2023lmformatenforcer` — lm-format-enforcer (MIT).
- `dong2024xgrammar` — XGrammar (mlc-ai; Apache-2.0).
- `ugare2024syncode` — SynCode (uiuc-focal-lab; MIT; soundness/completeness).
- `microsoft2023aici` — AICI (microsoft; MIT; token-level prompt-editing — closest decode-loop
  analogue to RVR's re-steer).

*Framework prior art (the RVR mechanism shipped in production — novelty-pivot cites):*
- `langgraph2024` — LangGraph `ToolNode` `INVALID_TOOL_NAME_ERROR_TEMPLATE` (MIT). Strongest single
  prior-art for RVR mechanism. (Distinct from existing `langchain_toolnotfound2025` if that is the
  blog; otherwise reuse.)
- `smolagents2024` — smolagents `execute_tool_call` "Unknown tool ... should be one of" (Apache-2.0).
- `pydanticai2024` — pydantic-ai `ModelRetry` (MIT). Canonical reference impl of the RVR loop.
- `instructor2024` — instructor validate→reask→retry (MIT). Also pattern source for revision skill.

*Benchmark / harness context:*
- `seal2024` — Seal-Tools (NLPCC 2024; fairyshine; Apache-2.0). +run (#2).
- `song2023restgpt` — RestGPT / RestBench (MIT). +run (#3 data).
- `inspect2024` — inspect_ai / inspect_evals (UK AISI; MIT). Cite as recognized BFCL+tau2 harness
  whose `multi_turn_match` is state-based and surfaces no per-call TEHR (reinforces our gap).
- `nestful2024` — NESTFUL (Apache-2.0, nested calls) — optional harder axis, cite.
- `rotbench2024` — RoTBench (Apache-2.0, controlled noise levels) — pairs with decoy arm A4, cite.

*Automated-review / persona provenance (for the skill + personas section, if cited):*
- `microsoft2024llmrubric` — LLM-Rubric (ACL 2024; MIT). Calibrated rubric distributions.
- `marg2024`, `agentreview2024` — MARG / AgentReview (Apache-2.0). Multi-agent review scaffolds.

> NOTE on cite-only-but-non-vendorable items that may still be CITED in prose (no data/code copied):
> ToolSandbox (Apple NOASSERTION), NexusRaven (CC-BY-NC data), AI-Scientist(-v2) & CycleReviewer
> (RAIL/Mistral-derivative NOASSERTION), ComplexFuncBench (no license). Citing a paper is always fine;
> redistributing its artifacts is the restricted act.

---

## (d) LICENSE-SAFE VENDOR LIST

**SAFE TO VENDOR (Apache-2.0 / MIT — copy code/data into our repo WITH NOTICE + attribution):**
- gorilla-BFCL (Apache-2.0) — code + data + `eval_checker`. *Already vendored.*
- tau-bench (MIT) — data + loader (incl. airline modules). *Already vendored.*
- **RestGPT → RestBench data + OpenAPI specs only** (MIT). NOT the agent.
- **Seal-Tools data** (Apache-2.0). Reimplement metrics; do NOT vendor their `eval()`-scorer.
- BFCL single-turn / irrelevance categories (Apache-2.0). Already on disk.
- outlines (Apache-2.0) — **import as dep**; thin adapter vendorable.
- lm-format-enforcer (MIT) — adapter vendorable (optional).
- ToolEmu JSON assets (`assets/all_toolkits.json`, `all_cases.json`; Apache-2.0) — for decoy stress
  test; do NOT run its runner (dead langchain pins).
- inspect_ai / inspect_evals (MIT) — data-fetch/category-split patterns vendorable (citation-first).
- AgentLaboratory (MIT) — borrow PATTERNS (`papersolver.py` compile-gate, `agents.py` rubric prompts)
  for the revision skill; flat/monolithic so reimplement rather than copy.

**RUN-EXTERNALLY-ONLY (license permits running as a dep; do NOT copy source into our artifact):**
- ToolSandbox (Apple NOASSERTION, no patent grant) — run+cite; reimplement minefield idea if needed.
- ToolACE-2-8B weights (Llama-3.1 Community) — inference-only baseline; attribute "Built with Llama".

**CITE-ONLY (forbidden to vendor, or nothing useful to vendor):**
- NexusRaven (CC-BY-NC-4.0 data) — never vendor data.
- AI-Scientist / AI-Scientist-v2 (RAIL-derivative: §3.2(e) manuscript machine-generated disclosure
  would attach to OUR paper; §3.3 propagates restrictions) — reimplement rubric/reflection only.
- CycleReviewer/DeepReviewer (Mistral-derivative, non-commercial, registration-gated) — reimplement
  multi-persona pattern only.
- AutoGPT `autogpt_platform/` (PolyForm Shield non-compete) — never touch; MIT core only if ever.
- ToolBench RapidAPI corpus (gated; archived snapshots CC-BY-NC) — never vendor via StableToolBench.
- ComplexFuncBench, mcp-bench (no LICENSE = all-rights-reserved).
- Plus the standard cite-only set: ToolBench, API-Bank, MetaTool, ToolBeHonest, AgentBench, AppWorld,
  ToolACE-dataset (format-mismatched), lm-eval-harness, helm, openai-evals, deepeval, promptfoo,
  guidance, jsonformer, langgraph/crewAI/dspy/letta/storm/paper-qa (all permissive — cite freely).

**Confidence: HIGH.** Every license was read from raw file bytes in the verification passes, not
GitHub's classifier. No GPL/AGPL anywhere in the candidate set.

---

## (e) WHAT TO SKIP, AND WHY

- **ToolSandbox as a 1-day win — SKIP (defer to later phase).** Highest scientific adjacency (3rd
  stateful multi-turn surface) but worst effort/repro profile for our stack: user simulator is
  hardcoded GPT-only (mandatory OpenAI spend + version drift every run), **no MLX serving path** (our
  adapter is in-process, not HTTP; vLLM can't load MLX 4-bit), needs a new Qwen3 agent role, and Apple
  NOASSERTION license. Cite as prior art regardless.
- **StableToolBench TEHR-only loader — SKIP for now (4th-priority fallback).** Code license clean but
  (a) per-query registries are SMALL (median 4-7, max 13) so it does NOT add the large-registry regime
  the original brief assumed — Seal-Tools does that better; (b) full SoPR/SoWR is Linux/CUDA + 2023
  pins + GPT-4 judge (won't run on M5); (c) underlying ToolBench data is gated. Cite for
  stability-vs-existence differentiation.
- **inspect_ai as the runner — SKIP (cite + optional cross-check only).** Its multi-turn scorer is
  state-based and surfaces NO per-call TEHR (out-of-registry call returns an internal "Method not
  found" string and silently degrades state match). Adopting it = standing up a second runtime +
  revalidating MLX tool-call parsing for zero TEHR benefit. Use only to cross-check API-family accuracy
  against a recognized harness if time permits.
- **ToolBeHonest as a benchmark we RUN — SKIP (cite-only + reuse its taxonomy as a persona rubric).**
  It is a per-sample static reasoning diagnostic, not per-call live execution; running it yields a
  differently-defined number to reconcile. Keep it as the key differentiation + baseline anchor
  (GPT-4o 37.0 / Gemini-1.5-Pro 45.3 *do* fabricate tools vs our Anthropic 4.x = 0).
- **guidance as a constrained-decoding arm — SKIP (cite in the family).** No MLX backend; Anthropic
  backend is in `broken_models/`. Off critical path; Outlines is the engine we actually run.
- **NexusRaven — SKIP all runs/vendoring.** CC-BY-NC data, dead 2023 langchain, superseded model.
  Light cite for the forced-choice-over-registry framing.
- **API-Bank loader — SKIP (cite-only).** Free-text `[Api(...)]` DSL + implicit per-turn registries +
  heavy retrieval deps; loader is 3-5 days (note: `api-bank/` subdir is Apache-2.0, not MIT), not a
  quick win.
- **autogen / smolagents / crewAI as runtimes — SKIP vendoring.** Heavy actor runtimes, no MLX client;
  our adapters already cover MLX+API. Cite smolagents `execute_tool_call` as RVR prior art; optional
  scaffold-robustness ablation is MED-HIGH effort with a measurement-validity confound (MLX text-parses
  tool calls → parse misses contaminate TEHR) — API-models-first if ever pursued.
- **lm-format-enforcer / 2nd decode engine — SKIP unless schedule permits.** One engine (Outlines)
  proves the structural-TEHR=0 point; wiring a second burns deadline time for a marginal data point.
- **AI-Scientist / CycleReviewer code & prompts — SKIP vendoring entirely (study-only).** Copying
  their code/prompt text would attach AI-Scientist's §3.2(e) manuscript machine-generated disclaimer to
  our ICML paper and CycleReviewer's non-commercial/registration terms to our harness. Reimplement
  rubric shapes/scales from scratch (those are not copyrightable).

---

## CONCRETE 1-DAY EXECUTION ORDER (harness/breadth track)

0. **(P0)** Add root LICENSE (Apache-2.0) + NOTICE. ~30 min.
1. **Morning (LOW):** extend `bfcl.py` for single-turn + irrelevance/live; add single-turn branch
   (`turns_max=1`, stub executor) + new `BenchmarkName`. Run n≈150 single-turn + full irrelevance
   across Anthropic 4.x + OpenAI + MLX Qwen3 4-bit. *Kills multi-turn + abstention objections.*
2. **Late morning (LOW):** add tau-bench **airline** loader path (module swap). *Free 2nd multi-turn
   domain.*
3. **Midday (LOW-MED):** write `seal_tools.py` (schema normalizer + registry from `tool.jsonl`); run
   in/out-domain × both registry-presentation variants on capped n. *Kills small-registry objection +
   adds generalization axis + answers "does registry size drive TEHR?".*
4. **Afternoon (MED):** write `restbench.py` (OpenAPI→registry); run all 157 TMDB+Spotify. *Kills
   synthetic-tools-only objection; sets up RVR-vs-API-Selector prior-art contrast.*
5. **Cross-cutting:** build the A1/A2/A3 intervention ladder (~1 day total; A2 <1 hr); wire A5 Outlines
   `ConstrainedMLXAdapter` (MED — budget token-accounting glue). Rerun **RVR on every new split**.
   Report per-call TEHR for every family on every split + BFCL `eval_checker` accuracy column.

## PARALLEL TRACK — paper-revision skill + reviewer personas (no harness code)

- **Personas (add 4):** 13 Construct-Validity & Failure-Taxonomy Auditor (highest leverage — guards the
  0-event/single-category headline; reuse ToolBeHonest 6-way taxonomy); 14 Intervention/Causal-Ablation
  Reviewer (forces the A1/A2/A3 control arms); 15 Rubric-Anchored Area Chair (calibrated lenient/harsh
  scoring, LLM-Rubric idea); 16 Generalization/Cross-Family Breadth Reviewer (mandatory main-track
  depth gate). Run 13/14/16 in parallel; 15 as a sequential meta-gate consuming their outputs.
- **Skill (`/spotlight-revision`) — fold in 5 patterns:** P1 compile-gated per-edit validation w/
  auto-revert (AgentLaboratory, MIT); P2 claim-grounding ledger w/ source re-ranking (paper-qa,
  Apache-2.0; ReviewGrounder as design echo of RVR); P3 calibrated rubric + self-consistency
  (few-shot anchors, reflection/ensemble — AI-Scientist/CycleReviewer study-only, LLM-Rubric MIT);
  P4 `13_coverage_moderator` persona (Co-STORM under-discussed-evidence finder, MIT); P5 per-entry
  experiment solve loop (AgentLaboratory mlesolver pattern). All reimplemented in our orchestration
  layer — zero code vendored.

**One-line thesis for the breadth section:** BFCL single-turn (removes the multi-turn variable) +
Seal-Tools (large diverse registry + in/out-domain generalization) + RestBench (real REST/OpenAPI
domain) + tau-bench airline turn a single-setting result into a multi-benchmark, multi-domain,
multiple-turn-structure characterization of tool-existence hallucination — all permissively licensed,
all on the existing MLX + API harness, all within a day.
