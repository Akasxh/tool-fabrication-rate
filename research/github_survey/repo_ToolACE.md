# Repo survey: ToolACE

- **Repo:** Team-ACE/ToolACE (HuggingFace org, NOT GitHub)
- **Canonical URL:** https://huggingface.co/datasets/Team-ACE/ToolACE (dataset) · https://huggingface.co/Team-ACE (org) · paper https://arxiv.org/abs/2409.00920 (ICLR 2025)
- **Given URL https://github.com/Team-ACE/ToolACE → 404.** `Team-ACE` is a HuggingFace organization, not a GitHub org. There is **no official GitHub code repo** for ToolACE. Probed `Team-ACE/ToolACE`, `Huawei-Noah/ToolACE`, `noahlab/ToolACE` — all 404 on GitHub.
- **Stars:** N/A (no GitHub repo). HF traction instead: dataset 11.3k downloads / 179 likes; ToolACE-8B model 54.9k downloads / 77 likes (HF, 2026-05-29). Community GitHub forks exist (e.g. `zuoyifan132/ToolAce`, `XiangxiTian/ToolACE-finetune`) but none are authoritative.
- **License:** **Apache-2.0** (SPDX `Apache-2.0`) — confirmed on BOTH the `Team-ACE/ToolACE` dataset card and the `Team-ACE/ToolACE-8B` model card. NOTE: model is finetuned from `Meta-Llama-3.1-8B-Instruct`, so the **Llama 3.1 Community License also applies to the model weights** (acceptable-use + naming/attribution constraints). The *dataset* is clean Apache-2.0.
- **Category:** benchmark (but see below — what's actually released is a *dataset*, not a runnable benchmark)

## What it is
ToolACE ("Winning the Points of LLM Function Calling", Liu et al., Huawei Noah's Ark
Lab, ICLR 2025) is primarily a **synthetic tool-learning data generation pipeline** plus
the resulting **training dataset and finetuned models**. The pipeline (Tool
Self-evolution Synthesis) curates a pool of 26,507 synthetic APIs across 390 domains,
generates multi-turn dialogs via a multi-agent interplay, and filters with a dual-layer
(rule-based + model-based) verification system. Models finetuned on this data
(ToolACE-8B, on Llama-3.1-8B) hit SOTA-for-size on BFCL, rivaling GPT-4-class models.

**What is actually downloadable:**
- `Team-ACE/ToolACE` dataset: ~11.3k rows (a released *subset* of the full training
  set; 37.2 MB JSON). Schema is ShareGPT-style: `{system, conversations:[{from:
  user|assistant|tool, value}]}`. Assistant tool calls are encoded as a **string DSL**,
  e.g. `value = "[Market Trends API(trend_type=\"MARKET_INDEXES\", country=\"us\")]"` —
  NOT OpenAI/JSON function-call objects. Tool schemas live in the long `system` string.
- Models: `ToolACE-8B`, `ToolACE-2-Llama-3.1-8B`, `ToolACE-2.5-Llama-3.1-8B`.

**What is NOT released:** the paper's "ToolACE benchmark" (an executable function-call
eval) was never published as standalone code. The paper *evaluates on* BFCL and API-Bank
(both of which we already survey / wire). There is no eval harness, no scorer, no
generation-pipeline code to clone.

## Concrete reuse verdict (for our TEHR / RVR paper)
- **RUN as an extra benchmark: NO (effectively not possible).** There is no released
  ToolACE benchmark code or held-out executable test set — only a *training* dataset and
  model weights. It cannot serve as an evaluation benchmark for TEHR without us building
  an eval from scratch, and even then it would just be a relabeled BFCL-style task. The
  paper's own numbers come from BFCL/API-Bank, which we already cover. Skip as a benchmark.
