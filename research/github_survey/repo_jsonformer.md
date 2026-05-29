# Repo Survey: jsonformer

- **Repo:** 1rgs/jsonformer
- **URL:** https://github.com/1rgs/jsonformer
- **Stars:** 4,926 (verified via `gh api`, 2026-05-29)
- **License:** MIT (SPDX: MIT) — verified via `gh api repos/1rgs/jsonformer/license`
- **Activity:** Last push 2024-02-24; not archived but effectively dormant (~2 years no commits)
- **Category:** constrained-decoding

## What it does
Jsonformer is a thin wrapper around HuggingFace `transformers` causal-LM models that
guarantees schema-valid JSON output. Core idea: in structured data many tokens are
fixed/predictable (braces, keys, quotes, commas), so the wrapper *emits the fixed
tokens itself* and only delegates *content* tokens (string/number/bool values) to the
model. It walks a JSON Schema and constrains generation per-type:
- `number`, `boolean`, `string`, `array`, `object` (a subset of JSON Schema; no enums,
  no regex/format constraints, no `oneOf`/`anyOf`, no min/max).
- String generation stops on a `"` token; numbers parsed greedily; booleans picked by
  comparing logits of true/false tokens.

It is HuggingFace-only (needs `model`, `tokenizer`, logits access). It is **not** a
benchmark, has no datasets, no metrics, no eval loop. It is a generation-time decoding
constraint, comparable to Outlines / Guidance / lm-format-enforcer (but older, simpler,
and unmaintained).

## Relevance to our paper (TEHR / RVR on BFCL multi-turn)
Our problem is **tool-existence hallucination** — the model invents a tool name not in
the registry. Jsonformer constrains the *shape* of JSON, not the *vocabulary of a
field value*. Out of the box it cannot prevent a hallucinated tool name (a `string`
field is free-form). To constrain the tool name it would need enum/grammar support,
which jsonformer does not have. So it is conceptually adjacent but mechanically
insufficient for our core metric.

## Concrete judgments

**RUN as an extra benchmark?** No. It is not a benchmark — no tasks, no scoring, no
data. Nothing to run.

**Reuse a COMPONENT in our harness?** No (skip). Our harness runs MLX + API models
(Anthropic 4.x, Qwen3 4-bit via MLX). Jsonformer requires HuggingFace logits-level
access; it does not support MLX or remote APIs (the two backends we actually use).
Wiring it in would mean adding a third backend purely to demo constrained decoding —
not worth it. If we ever wanted constrained decoding, Outlines or lm-format-enforcer
are maintained and broader; jsonformer is the weakest of the family.

**Reuse as a BASELINE?** Weakly, and only as prior art rather than a runnable baseline.
A "constrained-decoding eliminates malformed/invalid calls" baseline is a natural
comparison point to our RVR re-prompting intervention — RVR is a *post-hoc detect-and-
reprompt* fix, whereas constrained decoding is a *prevention-at-generation* fix. But to
make jsonformer an actual hallucination baseline you'd need enum constraints over the
tool-name field (grammar-level), which jsonformer lacks; you would reach for
Outlines/Guidance/XGrammar instead. So jsonformer itself is not a fair runnable baseline
for TEHR.

**Cite as PRIOR ART?** Yes — this is the strongest use. It is the canonical, highly
visible (4.9k stars) example of the "fill fixed tokens, only generate content tokens"
constrained-JSON-decoding approach. Useful in related-work to frame the contrast:
constrained decoding prevents *structural* invalidity but does not by itself address
*semantic* tool-existence hallucination, motivating a detect-and-reprompt intervention
(RVR). Pair the cite with Outlines/Guidance for completeness.

**Borrow a PATTERN for the paper-revision skill / reviewer personas?** No. It is a
runtime decoding library; nothing transfers to skills or reviewer rubrics.

## Effort & risk
- **Effort to integrate:** High relative to payoff (would need a new HF backend + grammar
  extension). Effort to cite: trivial.
- **License risk:** None. MIT — permissive, compatible with citing and with any code reuse.
- **Maintenance risk:** Dormant (~2yr). Fine for a citation; a liability if used as a live
  dependency.

## Recommendation
**cite-only.** Use as prior art representing constrained-decoding to contrast prevention-
at-generation vs. our detect-and-reprompt RVR intervention. Do not run, do not vendor,
do not build a baseline on it directly (use Outlines/XGrammar if a constrained-decoding
baseline is wanted).

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verified independently against the live repo (`gh api`) and the raw source, not the survey summary.

**License — CONFIRMED MIT (SPDX: MIT), high confidence.**
- The actual license file is `license.txt` (lowercase), NOT `LICENSE`. The survey's
  cited command `gh api repos/1rgs/jsonformer/license` resolves correctly (GitHub fuzzy
  detection -> MIT), but a direct `contents/LICENSE` fetch 404s because of the filename.
  Minor sloppiness in the survey's verification trail; the SPDX conclusion is correct.
- Read `license.txt` verbatim: standard MIT text, "Copyright (c) 2018 Rahul Sengottuvelu".
  GitHub license API and the file agree: MIT.
- License risk for us: NONE. MIT is permissive — we may cite, run externally, AND vendor
  into a permissive codebase. (The task flagged GPL/AGPL as a vendoring blocker; that does
  NOT apply here — this is MIT, so vendoring would be legally fine if we ever wanted to.)

