# Repo Survey: StableToolBench

- **Repo:** THUNLP-MT/StableToolBench
- **URL:** https://github.com/THUNLP-MT/StableToolBench
- **Stars:** 234 (gh api, 2026-05-29)
- **Forks:** 24 | **Open issues:** 19 | **Archived:** no | **Last push:** 2025-04-15
- **License:** Apache-2.0 (SPDX, permissive — verified via gh api `.license.spdx_id`)
- **Paper:** Guo et al., "StableToolBench: Towards Stable Large-Scale Benchmarking on Tool Learning of LLMs", Findings of ACL 2024 (arXiv:2403.07714). Built on ToolBench.
- **Project page:** https://zhichengg.github.io/stb.github.io/

## What it does
A tool-learning benchmark derived from ToolBench (16k+ real RapidAPI tools). The core
contribution is fixing the *instability* of real online APIs by replacing them with a
**virtual API server**:
- **Caching system** — replays cached real request/response pairs for reproducibility.
- **API simulators** — when no cache hit, an LLM (GPT-4 family) or a trained simulator
  (MirrorAPI, served via vLLM, covers 7000+ tools) fabricates a plausible API response.
- **Solvable query filtering** — queries pre-filtered by consensus of gpt-4-turbo,
  gemini-pro, claude-2 to remove unsolvable/ambiguous tasks.

Evaluation metrics: **Solvable Pass Rate (SoPR)** and **Solvable Win Rate (SoWR)**, both
GPT-4-as-judge; plus a newer Final-Answer-Correctness (FAC) judge. Tasks are multi-step
tool-calling trajectories using CoT or DFS (DFSDT) search. Supported reference systems:
GPT-3.5/4 (CoT/DFS), ToolLLaMA v2.

## Setup / cost reality
- Requires: ToolBench data download (HuggingFace + access-form key), OpenAI API keys for
  the GPT-4 judge AND the GPT-based API simulator, optional vLLM GPU server for MirrorAPI,
  optional Docker. Config via YAML (endpoints, ports, cache paths).
- Running it means standing up the virtual API server **and** paying for GPT-4 judging on
  every trajectory. Non-trivial infra + recurring API spend. Trajectories are long
  (DFSDT search trees), so token cost per task is high.

## Concrete judgement for our paper (TEHR / RVR)

**RUN as an extra benchmark — MEDIUM-HIGH effort, qualified yes.**
This is the single best candidate among tool-learning benches for *breadth on tool
hallucination* because its scale (hundreds of tools per query domain, 16k+ tool universe)
makes the tool registry large and easy to mis-remember — exactly the regime where
TEHR (calling a tool not in the registry) should rise. But: (a) the virtual API server +
GPT-4 judge is heavy infra and recurring cost; (b) our harness's `Task` abstraction
(`registry` + `expected_outcome`, see harness/bench_loaders/tau_bench.py) needs a new
loader that parses ToolBench's `*.json` query files and the per-query `relevant APIs` /
tool-doc JSON into our OpenAI-shape registry. TEHR does NOT need the judge or the API
server at all — it is computed from "called tool name ∈ registry?", which is a pure
trajectory-side metric. **So we can run a cheap TEHR-only variant** (drive models over
StableToolBench queries + tool docs, log calls, never even invoke the virtual server) and
skip SoPR/SoWR. That makes a third benchmark family realistic without the cost blowup.
RVR (re-prompt with registry on a bad call) maps cleanly: on a non-existent-tool call,
re-inject the query's tool-doc list.

**Reuse a COMPONENT in our harness — LOW-MEDIUM effort, yes (data + registry parsing).**
The valuable reusable asset is the **query dataset + per-query tool documentation JSON**
(Apache-2.0, safe to vendor with attribution). A `stabletoolbench.py` loader mirroring
`tau_bench.py` would: read the solvable-query files, build `registry` from each query's
candidate tool docs, set `expected_outcome` from the query's solvable label. The virtual
API server itself is NOT worth reusing for our metric — it solves a problem (API uptime)
orthogonal to tool-existence hallucination.

**BASELINE — partial.** SoPR/SoWR are task-success metrics, not hallucination metrics, so
they are not a direct baseline for TEHR. But their published GPT-3.5/4/ToolLLaMA SoPR
numbers give a *reference task-success backdrop* if we want to show TEHR moves
independently of pass rate. Treat as context, not a head-to-head baseline.