- **Reuse a COMPONENT in our harness: LOW value / NO.** The dataset's string-DSL tool-call
  format is incompatible with our `Task`/registry pipeline (we use JSON function schemas;
  BFCL/tau-bench loaders assume that). A `bench_loaders/toolace.py` would mean writing a
  DSL→schema parser for a *training* set with no gold per-call correctness oracle —
  effort with no payoff for measuring per-call hallucination.
- **Use as a BASELINE: YES, as a MODEL baseline (this is the strongest use).**
  `Team-ACE/ToolACE-8B` is a strong, openly-licensed, BFCL-SOTA-for-size **8B function-calling
  model**. Running it through our existing BFCL multi-turn loader to report its per-call TEHR
  alongside Qwen3 (where we found the non-monotonic 0–1.87% curve) and Anthropic 4.x (0 events)
  directly serves the "more model families / baselines" ICML-breadth goal. It is MLX-runnable
  (Llama-3.1-8B arch; 4-bit conversion is routine) and API-free. This is the one concrete win.
- **CITE as PRIOR ART: YES.** Cite Liu et al. ToolACE (ICLR 2025) as (a) a leading
  synthetic-tool-data / function-calling-training contribution, and (b) prior art to
  *differentiate* from: ToolACE optimizes BFCL *accuracy* via training data; our
  contribution is an orthogonal per-call *reliability* instrument (tool-existence
  hallucination) + an inference-time intervention (RVR), not a training recipe. Good
  "they improve scores, we measure a failure mode they don't surface" framing.
- **PATTERN for paper-revision skill / reviewer personas: MARGINAL.** One transferable
  idea: ToolACE's **dual-layer verification (rule-based + model-based) of generated
  data** is a clean template for a reviewer persona that interrogates "how do you know
  your synthetic/annotated eval items are correct?" — useful as a data-quality-skeptic
  prompt. No code reuse.

## Effort & license risk
- **License risk: LOW for the dataset (Apache-2.0).** For the **ToolACE-8B model
  baseline**, the **Llama 3.1 Community License applies** — there's an acceptable-use
  policy and a "Built with Llama" / naming-attribution requirement. We only *run inference*
  for a baseline (no redistribution of weights), which is squarely fine, but the paper
  must attribute correctly. MED-LOW overall; flag the Llama license in the artifact notes.
- **Effort:**
  - Model baseline via existing BFCL loader: **LOW** (download HF weights, MLX 4-bit
    convert, point our runner at it — same path as our other local models).
  - Building any ToolACE *dataset*-based eval loader: **MED-HIGH** and not worth it (DSL
    parser + no correctness oracle).
- **Watch-outs:** (1) Don't conflate the *dataset subset* on HF (11.3k rows) with the
  full training corpus — the full set is not public. (2) The HF tool-call DSL is bespoke;
  any parsing is brittle. (3) When citing, the canonical artifact is the HF org + arXiv
  2409.00920 — do NOT cite a GitHub URL (none exists). (4) ToolACE-8B is trained on
  BFCL-adjacent synthetic data, so a *low* TEHR on BFCL for this model could partly
  reflect train/eval distribution overlap — note that caveat if we report it.

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)
Verdict: **survey is ACCURATE and appropriately conservative.** No over-optimism to penalize; one caveat to elevate.

