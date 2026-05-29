# Repo survey: HELM (Holistic Evaluation of Language Models)

- **Repo:** stanford-crfm/helm
- **Canonical URL:** https://github.com/stanford-crfm/helm (live, no 404)
- **Stars:** 2,804 (gh api, 2026-05-29)
- **License:** Apache-2.0 (SPDX: Apache-2.0) — verified via `gh api .license.spdx_id`
- **Language:** Python · actively maintained (last push 2026-05-29, same day)
- **Homepage:** https://crfm.stanford.edu/helm
- **Category:** eval-harness

## What it does
HELM is Stanford CRFM's framework for **holistic, reproducible, transparent** evaluation
of foundation models (LLMs + multimodal). Its thesis is *breadth*: evaluate many models
across many **scenarios** along many **metrics** (accuracy, calibration, robustness,
fairness, bias, toxicity, efficiency) and publish standardized leaderboards (HELM Classic,
HELM Lite, HELM Instruct, HEIM for image gen, MMLU/Air-Bench/Safety/Arabic/medical
sub-leaderboards, etc.). Architecture: ~290 `*_scenario.py` files (scenario = dataset +
task definition), a large `metrics/` package (`basic_metrics.py`, bias/toxicity/code/SQL
metrics, ...), declarative `run_entries/*.conf` run specs (~70), and a `clients/` layer of
model adapters (Anthropic, OpenAI incl. Responses API, HuggingFace pipeline/inference).
Results render in a React `helm-frontend`.

**Critically for us: HELM has NO tool/function-calling or agentic scenarios.** A recursive
tree search for scenarios matching tool/agent/function/bfcl/tau/gorilla/call returned
**zero** matches. There is no tool registry, no multi-turn tool rollout, and no MLX client.
Its request model is prompt -> completion -> scored metric, same static-eval abstraction as
lm-eval (just far broader in scenario/metric coverage and with more "holistic" axes).

## Fit for our paper (TEHR / RVR on BFCL multi-turn)

Our harness (`harness/bench_loaders/{bfcl,tau_bench}.py`, per-task tool `registry`,
family adapters in `harness/adapters/{anthropic,openai,mlx}_adapter.py`, `cost_meter.py`,
`intervention/` RVR) measures a per-call **Tool-Existence Hallucination Rate** over
multi-turn tool-calling rollouts. HELM cannot express any of that.

Verdict by axis:

- **RUN as an extra benchmark? NO.** No tool-call surface anywhere in HELM, so TEHR/RVR
  is not measurable through it. The only conceivable use is the same as lm-eval: an
  orthogonal **general-capability sanity panel** (MMLU/safety/bias) to show our Qwen3
  4-bit checkpoints and Anthropic 4.x models behave normally before/after RVR. But that
  overlaps lm-eval (already surveyed as the lighter option), needs its own `clients/`
  adapter (no MLX client exists — we'd have to write one against HELM's client API), and
  is a heavyweight install. Effort: high for low marginal value. Use lm-eval instead if a
  sanity panel is wanted.

- **Reuse a COMPONENT in our harness? LOW / NO.** Apache-2.0 permits vendoring, but
  HELM's scenario/metric/client stack is built around its static-eval abstraction and is
  heavier than our purpose-built tool-calling pipeline. Nothing in `metrics/` computes a
  tool-existence rate. Its `clients/anthropic_client.py` / `openai_client.py` are not a
  shortcut over our existing adapters. Not worth pulling in as a dependency.

- **Reuse as a BASELINE? NO.** HELM is not a tool-hallucination method nor an
  intervention; there is nothing for RVR to be baselined against here.

- **Cite as PRIOR ART? YES — and high-value.** HELM is *the* canonical reference for
  "holistic / multi-metric / multi-scenario LM evaluation." It is the strongest
  positioning cite for our Related Work: the field's flagship breadth-oriented harness
  evaluates accuracy/calibration/robustness/bias/toxicity/efficiency but has **no notion
  of tool existence or tool-call validity**. That gap is exactly the wedge for per-call
  TEHR + RVR. Pair it with lm-eval (and optionally BIG-bench/BFCL/tau-bench) to frame
  TEHR/RVR as agentic tool-calling evaluation that even the most holistic harness omits.
  Also a clean cite for "reproducible, transparent, leaderboard-style eval" as a design
  value we inherit — useful for the harness-design narrative reviewers reward.

