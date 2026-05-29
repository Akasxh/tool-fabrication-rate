# Repo Survey: smolagents

- **Repo:** huggingface/smolagents
- **URL:** https://github.com/huggingface/smolagents (live, no 404)
- **Stars:** 27,581 | Forks: 2,622 | Open issues: 564 (as of 2026-05-29)
- **License:** Apache-2.0 (SPDX, confirmed via GitHub API) — permissive, no copyleft risk
- **Language:** Python | Active (last push 2026-05-29) | Not archived
- **Category:** agent-framework

## What it is
A barebones HF library for agents that "think in code" — the headline abstraction is
`CodeAgent`, which writes Python actions instead of JSON tool calls, plus a `ToolCallingAgent`
for classic JSON tool-call style. Provides a model-abstraction layer (`Model` subclasses:
`MLXModel`, `VLLMModel`, `TransformersModel`, `LiteLLMModel`, `OpenAIModel`, `AmazonBedrockModel`,
`InferenceClientModel`, etc.), a `Tool` system, sandboxed Python executors (local + E2B/Docker
remote), MCP client support, memory, and a Gradio UI. It is a *framework for building/running
agents*, not a benchmark or eval suite.

## Concrete judgment for our paper

### RUN as an extra benchmark? NO.
smolagents ships no benchmark dataset and no scored eval harness — it is execution
infrastructure. There is nothing to "run" that produces a TEHR-style metric. The `examples/`
dir is demos, not a graded suite.

### Reuse a COMPONENT in our harness? LOW-VALUE / SKIP.
Our harness already has its own clean adapter layer (`harness/adapters/`, `harness/registry.py`)
and bench loaders, and we already run MLX + API models directly. smolagents' `Model` classes
(`src/smolagents/models.py`: `MLXModel` line 751, `LiteLLMModel`, `OpenAIModel`) cover the same
ground we built ourselves. Pulling in smolagents as a dependency would add a heavy framework and
its own control flow on top of our purpose-built per-call tracing. Not worth the integration
cost; our adapters are more controllable for measuring per-call TEHR. Apache-2.0 makes *copying a
small pattern* legally trivial, but there is no component we actually need.

### Reuse as a BASELINE? MAYBE — as an agent-scaffold ablation, not core.
smolagents could serve as a third-party agent scaffold to show TEHR is scaffold-robust: run the
same models under `ToolCallingAgent`/`CodeAgent` and check whether tool-existence hallucination
rates differ from our bare harness. This is a *nice-to-have breadth ablation*, not a headline
baseline. Effort: medium (wire BFCL tools into smolagents' `Tool` interface + capture per-call
events). Only pursue if reviewers push on "is TEHR an artifact of your specific scaffolding."

### Cite as PRIOR ART? YES.
Cite as a widely-used (27k-star) open agent framework and as the canonical example of the
"code-agent" execution paradigm (vs JSON tool calls). Useful for situating our tool-existence
hallucination work in the agent-tooling landscape and for the related-work/limitations framing
("results may differ under code-action scaffolds like smolagents").

### Borrow a PATTERN — for the paper, and notably for our RVR framing. YES (most useful finding).
`agents.py::execute_tool_call` (line ~1463) does exactly the guardrail our RVR intervention
formalizes:
```python
available_tools = {**self.tools, **self.managed_agents}
if tool_name not in available_tools:
    raise AgentToolExecutionError(
        f"Unknown tool {tool_name}, should be one of: {', '.join(available_tools)}.", ...)
```
The error string echoes the available-tool list straight back into the agent loop — i.e., a
production framework already re-prompts with the tool registry on a bad call. This is strong
prior-art support that our RVR (re-prompt with the registry on a hallucinated tool) is the
*natural, deployed* remedy, and lets us cite a 27k-star library as evidence the intervention is
practical rather than contrived. Worth one sentence in the intervention section + related work.

For the paper-revision skill / reviewer personas there is no useful pattern here (it's an agent
runtime, not a writing/review tool).

## Effort & risk summary
- **License risk:** none (Apache-2.0, permissive).
- **Integration effort:** RUN = n/a; component reuse = not needed; baseline ablation = medium;
  cite = trivial; pattern borrow (RVR prior-art cite) = trivial.
- **Bottom line:** Cite as prior art (esp. the unknown-tool re-prompt as RVR precedent);
  optionally use as a scaffold-robustness baseline ablation if reviewers demand it. Do not run as
  a benchmark and do not adopt as a harness dependency.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

**Method:** GitHub API + raw `LICENSE` + raw `src/smolagents/{models.py,agents.py}` +
`pyproject.toml`, read line-by-line. Did not trust the survey's own summaries.

