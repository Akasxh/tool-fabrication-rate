# Repo survey: instructor

- **Repo:** 567-labs/instructor
- **Canonical URL:** https://github.com/567-labs/instructor (URL given resolves, no 404)
- **Stars:** 13,064 (gh api, 2026-05-29)
- **License:** MIT (SPDX, from repo metadata + LICENSE)
- **Language:** Python
- **Maintenance:** very active — `pushed_at` 2026-05-24 (~5 days before survey), not archived
- **Category:** constrained-decoding / structured outputs

## What it is

"Structured outputs for LLMs." A thin library that wraps a chat-completions
client (OpenAI, Anthropic, Gemini, Mistral, local via llama-cpp/ollama, etc.)
and lets you pass a Pydantic `response_model`. It coerces the model into
returning that schema using one of several **modes** (`TOOLS` / function
calling, `JSON`, `MD_JSON`, `JSON_SCHEMA`, provider structured-output APIs).
The defining feature is the **validation + reask retry loop**: it parses the
response into the Pydantic model, and on `ValidationError` it **re-prompts the
model with the validation error message appended** ("reask") up to
`max_retries`, until the output validates or retries are exhausted
(`InstructorRetryException`). Modules of note: `instructor/v2/core/retry.py`
(the reask loop), `mode.py`, `function_calls.py`, `dsl/`, `providers/`,
`validation/`, `hooks.py`.

Crucially: it is a **runtime structured-output / self-correction wrapper**, NOT
a benchmark, NOT a dataset, NOT an eval harness. It produces no tasks, metrics,
or scores.

## Relevance to our paper (TEHR + RVR intervention on BFCL/tau-bench)

The high-value connection is to **RVR, not TEHR**. Our RVR intervention
("re-prompt with the tool registry on a bad call") is structurally an instance
of exactly the pattern instructor productionized: detect a malformed/invalid
model output, then re-prompt with corrective context and retry. Instructor's
reask loop re-prompts with a *Pydantic ValidationError*; RVR re-prompts with
the *tool registry* after a tool-existence-hallucination. Same control-flow
template (validate → inject corrective signal → retry), different validator and
different corrective payload.

There is also a narrower technical link: instructor's `TOOLS` mode generates a
JSON Schema from the Pydantic model and hands it to the provider's
function-calling API — the same OpenAI-shape tool schema our `bench_loaders/`
normalize BFCL registries into. So instructor is one concrete library that, if
misconfigured or pointed at a model that ignores the schema, could *emit* the
very tool-existence hallucinations we measure — but it does not measure them.

It ships no BFCL/tau-bench loaders and no tool-existence metric, so it is not a
benchmark we can run.

## Concrete verdict

| Use | Verdict | Notes |
|---|---|---|
| RUN as extra benchmark | **No** | Not a benchmark/dataset/harness. Nothing to run for breadth. |
| Reuse a COMPONENT in harness | **Maybe (low value)** | Could in principle use instructor as the structured-output client for API models, but our adapters already speak Anthropic/OpenAI tool-calling natively and we deliberately want *raw* model behavior (TEHR depends on observing un-corrected calls). Adding instructor's auto-reask would *mask* the very hallucinations we measure unless disabled — net negative for the measurement path. |
| Reuse as a BASELINE | **Yes (for RVR, weak-to-moderate)** | Instructor's validation-reask loop is the canonical OSS realization of "re-prompt-on-bad-output." We can frame RVR as a *tool-existence-specific* instance of this family and, if we want a concrete baseline, contrast RVR against a generic reask (re-prompt with a generic "that was invalid, try again" message) vs RVR's registry-grounded reask. Useful ablation framing rather than a turnkey numeric baseline. |
| Cite as PRIOR ART | **Yes — strongest use** | 13k-star, de-facto OSS structured-output/self-correction library. Cite it to (a) position RVR within the established validate→reask→retry paradigm and (b) show TEHR is orthogonal: instructor enforces *output-schema* validity, not *tool-existence* validity against a registry. Clean differentiation point for reviewers. |
| Borrow PATTERN for paper-revision skill / personas | **Yes (moderate)** | The validate → structured-error → reask loop is a strong pattern for the paper-revision skill: a reviewer persona emits a *typed/structured* critique (à la Pydantic validation error), and the revision agent re-prompts the draft generator with that structured error until the critique-schema passes. Their `hooks.py` (pre/post completion hooks) and the retry abstraction are worth a read for designing the persona→revise→re-check loop. Pattern only, no code dependency needed. |