- **Borrow a PATTERN for the paper-revision skill / personas? MEDIUM (indirect).**
  HELM's core methodological move — **declare the evaluation as an explicit
  (scenario x metric) matrix and report it holistically rather than a single headline
  number** — is a strong reviewer-facing framing. For the paper-revision skill / reviewer
  personas this translates to a rubric item: "does the paper present a (model-family x
  benchmark x metric) coverage matrix, and are robustness/cost/efficiency axes reported,
  not just the headline TEHR?" A "HELM-style holism" persona can push for breadth and
  multi-axis reporting (which aligns with the main-track-breadth goal: more
  benchmarks/baselines/families + cost-quality-gap). This is a pattern for the
  skill/personas, not code reuse.

## License risk
None. Apache-2.0 — permissive, patent grant included, allows reuse/vendoring with
attribution + NOTICE. Citing carries zero risk.

## Bottom line
**cite-only** (high-value prior-art / positioning cite), with a secondary **reuse-pattern**
payoff for the revision skill (the scenario x metric holism rubric / a "holism" reviewer
persona). Do NOT run TEHR through it (no tool surface), do NOT use as a baseline, and skip
it as a sanity panel in favor of the lighter lm-eval. Cite HELM prominently in Related Work
as the holistic-eval flagship that omits tool-existence — the precise gap TEHR/RVR fills.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Method: did not trust the survey summary. Decoded the actual LICENSE file, cross-checked
the packaging license metadata, re-pulled stars, and ran independent code searches +
web searches against the live repo.

**License — CONFIRMED Apache-2.0 (triple-sourced, not just the SPDX summary).**
- `LICENSE` file decoded from `gh api .../contents/LICENSE` → literal "Apache License,
  Version 2.0, January 2004" full text. Not a relicensed/modified variant.
- `pyproject.toml` → `license = { text = "Apache License 2.0" }`.
- OSI classifier → `"License :: OSI Approved :: Apache Software License"`.
- `gh api .license.spdx_id` → `Apache-2.0`.
All four agree. **This is PERMISSIVE, NOT GPL/AGPL.** The reviewer's GPL/AGPL vendoring
concern does NOT apply here — Apache-2.0 permits vendoring into our (permissive) codebase
with attribution + NOTICE retention and includes a patent grant. The survey's "license
risk: none" is accurate and not over-optimistic. (Standard hygiene if we ever vendor:
keep the Apache header + NOTICE; we are not planning to vendor anyway.)

**Stars — CONFIRMED, correct order of magnitude.** 2,804 (gh api, 2026-05-29). ~3k =
low-thousands. The survey did NOT inflate this. (For calibration: lm-eval is ~10k. HELM
is a smaller star count than lm-eval — the survey's preference for lm-eval as the
"lighter / more-used sanity panel" is consistent with this.) Repo is live, not archived,
last push 2026-05-29 (genuinely actively maintained — confirmed).

**"No tool surface" claim — SUBSTANTIVELY TRUE, but the survey OVERSTATED the absolute.**
- The survey said a recursive search "returned ZERO matches" for tool/agent/function/
  bfcl/tau/gorilla. My independent code search found: `tau_bench`=0, `gorilla`=0,
  `mlx`=0, `tool_use`=0 — BUT `"function calling"`=6 and `"agent"`=11 incidental hits.
  So "zero matches anywhere" is too strong as literally stated.
- However, these are incidental string matches (scenario prose, client API kwargs), NOT
  dedicated tool-existence / multi-turn tool-call scenarios. Web cross-check confirms:
  HELM's canonical framework has NO first-class tool-calling/agentic scenario; CRFM
  describes tool-use/agentic eval as a ROADMAP/future direction, and "HELM-AE
  (Agent Evaluation)" references trace to third-party blogs, not the repo. So the
  survey's OPERATIVE conclusion — TEHR/RVR is not measurable through HELM, no tool
  registry, no multi-turn tool rollout — HOLDS. Penalty: minor overclaim on the absolute
  ("zero") phrasing; conclusion unaffected.

**"No MLX client" claim — CONFIRMED.** `src/helm/clients/` contains anthropic_client,
openai_client, openai_responses_client, huggingface_{client,pipeline,inference} +
Azure/Stanford-health variants. There is NO `mlx_client.py`. So running our Qwen3 4-bit
MLX checkpoints through HELM would require writing a brand-new MLX client against HELM's
client API. Anthropic + OpenAI API models WOULD work out-of-the-box (those clients exist),
so the "API half" of our harness is reusable through HELM; the "MLX half" is not. The
survey's "high effort for low marginal value" framing is fair.

