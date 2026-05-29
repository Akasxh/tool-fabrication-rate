# Repo survey: promptfoo

- **Repo:** promptfoo/promptfoo
- **Canonical URL:** https://github.com/promptfoo/promptfoo (live, no 404)
- **Stars:** 21,702 (gh api, 2026-05-29)
- **License:** MIT (SPDX: MIT) — verified via `gh api .license.spdx_id`
- **Language:** TypeScript/Node · very actively maintained (last push 2026-05-29, daily releases)
- **Age:** created 2023-04-28; 30 contributors; 1,911 forks; 304 open issues
- **Category:** eval-harness

## What it does
A **developer/CI-oriented LLM testing and red-teaming tool**. Two product surfaces:

1. **Eval:** declarative **YAML configs** (`promptfooconfig.yaml`) that define prompts ×
   providers × test cases, then run **assertions** over outputs. Assertion types include
   deterministic checks (`equals`, `contains`, `regex`, `is-json`, `latency`, `cost`),
   programmatic checks (`javascript`, `python`), and **model-graded** checks
   (`llm-rubric`, `model-graded-closedqa`, `answer-relevance`, `factuality`, `g-eval`).
   Outputs a web/CLI matrix view; integrates into CI/CD.
2. **Red team / pentest:** generates adversarial inputs (jailbreaks, prompt injection, PII
   leakage, etc.) against an endpoint and scores vulnerabilities. This is the marketing
   headline ("Used by OpenAI and Anthropic") and the `pentesting`/`red-teaming` topics.

Provider coverage is broad (OpenAI, Anthropic, Gemini, DeepSeek, local/HTTP, etc.). It is
a **prompt/response testing framework**, not an academic benchmark. It has assertion
support for tool/function-call outputs (`is-valid-function-call`, `is-valid-openai-tools-call`
schema checks) but **no notion of a tool registry, multi-turn agentic rollout, or
tool-existence hallucination as a measured rate.**

## Fit for our paper (TEHR / RVR on BFCL multi-turn)

Our harness (`harness/bench_loaders/*.py`, per-task tool `registry`, family-specific
adapters in `harness/adapters/`, `cost_meter.py`, `intervention/` RVR re-prompt) is
purpose-built for **multi-turn tool-calling** and a per-call **Tool-Existence
Hallucination Rate**. promptfoo operates at the single-prompt/assertion level and is a
Node app; the headline contribution cannot be expressed through it.

Concrete verdict by axis:

- **RUN as an extra benchmark? NO.** promptfoo ships no tool-calling benchmark dataset,
  no tool registry, and no multi-turn agent loop. Its function-call assertions only
  validate that a single emitted call matches a provided JSON schema — they cannot detect
  a call to a *non-existent* tool across a multi-turn trajectory, which is exactly TEHR.
  Wiring BFCL/tau-bench into promptfoo's YAML + writing a custom JS/Python assertion to
  re-implement our hallucination classifier would be **more work than our harness already
  does**, in a second language (TS/Node), with no scientific upside. Skip.

- **Reuse a COMPONENT in our harness? NO (language + scope mismatch).** It is TypeScript;
  our harness is Python (uv-managed). Vendoring its assertion engine buys nothing our
  `stats/` + runner classifier doesn't already do, and adds a Node toolchain. MIT makes it
  legal but not worth it.

- **Reuse as a BASELINE? NO.** RVR is an *intervention* (re-prompt with the tool registry
  on a bad call). promptfoo has no comparable intervention/repair mechanism — its red-team
  module *generates* attacks, it does not *correct* model behavior mid-trajectory. Nothing
  to baseline RVR against.

- **Cite as PRIOR ART? YES (secondary, optional).** Worth a one-line Related Work cite as
  the leading **industry/CI LLM-eval-and-red-teaming framework**, to contrast with our
  academic agentic-tool-calling metric: industry harnesses score per-prompt assertions and
  do red-team attack generation, but **none expose a per-call tool-existence hallucination
  rate over multi-turn tool-calling trajectories**. Useful to show breadth-awareness for a
  main-track submission and to differentiate "assertion/red-team testing" from "behavioral
  metric + intervention." Lower priority than lm-eval / BFCL / tau-bench citations.

