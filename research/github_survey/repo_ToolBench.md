# Repo Survey: ToolBench (ToolLLM)

- **Repo:** OpenBMB/ToolBench
- **Canonical URL:** https://github.com/OpenBMB/ToolBench (URL valid, not 404)
- **Homepage/paper:** ToolLLM, ICLR'24 spotlight — https://openbmb.github.io/ToolBench/
- **Stars:** 5,652 (gh api, 2026-05-29) · Forks: 485 · Open issues: 161
- **License:** Apache-2.0 (SPDX `Apache-2.0`) — permissive, low legal risk
- **Last push:** 2025-05-21 (maintained but slowing; superseded in practice by StableToolBench)
- **Category:** benchmark

## What it is
ToolBench is the dataset + training + eval suite behind ToolLLM. It collects **16,464 real-world REST APIs from RapidAPI** and ChatGPT-generated instructions/solution paths over them, split into G1 (single-tool), G2 (intra-category multi-tool), G3 (intra-collection multi-tool). Ships:
- the SFT instruction-tuning data + ToolLLaMA model,
- an **API retriever** (sentence-embedding retrieval over the 16K API corpus),
- a DFSDT (depth-first search decision tree) inference agent,
- **ToolEval**: an LLM-judge evaluator reporting **Pass Rate** (did the agent complete the instruction within an OpenAI-call budget) and **Win Rate / Preference** (ChatGPT judges which of two action sequences is better; ~87% / ~80% claimed human agreement).

## Critical caveat: live RapidAPI dependency
Execution requires a **live RapidAPI backend** keyed behind a Google Form ("ToolBench key"), and the original server has had IP/availability churn (README notes a 2024-08 IP migration). This non-reproducibility is exactly why the **StableToolBench** fork exists (zhichengg/StableToolBench, 234 stars, Apache-2.0, last push 2025-04) — it replaces live API calls with a cached/simulated API-response server. For any reproducible 2026 result, StableToolBench is the realistic target, not raw ToolBench.

## Fit assessment for our paper (TEHR / tool-existence hallucination + RVR)

**Run it as an extra benchmark? — Marginal / not as-is. Effort: HIGH.**
- Our TEHR metric is a *per-call* check: does the model emit a tool name absent from the provided registry? ToolBench's native metrics (Pass Rate, Win Rate) are end-to-end LLM-judge outcome metrics, not per-call existence checks — so we'd *not* reuse ToolEval, we'd recompute TEHR ourselves over the call traces.
- The bigger problem is the registry contract. Our TEHR needs a closed, known-per-task tool set (BFCL gives this cleanly; tau-bench too). ToolBench tasks operate over a *retrieved* subset of the 16K-API corpus, so "tool does not exist" is fuzzy: a hallucinated name might be a real RapidAPI tool that simply wasn't retrieved. That muddies the central definition unless we fix the registry to the retrieved-5 set and treat anything outside it as a TEHR event — defensible but needs an explicit framing decision.
- Live-API non-reproducibility makes raw ToolBench a poor fit for a camera-ready table. StableToolBench's simulated server is the only sane way to run it, adding a second integration.

