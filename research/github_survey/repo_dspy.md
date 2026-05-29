# Repo survey: dspy

- **Repo:** stanfordnlp/dspy
- **URL:** https://github.com/stanfordnlp/dspy (canonical; did NOT 404)
- **Homepage / docs:** https://dspy.ai
- **Stars:** 34,720 (gh api, 2026-05-29)
- **License:** MIT (SPDX, confirmed via `gh api repos/stanfordnlp/dspy`)
- **Language:** Python
- **Status:** Very active. Last push 2026-05-29 (same day as survey); not archived.
  7.5M+ monthly downloads; production adoption (Shopify, Dropbox, AWS).
- **Category:** agent-framework (NOT a benchmark — like guidance/instructor in this set)

## What it is
DSPy is a framework for **programming, not prompting** LLMs. You declare tasks as
typed **Signatures** (InputField/OutputField), pick a **Module** (execution strategy),
and optionally run an **Optimizer** to auto-tune prompts/demos against a metric.

Core abstractions relevant to us:
- **Signatures** — typed I/O contracts for an LM call (the prompt is generated, not
  hand-written).
- **Modules** — `Predict`, `ChainOfThought`, **`ReAct`** (tool-use + reasoning loop),
  **`BestOfN`**, **`Refine`** (re-run a module until an output satisfies a reward/
  constraint), **`CompleteAndGrounded`** (groundedness/hallucination-oriented metric).
- **Tools / agents** — `ReAct` lets a module call external tools (search, calculator,
  code exec) in a thought/action loop. Tools are passed as Python callables; the model
  selects among them. This is the directly tool-relevant surface.
- **Optimizers (teleprompters)** — GEPA, MIPROv2, BootstrapFewShot, etc. Auto-tune
  instructions/few-shot demos from labeled examples + a metric.
- **Evaluation** — built-in metrics (`SemanticF1`, `answer_exact_match`) and a small
  `Evaluate` harness; multimodal (image/audio) fields are first-class.

## Fit vs our paper
Our paper measures a **per-call Tool-Existence Hallucination Rate (TEHR)** on BFCL/
tau-bench (Anthropic 4.x = 0 events; Qwen3 4-bit non-monotonic, peak 1.87% at 14B) and
proposes **RVR** — detect a call to a tool not in the registry, re-inject the registry,
re-prompt. DSPy is **not a benchmark** and ships **no tool-hallucination dataset or
TEHR-style metric**. Its relevance is as (1) a *conceptual sibling* to RVR via the
`Refine` re-run-on-failed-reward loop, and (2) a possible *agent-construction layer* if
we ever needed an off-the-shelf ReAct loop. Neither is on our critical path; our harness
already drives BFCL + tau-bench directly across MLX + API models.

## Concrete verdict per use mode

- **RUN as an extra benchmark? — NO / N/A.** DSPy is a programming framework, not a
  benchmark. No dataset, no scored tool-hallucination task. Skip.

- **Reuse a COMPONENT in our harness? — NO (low value, real risk).** We could wrap
  models in `dspy.ReAct` to get a tool-loop, but our `harness/bench_loaders/*.py`
  already implement BFCL/tau-bench tool calling directly against MLX + API backends.
  Adopting DSPy would (a) insert a prompt-generation layer between us and the raw tool
  call — which is exactly the surface where TEHR lives, so it would *contaminate the
  measurement* (DSPy's generated prompts/demos would change hallucination rates and make
  the number a property of DSPy, not the model), and (b) add a heavy dependency. Reject
  for measurement integrity, not just effort.

- **Reuse as a BASELINE? — MAYBE, narrow and optional.** The honest baseline framing is
  **`dspy.Refine` as a generic self-correction loop vs our task-specific RVR.** `Refine`
  re-runs a module until an output passes a reward function — structurally the same
  "detect-failure, retry" shape as RVR, but reward-agnostic and prompt-only. A baseline
  arm "generic Refine-style retry (no registry re-injection)" would show that RVR's
  *registry-grounded* re-prompt beats a naive retry. This is a nice ablation-style
  contrast but it does NOT require importing DSPy — we can implement the generic-retry
  baseline ourselves in ~30 lines and just *cite* DSPy as the canonical instance of the
  pattern. Recommend: cite, don't depend.

- **Cite as PRIOR ART? — YES.** With 34.7k stars and production adoption, DSPy is the
  canonical reference for (a) declarative LM programming / auto-optimized prompting and
  (b) the **`Refine` / `BestOfN` retry-until-valid** family. Reviewers in the agent
  space will know it. Cite it in related work as the framework-level take on
  "structure + retry" so RVR is positioned as a *targeted, registry-grounded*
  intervention rather than reinventing self-refinement. Also worth a one-line
  differentiation: DSPy optimizes prompts to a metric; RVR injects the ground-truth tool
  registry at failure time — orthogonal mechanisms.

