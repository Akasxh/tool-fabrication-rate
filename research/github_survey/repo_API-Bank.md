# Repo Survey: API-Bank

- **Repo:** `AlibabaResearch/DAMO-ConvAI` (API-Bank lives in subdir `/api-bank`)
- **Canonical URL:** https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/api-bank
- **Stars (monorepo):** 1,555 (whole DAMO-ConvAI repo; API-Bank is one of many subprojects, not separately starred)
- **License:** MIT (SPDX: `MIT`) — verified via `gh api`. Repo-level license is MIT; the `api-bank/LICENSE` file also exists. **Low license risk.**
- **Last pushed:** 2026-01-22 (monorepo; API-Bank code itself is stable since ~2023)
- **Paper:** API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs — **EMNLP 2023 main** (aclanthology.org/2023.emnlp-main.187), arXiv:2304.08244. (Note: commonly mis-cited as ACL 2024; it is EMNLP 2023.)

## What it is

A benchmark + runnable evaluation system for tool-augmented LLMs. Headline numbers:
- 73 executable API tools in the eval harness; 314 annotated dialogues with 753 API calls.
- A separate training set (1,888 dialogues / 2,138 APIs / ~1,000 domains) used to train their "Lynx" model — not relevant to us.
- Three difficulty levels:
  - **Lv1** — call a known API given the query (the API is given).
  - **Lv2** — retrieve the right API then call it.
  - **Lv3** — plan + multiple API calls across a dialogue (uses `lv3_evaluator.py`).

### Mechanics (from `evaluator.py`)
- Model must emit calls in the textual format `[ApiName(key1='value1', key2='value2')]`, extracted by regex `r"\[(\w+)\((.*)\)\]"`.
- Scoring: (a) API name must match ground truth; (b) the call is **actually executed** against a local mock API implementation, and `api.check_api_call_correctness(result, gt_result)` compares outputs; (c) free-text responses scored by **ROUGE-L F** (flag < 0.2).
- Error categories logged: API name mismatch, execution exceptions, KeyError, missing API call, low-ROUGE response.
- **No explicit hallucinated-tool category.** A fabricated API name just falls into "name mismatch" or an execution exception — it is not isolated or counted as a tool-existence error. This is exactly the gap our TEHR metric fills.

## Concrete judgment for our paper

### 1. RUN it as an extra benchmark? — **Possible but medium-high effort; partial fit.**
- Pros: APIs are locally executable (deterministic, no network), MIT-licensed, multi-turn (Lv3 maps to our multi-turn TEHR story), well-defined ground truth.
- Cons / effort:
  - **Different call format.** Our harness (`bfcl.py`, `tau_bench.py`) yields `Task` objects with a normalized OpenAI-shape `registry` and consumes structured tool-call JSON from the model. API-Bank expects free-text `[ApiName(...)]` and parses with regex. To compute **TEHR** we only need the tool registry per turn + the names the model emits, so we would write a new `bench_loaders/api_bank.py` that (a) loads `lv1-lv2-samples`/`lv3-samples` dialogues, (b) exposes the available API set per turn as a registry, (c) reuses our existing per-call tool-existence check rather than API-Bank's `evaluator.py`. Their executor and ROUGE scorer are **not** needed for TEHR.
  - Their per-API mock implementations live in `apis/` + `init_database/` (sqlite seed) — only needed if we want full task-success scoring, not for TEHR.
  - Estimated: ~1–2 days to add a loader that surfaces the registry + ground-truth/available API names; longer if we also want their full accuracy metric.
- **Recommendation:** worth it as a **third benchmark** for breadth (alongside BFCL + tau-bench) *if* we only port the registry + name-emission path and run our own TEHR/RVR on top. Skip their executor.

### 2. Reuse a COMPONENT in our harness? — **Low value, skip.**
- The regex extractor and ROUGE scorer are trivial and not aligned with our structured-tool-call pipeline. Their executable mock-API layer is heavy (sqlite, per-API Python) and only buys task-success scoring we don't currently report. Don't vendor it.

### 3. Reuse as a BASELINE? — **No (not a method/baseline).**
- API-Bank is a benchmark, not an intervention or model. Their "Lynx" trained model is a baseline *within their benchmark*, irrelevant to RVR. Nothing to reuse as a baseline for our cost-quality-gap / RVR claims.

### 4. Cite as PRIOR ART? — **Yes, strongly recommended.**
- It is a foundational tool-use benchmark and directly motivates the gap we exploit: API-Bank executes calls and scores correctness/ROUGE but **does not isolate tool-existence hallucination as a metric**. Cite to (a) establish the tool-augmented-LLM eval lineage, and (b) differentiate: "Prior tool-use benchmarks (API-Bank, BFCL, tau-bench) measure call correctness/task success but fold nonexistent-tool invocations into generic execution failures; we define a dedicated per-call TEHR." Good breadth signal for main-track ICML.