- **Borrow a PATTERN for the paper-revision skill / reviewer personas? YES — best value
  here.** Two transferable patterns:
  1. **`llm-rubric` / `g-eval` / `model-graded-closedqa` assertion design.** promptfoo's
     model-graded assertions are essentially structured **LLM-as-judge rubrics**: a fixed
     rubric prompt, a scored pass/fail with rationale, deterministic thresholding. This is
     a clean template for our **reviewer personas** (each persona = a rubric assertion with
     explicit criteria + score + justification) and for an automated **paper-revision
     gate** that checks a draft against ICML-reviewer criteria before we ship. Adopt the
     *shape* (rubric text → JSON score+reason), not the code.
  2. **Declarative YAML test-matrix + CI gate pattern** for running persona reviews over a
     paper draft as a reproducible, versioned matrix (persona × section), mirroring
     promptfoo's prompts×providers×asserts grid. Strengthens a reproducibility narrative.

## License risk
None. MIT — permissive, allows reuse/vendoring with attribution. Citing it and borrowing
the rubric/assertion *pattern* (reimplemented in Python) carries zero risk.

## Bottom line
**reuse-pattern** (with an optional secondary prior-art cite). Do **not** try to run TEHR
through it, vendor it, or baseline RVR against it — wrong language, wrong abstraction,
no tool-registry/multi-turn/intervention concepts. The real payoff is borrowing its
**model-graded `llm-rubric`/`g-eval` assertion pattern** to structure our reviewer
personas and an automated paper-revision gate, plus a light Related Work cite to
differentiate academic tool-hallucination measurement from industry assertion/red-team
testing.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verified by re-querying the GitHub API and reading source directly. Verdict: survey is
**substantially accurate** with two corrections, one of them material to a TEHR paper.

### License — CONFIRMED MIT (SPDX: MIT), with caveats
- Root `LICENSE` read verbatim from `raw.githubusercontent.com`: standard unmodified MIT,
  `Copyright (c) Promptfoo 2025`. No dual-license, Commons Clause, SSPL, BSL, or
  proprietary/enterprise carve-out in the root license. `gh api .../license` agrees: `MIT`.
- **NEW finding the original survey missed:** the repo vendors third-party code under two
  *additional* LICENSE files: `src/external/APACHE_LICENSE` (Apache-2.0) and
  `src/redteam/providers/crescendo/LICENSE` (MIT, derived from Microsoft Azure/PyRIT).
  Both are permissive and compatible with a permissive codebase — **no copyleft/AGPL/GPL
  trap anywhere.** This does not change the vendoring verdict but means a clean-room
  reimplementation is still the right call (you would not vendor TS into a Python harness
  regardless). License risk for cite/run-external/borrow-pattern remains zero.
- `license_confirmed: true`.

### Stars — CONFIRMED order of magnitude
- `gh api` returns **21,702 stars** (matches survey exactly), 1,911 forks, created
  2023-04-28, last push 2026-05-29, language TypeScript. ~2x10^4, i.e. tens of thousands.
  Healthy and actively maintained. No inflation.

### Reuse-pattern claim — PRESSURE-TESTED, mostly holds, but survey OVERSTATED the gap
The survey's hard "NO" on running TEHR through promptfoo is correct on net, but its
justification contains a **factual overstatement that must be corrected** so we don't
mis-cite it in Related Work:

- **Survey claim:** promptfoo's function-call assertions "cannot detect a call to a
  *non-existent* tool." **This is WRONG.** Reading `src/providers/openai/util.ts`
  `validateFunctionCall()` (lines 784-820): it explicitly does
  `interpolatedFunctions?.find(f => f.name === functionName)` and throws
  `Called "X", but there is no function with that name` when the model invokes a tool
  absent from the declared list. That **is** a single-call tool-existence check — the
  atomic primitive underlying TEHR. The `is-valid-function-call` assertion
  (`src/assertions/functionToolCall.ts`) surfaces exactly this.
