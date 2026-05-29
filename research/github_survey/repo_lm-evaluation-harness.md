# Repo survey: lm-evaluation-harness

- **Repo:** EleutherAI/lm-evaluation-harness
- **Canonical URL:** https://github.com/EleutherAI/lm-evaluation-harness (live, no 404)
- **Stars:** 12,737 (gh api, 2026-05-29)
- **License:** MIT (SPDX: MIT) — verified via `gh api .license.spdx_id`
- **Language:** Python · actively maintained (last push 2026-05-11)
- **Category:** eval-harness

## What it does
A unified framework for **few-shot evaluation of generative LMs** across 60+ standard
academic benchmarks (MMLU, HellaSwag, GSM8K, TruthfulQA, ARC, HumanEval, ...) with
hundreds of subtask variants. It is the engine behind HF's Open LLM Leaderboard and is
used by NVIDIA, Cohere, Mosaic, etc. Tasks are defined declaratively in **YAML** (Jinja2
prompts, Promptsource imports). Broad backend coverage: HF Transformers, vLLM, SGLang,
OpenAI / Anthropic / Cohere / LiteLLM APIs, OpenAI-compatible local servers, NeMo,
Megatron-LM, OpenVINO, AWS Neuron.

Request types are the classic four: `loglikelihood`, `loglikelihood_rolling`,
`generate_until`, and multiple-choice. **It does not model tool/function calling, a tool
registry, or agentic multi-turn rollouts.** No BFCL, tau-bench, or function-calling tasks
ship with it.

## Fit for our paper (TEHR / RVR on BFCL multi-turn)

Our harness (`harness/bench_loaders/*.py`, per-task tool `registry`, family-specific
adapters in `harness/adapters/`, `cost_meter.py`, intervention/RVR) is purpose-built for
**multi-turn tool-calling** and a per-call **Tool-Existence Hallucination Rate**. lm-eval
operates on a fundamentally different abstraction (static prompt -> scored completion),
so the headline contribution cannot be expressed in it.

Concrete verdict by axis:

- **RUN as an extra benchmark? NO (not for the headline).** lm-eval has no tool-call
  surface, so TEHR/RVR cannot be measured through it. It *could* provide an orthogonal
  **general-capability sanity panel** (MMLU/GSM8K/IFEval) to show our Qwen3 4-bit
  checkpoints and Anthropic models are "normal" before measuring TEHR — but that is a
  nice-to-have appendix table, not a tool-hallucination benchmark. Effort to wire even
  that: medium (separate CLI, separate model abstraction; our MLX adapters would need its
  model API, easier to just call `lm_eval` standalone on the same checkpoints).

- **Reuse a COMPONENT in our harness? LOW value.** Our registry/adapter/metric stack
  already exists and is tighter than lm-eval's generic plumbing. The only mildly reusable
  idea is its **YAML task-config pattern** (see below under PATTERN). Pulling in the
  package as a dependency is not worth it — MIT makes it legal, but it adds a heavy dep
  for no functional gain.

- **Reuse as a BASELINE? NO.** It is not a tool-hallucination method or an intervention;
  there is nothing to baseline RVR against here.

- **Cite as PRIOR ART? YES — and necessary.** This is the canonical reference for
  "standard LM evaluation harness" and explicitly the contrast class for our paper:
  established harnesses score static tasks (loglikelihood/MC/generate-until) and have **no
  notion of tool existence**, which is exactly the gap our per-call TEHR metric fills.
  Cite it (and optionally HELM, BIG-bench) in Related Work to position TEHR/RVR as
  agentic/tool-calling evaluation that existing harnesses do not cover. Also a good cite
  for "config-driven, reproducible eval" as a design value we inherit.

- **Borrow a PATTERN for the paper-revision skill / personas? LOW/INDIRECT.** Nothing for
  the revision skill specifically. One transferable engineering pattern: **declarative
  YAML task specs + a fixed request-type taxonomy** — we could frame our bench_loaders as
  emitting a small fixed set of "tool-call request types," mirroring lm-eval's clean
  task-config story, which strengthens the reproducibility narrative reviewers like.

## License risk
None. MIT — permissive, allows reuse/vendoring with attribution. Citing it carries zero
risk.

## Bottom line
**cite-only** (with an optional low-priority appendix sanity panel). It is the textbook
prior-art contrast for "evaluation harness that has no concept of tool existence," which
is precisely the wedge for TEHR/RVR. Do not try to run TEHR through it or use it as a
baseline; do cite it prominently in Related Work and Methods (harness design).

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Independently re-verified every load-bearing claim against the GitHub API and the actual
source files. Net: the survey's facts hold up; its `cite-only` verdict is CORRECT; but
one nice-to-have suggestion (the "sanity panel") is over-optimistic and is downgraded.

**License — CONFIRMED, exact SPDX = MIT.** Did not trust the API summary alone: decoded
the actual `LICENSE.md` blob via the contents API. It is verbatim MIT text, "Copyright
(c) 2020 EleutherAI". `gh api .../license` also returns spdx_id=`MIT`. This is PERMISSIVE
— no GPL/AGPL/copyleft trap. We may legally vendor, modify, or run it, with attribution.
The survey's "License risk: None" is accurate. (The GPL/AGPL vendoring concern raised in
the task does NOT apply here — MIT is safe to vendor into our permissive codebase.)

**Stars — CONFIRMED.** `gh api` returns 12,737 today, matching the survey's number
exactly. Order-of-magnitude ~10^4. Not archived; default branch `main`; last push
2026-05-11 (matches survey). Actively maintained claim holds.