### 5. Borrow a PATTERN for the paper-revision skill / personas? — **Minor.**
- The Lv1/Lv2/Lv3 difficulty stratification is a clean pattern (capability decomposition: call / retrieve+call / plan+call) that a reviewer persona could cite when pushing us to stratify TEHR by task difficulty. Low priority, optional.

## Bottom line
MIT license (safe). Best immediate use: **cite as prior art and differentiate** (TEHR vs their correctness/ROUGE scoring). Secondary: **port a lightweight loader** to run it as a third benchmark for breadth, surfacing only the per-turn API registry and emitted names through our existing TEHR/RVR path — do **not** vendor their executor or ROUGE evaluator. Not usable as a method baseline.

---

## ADVERSARIAL VERIFICATION (2026-05-29, Opus 4.8)

Independent re-check of the claims above. **Bottom line: one materially wrong license claim and a soft-pedaled effort estimate; the rest holds.**

### License — CLAIM IS WRONG (but outcome still permissive)
- The survey states **"License: MIT … the `api-bank/LICENSE` file also exists"** and labels the whole thing MIT. I read both LICENSE files verbatim:
  - **Repo root** `/LICENSE` → genuinely **MIT** (`Copyright (c) 2022 Alibaba Research`). Confirmed via `gh api` (`license.spdx_id = MIT`) AND by reading the raw file.
  - **`api-bank/LICENSE`** (the code+data we would actually consume) → **Apache-2.0**, NOT MIT. Opening line `Apache License / Version 2.0, January 2004`. The survey asserted this file "exists" but never read it and wrongly folded it under MIT.
- **Effective SPDX for what we'd touch: `Apache-2.0`.** No non-commercial / research-only / CC-BY-NC clause in either file — so the practical "safe to use" verdict survives.
- **But Apache-2.0 ≠ MIT for vendoring.** If we vendor API-Bank code into our (likely MIT/permissive) repo we must: retain the Apache headers, propagate any NOTICE file, and state changes made. MIT has none of these. The survey's "Low license risk / vendor freely" tone undersells these obligations. NOT GPL/AGPL, so no copyleft contamination — running externally and citing are both fine.

### Stars — CONFIRMED
- `gh api` → **1,555** stars on the `AlibabaResearch/DAMO-ConvAI` monorepo. Order-of-magnitude (~1.5k) is correct, and the survey correctly notes API-Bank is a subdir, not separately starred. No inflation.

### Venue / paper facts — CONFIRMED
- **EMNLP 2023 main** (aclanthology 2023.emnlp-main.187, arXiv:2304.08244) confirmed; the survey's "often mis-cited as ACL 2024 → actually EMNLP 2023" correction is right.
- 73 APIs / 314 dialogues / 753 calls and the Lynx training set (1,888 dialogues / 2,138 APIs / 1,000 domains) all match the abstract. No inflation.
- Repo is **not archived**, last push 2026-01-22 — confirmed.

### "cite-only" / runnability pressure-test — SURVEY IS TOO OPTIMISTIC ON EFFORT
The survey's "~1–2 days to add a loader surfacing the per-turn registry" understates the work for our MLX+API harness:
- **No clean per-turn registry exists.** Lv3 samples (`lv3-samples/*.txt`) are semi-structured **scene scripts** (free text: Scene / Key Info / ground-truth `API Calls:` list), not JSON and not an explicit per-turn available-tool set. To compute TEHR ("did the model invoke a tool outside the available set?") we must reconstruct the available-tool universe ourselves from `apis/` + `lv3_apis/` + `tool_manager.py`. Lv1/Lv2 are cleaner but Lv2 explicitly requires **retrieval** of the API before calling.
- **Heavy dep for the retrieval path.** `requirements.txt` pins `sentence_transformers==2.2.2` (pulls torch + transformers) plus `selenium`, `googletrans`, `nltk`. None are needed if we only do TEHR over a precomputed registry, but the as-shipped Lv2/Lv3 tool_manager retrieval depends on sentence_transformers. On our M5/MLX box this is CPU-torch, not blocking but not "free."
- **Our type contract must change.** `harness/types.py` hardcodes `BenchmarkName = Literal["bfcl", "tau_bench"]` and `Task.registry` is canonical OpenAI shape (`{name:{name,description,parameters:<JSON-Schema>}}`). API-Bank has no JSON-Schema tool specs — we'd synthesize OpenAI-shape schemas from their Python API signatures. That's a real adapter, not a thin loader. Realistic estimate: **3–5 days**, not 1–2, to get a defensible TEHR-able loader for Lv1/Lv2; Lv3 (the part that maps to our multi-turn story) is the hardest because the available-tool set is implicit.

