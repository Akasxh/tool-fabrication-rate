# Repo Survey: langgraph

- **Repo:** langchain-ai/langgraph
- **Canonical URL:** https://github.com/langchain-ai/langgraph (URL valid, no 404)
- **Docs:** https://docs.langchain.com/oss/python/langgraph/
- **Stars:** 33,299 (gh api, 2026-05-29)
- **Forks:** 5,618 | Open issues: 548 | Active (pushed 2026-05-28), not archived
- **License:** MIT (SPDX `MIT`, confirmed via `gh api .../license`) — permissive, no copyleft risk
- **Language:** Python (monorepo under `libs/`: `langgraph`, `prebuilt`, `checkpoint*`, `cli`, `sdk-py`, `sdk-js`)
- **Category:** agent-framework

## What it does
LangGraph is a low-level orchestration framework for building stateful, multi-step
LLM agents as graphs (nodes + edges + shared state), with persistence/checkpointing,
streaming, human-in-the-loop interrupts, and prebuilt agent executors. It is the
graph runtime under LangChain's agent stack. Relevant subpackage `libs/prebuilt`
ships `ToolNode`, `chat_agent_executor.py` (ReAct-style executor), `tool_validator.py`
(`ValidationNode`), and tool-call transform/stream helpers.

## Concrete relevance to SCALE (TEHR + RVR)

### MOST IMPORTANT: prior art for the RVR intervention
`libs/prebuilt/langgraph/prebuilt/tool_node.py` contains `ToolNode._validate_tool_call`,
which does *exactly* our tool-existence-hallucination detect-and-reprompt loop:

```python
INVALID_TOOL_NAME_ERROR_TEMPLATE = (
    "Error: {requested_tool} is not a valid tool, try one of [{available_tools}]."
)
def _validate_tool_call(self, call):
    requested_tool = call["name"]
    if requested_tool not in self.tools_by_name:
        content = INVALID_TOOL_NAME_ERROR_TEMPLATE.format(
            requested_tool=requested_tool,
            available_tools=", ".join(all_tool_names))
        return ToolMessage(content, name=requested_tool,
                           tool_call_id=call["id"], status="error")
```

This is the production-framework analog of RVR: when a model calls a tool not in the
registry, return an error ToolMessage that re-lists the available tools so the model
self-corrects on the next turn. The deprecated `ValidationNode` (`tool_validator.py`)
generalizes this to pydantic-schema validation with a `_default_format_error` that
ends "Respond after fixing all validation errors." — same re-prompt-on-bad-call shape.

Implication for the paper: RVR is **not novel as a mechanism** (LangGraph ships it as
a default-on behavior). Our contribution must be framed as (a) *measuring* the
underlying per-call TEHR that this guardrail silently absorbs in production, and
(b) quantifying RVR's recovery effect across model families — i.e., we measure what
LangGraph's `ToolNode` papers over. We should CITE this as the canonical industry
guardrail and differentiate on measurement, not invention.

## Per-axis verdict

- **RUN as extra benchmark:** NO. LangGraph is an orchestration runtime, not a
  benchmark or dataset. Nothing to score against. (BFCL / tau-bench remain our
  benchmark sources.)
- **Reuse a COMPONENT in our harness:** LOW VALUE / SKIP. Our harness has its own
  clean adapter+registry abstraction (`harness/registry.py`, `bench_loaders/*.py`)
  with canonical OpenAI tool-shape and three adapters (Anthropic/OpenAI/MLX). Pulling
  in `ToolNode` would drag the whole `langgraph` + `langchain-core` dependency tree
  (pydantic-v1/v2 dual support, RunnableCallable internals) for ~30 lines of logic we
  already implement more directly. Reimplementing the validate-and-reprompt is trivial;
  vendoring is not worth the coupling.
- **Reuse as BASELINE:** WEAK MAYBE. Could position LangGraph `ToolNode`'s default
  error-reprompt as the "off-the-shelf guardrail baseline" that RVR is benchmarked
  against — but functionally RVR already *is* that pattern, so a side-by-side adds
  little. Better used as the named real-world instantiation of the baseline behavior
  than as a separately-run system.
- **Cite as PRIOR ART:** YES — strongest use. `ToolNode._validate_tool_call` /
  `INVALID_TOOL_NAME_ERROR_TEMPLATE` is the concrete, widely-deployed (33k-star,
  MIT) instance of "re-prompt with the tool registry on an invalid tool name."
  Cite to (1) establish that the intervention is industry-standard and (2) sharpen
  our novelty claim toward measurement of TEHR rather than the intervention itself.
- **Borrow a PATTERN for paper-revision skill / personas:** MINIMAL. Not a writing
  or review tool. The only transferable idea is the error-template wording
  ("try one of [...]") as a phrasing reference for RVR's prompt; not skill-relevant.

## Effort & risk
- **Effort:** LOW for citation/differentiation (done — code located and quoted).
  HIGH and not recommended for harness integration (heavy dep tree, dual-pydantic).
- **License risk:** NONE for citation. NONE for vendoring a small snippet (MIT,
  attribution only) — but we should not need to.
- **Bottom line:** Treat as **cite-only prior art** that reframes RVR's novelty.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

Independently re-checked every load-bearing claim. The survey holds up; no over-optimistic claims found.