**PRIOR ART — yes, cite.** Strong, well-known prior art on tool-learning evaluation and
on benchmark *stability/reproducibility*. We should cite it to (a) position our work
relative to large-scale tool benchmarks beyond BFCL/tau-bench, and (b) DIFFERENTIATE: they
stabilize the *environment* (API responses); we measure a *failure mode* (calling a tool
that does not exist in the registry) that their success-rate metrics do not isolate. Their
"API simulator hallucinates a response" mechanism is itself worth a sentence — it can mask
tool-existence errors, which strengthens our motivation for a registry-membership metric.

**PATTERN for paper-revision skill / personas — minor.** Their solvable-query
multi-judge consensus filtering (3 models must agree a task is solvable) is a reusable
*rubric pattern* for a reviewer persona that demands "is this eval well-posed / are tasks
filtered for solvability?" Worth encoding as a reviewer check, not a code reuse.

## License risk
Apache-2.0 = low risk. Permissive, allows commercial + redistribution with attribution and
NOTICE preservation. CAVEAT: the underlying **ToolBench data** has its own terms (gated
HF download + access form); confirm ToolBench's data license before vendoring the query
files into our repo. The StableToolBench *code* is clean Apache-2.0.

## Bottom line
Best fit = (1) cite as prior art and explicitly differentiate (env-stability vs
tool-existence failure), and (2) build a TEHR-only loader over its solvable queries + tool
docs to add a third benchmark family cheaply, bypassing the GPT-4 judge and virtual server.
Full SoPR/SoWR reproduction is possible but high-cost and not needed for our headline.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

**License — CONFIRMED Apache-2.0 (read the actual LICENSE text, not just the classifier).**
- `gh api .license.spdx_id` returns `Apache-2.0`, but that field is a fuzzy classifier and not
  authoritative. I fetched the raw `LICENSE` blob: it is the verbatim "Apache License, Version
  2.0, January 2004" boilerplate. SPDX `Apache-2.0` is genuine. Permissive — safe to vendor the
  *code* with attribution + NOTICE preservation. NOT GPL/AGPL; no copyleft vendoring blocker.
- **Data caveat stands and is the real risk.** The query files depend on the upstream OpenBMB/
  ToolBench corpus. Upstream ToolBench's *current* LICENSE is also Apache-2.0 (verified raw file),
  BUT (a) archived 2023 snapshots of ToolBench were CC-BY-NC-4.0, and (b) ToolBench's full tool
  set + cache require a **gated download** (HuggingFace + a "ToolBench key" application form that
  the StableToolBench README itself notes can go unanswered). The RapidAPI-derived content is
  "research/educational use only" per ToolBench's own terms. => Treat the per-query JSON as
  research-use, attribute both StableToolBench AND ToolBench, and do NOT assume the underlying
  API content is freely redistributable just because the code is Apache-2.0.

**Stars — CONFIRMED order of magnitude.** 234 stars (re-pulled twice, 2026-05-29). Hundreds, not
thousands. Survey's "234" is exact and correct. Forks 24, open issues 19, not archived, last push
2025-04-15 (~13 months stale as of today; maintained-ish but not active).

**"run-as-benchmark" claim — PARTIALLY OVERSTATED; downgraded to RUN-AS-BENCHMARK (TEHR-only),
NOT full reproduction.** Pressure-test results:
- GOOD NEWS (verified): the `solvable_queries/test_instruction/*.json` files ARE self-contained
  per-query registries. Each entry has keys `['api_list', 'query', 'relevant APIs', 'query_id']`.
  `api_list` is a clean list of tool docs (tool_name, api_name, params, template_response) — maps
  directly to our `registry`, and `relevant APIs` gives ground-truth for an RVR re-inject. This
  confirms the survey's core reuse claim: a `stabletoolbench.py` loader mirroring `tau_bench.py`
  is feasible and the TEHR metric (called-tool-name ∈ registry?) needs NEITHER the virtual server
  NOR the GPT-4 judge. This is the genuinely usable path for our MLX+API harness.