**Pressure-test of the cite-only verdict — UPHELD.** Given (a) no tool-call surface,
(b) no MLX client (our headline Qwen3 4-bit results can't run without new adapter code),
and (c) heavyweight install, HELM is not worth running as our extra benchmark or vendoring
as a component. It IS the right canonical prior-art cite for "holistic multi-metric LM
eval that omits tool-existence." Could we *technically* run it? Only the API-model path,
only for an orthogonal MMLU/safety panel that lm-eval already covers more cheaply — so
"cite-only" is the correct call, NOT "run-as-benchmark."

**Net:** survey is accurate and appropriately conservative on the decision; one minor
overclaim (literal "zero matches" vs. actual 6+11 incidental hits) that does not change
the verdict. Final: **cite-only**, license **Apache-2.0 (permissive, vendoring-safe)**,
confidence **high**.

---

## ADVERSARIAL VERIFICATION #2 (2026-05-29, second independent re-check)

Re-ran every load-bearing claim from scratch via `gh api`; did not trust the summary OR
the first verification block.

**License — CONFIRMED Apache-2.0, quadruple-sourced.**
- `gh api .../contents/LICENSE` decoded → literal "Apache License, Version 2.0,
  January 2004" full text (head verified). Unmodified standard license.
- `pyproject.toml` → `license = { text = "Apache License 2.0" }`.
- OSI classifier → `"License :: OSI Approved :: Apache Software License"`.
- `gh api repos/stanford-crfm/helm --jq .license.spdx_id` → `Apache-2.0`.
**PERMISSIVE, NOT GPL/AGPL.** The reviewer's GPL/AGPL "cite/run-external but don't vendor"
concern does NOT apply — Apache-2.0 permits vendoring into our permissive codebase with
attribution + NOTICE retention, plus a patent grant. `license_confirmed = true`.

**Stars — CONFIRMED.** `stargazers_count = 2804` (gh api, 2026-05-29). Order of magnitude
~3k (low-thousands). NOT inflated. For calibration this is below lm-eval (~10k), consistent
with the survey preferring lm-eval as the lighter sanity panel. `archived = false`,
`pushed_at = 2026-05-29` → genuinely live and actively maintained.

**No MLX client — CONFIRMED via directory listing.** `src/helm/clients/` =
{anthropic_client, openai_client, openai_responses_client, azure_openai_client,
huggingface_{client,pipeline,inference}, stanfordhealthcare_* variants}. NO `mlx_client.py`.
Consequence (load-bearing for us): our headline **Qwen3 4-bit MLX** checkpoints CANNOT run
through HELM without writing a new MLX client against HELM's client API. The Anthropic +
OpenAI API half of our harness WOULD run out-of-box. So "high effort for low marginal
value" is fair and not over-pessimistic.

**No tool/agentic surface — CONFIRMED, and my counts were even lower than block #1.**
Independent `search/code` totals on the live repo: `bfcl`=0, `tau_bench`=0, `gorilla`=0,
`tool_use`=0, `"function calling"`=0, `mlx`=0, `agent`=11. (Block #1 reported
"function calling"=6; GitHub code-search is index-dependent, but both runs agree these are
incidental, not first-class tool-call scenarios.) No tool registry, no multi-turn tool
rollout. TEHR/RVR is NOT measurable through HELM. Operative conclusion HOLDS.

**Claims-check / penalty:** The survey's lone overclaim is the absolute "ZERO matches"
phrasing for the scenario search ("agent" actually has 11 incidental hits, none of them
tool-call scenarios). Minor, does not move the verdict. Everything else — Apache-2.0,
~3k stars, actively maintained, no MLX client, no tool surface, license risk none — is
accurate and appropriately conservative.

**Pressure-test of cite-only — UPHELD.** Could we actually run/reuse it given our MLX+API
harness + license? License is no barrier (permissive). But (a) no tool-call surface means
our actual contribution (per-call TEHR + RVR) is unmeasurable through it; (b) no MLX client
means our headline local results need new adapter code; (c) the only technically-runnable
path (API models on an MMLU/safety/bias panel) is orthogonal to our claim and already
covered more cheaply by lm-eval. So NOT run-as-benchmark, NOT include-parts/vendoring.
It IS the canonical prior-art cite for "holistic multi-metric LM eval that omits
tool-existence" — the precise gap TEHR/RVR fills. **Verdict: cite-only, confidence high.**