**Reuse a component in our harness? — Yes, modest. Effort: MED.** The G1/G2/G3 instruction JSONs + per-task `toolenv` API json schemas could feed a new `harness/bench_loaders/toolbench.py` mirroring `bfcl.py` (build per-task `Task.registry` from the retrieved/involved API schemas, run our own adapters, recompute TEHR + RVR offline). This is multi-turn, function-calling, very different tool *distribution* from BFCL (real noisy RapidAPI schemas vs. BFCL's curated stateful classes) — genuinely adds breadth. The retriever and DFSDT agent are NOT worth importing; our harness drives its own MLX/API adapters.

**Reuse as a baseline? — Cite, don't run. Effort: LOW.** ToolLLaMA is a 2023 LLaMA-2-7B SFT model; not a competitive baseline for an Anthropic-4.x / Qwen3 comparison. Use the *numbers/framing* as prior art, not a re-run.

**Cite as prior art? — Yes, strongly. Effort: LOW.** Directly relevant: the 2023-08-08 ToolLLaMA release explicitly markets "lower API hallucination than ChatGPT," and the original ToolLLM paper discusses API/tool hallucination as a failure mode. This is the natural citation to position TEHR against — they *named* the phenomenon but measured it only coarsely (via Pass Rate degradation), whereas we give a clean per-call rate. Good differentiation hook for the related-work + motivation sections.

**Borrow a pattern for the paper-revision skill / reviewer personas? — Yes, niche. Effort: LOW.** ToolEval's LLM-judge design (pre-defined criteria → prompt → multiple judgments → agreement-with-humans validation, ~87%/80%) is a clean template for a reviewer-persona rubric: define explicit criteria, sample multiple judgments, report inter-judge/human agreement as a reliability number. Worth lifting the *validation-against-humans* framing into our persona evaluation methodology.

## Bottom line
- **Cite as prior art (PRIMARY use):** the original tool/API-hallucination claim is the thing TEHR sharpens — must-cite, must-differentiate.
- **Optional harness component (SECONDARY):** a `toolbench.py` loader over G1/G2/G3 + retrieved API schemas adds a real-world, noisy-registry breadth point distinct from BFCL/tau-bench — but only via **StableToolBench's** simulated server for reproducibility, and requires an explicit "TEHR over retrieved registry" definition. Budget HIGH effort if done.
- **Do NOT** run native ToolEval Pass/Win Rate or use ToolLLaMA as a baseline.
- **License:** Apache-2.0 throughout (incl. StableToolBench) — safe to vendor schemas/loader code with attribution.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

**Verified directly against source, not the survey summary:**

| Claim | Survey said | Independent check | Verdict |
|---|---|---|---|
| LICENSE file (repo) | Apache-2.0 | Fetched `master/LICENSE`: verbatim "Apache License / Version 2.0, January 2004". SPDX `Apache-2.0` (gh api `license.spdx_id`). | CONFIRMED |
| Stars | 5,652 | gh api `stargazers_count` = 5652. Order of magnitude (~5.6k) correct. | CONFIRMED |
| Forks / open issues | 485 / 161 | gh api: 485 / 161. | CONFIRMED |
| Last push / archived | 2025-05-21, maintained-but-slowing | `pushed_at` = 2025-05-21T15:46:59Z, `archived` = false, default branch `master`. | CONFIRMED |
| StableToolBench fork | 234 stars, Apache-2.0, push 2025-04 | gh api: 234 stars, `Apache-2.0`, `pushed_at` 2025-04-15. | CONFIRMED |
| Live RapidAPI dependency + Google-Form key | yes | README verbatim: "fill out our form … send you the ToolBench key"; "2024.8 Update: We have updated the RapidAPI server with a new IP". | CONFIRMED |

**Where the survey is OVER-OPTIMISTIC / incomplete:**

1. **"License: Apache-2.0 throughout" is over-broad — the MODEL is NOT Apache-2.0.** ToolLLaMA (`ToolBench/ToolLLaMA-2-7b-v2`) carries the **LLaMA-2 Community License** (HF tag `llama2`, base `LLaMA-2-7b-hf`), Meta's bespoke license with a 700M-MAU clause and use-policy restrictions — NOT permissive Apache-2.0. Impact is LOW because we already recommend NOT running ToolLLaMA, but the blanket "Apache-2.0 throughout" claim is wrong if read literally. Correct statement: **code + dataset = Apache-2.0; model weights = LLaMA-2 Community License.**

2. **The dataset's Apache-2.0 carries an explicit "research and educational purposes" framing + RapidAPI provenance.** README verbatim: ToolBench "is intended solely for research and educational purposes … distributed under Apache License 2.0." The schemas describe 16K **third-party RapidAPI** endpoints whose own ToS govern *live calls*. The Apache-2.0 license on the *schema text/JSON* is genuine and DOES permit vendoring a loader with attribution — so the survey's "safe to vendor schemas/loader code" is technically correct — but the research-only framing + third-party API provenance means we should (a) attribute, (b) ship only schema metadata (not RapidAPI keys/responses), (c) not imply endorsement. Minor flag, not a blocker.

3. **License-vendor risk gate (the GPL/AGPL check requested): PASS.** ToolBench code + data are Apache-2.0, a permissive OSI license — **we CAN vendor schema/loader code into our (permissive) codebase with attribution + NOTICE.** No copyleft contamination. This is the opposite of a GPL/AGPL repo: had it been (A)GPL we could only cite/run-externally; it is not, so vendoring is allowed. The only non-permissive artifact in the project is the *model*, which we are not touching.

**Pressure-testing the recommendation — would we ACTUALLY run/reuse it on our MLX+API harness?**
- **As a runnable extra benchmark: realistically NO for camera-ready.** Native execution needs the live (or StableToolBench-simulated) RapidAPI server. Our harness drives MLX + API model *adapters*; it has no concept of a live tool-execution backend (BFCL/tau-bench loaders build a static `Task.registry` from per-task schemas and we recompute TEHR offline over call traces — confirmed in `harness/bench_loaders/bfcl.py`). Wiring a live/simulated execution server is a NEW integration class, not a loader. HIGH effort, two repos (ToolBench + StableToolBench), and our TEHR/RVR metrics are *offline trace-level* and do not even require live execution — so running the server buys us little. The survey's "MED effort loader" is the only defensible reuse, and it is **schema-extraction only** (build `Task.registry` from G1/G2/G3 involved-API schemas; no server). That is consistent with our harness and is the realistic path if we want ToolBench breadth.
- **"TEHR over retrieved registry" caveat is real and the survey correctly flagged it:** ToolBench's open 16K-API world means a "hallucinated" name may be a real-but-unretrieved tool, muddying the closed-registry premise TEHR relies on. Requires an explicit framing decision; this genuinely dampens its value vs. BFCL/tau-bench's clean closed registries.
- **As a baseline / ToolEval re-run: NO, agreed.** ToolLLaMA (2023 LLaMA-2-7B) is not competitive against Anthropic-4.x / Qwen3, and ToolEval's Pass/Win Rate are not per-call existence metrics.

**Net adjustment to the survey verdict:** recommendation stands as **cite-only for the paper's claims, with an OPTIONAL schema-only harness loader** (`harness/bench_loaders/toolbench.py`) if main-track breadth demands a noisy real-world registry — but do NOT run native ToolEval/live-server, and correct the license statement to "Apache-2.0 code+data; LLaMA-2 Community License model." The "cite-only" framing is sound; the survey slightly oversold license cleanliness (model) and under-stressed that *running* it (not just vendoring schemas) is a HIGH-effort new integration our harness is not built for.

**Confidence: HIGH** (license, stars, fork, and README claims all confirmed against primary source; model-license correction confirmed on HF).