- OVERSTATEMENT #1 (material): survey says scale gives "hundreds of tools per query domain ...
  large registry easy to mis-remember — exactly the regime where TEHR should rise." FALSE at the
  per-query level. Measured registry size per query (G1_instruction, n=163): min 1 / median 5 /
  max 10 tools. The 16k-tool universe is NOT presented to the model per call; each query exposes
  ~5 candidate tools. That is SMALLER than some BFCL multi-turn registries. The "large registry
  pressure on TEHR" rationale does not hold as written — the breadth value is *diversity of tool
  schemas across queries*, not large per-call registries. Adjust the paper rationale accordingly.
- OVERSTATEMENT #2 (cost framing): full SoPR/SoWR/FAC reproduction requires standing up the
  virtual API server (Docker/FastAPI, pinned ancient deps: transformers==4.28.1, langchain==
  0.0.229, deepspeed==0.9.2, torch>=1.12, bitsandbytes — a CUDA/Linux stack that will NOT run on
  our M5 MLX box and conflicts with a modern env) AND OpenAI gpt-4-turbo-preview keys for both the
  judge and the GPT API simulator. Inference is routed through `http://localhost:8080/virtual`,
  i.e. models are wrapped behind their server, not called directly. For our harness that is heavy,
  Linux-GPU-bound, and recurring-cost infra. The survey did acknowledge cost but undersold the
  env/platform incompatibility (MirrorAPI vLLM server is CUDA; dep pins are 2023-era).
- NET: the survey's "RUN as an extra benchmark — MEDIUM-HIGH, qualified yes" is defensible ONLY
  for the TEHR-only data-reuse path. The full benchmark is effectively run-externally-only for us
  (Linux+CUDA+OpenAI), not vendorable as a live eval. I downgrade the headline recommendation to
  **run-as-benchmark (TEHR-only loader over the query JSON), and cite for the rest.**

**Net penalty applied:** survey was over-optimistic on (a) per-query registry scale and (b)
infra/platform portability to our MLX stack, and slightly under-flagged the ToolBench data
gating/research-use terms. Core reusable asset (self-contained query+tool-doc JSON, Apache-2.0
code) is real and confirmed.

**FINAL VERDICT:** license Apache-2.0 (confirmed, high confidence). Recommend **include-parts /
run-as-benchmark**: build a TEHR-only loader over `solvable_queries/test_instruction/*.json`
(attribute StableToolBench + ToolBench; honor research-use terms on the API content), and cite the
full benchmark + stability-vs-existence differentiation as prior art. Do NOT attempt full
SoPR/SoWR reproduction inside our harness (Linux/CUDA/OpenAI-bound, stale deps, recurring cost).

---

## INDEPENDENT RE-VERIFICATION #2 (2026-05-29, Opus — fresh pull, no trust of prior notes)

I re-pulled every load-bearing fact from source rather than trusting either the original survey or
the first adversarial pass. Results below; where I confirm a prior claim I say so explicitly.

**License — CONFIRMED Apache-2.0, HIGH confidence (verbatim text, not just classifier).**
- `gh api repos/THUNLP-MT/StableToolBench` → `license.spdx_id = Apache-2.0`, `key = apache-2.0`.
- Decoded the raw LICENSE blob: it is the verbatim "Apache License, Version 2.0, January 2004"
  boilerplate. Genuine SPDX `Apache-2.0`. NOT GPL/AGPL — no copyleft vendoring blocker. The *code*
  is safe to vendor into our (permissive) codebase with attribution + NOTICE preservation.
- Upstream OpenBMB/ToolBench LICENSE also decoded raw: also Apache-2.0 (5.6k stars). So both the
  StableToolBench code AND the upstream code layer are permissive.