- **Borrow a PATTERN for the paper-revision skill / reviewer personas? — YES, two.**
  1. Reviewer-persona objection: *"Isn't RVR just self-refinement / a Refine loop
     (DSPy)? What does registry re-injection add over a generic retry, and did you
     ablate against a content-free retry baseline?"* Bake this into a persona so we
     pre-empt it — and it directly motivates the optional baseline above.
  2. Method pattern for the **paper-revision skill**: DSPy's **Signature → Module →
     Optimizer (metric-driven)** decomposition is a clean template for structuring a
     revision pass — declare the revision task as a typed signature, run a fixed
     module, score against a rubric metric, iterate. Lightweight pattern borrow only;
     no code dependency.

## Effort & license risk
- **License risk: NONE.** MIT — permissive, attribution only. Safe to vendor code,
  borrow patterns, cite, or depend on.
- **Effort:**
  - Cite as prior art — trivial.
  - Reviewer-persona + revision-skill pattern — trivial.
  - Generic-retry baseline (hand-rolled, citing DSPy `Refine`) — low; off critical path.
  - Adopting DSPy as a harness component — medium-high effort AND harmful to measurement
    integrity; do not.

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verifier mandate: confirm LICENSE from the actual file, confirm stars order-of-magnitude,
pressure-test the cite-only / runnability claims, penalize over-optimism.

**License — CONFIRMED MIT (SPDX: MIT), triple-sourced.**
- `gh api repos/stanfordnlp/dspy` -> `license.spdx_id = MIT`.
- Actual `LICENSE` file (base64-decoded from contents API) is verbatim MIT text,
  "Copyright (c) 2023 Stanford Future Data Systems". Not a misclassified summary.
- PyPI `dspy` 3.2.1 metadata also carries full MIT text.
- => Survey's "License risk: NONE / safe to vendor" is ACCURATE. No GPL/AGPL trap here.
  (For the record: had it been GPL/AGPL we could cite + run-externally but NOT vendor into
   our permissive harness — N/A in this case.)

**Stars — CONFIRMED order of magnitude 10^4.** gh api = 34,721 today vs survey's 34,720
(off by 1, same-minute drift). Accurate, not inflated.

**Status — CONFIRMED.** Not archived; `pushed_at` 2026-05-29 (same day); Python; on PyPI
(3.2.1, requires-python >=3.10,<3.15) so pip-installable with no friction.

**Runnability under OUR MLX + API harness — survey is OPTIMISTIC on the MLX half.**
- DSPy's `dspy.LM` backend is **LiteLLM**. LiteLLM natively supports Anthropic + OpenAI,
  so the **API half of our harness is genuinely reachable** through DSPy.
- LiteLLM has **NO native MLX / Apple-Silicon provider** (verified against LiteLLM provider
  docs). Our harness runs MLX models *directly* (native MLX adapter:
  `harness/tests/test_mlx_adapter.py`, `harness/tests/fixtures/mlx_responses.json`). To
  drive our Qwen3-4bit MLX models through DSPy you'd have to stand up an OpenAI-compatible
  local server in front of MLX — extra infra the survey never mentions. So any "wrap our
  models in dspy.ReAct" idea is only half-true: trivial for API models, non-trivial for the
  MLX models that produce our headline non-monotonic curve.

**`Refine` mischaracterized (minor but real).** Survey describes it as "re-run a module
until an output satisfies a reward/constraint" — a clean detect-failure/retry sibling to
RVR. The actual `dspy/predict/refine.py` runs the module up to N times at temperature=1.0
with varying rollout IDs and returns the **best** (or first-above-threshold) prediction,
and on failure synthesizes **LLM feedback** (the `OfferFeedback` signature) to steer
retries. It is best-of-N-with-self-feedback, NOT a content-free retry loop. This makes the
proposed "generic Refine-style retry (no registry re-injection)" baseline framing slightly
off: a faithful DSPy-Refine baseline already includes a self-feedback mechanism, so the
honest contrast is "RVR's registry re-injection vs DSPy's free-form self-feedback retry",
not "RVR vs naive retry". The hand-rolled cheap baseline is still fine — but do not claim
it faithfully reproduces DSPy `Refine`; cite Refine as the *self-feedback* instance.

