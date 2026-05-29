# Repo survey: deepeval

- **Repo:** confident-ai/deepeval
- **Canonical URL:** https://github.com/confident-ai/deepeval (URL given resolves, no 404)
- **Stars:** 15,783 (gh api, 2026-05-29)
- **Forks:** 1,479 | **Open issues:** 282
- **License:** Apache-2.0 (SPDX, from repo metadata + LICENSE.md)
- **Language:** Python
- **Maintenance:** very active — `pushed_at` 2026-05-28 (last commit ~1 day before survey), not archived
- **Category:** eval-harness

## What it is

"The LLM Evaluation Framework." A pytest-style library for unit-testing LLM
apps. Core abstraction is `LLMTestCase` (input, actual_output, expected_output,
tools_called, expected_tools, available_tools, context, retrieval_context) +
a large catalog of **metrics**, most of which are LLM-as-a-judge
(G-Eval / DAG builder) but some are deterministic (exact_match, pattern_match,
tool_correctness). Also ships `deepeval/benchmarks/` re-implementations of
standard academic benchmarks (MMLU, GSM8K, HumanEval, BBH, DROP, HellaSwag,
ARC, TruthfulQA, BoolQ, IFEval, LogiQA, MathQA, SQuAD, Winogrande, BBQ,
EquityMedQA, LAMBADA, BIG-Bench-Hard).

Has a commercial backend (Confident AI / confident-ai.com) the OSS lib can log
to, but the framework runs fully locally and the metrics do not require the
SaaS.

## Relevance to our paper (TEHR / tool-existence hallucination + RVR on BFCL/tau-bench)

deepeval has a whole **agentic-metrics** family directly adjacent to our topic:

- `metrics/tool_correctness/` — deterministic set comparison of
  `tools_called` vs `expected_tools` (with `should_exact_match`,
  `should_consider_ordering` flags). Optionally takes `available_tools` and
  runs an LLM-judge `_get_tool_selection_score` to assess whether called tools
  were appropriate given the available set. This is the closest existing thing
  to our TEHR — but note it is fundamentally a *correctness vs expected* metric,
  NOT a per-call tool-existence-hallucination rate. It does not isolate
  "model called a tool that does not exist in the registry" as a first-class
  event; that gap is exactly our contribution.
- `metrics/tool_use/`, `metrics/mcp_use_metric/`, `metrics/task_completion/`,
  `metrics/goal_accuracy/`, `metrics/plan_adherence/`, `metrics/step_efficiency/`
  — agent-quality metrics, all LLM-judge based.
- `metrics/hallucination/` — RAG-style hallucination (output vs provided
  context), NOT tool-existence hallucination. Different construct, do not
  conflate in the paper.

It does NOT ship BFCL or tau-bench loaders, so it is not a drop-in replacement
for our harness benchmarks.

## Concrete verdict

| Use | Verdict | Notes |
|---|---|---|
| RUN as extra benchmark | No | The `benchmarks/` are MMLU/GSM8K-style QA, not tool-use; irrelevant to TEHR. tau/BFCL not included. |
| Reuse a COMPONENT in harness | Maybe (low value) | Could wrap `ToolCorrectnessMetric` as an adapter, but our `bench_loaders/*` + `intervention/` already compute exact tool-call comparisons. Adding an LLM-judge dep (extra API cost, nondeterminism) is not worth it for a deterministic existence check. |
| Reuse as a BASELINE | **Yes — strongest use** | `ToolCorrectnessMetric` (esp. the `available_tools` + tool-selection-score path) is a credible, widely-used *prior-art metric* to contrast against TEHR. Frame: existing frameworks measure tool *correctness vs expected*, none isolate per-call tool-*existence* hallucination on a registry. Lets a reviewer see we surveyed the de-facto OSS eval framework. |
| Cite as PRIOR ART | **Yes** | 15.8k-star de-facto OSS LLM-eval framework; cite for breadth/positioning and to differentiate TEHR from tool_correctness/hallucination metrics. |
| Borrow PATTERN for paper-revision skill / personas | Minor | Their G-Eval / DAG (deterministic graph-based LLM-judge) decomposition is a clean pattern for rubric-structured judging; could inform a reviewer-persona rubric. Also `skills/` dir exists in-repo worth a glance. Not load-bearing. |