- **What the survey got RIGHT (the limitations that actually matter):**
  1. **Provider-locked.** Existence checking only fires for OpenAI and Google
    (AIStudio/Vertex/Live) providers — it `throw`s "Provider does not have functionality
    for checking function call" for anything else. Our MLX/local + Anthropic + Qwen3
    families would get **no** tool-existence checking out of the box. This alone kills
    "run TEHR through it."
  2. **Single-call, not a rate over multi-turn trajectories.** It validates one emitted
    call against a static schema. There is no agent loop, no tool *registry* abstraction,
    no per-call rate aggregated across a multi-turn rollout, no BFCL/tau-bench dataset.
    TEHR-as-a-metric does not exist here.
  3. **No intervention / no RVR analog.** Confirmed: red-team module *generates* attacks;
    nothing re-prompts/repairs mid-trajectory. Nothing to baseline RVR against.
  4. **TypeScript/Node** vs our Python/uv harness — vendoring buys nothing.

- **Net:** the survey's *verdict axes* are correct (skip as benchmark, skip as component,
  skip as baseline, optional secondary prior-art cite, borrow the `llm-rubric`/`g-eval`
  rubric *shape* for reviewer personas). But the Related Work framing must be tightened:
  do NOT write "promptfoo cannot detect tool-existence hallucination." The honest,
  defensible framing is: *industry harnesses like promptfoo perform single-call,
  provider-specific schema/existence validation of emitted function calls, but expose no
  tool-registry-grounded per-call hallucination RATE over multi-turn agentic trajectories
  and no intervention mechanism.* A reviewer who reads promptfoo's source (plausible) would
  catch the overstated version and ding us.

### Structured verdict
- repo: promptfoo/promptfoo
- license_spdx: MIT (root); vendored Apache-2.0 + MIT subcomponents, all permissive
- recommend: cite-only (secondary/optional prior art) + borrow the rubric *pattern* for
  the paper-revision skill / reviewer personas; do NOT run-as-benchmark, do NOT vendor,
  do NOT use as RVR baseline
- confidence: high
- claims_check: stars (21,702) accurate; license (MIT) accurate and confirmed at file
  level; the reuse-pattern direction is right BUT the survey overstated the capability
  gap by claiming promptfoo cannot detect non-existent-tool calls — it can, for
  OpenAI/Google, at single-call granularity. Real differentiators are provider-lock,
  no multi-turn rate, no tool registry, no intervention.
- caveats: correct the Related Work sentence before submission; promptfoo's single-call
  existence check is genuine prior art for the *primitive*, so frame our contribution as
  the multi-turn RATE + registry grounding + RVR intervention, not as "they can't detect
  it at all."

---

## INDEPENDENT RE-VERIFICATION #2 (2026-05-29, Opus 4.8, from-scratch)

Re-ran every check independently against the live GitHub API and raw source — did not
trust the survey body OR the prior verification block. Concur with both on substance; one
prior claim slightly tightened. Verdict: **MIT confirmed at file level, stars confirmed,
reuse-pattern verdict holds, original survey's "cannot detect non-existent tool" claim is
genuinely WRONG and must not be repeated in Related Work.**

### License — CONFIRMED MIT (SPDX: MIT)
- `gh api repos/promptfoo/promptfoo` -> `license.spdx_id = MIT`; `.../license` endpoint
  -> `{name: MIT License, path: LICENSE, spdx: MIT}`.
- Read root `LICENSE` verbatim from `raw.githubusercontent.com/.../main/LICENSE`: standard
  unmodified MIT text, `Copyright (c) Promptfoo 2025`. No Commons Clause, BSL, SSPL,
  dual-license, or enterprise/proprietary carve-out in the root license file.