### License — CONFIRMED, no inflation.
- Raw `LICENSE` file header: "Apache License Version 2.0, January 2004". SPDX = **Apache-2.0**.
- GitHub API `license.spdx_id` = `Apache-2.0` (independent second source — agrees).
- Core `pyproject.toml` deps (huggingface-hub, requests, rich, jinja2, pillow, python-dotenv) are
  all permissive (Apache/BSD/MIT/HPND). **No GPL/AGPL anywhere in the core.** The
  GPL/AGPL-cannot-vendor concern raised in the task does NOT apply here. Apache-2.0 permits
  vendoring into a permissive codebase with attribution + NOTICE. Survey's "license risk: none"
  is accurate.

### Stars — CONFIRMED, correct order of magnitude.
- API: 27,581 stars / 2,622 forks / 564 open issues — matches survey exactly. ~10^4 ("27k-star")
  framing is fair. Not archived; pushed 2026-05-29 (actively maintained). All accurate.

### Code-pattern claims — CONFIRMED but line number slightly off.
- `execute_tool_call` is at `agents.py:1453` (survey said "~1463"; the `raise` is at line 1467 —
  within the method, so the cited snippet is real, just mis-located by ~10 lines).
- The unknown-tool guardrail is verbatim: `if tool_name not in available_tools: raise
  AgentToolExecutionError(f"Unknown tool {tool_name}, should be one of: {', '.join(available_tools)}.")`.
  The error string DOES echo the full available-tool list back into the loop. **RVR-precedent
  claim holds** — this is the single most valuable, fully-substantiated finding.

### Baseline-ablation claim — OVER-OPTIMISTIC, needs a caveat (main correction).
The survey (lines 35-40) proposes running our MLX models under `ToolCallingAgent`/`CodeAgent` as
a "scaffold-robustness baseline" at "medium effort." Reading `models.py:751-857`:
- `MLXModel.generate` accepts `tools_to_call_from` but injects tools **into the prompt** via
  `tokenizer.apply_chat_template(messages, tools=tools, ...)` — there is NO native structured
  tool-calling. It returns a `ChatMessage` with `content=text` only; `tool_calls` is unset.