### Verdict
- **license_spdx = Apache-2.0** (for the api-bank subdir we'd use; repo root is MIT — survey conflated them).
- **recommend = cite-only** as the primary, safe action. The "run as third benchmark" path is *feasible* (permissive license, no copyleft, locally executable) but is **medium-high effort (3–5 days)**, contradicting the survey's 1–2 day framing — so it is a *stretch*, not a quick win. If we do vendor any code, comply with Apache-2.0 (headers + NOTICE), do not treat it as MIT.
- Cite-as-prior-art / differentiation argument (no isolated tool-existence metric) is sound and is the highest-value use.

---

## ADVERSARIAL RE-VERIFICATION #2 (2026-05-29, Opus 4.8, independent pass)

Re-ran every check from scratch against the live GitHub API and raw file contents; did NOT trust the block above. **The prior adversarial block is accurate. I confirm all of it and add two refinements.**

### License — INDEPENDENTLY CONFIRMED (the MIT label is a trap)
- Read both LICENSE files raw (base64-decoded via `gh api contents`):
  - Root `/LICENSE` = **MIT** (`Copyright (c) 2022 Alibaba Research`). `gh api repos/.../DAMO-ConvAI --jq .license.spdx_id` returns **`MIT`** — but that field reflects ONLY the repo-root file; the GitHub license detector does not see subdirectory overrides. Anyone trusting the API field (or the original survey) inherits the wrong license for the code we'd actually consume.
  - **`api-bank/LICENSE` = Apache-2.0** (`Apache License / Version 2.0, January 2004`). This is the subtree that holds the benchmark code+data we would load. **Effective SPDX for our use = `Apache-2.0`.**
- **Refinement A (NOTICE):** I checked `api-bank/` for a NOTICE file — **none exists**, and the Apache LICENSE is the stock unmodified template (boilerplate `Copyright [yyyy] [name]` appendix, no filled-in attribution). So the vendoring burden is: retain the Apache-2.0 license text + per-file Apache headers + state modifications. There is *no* NOTICE file to propagate (one fewer obligation than a generic Apache repo). Still strictly heavier than MIT.
- Not GPL/AGPL → no copyleft contamination. Citing and running-externally are unconditionally fine; vendoring into our (permissive) repo is allowed but carries Apache attribution duties. The original survey's "Low license risk / MIT" framing is **materially wrong** for the subdir and must not be used.

### Stars — CONFIRMED
- `gh api` → **1,555** stars on the monorepo. ~1.5k order-of-magnitude correct; API-Bank is a subdir, not separately starred. No inflation.

### Venue — CONFIRMED
- aclanthology.org/2023.emnlp-main.187 fetched live: "API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs", **EMNLP 2023**, pp. 3102–3116. The "often mis-cited as ACL 2024" correction is right.

### Runnability / "cite-only" pressure-test — CONFIRMED, survey's 1–2 day estimate is too optimistic
- Live-inspected the data: `lv3-samples/*.txt` are free-text **scene scripts** ("Scene / First Utterance / Key Info / API Calls:") — no per-turn JSON registry, available-tool set is implicit. To compute TEHR we must reconstruct the tool universe from `apis/` + `lv3_apis/` + `tool_manager.py`.
- **Refinement B (mild mitigant):** Lv1/Lv2 live in `lv1-lv2-samples/` as `.jsonl` and the filenames encode the in-scope APIs (e.g. `AddAgenda-AddMeeting-GetUserToken-level-2-2.jsonl`), so the per-sample candidate-tool set is partially recoverable for those levels. Lv3 (the multi-turn part that maps to our story) remains the hard case.
- `requirements.txt` confirmed: `sentence_transformers==2.2.2`, `nltk==3.6.5`, `googletrans==3.1.0a0`, `selenium`, `bs4` — heavy (the retrieval/Lv2 path pulls torch). Not needed for a registry-only TEHR pass, but the as-shipped harness depends on them.
- Our side confirmed: `harness/types.py` hardcodes `BenchmarkName = Literal["bfcl", "tau_bench"]` and `Task.registry` is canonical OpenAI JSON-Schema; API-Bank ships Python API signatures, not JSON-Schema. A real adapter (synthesize OpenAI-shape schemas from signatures) is required, not a thin loader. **3–5 day estimate stands; 1–2 days is unrealistic.**

### Final verdict (this pass)
- **license_spdx = Apache-2.0** for the `api-bank/` subtree we would touch (repo root is MIT; the original survey conflated them — do NOT treat as MIT).
- **recommend = cite-only.** Highest-value, zero-risk use is cite-as-prior-art + differentiation (no isolated tool-existence metric). Running it as a third benchmark is *feasible* (permissive, no copyleft, locally executable) but medium-high effort (3–5 days) and thus a stretch, not a quick win. If any code is vendored, comply with Apache-2.0 (license text + headers + state changes); no NOTICE file to carry.
- Confidence: **high** (all claims checked against raw source/API this pass).
