# License-Risk Audit — SCALE / TEHR / RVR (ICML 2026)

**Synthesist:** license-risk-audit
**Date:** 2026-05-29
**Sources:** verified `repo_*.md` + `discover_*.md` in `research/github_survey/`. Every license below was confirmed in the verification blocks by decoding the raw `LICENSE`/`LICENSE-CODE`/`DATA_LICENSE` bytes (not just GitHub's fuzzy `spdx_id` classifier).

## TL;DR

**No GPL/AGPL anywhere in the candidate set.** The "copyleft veto" the task worried about does not fire on a single repo. The real risks are different and concrete:

1. **CC-BY-NC-4.0 NonCommercial data** — `NexusRaven` eval data. NEVER vendor/redistribute.
2. **Non-OSI bespoke licenses (NOASSERTION)** — `ToolSandbox` (Apple Sample Code), `AI-Scientist(-v2)` (RAIL-derivative, use-restricted + manuscript-disclosure clause), `CycleReviewer` (Mistral-derivative, non-commercial + registration-gated). NEVER vendor.
3. **Source-available non-compete** — `AutoGPT` `autogpt_platform/` (PolyForm Shield). NEVER vendor (the rest of AutoGPT is MIT and fine).
4. **Dual code/data or code/weights splits** that must be read at the *sub-directory* level — `autogen` (MIT code / CC-BY-4.0 docs), `NexusRaven` (Apache code / CC-BY-NC data), `ToolACE` (Apache dataset / Llama-3.1 Community weights), `AutoGPT` (MIT / PolyForm).
5. **One housekeeping blocker on our side:** **our own repo has no `LICENSE` file.** Before vendoring ANY MIT/Apache code we must declare our outbound license, or the MIT/Apache notice-retention obligation is incoherent. (Flagged in `repo_autogen.md`.)

---

## A. Cross-check of every VENDORING candidate (include-full / include-parts / vendor-component)

The recommendation table marks these for code/data inclusion. Verdict column is the license-cleared decision.

| Repo | Rec in table | License (verified) | Copyleft / NC / non-OSI? | VENDOR VERDICT |
|---|---|---|---|---|
| **gorilla-BFCL** | include-parts | Apache-2.0 (raw LICENSE + pyproject + README all agree; data also Apache-2.0) | No | **SAFE TO VENDOR** (already vendored). Code + data + `eval_checker` clean. |
| **StableToolBench** | include-parts | Apache-2.0 (raw LICENSE verbatim) | No — but see data caveat | **SAFE TO VENDOR THE CODE.** Caveat: underlying **ToolBench RapidAPI corpus** is gated (HF + key form) and archived 2023 snapshots were CC-BY-NC-4.0; do NOT vendor the RapidAPI tool data without confirming its terms. Vendor only the loader-relevant query/tool-doc files you build yourself. |
| **ToolEmu** | include-parts | Apache-2.0 (raw LICENSE; `setup.py` classifier wrongly says MIT — both permissive, no risk) | No | **SAFE TO VENDOR JSON assets/prompts.** Retain Apache NOTICE. Code is ~2yr stale (obsolete LangChain pins) — treat code as read-only reference. Final verdict in survey is cite-only, but vendoring assets is legally clean if wanted. |
| **RestGPT** | include-parts | MIT (raw LICENSE, "Copyright (c) 2023 Yifan Song", full grant) | No | **SAFE TO VENDOR RestBench DATA + frozen OpenAPI specs.** Do NOT vendor/run the agent (hard-wired to retired `text-davinci-003`, no lockfile). Data-only path is MIT-clean. |
| **ToolACE** | vendor-component | Dataset Apache-2.0; **weights = Llama-3.1 Community License** | No copyleft; weights are use-restricted | **NOTHING RUNNABLE TO VENDOR** (no eval harness/scorer ever released; tool-call format is a bespoke string DSL). Dataset is Apache (vendorable in principle) but format-mismatched. **Weights: run-as-baseline ONLY, never relicense** (Llama-3.1 Community terms + "Built with Llama" attribution). |
| **outlines** | include-parts | Apache-2.0 (raw LICENSE; all transitive deps permissive) | No | **IMPORT AS DEP, do not vendor.** Thin adapter vendoring is legally fine with NOTICE, but `import outlines` is the right move. Safe. |
| **lm-format-enforcer** | include-parts | MIT (confirmed 3 ways: raw LICENSE "Copyright (c) 2023 Noam Gat" + pyproject + spdx) | No | **SAFE TO VENDOR an adapter** with MIT notice. (Survey lifts it from cite-only to include-parts.) |
| **autogen** | include-parts | **SPLIT: code = MIT (`LICENSE-CODE`), docs = CC-BY-4.0 (root `LICENSE`)** | No copyleft | **CODE SAFE TO VENDOR (MIT).** Do NOT copy docs/figures/prose without CC-BY-4.0 attribution. Practically: don't vendor (heavy actor runtime, no MLX client). Optional external API-only baseline. |
| **smolagents** | include-parts | Apache-2.0 (raw LICENSE; deps all Apache/BSD/MIT/HPND) | No | **SAFE TO VENDOR (Apache).** Practically reimplement — our adapters already cover MLX+API. Cite + optional baseline. |
| **AgentLaboratory** | include-parts | MIT (raw LICENSE, "Copyright (c) 2025 Samuel Schmidgall") | No | **SAFE TO VENDOR (MIT).** But code is flat/monolithic — borrow PATTERNS (`papersolver.py` compile-gated edit loop, `agents.py` reviewer-role prompts) for the paper-revision skill rather than vendoring. |

**Result: all 10 vendoring candidates are permissive (Apache-2.0 / MIT) on the code we'd actually touch.** No GPL/AGPL/CC-NC contamination in any *vendoring* candidate. Two carry sub-component caveats that must be respected: StableToolBench (gated RapidAPI data), ToolACE (Llama-3.1 weights, inference-only).

---

## B. Items that must be RUN-EXTERNALLY-ONLY or CITE-ONLY due to license (NOT vendorable)

| Repo | License (verified) | Why not vendorable | Allowed use |
|---|---|---|---|
| **NexusRaven** | Code Apache-2.0 / **DATA = CC-BY-NC-4.0** (`DATA_LICENSE`, verbatim "Attribution-NonCommercial 4.0") | NonCommercial data is a poor fit for a commercially-unencumbered, reproducible artifact release | **CITE-ONLY.** Do NOT vendor or redistribute the eval data. (Code is technically Apache but not worth it; model is a superseded 2023 13B.) |
| **ToolSandbox** | **NOASSERTION** — custom Apple Sample Code license ("Copyright (C) 2024 Apple Inc.") | Non-standard, **no patent grant**, Apple-name restriction; vendoring Apple-licensed source complicates our open-source artifact's license story | **RUN-AS-BENCHMARK (external dep) + CITE.** Do NOT copy their source into our distributed repo. Re-implement the "minefield / insufficient-info" idea ourselves if needed. |
| **AI-Scientist** | **NOASSERTION** — "AI Scientist Source Code License v1.0" (RAIL-derivative) | Non-OSI; §3.2(e) **manuscript machine-generated disclosure** obligation would attach to our ICML paper; §3.3 propagates use-restrictions downstream. NOT copyleft, but incompatible with a permissive release. | **CITE-ONLY** (+ re-implement reviewer-rubric pattern from scratch). |
| **AI-Scientist-v2** | **NOASSERTION** — same RAIL-derivative license | Same as above: field-of-use restrictions + mandatory machine-generated disclosure + full-license-redistribution requirement | **CITE-ONLY** (+ reimplement reflection/reviewer pattern). |
| **CycleReviewer** | **NOASSERTION** — "CycleResearcher License" (Mistral AI Research License derivative) | **Non-commercial + registration-gated**, bars separating code from weights, mandates AI-assistance disclosure. *More* restrictive than GPL/AGPL for our purposes. | **CITE-ONLY** (+ register before any external run; reimplement DeepReviewer multi-persona pattern). |
| **AutoGPT** | **SPLIT: core = MIT / `autogpt_platform/` = PolyForm Shield (source-available NON-COMPETE)** | PolyForm Shield forbids building a competing product; non-OSI | **CITE-ONLY.** If ever borrowing code, only from the MIT core (`autogpt/`, AGBenchmark) — NEVER from `autogpt_platform/`. |

---

## C. Clean three-bucket table (the deliverable)

### SAFE TO VENDOR (permissive Apache-2.0 / MIT — copy code/assets into our repo with NOTICE + attribution)
- **gorilla-BFCL** (Apache-2.0) — code + data + eval_checker. *Already vendored.*
- **tau-bench** (MIT) — data + loader. *Already vendored (`harness/data/tau_bench_retail/`).*
- **RestGPT → RestBench data + OpenAPI specs only** (MIT). Not the agent.
- **Seal-Tools data** (Apache-2.0) — for a `seal_tools.py` loader. Reimplement metrics, don't vendor their `eval()`-on-strings scorer.
- **StableToolBench code** (Apache-2.0) — but NOT the gated ToolBench RapidAPI corpus.
- **outlines** (Apache-2.0) — import as dep; thin adapter vendorable.
- **lm-format-enforcer** (MIT) — adapter vendorable.
- **inspect_ai / inspect_evals** (MIT) — BFCL data-fetch + category-split patterns vendorable.
- **autogen code** (MIT via `LICENSE-CODE`) — legal but not worth it (heavy runtime, no MLX).
- **smolagents** (Apache-2.0) — legal but reimplement.
- **AgentLaboratory** (MIT) — legal; borrow patterns instead.
- **ToolEmu JSON assets/prompts** (Apache-2.0) — legal; primary use is cite.
- *(ToolACE dataset is Apache-2.0 but format-mismatched — vendoring fails on merit, not license.)*

### RUN-EXTERNALLY-ONLY (license permits running as a dependency, but DO NOT copy source into our distributed artifact)
- **ToolSandbox** (NOASSERTION / Apple Sample Code) — run as external benchmark dep; cite; reimplement minefield idea.
- **ToolACE-8B weights** (Llama-3.1 Community License) — inference-only baseline; attribute "Built with Llama"; never relicense.
- *(AI-Scientist / CycleReviewer can be run externally after registration but offer nothing runnable for our harness — effectively cite-only.)*

### CITE-ONLY (license forbids vendoring into a permissive repo, OR nothing useful to vendor)
- **NexusRaven** — CC-BY-NC-4.0 data; cite as 2023 forced-choice-FC prior art.
- **AI-Scientist** — RAIL-derivative; reimplement reviewer rubric.
- **AI-Scientist-v2** — RAIL-derivative; reimplement reflection loop.
- **CycleReviewer** — non-commercial Mistral-derivative; reimplement multi-persona reviewer.
- **AutoGPT** — cite MIT core only; never touch `autogpt_platform/` (PolyForm).
- Plus the table's existing cite-only set (ToolBench, API-Bank, MetaTool, ToolBeHonest, AgentBench, AppWorld, lm-eval-harness, deepeval, helm, openai-evals, promptfoo, guidance, instructor, jsonformer, langgraph, crewAI, dspy, letta, reflexion, paper-qa, storm) — all permissive MIT/Apache, no risk; cite freely.

---

## D. Ranked, actionable plan

**P0 — Blocker before any vendoring (do first):**
1. **Add a `LICENSE` to our own repo** (Apache-2.0 recommended for max inbound compatibility, including the Apache-2.0 patent grant). Without it, every MIT/Apache notice-retention obligation we inherit is undefined. (Source: `repo_autogen.md` verification — "our repo currently has NO LICENSE file".)
2. **Create a `NOTICE` / `THIRD_PARTY_LICENSES` file** listing every vendored repo + its license. Mandatory for Apache-2.0 and good practice for MIT.

**P1 — Vendor the high-value, clean benchmark data (serves ICML breadth):**
3. **RestBench data + OpenAPI specs** (MIT) → `harness/bench_loaders/restbench.py`. Second tool-existence domain (real REST APIs), per-call TEHR with stubbed execution, no live keys. Clean.
4. **Seal-Tools data** (Apache-2.0) → `harness/bench_loaders/seal_tools.py` (in/out-domain splits). Reimplement API-F1/Param-F1 ourselves; do NOT vendor their scorer.
5. **gorilla-BFCL single-turn / irrelevance categories** (Apache-2.0) — already-vendored repo; low effort.

**P2 — Run-external benchmarks/baselines (no vendoring):**
6. **ToolSandbox** as an external benchmark dep (NOASSERTION/Apple) — run + cite, do NOT vendor source. Highest-value third multi-turn family after our own loaders.
7. **inspect_ai** (MIT) — run BFCL/tau2/agentic evals under one runner for breadth; vendoring is legal if we want the data-fetch pattern. Caveat: validate MLX OpenAI-compatible tool-call parsing before trusting TEHR off its traces.
8. **ToolACE-8B** as an inference-only baseline (Llama-3.1 Community) — frame as in-distribution FC specialist; cross-check on tau-bench. BFCL already ships a ModelConfig handler for the ToolACE-2 family (low plumbing).

**P3 — Pattern-borrow for the paper-revision skill / reviewer personas (no code vendoring):**
9. **AgentLaboratory** (MIT) — `papersolver.py` compile-gated section-edit loop + `agents.py` role prompts. Reimplement (code is monolithic).
10. **AI-Scientist `perform_review.py`** rubric pattern + **CycleReviewer/DeepReviewer** multi-persona reconcile — reimplement from scratch ONLY (both licenses forbid vendoring).

**Hard DO-NOT list (license-driven):**
- ❌ Do NOT vendor/redistribute **NexusRaven eval data** (CC-BY-NC-4.0).
- ❌ Do NOT copy **ToolSandbox** source into the distributed artifact (Apple non-standard, no patent grant).
- ❌ Do NOT vendor any **AI-Scientist / AI-Scientist-v2** code (RAIL manuscript-disclosure + downstream-propagation clauses would attach to our paper).
- ❌ Do NOT vendor **CycleReviewer** code/weights (non-commercial + registration-gated).
- ❌ Do NOT touch **AutoGPT `autogpt_platform/`** (PolyForm Shield non-compete).
- ❌ Do NOT vendor the **ToolBench RapidAPI corpus** pulled via StableToolBench (gated; archived snapshots were CC-BY-NC).
- ❌ Do NOT relicense **ToolACE-8B weights** (Llama-3.1 Community) — inference-only.

**Confidence:** HIGH. Every license was read from raw file bytes in the verification passes, not inferred from GitHub's classifier. No GPL/AGPL present; the actionable risks are NC-data, non-OSI bespoke licenses, and one missing LICENSE on our own side.