**"No tool-calling / no BFCL / no tau-bench" — CONFIRMED.** Request types are the four
classic ones (`loglikelihood`, `loglikelihood_rolling`, `generate_until`,
`multiple_choice`). No function-calling/tool-registry/agentic-rollout surface. So TEHR/RVR
genuinely cannot be expressed in it. The wedge framing for Related Work is legitimate.

**MLX claim — CORRECTION (survey slightly overstated implicitly).** There is NO MLX
backend (`search/code` for "mlx" = 0 hits; no mlx file in `lm_eval/models/`). What exists
is PyTorch **MPS** (`--device mps`), which is NOT our MLX path. Our local Qwen3 4-bit
checkpoints run under MLX; to use lm-eval on them we would either (a) re-load via HF
Transformers+MPS (different runtime, different quantization, so NOT the same artifact we
measure TEHR on — results would not be apples-to-apples) or (b) write a custom model
adapter. Either way it does not reuse our existing MLX adapters.

**"Optional appendix sanity panel" — DOWNGRADED to LOW/skip.** The survey floated running
MMLU/GSM8K/IFEval to show our models are "normal." Two problems it missed:
  1. The **Anthropic backend does not support `loglikelihood`** — both `AnthropicLM` and
     `AnthropicChat` raise NotImplementedError / "does not support the return of
     loglikelihood". So MC/loglikelihood benchmarks (much of MMLU-style scoring) cannot run
     on our Anthropic 4.x models through lm-eval at all; only `generate_until` tasks work.
     A clean cross-family sanity panel is therefore NOT free.
  2. The MLX-vs-MPS mismatch above means the Qwen3 numbers would be on a different runtime
     than our TEHR measurements, weakening the "these are the same models" argument.
  This panel is a reviewer nice-to-have at best and carries real wiring cost; do not commit
  to it.

**Verdict: cite-only (confidence HIGH).** Cite prominently as the canonical static-eval
harness with no notion of tool existence — exact prior-art contrast for TEHR/RVR. Do NOT
run as our headline benchmark, do NOT use as a baseline, do NOT bank on the sanity panel.
License is MIT, so vendoring/reuse is legally fine if ever wanted, but offers no
functional gain over our existing registry/adapter/metric stack.

---

## INDEPENDENT RE-VERIFICATION #2 (2026-05-29, second adversarial pass)

Re-checked every load-bearing claim from scratch against the GitHub API + raw source
blobs (did not trust the prior section). Result: prior verdict HOLDS; no overstatement
survived. Details:

- **LICENSE — CONFIRMED, SPDX = MIT.** Did not trust `.license.spdx_id` alone: decoded the
  raw `LICENSE.md` blob via the contents API. It is verbatim MIT, "Copyright (c) 2020
  EleutherAI" (full permission grant incl. modify/merge/sublicense). API `spdx_id` also =
  `MIT`. PERMISSIVE — no GPL/AGPL copyleft. The task's GPL/AGPL vendoring trap does NOT
  apply: we may legally vendor lm-eval into our (permissive) codebase with attribution.
  `license_confirmed = true`.

- **STARS — CONFIRMED.** `gh api` = 12,737 (order ~10^4). Survey's exact figure matches.
  Not archived, not a fork, default branch `main`, last push 2026-05-11 (actively
  maintained holds).

- **MLX — CONFIRMED NO MLX BACKEND.** Code search `mlx repo:...` = 0 hits. Enumerated
  `lm_eval/models/`: backends are HF/vLLM/SGLang/OpenAI/Anthropic/LiteLLM/NeMo/Megatron/
  TRT-LLM/Neuron/gguf/mamba/winml/watsonx/optimum-{habana,ipex,lm}/textsynth — NO mlx.
  Only PyTorch MPS exists, which is a different runtime than our MLX 4-bit checkpoints.
  Running our Qwen3 artifacts through lm-eval means re-loading under HF (different
  quantization) or writing a custom adapter — NOT apples-to-apples with our TEHR numbers.

- **Anthropic loglikelihood — CONFIRMED LIMITATION.** Read raw `anthropic_llms.py`:
  `loglikelihood` and `loglikelihood_rolling` raise NotImplementedError ("No support for
  logits"); the Chat class raises "Anthropic Chat Completions API does not support the
  return of loglikelihood" (lines 269-273, 380-382). So MC/loglikelihood-scored tasks
  (most of MMLU-style) CANNOT run on our Anthropic 4.x via lm-eval — only `generate_until`.
  The "sanity panel" idea is genuinely NOT free for the API family. Downgrade stands.

- **No tool/function-calling surface — CONFIRMED.** Request taxonomy is the 4 classic types
  (`loglikelihood`, `loglikelihood_rolling`, `generate_until`, `multiple_choice`); no tool
  registry / agentic rollout. TEHR/RVR is inexpressible here. The Related-Work wedge
  ("static-eval harness with no notion of tool existence") is legitimate prior art.

**CLAIMS CHECK (did the survey overstate?):** Stars NOT overstated (exact). License NOT
overstated (truly MIT/permissive). Usability: the survey's headline `cite-only` is
honest, BUT the original pre-adversarial draft floated an MLX-runnable "sanity panel"
that is over-optimistic — there is no MLX backend and the Anthropic family can't do
loglikelihood tasks. That optimism was already caught and downgraded in pass #1; I
confirm the downgrade. No remaining over-optimistic claim.

**FINAL VERDICT: cite-only (confidence HIGH).** Canonical static-eval harness with no
concept of tool existence = exact prior-art contrast for our per-call TEHR + RVR. Do NOT
run as headline benchmark (no tool surface), do NOT use as a baseline (no
method/intervention to compare), do NOT bank on a cross-family sanity panel (no MLX path;
Anthropic can't score loglikelihood tasks). MIT license means reuse/vendoring is legal if
ever desired, but yields no functional gain over our existing harness.