- `gh api search/code filename:LICENSE` -> exactly 3 license files:
  `LICENSE` (root, MIT), `src/external/APACHE_LICENSE` (Apache-2.0, vendored),
  `src/redteam/providers/crescendo/LICENSE` (MIT, PyRIT-derived). All permissive,
  **no GPL/AGPL/copyleft anywhere**. The user's GPL/AGPL caveat does NOT apply — vendoring
  would be legally permitted, though still not advisable on language-mismatch grounds.
- `license_confirmed: true`, `license_spdx: MIT`.

### Stars — CONFIRMED, no inflation
- `gh api` -> 21,702 stars, 1,911 forks, 304 open issues, created 2023-04-28, last push
  2026-05-29, not archived. Order of magnitude ~2x10^4 (tens of thousands). Matches survey
  exactly. Actively maintained.

### Stack — CONFIRMED TypeScript/Node, NOT Python
- `languages` API: TypeScript 27.3 MB vs **Python only 52 KB** (provider shims/examples,
  not core). `package.json`: `main: ./dist/src/index.js`, `bin: promptfoo/pf`,
  `engines.node ^20.20.0 || >=22.22.0`. It is a Node CLI. Vendoring into our Python/uv
  MLX+API harness is a non-starter on toolchain grounds regardless of the permissive license.

### Reuse-pattern claim — PRESSURE-TESTED against source, holds; gap-overstatement re-confirmed
Read the actual source, not the summary:
- `src/providers/openai/util.ts` `validateFunctionCall()` line 810-812:
  `interpolatedFunctions?.find((f) => f.name === functionName)?.parameters` then
  `throw new Error('Called "${functionName}", but there is no function with that name')`.
  -> promptfoo **DOES** detect a call to a non-existent/undeclared tool. The original
  survey's "cannot detect a call to a non-existent tool" is factually wrong; the prior
  verification's correction is right.
- `src/assertions/functionToolCall.ts` `handleIsValidFunctionCall`: dispatches existence
  validation ONLY for `OpenAiChatCompletionProvider` and Google
  `AIStudio/Live/Vertex` providers; the `else` branch throws
  `Provider does not have functionality for checking function call.` -> **provider-locked**.
  Our Anthropic 4.x / MLX-local / Qwen3 families get NO tool-existence checking out of the
  box. This independently kills "run TEHR through it."
- Confirmed it is single-call schema/existence validation: no tool *registry* abstraction,
  no multi-turn agent loop, no per-call RATE aggregated over a trajectory, no BFCL/tau-bench
  dataset shipped. TEHR-as-a-metric does not exist in promptfoo.
- Red-team module *generates* adversarial inputs / produces remediation *reports*; there is
  no mid-trajectory re-prompt/repair loop -> no RVR analog -> nothing to baseline RVR against.

### Penalty assessment of survey optimism
- Survey's headline verdict (`reuse-pattern` + optional cite) is NOT over-optimistic — it
  correctly says skip-as-benchmark / skip-as-component / skip-as-baseline. No penalty there.
- The ONE over-claim is in the justification prose ("cannot detect a call to a non-existent
  tool"), which over-states the capability gap in OUR favor. Left uncorrected this would be
  a citable factual error a source-reading reviewer could catch. Correct the Related Work
  sentence to: *industry harnesses (e.g. promptfoo) perform single-call, provider-specific
  schema/existence validation of an emitted function call, but expose no
  tool-registry-grounded per-call hallucination RATE over multi-turn agentic trajectories,
  and no intervention/repair mechanism.*

### Structured verdict #2
- repo: promptfoo/promptfoo
- license_spdx: MIT (root, verbatim); vendored Apache-2.0 + MIT subcomponents, all permissive
- recommend: cite-only (secondary/optional prior art) + borrow the `llm-rubric`/`g-eval`
  rubric *shape* (reimplemented in Python) for the paper-revision skill / reviewer personas.
  Do NOT run-as-benchmark, do NOT vendor, do NOT use as RVR baseline.
- confidence: high
- license_confirmed: true