## Effort & risk

- **Effort:** low for cite/baseline (read docs, run one `ToolCorrectnessMetric`
  comparison on a handful of BFCL traces to report numbers). Medium if we wrap
  it as a harness adapter (new dep, LLM-judge wiring, MLX-model compat). High /
  not worth it to run their academic benchmarks.
- **License risk:** **low.** Apache-2.0 is permissive and compatible with our
  harness; attribution + NOTICE only. No copyleft. Safe to import or vendor
  small components with attribution.
- **Caveat:** most metrics are LLM-judge → cost + nondeterminism; their
  `hallucination` metric is RAG-grounding, a *different* construct from ours —
  must differentiate explicitly to avoid reviewer confusion.

## Bottom line

Best used as a **baseline + prior-art citation**: position TEHR against
deepeval's `ToolCorrectnessMetric` to show no existing OSS framework isolates
tool-existence hallucination as a per-call rate. Low effort, low license risk.
Do not run its benchmarks; do not vendor its LLM-judge metrics into the harness.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

Method: independent `gh api` calls + direct fetch of LICENSE file contents and
source/docs. Did not trust the survey's metadata summary.

**License — CONFIRMED, Apache-2.0.** Verified two ways: (1) `gh api
repos/.../license` returns `spdx_id: Apache-2.0`, file is `LICENSE.md`; (2)
decoded the actual file body — it is the verbatim Apache License 2.0 text
("Apache License / Version 2.0, January 2004 ... TERMS AND CONDITIONS"). This is
a permissive, NON-copyleft license. The survey's stated SPDX is correct. No
GPL/AGPL concern: we MAY vendor components into our (permissive) codebase with
attribution + NOTICE; the GPL/AGPL "external-use-only" caveat does NOT apply here.

**Stars — CONFIRMED.** `stargazers_count: 15783` (gh api, 2026-05-29). Matches
survey exactly; order of magnitude ~10^4 (15.8k). Forks 1479, open issues 282,
not archived, `pushed_at: 2026-05-28` — all match. Maintenance claim is accurate.

**"Cite-only / baseline" claim — PRESSURE-TESTED, holds, with refinement.**
- Verified from source (`tool_correctness.py`) and docs: the metric's PRIMARY
  score is a deterministic ratio (correctly-used tools / total tools called) vs
  `expected_tools`. The `available_tools` field feeds a SECONDARY LLM-judge
  "tool selection optimality" score; final = MIN of the two. Confirmed it does
  NOT validate tool existence against a registry — "There is no validation that
  tools_called actually exist as registered tools." The survey's central
  differentiation claim (deepeval measures correctness-vs-expected and
  selection-optimality, NOT per-call tool-existence hallucination) is ACCURATE
  and is the cleanest contrast for TEHR. Strongest use = prior-art/baseline.
- COULD we actually run/reuse it on our MLX+API harness? Yes, but with a real
  catch the survey under-weighted: deepeval's metrics default to OpenAI GPT
  judges. Custom/local judges are supported only by subclassing
  `DeepEvalBaseLLM` (6 methods), and the docs explicitly warn local/small models
  "struggle with valid JSON" and recommend lm-format-enforcer or instructor to
  confine output. So wiring our MLX models in as JUDGES is non-trivial (JSON
  enforcement work) — another reason to NOT adopt the LLM-judge metrics and to
  treat deepeval as cite/baseline, not as harness infrastructure. The pure
  deterministic `ToolCorrectnessMetric` path (no `available_tools`) needs no LLM
  and could be wrapped cheaply, but it's redundant with our existing exact
  tool-call comparison in `bench_loaders/*` — low marginal value.
- No BFCL/tau-bench loaders shipped (consistent with survey). Their `benchmarks/`
  are QA-style (MMLU/GSM8K/etc.), irrelevant to TEHR. "Do not run as benchmark"
  stands.