**Stars — CONFIRMED 4,926 (order of magnitude ~5k), high confidence.** Forks 185, not
archived, last push 2024-02-24 (dormant ~15 months as of today, not "~2 years" — the
survey slightly over-aged it, in the conservative direction so harmless). Survey did not
overstate popularity.

**"cite-only" claim — PRESSURE-TESTED, HOLDS, high confidence.** Confirmed against source:
- `jsonformer/main.py` constructor requires `transformers.PreTrainedModel` +
  `PreTrainedTokenizer`; it calls `self.model.forward(...)`, reads `output.logits[0,-1]`,
  and uses `self.model.device`. Hard-coupled to PyTorch/HF logits-level access.
- `logits_processors.py` subclasses HF `LogitsWarper`/`StoppingCriteria` over raw `torch`
  logit tensors.
- Our harness backends are MLX (local) + Anthropic/OpenAI APIs. NEITHER exposes the raw
  per-step logits tensor jsonformer manipulates. Remote APIs cannot run it at all; MLX
  would need a from-scratch reimplementation of the logits processors. So we genuinely
  CANNOT run/reuse it in-harness without adding a third HF/PyTorch backend.
- `generate_value` dispatches on exactly {number, boolean, string, array, object} and
  raises `ValueError("Unsupported schema type")` otherwise. NO enum, NO regex/format, NO
  oneOf/anyOf, NO grammar. A tool name is a free-form `string` field — jsonformer cannot
  constrain it to a registry. Mechanically insufficient for TEHR even if backend existed.

**Verdict: agree with cite-only.** Survey did not over-claim on stars/license/usability;
if anything it was conservative (over-aged the repo, under-stated that MIT permits
vendoring). The one correction: license file is `license.txt`, and the "run/reuse"
infeasibility is even firmer than stated — it's a backend incompatibility (no logits via
MLX/API), not merely a "not worth it" judgment.

---

## SECOND INDEPENDENT ADVERSARIAL RE-CHECK (2026-05-29, fresh verification against live repo + source)

Re-verified from scratch against the live GitHub API and raw source files, NOT trusting
the survey body or the prior adversarial section above. All checks reproduced.

**License — CONFIRMED MIT (SPDX: `MIT`), HIGH confidence.**
- `gh api repos/1rgs/jsonformer/license` -> `{"license":"MIT","name":"license.txt","path":"license.txt"}`.
- Pulled the file contents verbatim (base64-decoded): standard MIT text, "Copyright (c) 2018
  Rahul Sengottuvelu". No modifications, no dual-license, no added clauses.
- Confirmed the filename gotcha: `contents/LICENSE` returns HTTP 404; the file is lowercase
  `license.txt`. GitHub's license detector resolves it correctly to MIT regardless.
- The task's GPL/AGPL vendoring concern is MOOT: MIT is fully permissive. We may cite, run
  externally, AND vendor/modify into our (permissive) harness with only attribution. No
  copyleft, no viral obligation. This is NOT a vendoring blocker.

**Stars — CONFIRMED 4,926 (order of magnitude ~5k / 10^3), HIGH confidence.** forks=185,
archived=false, pushed_at=2024-02-24. Survey's star count is exact, not inflated.

**"cite-only" — PRESSURE-TESTED, HOLDS, HIGH confidence.** Verified directly from source:
- `pyproject.toml` runtime deps list only `termcolor`; torch/transformers/accelerate/
  bitsandbytes are in the DEV group — but they are de-facto required: `main.py:9` does
  `from transformers import PreTrainedModel, PreTrainedTokenizer` at module top level and the
  constructor (`main.py:20-21`) is typed to those. So importing jsonformer pulls HF anyway.
- HF/PyTorch logits coupling is real and unavoidable: `main.py` calls `self.model.forward(...)`,
  reads `output.logits[0, -1]`, calls `self.model.generate(..., logits_processor=[...])`, and
  uses `self.model.device`. `logits_processors.py` imports `from transformers import
  LogitsWarper, StoppingCriteria` and `torch`, subclassing them over raw `torch.FloatTensor`
  scores. There is NO abstraction layer to swap in MLX or an API backend.
- Our harness backends (MLX local + Anthropic/OpenAI APIs) expose neither raw per-step logit
  tensors nor a HF `PreTrainedModel`. Remote APIs cannot run it at all; MLX would require a
  full from-scratch reimplementation of the logits processors. -> genuinely NOT runnable/
  reusable in-harness without bolting on a 3rd HF/PyTorch backend. cite-only stands.
- Capability gap re-confirmed at `main.py:150-187`: `generate_value` dispatches on exactly
  {number, boolean, string, array, object}, else `raise ValueError("Unsupported schema type")`.
  No enum, no pattern/format, no oneOf/anyOf, no grammar. A tool name is a free-form `string`,
  so jsonformer cannot pin it to a registry — mechanically insufficient for TEHR regardless of
  backend. (Outlines / XGrammar / lm-format-enforcer are the right tools if a constrained-
  decoding baseline is ever wanted.)

**Claims-check summary:** The survey did NOT overstate stars (exact), license (correct SPDX),
or usability (if anything it under-sold the run-infeasibility and over-aged dormancy). No
over-optimism to penalize. Only nit: dev-vs-runtime dep grouping in pyproject is a non-issue
since HF is imported unconditionally.

**FINAL VERDICT: cite-only. license_confirmed = true (MIT). confidence = HIGH.**