Independently confirmed (did not trust survey summary):
- **GitHub URL is genuinely dead.** `GET https://github.com/Team-ACE/ToolACE` → HTTP 404; GitHub REST API `/repos/Team-ACE/ToolACE` → `{"status":"404","message":"Not Found"}`. arXiv 2409.00920 abstract points only to `huggingface.co/Team-ACE/`. The survey's central claim (no authoritative GitHub repo; Team-ACE is an HF org) holds. **Stars: N/A — confirmed, no repo to count.**
- **License = Apache-2.0 (SPDX `Apache-2.0`), confirmed from live HF metadata** on BOTH the dataset card (`apache-2.0`) and the `ToolACE-8B` model card (`apache-2.0`). NOT inferred from the survey. The survey's nuance is correct: the *dataset* is clean Apache-2.0, but `ToolACE-8B` is finetuned from `meta-llama/Llama-3.1-8B-Instruct` (confirmed in `config.json`: `_name_or_path` = Meta-Llama-3.1-8B-Instruct), so the **Llama 3.1 Community License also governs the weights** (acceptable-use + "Built with Llama" attribution). Inference-only use for a baseline is fine; redistribution of weights is constrained.
- **Traction order-of-magnitude confirmed:** dataset 11,352 downloads / 179 likes; ToolACE-8B 54,877 downloads / 77 likes (HF live, 2026-05-29). Matches survey's "11.3k/179" and "54.9k/77" — accurate, not inflated.
- **Architecture / MLX-runnability confirmed:** `config.json` shows `architectures:["LlamaForCausalLM"]`, `model_type:"llama"`, hidden 4096 / 32 layers / 8 KV heads / vocab 128256 / llama3 rope. Standard Llama-3.1-8B → `mlx_lm.convert` 4-bit is routine; ~4.5GB fits M5 32GB. Survey's "MLX-runnable, API-free" claim holds.
- **Tool-call format confirmed bespoke:** assistant turns encode calls as a string DSL `[FunctionName(param=val)]` inside `value`, not OpenAI/JSON function-call objects. Survey's "incompatible with our JSON-schema Task/registry pipeline; not worth a `bench_loaders/toolace.py`" is correct.

Vendor-component pressure-test (the key ask):
- **VENDOR dataset/pipeline into our codebase: N/A for licensing, NO on merit.** License would *permit* vendoring (Apache-2.0 is permissive, compatible with our likely-permissive repo — for the avoidance of doubt this is NOT a GPL/AGPL situation, so the copyleft veto does not apply here). But there is nothing runnable to vendor: no eval harness, no scorer, no generation-pipeline code was ever released — only a training-data subset + weights. So "vendor a component" fails on availability, not license.
- **VENDOR the model weights: NO.** Llama 3.1 Community License means weights cannot be relicensed under our repo's terms; treat as an *external dependency we run*, never as vendored source. Run-as-baseline only.
- **The survey's "one concrete win" (ToolACE-8B as a BFCL TEHR baseline) — qualified YES, but I elevate the caveat.** It is the right call for ICML breadth (extra open 8B function-calling family), but the train/eval-overlap caveat is more than a footnote: ToolACE-8B was *optimized on BFCL-adjacent synthetic data*, so a near-zero TEHR for it on BFCL is partly distributional, not a clean cross-family reliability signal. If reported, it must be framed as "in-distribution specialist" and ideally cross-checked on tau-bench (out-of-distribution for it) before drawing any monotonicity/family conclusion. Do not let it sit next to Qwen3/Anthropic as an apples-to-apples row without that disclaimer.

Net recommendation: **cite-only** as the artifact-level verdict (no GitHub to include, no vendorable runnable component, dataset format mismatched). The model-as-baseline path remains a legitimate *optional* add but is a separate decision with the overlap caveat attached, not an "include the repo" outcome. License confirmed; permissive; no copyleft risk.

## ADVERSARIAL VERIFICATION #2 (2026-05-29, second independent re-check, did NOT trust prior section)
Verdict: **survey + prior verification are ACCURATE.** Everything re-confirmed from live sources, not summaries. No over-optimism to penalize. One material NEW finding that *strengthens* the model-baseline path, and one terminology nit on the SPDX.