## Effort & risk

- **Effort:** low for cite/prior-art (read README + `v2/core/retry.py`, one
  paragraph in related work). Low-medium if we add a "generic reask" baseline
  arm to contrast with RVR — we can implement the generic reask directly in our
  intervention code in a few lines rather than importing instructor, which
  keeps the measurement path under our control. Adopting instructor as the
  client layer is medium effort and **counterproductive** for TEHR measurement.
- **License risk:** **very low.** MIT — permissive, no copyleft, compatible
  with our harness. Attribution only if we vendor any snippet (we likely won't).
- **Caveat:** instructor's auto-reask would *suppress* tool-existence
  hallucinations if it sat in front of our models. Keep it out of the
  measurement path; if used at all, only as a comparison arm with reask
  disabled/controlled.

## Bottom line

Best used as a **prior-art citation for RVR** and a **pattern source for the
paper-revision skill's persona→reask loop**. It is the canonical
validate-and-reask library; RVR is a tool-existence-specific instance of that
family, and TEHR measures a dimension (registry existence) it does not. Do not
run it as a benchmark, and do not insert it into the TEHR measurement path
(it would mask the events we count). MIT, very low license risk.

---

## ADVERSARIAL VERIFICATION (appended 2026-05-29, independent re-check)

**Verdict: survey is substantially ACCURATE. No over-optimistic claims found; minor nuance added below.**

### License — CONFIRMED MIT (SPDX: `MIT`), three independent sources
- Raw `LICENSE` file: full MIT text verbatim, `Copyright (c) 2023 Jason Liu`, no copyleft clauses.
- GitHub `/license` SPDX endpoint: `{"spdx":"MIT"}`.
- `pyproject.toml`: `license = { text = "MIT" }`.
- The survey's "MIT, very low license risk" is correct. Permissive — we may vendor snippets (attribution only) into our permissive harness, run externally, or cite freely. **No GPL/AGPL concern; the copyleft caveat in the task does not apply here.**

### Stars — CONFIRMED order-of-magnitude
- `gh api` (2026-05-29): `stargazers_count = 13064`. Survey says 13,064. Exact match, ~10^4. Not archived (`archived: false`), `pushed_at = 2026-05-24`. "Very active" is fair.

### Technical claims — CONFIRMED by reading source
- The reask loop lives in `instructor/v2/core/retry.py` (460 lines) as claimed. It uses `retry_if_exception_type(ValidationError)`, honors `max_retries`, and raises `InstructorRetryException`. `instructor/core/retry.py` is just a 3-line compat shim re-exporting from v2. Survey's path and mechanism description are correct.
- Provider dirs confirmed: anthropic, openai, gemini, mistral, bedrock, groq, cohere, etc.

### Pressure-test of "cite-only" claim — HOLDS, with one sharpened nuance
- Could we actually RUN/REUSE it in our MLX+API harness? **Partially, and the survey's "keep it out of the measurement path" conclusion is right for a different reason than license.** License is a non-blocker (MIT). The real blockers are methodological + integration:
  1. **No native MLX provider.** Provider list has NO `mlx` entry (`grep -ic mlx README` = 0; no mlx in providers/). Local models are reachable ONLY via Ollama or OpenAI-compatible endpoints. Our local arm runs MLX directly — instructor cannot drive our MLX models without us standing up an OpenAI-compat shim. The survey's "local via llama-cpp/ollama" phrasing slightly understates this gap; it should explicitly say **no MLX path**.
  2. **Methodological conflict (the decisive point, already correctly flagged):** instructor's auto-reask would *suppress* tool-existence hallucinations, contaminating TEHR. Correct.
- Net: **cite-only / pattern-source is the right call.** "Cite-only" is not over-optimistic; if anything the survey is slightly generous in implying easy reuse as a client layer for local models (the MLX gap makes that more friction than stated). For API models (Anthropic/OpenAI) instructor *would* integrate cleanly, but we want raw behavior, so we don't want it.

### Over-optimism penalty check
- No inflated stars (exact). No inflated license permissiveness (MIT is genuinely permissive). Usability is, if anything, slightly *overstated* for our specific MLX stack — corrected above. The "Yes (for RVR, weak-to-moderate)" baseline framing is honest (it's an ablation framing, not a turnkey numeric baseline).

**Final recommendation: cite-only** (prior art for RVR's validate→reask→retry paradigm + pattern source for the paper-revision skill). Do NOT vendor into the measurement path. License confirmed MIT — vendoring small snippets elsewhere is permissible but unnecessary. Confidence: high.
</content>
</invoke>

---

## ADVERSARIAL RE-VERIFICATION #2 (appended 2026-05-29, fully independent)

**Verdict: survey body + first adversarial pass are ACCURATE. License/stars confirmed from primary sources. One survey claim is mildly over-optimistic on local-model reuse; corrected below. Recommendation stands: cite-only.**

### License — CONFIRMED `MIT` (SPDX), 3 independent primary sources
- Raw `LICENSE` (githubusercontent): opens `MIT License` / `Copyright (c) 2023 Jason Liu` / "Permission is hereby granted, free of charge...". Permissive, **no copyleft clauses**.
- GitHub API `license.spdx_id = "MIT"`, `license.name = "MIT License"`.
- `pyproject.toml` `license = "MIT"`.
- **The task's GPL/AGPL copyleft caveat does NOT apply.** MIT is permissive: we may vendor snippets (attribution only) into our permissive harness, run externally, or cite freely. License is a non-blocker.

### Stars — CONFIRMED order-of-magnitude (10^4)
- GitHub API `stargazers_count = 13064` (2026-05-29). Matches survey's 13,064 exactly. `archived = false`, `pushed_at = 2026-05-24T05:22:48Z`, `language = Python`. "Very active" is fair.

### Usability pressure-test — "cite-only" HOLDS; survey is slightly generous on local reuse
Primary blockers are methodological + integration, NOT license:
1. **No MLX, AND no native Ollama/llama-cpp provider.** Verified the live `instructor/providers/` tree: anthropic, bedrock, cerebras, cohere, fireworks, gemini, genai, groq, mistral, openai, perplexity, vertexai, writer, xai. There is **no `mlx`, no `ollama`, no `llama_cpp` directory.** Local models are reachable only through the `openai` provider pointed at an OpenAI-compatible endpoint. Our local arm runs MLX directly, so instructor cannot drive our MLX models without us standing up an OpenAI-compat shim. The survey body's phrasing "local via llama-cpp/ollama" **overstates native support** — those are not first-class providers; they ride the OpenAI-compat path. (The prior adversarial pass flagged the MLX gap but understated it by leaving Ollama/llama-cpp as if native.)
2. **Methodological conflict (decisive):** instructor's auto-reask self-correction would suppress tool-existence hallucinations, contaminating TEHR. Keep it out of the measurement path. Confirmed correct.

### Over-optimism penalty
- Stars: exact, not inflated. License: genuinely permissive, not overstated. Maintenance: genuinely active.
- **Single over-optimistic claim:** ease of reusing instructor as the client layer for *local* models. Native local-provider support does not exist; only OpenAI-compat. For API models (Anthropic/OpenAI) it would integrate cleanly, but we want raw behavior so we don't want it anyway. Net effect on verdict: none.

**Final recommendation: cite-only** — prior art for RVR's validate→reask→retry paradigm and a pattern source for the paper-revision skill. Do NOT insert into the TEHR measurement path. License confirmed MIT (vendoring small snippets elsewhere is permissible but unnecessary). Confidence: high.