**Over-optimism penalties applied:** (1) Survey called local-model reuse
"medium" effort but did not flag the OpenAI-default + JSON-confinement burden for
MLX judges — that's the main practical friction. (2) "Vendor small components"
is license-safe (Apache-2.0) BUT the only component worth vendoring
(deterministic tool comparison) duplicates existing harness code, so the
practical value of vendoring is near-zero regardless of license.

**Net:** survey is accurate and not materially over-stated. License/stars/
maintenance all independently confirmed. Recommendation downgraded slightly from
the survey's "baseline" enthusiasm to **cite-only** as the safe default: cite as
de-facto OSS eval framework and use `ToolCorrectnessMetric` as a conceptual
prior-art contrast; running it as a live baseline is possible but costs
LLM-judge wiring (incl. MLX-judge JSON confinement) for little gain over our
existing deterministic comparison. Confidence: high (license + stars verified
from primary sources; source code confirms the metric semantics).

---

## ADVERSARIAL RE-VERIFICATION #2 (2026-05-29, second independent pass)

Re-ran every load-bearing claim against primary sources rather than trusting the
prior verification block.

**License — CONFIRMED Apache-2.0 (permissive, non-copyleft).**
- `gh api repos/confident-ai/deepeval` -> `"license":"Apache-2.0"`,
  `license_key: apache-2.0`.
- `gh api .../license` -> `spdx_id: Apache-2.0`, file `LICENSE.md`; decoded body
  is verbatim "Apache License / Version 2.0, January 2004 ... TERMS AND
  CONDITIONS". SPDX = **Apache-2.0**, confirmed.
- GPL/AGPL caveat from the brief does NOT apply: Apache-2.0 is permissive, so we
  may both run it externally AND vendor components into our (permissive) codebase
  with attribution + NOTICE. No copyleft contamination risk.

**Stars — CONFIRMED, order of magnitude 10^4.** `stargazers_count: 15783`
(~15.8k). Forks 1479, open_issues 282, `archived: false`,
`pushed_at: 2026-05-28T18:17:17Z`. All match the survey; maintenance is genuinely
active.

**Metric semantics — CONFIRMED from source (`tool_correctness.py`).** Score =
`min(tool_calling_score, tool_selection_score)`. tool_calling_score is a
deterministic compare of `tools_called` vs `expected_tools` (exact / LCS-ordered
/ name+param-overlap). tool_selection_score runs ONLY when `available_tools` is
set and is an LLM-judge appropriateness rating. Critically: **there is no hard
validation that a called tool exists in any registry** — the LLM only scores
"appropriateness," it does not flag a nonexistent-tool call as an error event.
This is the cleanest contrast for TEHR and the survey states it correctly.

**Runnability on our MLX+API harness — CONFIRMED, with the same friction the
survey flagged.** Docs confirm OpenAI is the default judge; custom/local models
require subclassing `DeepEvalBaseLLM` (4 methods: get_model_name, load_model,
generate, a_generate) AND the docs explicitly warn custom models may fail to
emit valid JSON, pointing to a separate JSON-confinement guide. So using our MLX
models as JUDGES is real work. The pure-deterministic ToolCorrectnessMetric path
(no available_tools) needs no LLM but duplicates our existing exact tool-call
comparison in `bench_loaders/*` — near-zero marginal value.

**Did the survey over-state anything? Minor, already self-corrected.** The
original body table leaned toward "baseline (strongest use)"; the first
verification block correctly downgraded to cite-only because (a) running it live
needs LLM-judge wiring incl. MLX-judge JSON confinement, and (b) the one
license-safe vendorable component is redundant with our harness. I concur. No
material overstatement of license, stars, or usability survives this pass.

**My verdict: cite-only.** Cite as the de-facto OSS LLM-eval framework (~15.8k
stars, Apache-2.0, actively maintained) and use `ToolCorrectnessMetric` as a
conceptual prior-art contrast: existing frameworks score tool correctness-vs-
expected and LLM-judged selection-optimality; none isolate per-call tool-
*existence* hallucination against a registry — that is our TEHR contribution.
Do NOT run its QA benchmarks (no BFCL/tau-bench; irrelevant to TEHR). Do NOT
vendor its LLM-judge metrics (cost + nondeterminism + MLX-judge JSON burden).
License-confirmed: true. Confidence: high.