**Net judgement on the survey:** core claims (MIT, ~34.7k stars, active, not-a-benchmark,
cite-as-prior-art, do-not-vendor-into-the-measurement) all hold up and the
measurement-contamination reasoning is sound and now *reinforced* by the MLX-integration
friction. Two over-optimism dings, both downgrades not reversals: (1) implied easy
model-wrapping ignores that MLX has no DSPy/LiteLLM path; (2) `Refine` is richer than the
"naive retry" framing implies. Recommendation **cite-only** stands and is, if anything,
strengthened — running/reusing DSPy buys us nothing on critical path and the MLX gap raises
the integration cost the survey underweighted.

## Bottom line
Not a benchmark and not a harness component (wrapping our tool calls in DSPy's
prompt-generation layer would contaminate TEHR). Real value is (1) **cite as prior art**
for declarative LM programming and the `Refine`/`BestOfN` retry-until-valid family, (2) a
**reviewer-persona objection** ("RVR vs generic Refine retry") plus the optional, cheap
**hand-rolled generic-retry baseline** it motivates, and (3) a **structuring pattern**
(Signature→Module→Optimizer) for the paper-revision skill. License is clean (MIT).

## SECOND-PASS ADVERSARIAL VERIFICATION (2026-05-29, independent re-check #2)

Re-ran the load-bearing checks from scratch rather than trusting pass #1.

**License — INDEPENDENTLY CONFIRMED MIT (SPDX: MIT).** `gh api repos/stanfordnlp/dspy`
returns `license_spdx = MIT`, `license_name = "MIT License"`. Decoded the ACTUAL
`LICENSE` file via `gh api .../license` (base64 → plaintext): verbatim MIT text,
"Copyright (c) 2023 Stanford Future Data Systems". Not a misclassified summary. The
survey's "License risk: NONE" is accurate.

**GPL/AGPL vendor trap — DOES NOT APPLY, and confirmed our side is permissive too.** Our
harness is **Apache-2.0** (`harness/pyproject.toml: license = { text = "Apache-2.0" }`).
MIT-into-Apache-2.0 is compatible, so dspy could *legally* be vendored. The reason we
still don't vendor is **measurement integrity** (prompt-gen layer contaminates TEHR) and
**effort**, NOT license. (Had dspy been GPL/AGPL, vendoring into our Apache-2.0 harness
would be the blocker — N/A here.)

**Stars — INDEPENDENTLY CONFIRMED 10^4.** `gh api` = 34,721 (vs survey 34,720; +1 drift).
Order of magnitude correct, not inflated.

**Status — CONFIRMED.** `archived=false`, `pushed_at=2026-05-29T02:23:56Z` (same day),
Python. Live and maintained.

**MLX runnability — INDEPENDENTLY CONFIRMED the friction is real.** Verified against the
current LiteLLM provider docs (live fetch): LiteLLM natively supports Anthropic + OpenAI
but has **NO native MLX/mlx-lm provider**; local models are reachable only via
OpenAI-compatible servers (ollama, vLLM, LM Studio, llamafile) or a custom-LLM shim. Our
harness instead drives MLX **directly** — `harness/adapters/mlx_adapter.py` calls
`mlx_lm.load`/`mlx_lm.generate` (see `harness/tests/test_mlx_adapter.py`). So routing our
Qwen3-4bit MLX models (the headline non-monotonic curve) through dspy WOULD require
standing up an OpenAI-compat server in front of MLX. Pass #1's MLX ding holds.

**"Hand-roll a generic-retry baseline citing DSPy" — ALREADY DONE NATIVELY (new finding).**
Our harness already ships the relevant baseline arms as pure functions, no dspy needed:
`harness/intervention/naive_retry.py` (C0.5, content-free "try again" feedback),
`harness/intervention/rvr.py` (C1, registry-grounded re-prompt),
`harness/intervention/framework_default.py` (C0.7), `harness/intervention/decoy_list.py`.
This strengthens cite-only further: the baseline dspy "motivates" is already implemented,
so dspy contributes literally zero code on the critical path — only a citation and the
reviewer-persona framing. Reinforces pass #1's caution that a hand-rolled naive retry is
NOT a faithful `Refine` (which is best-of-N + self-feedback); our `naive_retry` is
deliberately content-free and should be cited as such, with `Refine` cited separately as
the self-feedback instance.

**Net judgement (verifier #2):** every claim the survey rests on is true — MIT (from the
real file), ~34.7k stars, active, not-a-benchmark, cite-as-prior-art, do-not-vendor (for
integrity, not license). The only over-optimism is the implied ease of wrapping our models
in dspy.ReAct, which the MLX gap contradicts; downgrade, not reversal. Recommendation
**cite-only** confirmed and strengthened. Confidence: HIGH.