- `ToolCallingAgent` therefore relies on the base-class `Model.parse_tool_calls`
  (`models.py:583`) → `get_tool_call_from_text(content, tool_name_key, tool_arguments_key)` to
  TEXT-PARSE tool calls out of raw model output. This is brittle and **model-chat-template
  dependent**: if the MLX model's template doesn't emit tool calls in the expected key format,
  parsing fails or mis-fires. `MLXModel` also hard-`raise`s on `response_format` ("MLX does not
  support structured outputs"), so no schema-constrained fallback.
- **Implication for TEHR:** running our 4-bit Qwen3 MLX models as a `ToolCallingAgent` baseline
  would conflate genuine tool-existence hallucinations with smolagents' text-parsing failures —
  a confound that could inflate or distort the very metric we report. The ablation is closer to
  **medium-HIGH effort with a measurement-validity risk**, not a clean "medium." API models
  (OpenAI/LiteLLM/Bedrock paths use native tool-calling) would be cleaner; MLX would need a
  parser-error audit first. Survey under-stated this.
- `CodeAgent` sidesteps native tool-calling (it generates Python), but that changes the action
  space entirely — tool "existence" errors surface as `NameError`/`AttributeError` in the
  sandbox, not as `Unknown tool`. That is arguably interesting but is a DIFFERENT phenomenon from
  per-call TEHR; treating it as the same metric would be apples-to-oranges.

### "Cite-only" pressure-test — HOLDS.
- Run as our benchmark: NO (no dataset/scored eval — confirmed; `examples/` are demos). Correct.
- Vendor a component: legally fine (Apache-2.0) but our `harness/adapters/` already cover MLX+API
  with native per-call tracing; smolagents' MLX path is prompt-injection + text-parse, which is
  LESS controllable than what we have for measuring per-call TEHR. No component worth pulling.
  Correct.
- Cite as prior art + RVR precedent: YES, strongest use. Correct and verified.

**Net adjustment to verdict:** survey is substantially accurate (license, stars, RVR-precedent
all confirmed). The one over-optimistic claim is the baseline-ablation effort/cleanliness: for
MLX models it carries a real measurement-validity confound (smolagents text-parses tool calls
rather than using native tool-calling) and should be labeled medium-high effort + caveated, not a
drop-in "medium" baseline. Recommendation: **include-parts** — cite as prior art and use the
unknown-tool re-prompt as RVR precedent; treat the scaffold ablation as optional/conditional and
API-models-first if pursued. License confirmed Apache-2.0; vendoring legally permitted (no
copyleft).

---

## SECOND ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

**Method:** Re-derived every load-bearing claim from live sources, not from the survey or the
prior verification section. Sources: GitHub API, raw `LICENSE`, raw `src/smolagents/{agents.py,
models.py}` (line-addressed), raw `pyproject.toml`, repo top-level `contents` API.

### License — CONFIRMED Apache-2.0 (two independent sources).
- Raw `LICENSE` header: "Apache License / Version 2.0, January 2004". SPDX = **Apache-2.0**.
- GitHub API `license.spdx_id` = `Apache-2.0` (name "Apache License 2.0").
- Core `pyproject.toml` runtime deps: huggingface-hub, requests, rich, jinja2, pillow,
  python-dotenv — all permissive (Apache/BSD/MIT/HPND). Optional extras (boto3, torch,
  soundfile, blaxel) are likewise permissive. **No GPL/AGPL in core or extras.** The task's
  GPL/AGPL-vendoring concern is N/A here: Apache-2.0 permits vendoring into our permissive
  codebase with attribution + NOTICE. `license_confirmed = true`.

### Stars / liveness — CONFIRMED, correct order of magnitude.
- API now: 27,581 stars / 2,622 forks / 564 open issues; `archived=false`; `pushed_at`
  2026-05-29T05:14:10Z. The "27k-star" / ~10^4 framing is exact, not inflated. Actively
  maintained (pushed today).

### RVR-precedent code claim — CONFIRMED verbatim, line numbers now exact.
- `agents.py:1453 def execute_tool_call`; `1465 if tool_name not in available_tools:`;
  `1466-1467 raise AgentToolExecutionError(f"Unknown tool {tool_name}, should be one of:
  {', '.join(available_tools)}.", ...)`. The error string echoes the full available-tool list
  back into the agent loop. This is genuine production prior-art for RVR (re-prompt with the
  registry on a hallucinated/unknown tool). **Strongest, fully-substantiated finding — holds.**
  (Earlier survey said "~1463"; actual is 1453/1467 — trivial mislocation, snippet is real.)

### MLX baseline-ablation over-optimism — CONFIRMED as the key correction.
Verified line-by-line in `models.py`:
- `MLXModel.generate` (class at :751) **hard-raises** `ValueError("MLX does not support
  structured outputs.")` at line 825 on any `response_format`.
- Tools are injected into the prompt via `apply_chat_template(messages, tools=tools, ...)`
  (line 837) — NOT native structured tool-calling.
- It returns `ChatMessage(role=..., content=text, ...)` (lines 849-851) with `tool_calls`
  UNSET. Consequently `ToolCallingAgent` falls back to `Model.parse_tool_calls` (:583) →
  `get_tool_call_from_text` (:400, called at :589), which **text-parses** tool calls out of raw
  output keyed on `tool_name_key`/`tool_arguments_key`.
- **Confound for TEHR:** under smolagents, our 4-bit Qwen3 MLX models' tool calls are recovered
  by brittle, chat-template-dependent text parsing. A parse miss is NOT a tool-existence
  hallucination, yet it would surface as a malformed/unknown-tool event — directly contaminating
  the metric we report. So the "medium-effort scaffold-robustness baseline" is really
  **medium-HIGH effort + measurement-validity risk** for MLX. API paths (OpenAI/LiteLLM/Bedrock,
  which use native `tools=` schemas) are cleaner. Survey under-stated this; prior verification's
  correction is accurate and I independently reproduce it.
- `CodeAgent` is a different action space (Python); tool-existence errors there are
  `NameError`/`AttributeError` in the sandbox, not `Unknown tool` — apples-to-oranges with
  per-call TEHR. Confirmed.

### "Run as benchmark" / "cite-only" pressure-test — HOLDS.
- Top-level repo contents: `examples` (demos) + `tests` only; **no benchmark/dataset/eval-suite
  dir**. There is nothing that emits a TEHR-style score. RUN-as-benchmark = NO (confirmed).
- Vendor a component: legally fine (Apache-2.0) but unnecessary — our `harness/adapters/` give
  native per-call tracing for MLX+API; smolagents' MLX path (prompt-inject + text-parse) is
  strictly LESS controllable for measuring per-call TEHR. SKIP component reuse (confirmed).
- Cite as prior art + use unknown-tool re-prompt as RVR precedent: YES, the highest-value use.

### Survey-claims audit (did it overstate?).
- Stars/license/liveness: NOT overstated — exact.
- "license risk: none": correct.
- The ONE over-optimistic claim is the baseline ablation framed as a clean "medium": for MLX it
  is medium-high with a real confound. Already caveated in the first verification; I confirm.

**VERDICT: recommend = include-parts.** Cite smolagents as prior art (canonical code-agent
framework, 27k stars) AND cite `execute_tool_call`'s unknown-tool re-prompt as deployed precedent
for RVR. Do NOT run it as a benchmark (no eval suite) and do NOT vendor it (our adapters are more
controllable). The scaffold-robustness ablation is optional and, if pursued, must go
API-models-first with an MLX parser-error audit — not a drop-in baseline. License Apache-2.0,
confirmed from LICENSE file + API; vendoring legally permitted, no copyleft. Confidence: high.