- DATA-vs-CODE distinction (the real caveat, confirmed): the README explicitly requires a
  **ToolBench key via a Google Form** (https://forms.gle/oCHHc8DQzhGfiT9r6) to use the *virtual API
  server*, and the README itself warns the key application "did not get a response for a long time"
  is a known failure mode. The *solvable query JSON* appears unrestricted/freely downloadable; the
  *server/cache* is gated. The RapidAPI-derived API content is research-provenance regardless of the
  Apache header on the code. => Vendoring the query+tool-doc JSON for a TEHR-only metric is fine
  with attribution; do not assume the live API content is freely redistributable.

**Stars — CONFIRMED, order of magnitude correct.** 234 stars (re-pulled today). Hundreds, not
thousands. Forks 24, open issues 19, not archived, last push 2025-04-15 (~13.5 months stale).
Survey's exact figure 234 matches. Maintained-ish, not active.

**"run-as-benchmark" — CONFIRMED the prior pass's downgrade. Run TEHR-only; cite the rest.**
- VERIFIED (good news): I downloaded `solvable_queries/test_instruction/*.json` and parsed them.
  Each query entry has keys `['api_list', 'query', 'relevant APIs', 'query_id']`. `api_list` entries
  carry `['category_name','tool_name','api_name','api_description','required_parameters',
  'optional_parameters','method','template_response']` — a clean self-contained tool registry that
  maps directly onto our harness `registry`, and `relevant APIs` is ground truth for an RVR
  re-inject. So a `stabletoolbench.py` loader mirroring `tau_bench.py` is genuinely feasible, and
  the TEHR metric (called-tool-name ∈ registry?) needs NEITHER the virtual server NOR the GPT-4
  judge. This is the real usable path for our MLX+API stack. CONFIRMED.
- OVERSTATEMENT #1 — CONFIRMED and quantified harder. The ORIGINAL survey's rationale ("hundreds of
  tools per query domain ... large registry easy to mis-remember") is FALSE. Measured per-query
  `api_list` sizes across every split:
    - G1_instruction (n=163): min 1 / median 5 / max 10 / mean 5.29
    - G1_tool (n=158): min 1 / median 4 / max 10
    - G2_instruction (n=106): min 2 / median 7 / max 13
    - G3_instruction (n=61): min 3 / median 4 / max 9
  The MAX registry exposed to the model on any query is ~13 tools; typical is 4-7. The 16k-tool
  universe is never presented per call. This is COMPARABLE TO OR SMALLER THAN BFCL multi-turn
  registries — so StableToolBench does NOT give us a "large-registry pressure on TEHR" regime. The
  breadth value is *schema/domain diversity across queries*, not big per-call registries. The paper
  rationale must be rewritten accordingly (do not claim large registries raise TEHR here).
- OVERSTATEMENT #2 — CONFIRMED (platform/portability). `requirements.txt` pins a 2023 CUDA/Linux
  stack: `transformers==4.28.1`, `langchain==0.0.229`, `deepspeed==0.9.2`, `bitsandbytes==0.38.1`,
  `peft==0.3.0`, `torch>=1.12.0`, `fastapi==0.95.1`, `pydantic==1.10.7`. This will NOT run on the
  M5 MLX box and conflicts with any modern env; full SoPR/SoWR/FAC also needs the virtual API
  server (FastAPI/Flask, optional vLLM MirrorAPI = CUDA) plus OpenAI gpt-4-turbo/gpt-4o keys for
  both the judge AND the GPT API simulator, with model inference routed through the server. The
  ORIGINAL survey called this "MEDIUM-HIGH, qualified yes" and undersold the env incompatibility;
  the first adversarial pass correctly downgraded it. I concur with the downgrade.

**Penalty assessment of the survey as written:** the ORIGINAL survey (lines 1-89) overstated (a)
per-query registry scale (materially wrong — refuted by measurement), and (b) portability to our
MLX stack (it is Linux/CUDA-bound). It correctly identified the license, the data-gating caveat,
and the TEHR-only reuse path. The FIRST adversarial pass (lines 92-150) is accurate and I confirm
all of its corrections from independent source data; nothing in it was over-optimistic.

**MY FINAL VERDICT:** License Apache-2.0, confirmed from verbatim LICENSE text (high confidence).
Recommendation = **include-parts** (build a TEHR-only loader over the self-contained
`solvable_queries/test_instruction/*.json`; attribute StableToolBench + ToolBench; treat API
content as research-use) AND cite the full benchmark as prior art with the stability-vs-existence
differentiation. Do NOT vendor or run the full SoPR/SoWR pipeline (Linux+CUDA+OpenAI, 2023 dep
pins, recurring judge cost, ToolBench-key gating). Do NOT repeat the "large registry → higher TEHR"
claim — measured per-query registries are small (median 4-7, max 13).