- **LICENSE — CONFIRMED MIT (SPDX `MIT`).** Checked the actual root `LICENSE` file via
  `raw.githubusercontent.com` (not just the GH API summary): first lines read
  "MIT License / Copyright (c) 2024 LangChain, Inc." Also checked the monorepo
  subpackage `libs/prebuilt/LICENSE` (the lib that ships `ToolNode`) — also MIT.
  **No GPL/AGPL/copyleft anywhere.** Vendoring a snippet is legally fine (attribution only).
  GH API cross-check: `.license.spdx_id == "MIT"`.
- **STARS — CONFIRMED order-of-magnitude (~33k).** `gh api` returns 33,299 stars,
  5,618 forks, not archived, pushed 2026-05-28. "33k-star" claim is exact, not inflated.
- **CODE CLAIM — CONFIRMED.** `INVALID_TOOL_NAME_ERROR_TEMPLATE` and
  `_validate_tool_call` exist verbatim in
  `libs/prebuilt/langgraph/prebuilt/tool_node.py` exactly as quoted. The prior-art
  / RVR-is-not-novel-as-mechanism framing is sound and load-bearing for the paper.
- **"CITE-ONLY" PRESSURE TEST — CONFIRMED, with one factual nit.** Could we actually
  run/reuse it in our MLX+API harness? No, and cite-only is correct:
  - It is NOT a benchmark/dataset — nothing to score, so "run-as-benchmark" is wrong.
    BFCL / tau-bench remain the benchmark sources.
  - Reuse-as-component is genuinely low value. Per `libs/prebuilt/pyproject.toml`,
    `langgraph-prebuilt` runtime-requires `langchain-core>=1.3.1` and
    `langgraph-checkpoint` (which transitively pulls pydantic). The survey said it
    drags in "langgraph + langchain-core"; the *exact* deps are
    `langchain-core` + `langgraph-checkpoint` (langgraph itself is test-only). Minor
    naming inaccuracy — but the conclusion (heavy dep tree for ~30 lines we already
    implement) stands. Our harness's own registry/adapter abstraction is the right call.
  - LangGraph is also built around its own graph/`Runnable` execution model and message
    objects; it does not natively target MLX, so running our 4-bit Qwen3 / MLX models
    through it would require adapters anyway. Net: cite, do not integrate.
- **License-for-vendoring flag:** N/A in the cautionary sense — MIT is permissive, so
  the GPL/AGPL "cite-but-don't-vendor" warning does NOT apply here. We *could* vendor
  the ~30-line snippet with attribution; we simply shouldn't, for coupling reasons.

**VERDICT: cite-only.** Survey claims are accurate (stars, MIT license, code prior art).
Confidence HIGH. The single nit is the precise dependency names, which does not change
any recommendation.

---

## ADVERSARIAL VERIFICATION #2 (2026-05-29, second independent pass)

Re-ran every load-bearing check from scratch (raw LICENSE files + `gh api` + raw source), not trusting the survey body or the first verification block.

- **LICENSE = MIT (SPDX `MIT`) — CONFIRMED.** Root `LICENSE` (via raw.githubusercontent) reads
  "MIT License / Copyright (c) 2024 LangChain, Inc." Subpackage `libs/prebuilt/LICENSE` (the lib
  that ships `ToolNode`) is also MIT. `gh api .../license` and `.../repos` both return `spdx_id == "MIT"`.
  Grep of the LICENSE for GPL/copyleft/share-alike/reciprocal: 0 hits.
  **No copyleft anywhere.** The GPL/AGPL "cite-but-don't-vendor" caution does NOT apply — vendoring
  the ~30-line snippet is legally fine (MIT, attribution only). We simply choose not to, for coupling.
- **STARS — CONFIRMED ~33k.** `gh api` returns 33,300 stars (was 33,299 on the prior pass; normal drift),
  5,618 forks, `archived:false`, `pushed:2026-05-28`. Order-of-magnitude and "33k-star" claim are accurate, not inflated.
- **CODE PRIOR-ART CLAIM — CONFIRMED VERBATIM.** In `libs/prebuilt/langgraph/prebuilt/tool_node.py`:
  `INVALID_TOOL_NAME_ERROR_TEMPLATE` at L108-109 (`"Error: {requested_tool} is not a valid tool, try one of [{available_tools}]."`)
  and `_validate_tool_call` at L1268, invoked at L946 and L1093. Body matches the survey quote (returns an
  error `ToolMessage` re-listing available tools when the requested tool is absent). This is a genuine,
  default-on, production instance of the RVR detect-and-reprompt pattern. The "RVR is not novel as a mechanism;
  our contribution is measuring TEHR" framing is sound and load-bearing.
- **CITE-ONLY PRESSURE TEST — CONFIRMED.** Not a benchmark/dataset → "run-as-benchmark" is wrong; BFCL/tau-bench
  remain the benchmark sources. Component reuse is low-value: `langgraph-prebuilt` runtime-requires
  `langchain-core>=1.3.1` + `langgraph-checkpoint` (verified in `libs/prebuilt/pyproject.toml`; pydantic pulled
  transitively), a heavy tree for ~30 lines our harness already implements. LangGraph runs on its own graph/Runnable
  execution model and does not target MLX, so our 4-bit Qwen3/MLX models would need adapters regardless. Cite, do not integrate.

**No over-optimistic claims found to penalize.** The first verification block's only nit (precise dep names:
`langchain-core` + `langgraph-checkpoint`, not "langgraph + langchain-core") is correct and does not change any recommendation.

**VERDICT: cite-only. License MIT (confirmed). Confidence HIGH.**