Re-confirmed independently (live, 2026-05-29):
- **GitHub URL dead — re-confirmed.** `curl https://github.com/Team-ACE/ToolACE` → HTTP **404**; `api.github.com/repos/Team-ACE/ToolACE` → `{"status":"404","message":"Not Found"}`. GitHub repo search for "ToolACE function calling" returns only an unrelated 0-star repo. **No authoritative GitHub repo. Stars: N/A — correct.**
- **License = `Apache-2.0` — re-confirmed from HF API `cardData.license`** (not the rendered card, the raw API): dataset `Team-ACE/ToolACE` → `apache-2.0`; model `Team-ACE/ToolACE-8B` → `apache-2.0` (also tag `license:apache-2.0`). **SPDX is exactly `Apache-2.0`.**
- **Base model / dual-license nuance — re-confirmed.** HF API `cardData.base_model` = `meta-llama/Meta-Llama-3.1-8B-Instruct`; tags include `base_model:finetune:meta-llama/Llama-3.1-8B-Instruct`. `config.json` (via `resolve/main`, parsed live) = `{architectures:["LlamaForCausalLM"], model_type:"llama", _name_or_path:"/data/huangxu/OpenLLMs/Meta-Llama-3.1-8B-Instruct", hidden_size:4096, num_hidden_layers:32, vocab_size:128256}`. So the **Llama 3.1 Community License governs the weights** alongside the repo's Apache-2.0 declaration — confirmed, not inferred. Standard Llama-3.1-8B → MLX 4-bit is routine; MLX-runnable / API-free claim holds.
- **Traction order-of-magnitude — re-confirmed:** model 54,877 downloads / 77 likes; dataset 11,352 downloads / 179 likes. Matches "54.9k/77" and "11.3k/179" exactly. Not inflated.

NEW finding (prior verification missed this — it MATERIALLY affects the model-baseline path):
- **Our vendored BFCL repo already ships a ModelConfig for `Team-ACE/ToolACE-2-8B`.** In `harness/data/bfcl_v4/repo/berkeley-function-call-leaderboard/bfcl_eval/constants/model_config.py`: `ModelConfig(model_name="Team-ACE/ToolACE-2-8B", display_name="ToolACE-2-8B (FC)", org="Huawei Noah & USTC", license="Apache-2.0", model_handler=LlamaHandler, ...)`, and it is listed in `supported_models.py`. This is third-party (Gorilla/BFCL) corroboration of the Apache-2.0 + Llama-handler facts, AND it means the model-as-baseline path is **lower effort than the survey implies** — BFCL already has a registered FC handler for the ToolACE-2 family, so it slots into our existing BFCL loader as a native FC model rather than needing a from-scratch wiring. (Note: BFCL registers `ToolACE-2-8B`; the HF-surveyed weights are `ToolACE-8B` / `ToolACE-2-Llama-3.1-8B` — same family, all Llama-3.1-8B FC, all Apache-2.0.)

Vendor-component pressure-test (the key ask), re-affirmed:
- **Vendor a runnable component: NO — fails on availability, not license.** Apache-2.0 IS permissive and WOULD permit vendoring into our likely-permissive repo; this is explicitly **NOT a GPL/AGPL/copyleft situation**, so the copyleft veto does not apply. But there is no released eval harness/scorer/pipeline to vendor — only a training-data subset (bespoke `[Fn(param=val)]` string DSL, not JSON) + Llama-based weights. Nothing to vendor.
- **Vendor the weights: NO.** Llama 3.1 Community License → run as external dependency, never relicense as our source. Run-as-baseline only.
- **Model-as-baseline (the "one win"): qualified YES with the train/eval-overlap caveat elevated.** ToolACE-* was optimized on BFCL-adjacent synthetic data; a near-zero TEHR on BFCL is partly in-distribution, not a clean cross-family signal. Must be framed as "in-distribution FC specialist" and cross-checked on tau-bench (OOD for it) before any apples-to-apples row next to Qwen3 / Anthropic 4.x. Given BFCL already has the handler, running it is cheap — the *interpretation* is the hard part, not the plumbing.

Final artifact-level recommendation: **cite-only** (no repo to include, no vendorable runnable component, dataset format mismatched, copyleft N/A). Optional model-baseline add is now LOWER-effort than previously stated (BFCL ModelConfig exists) but carries the in-distribution caveat. License confirmed `Apache-2.0`; permissive; no copyleft risk; Llama-3.1 community terms on weights for inference-only use.
