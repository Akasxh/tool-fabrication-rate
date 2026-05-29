# Repo survey: letta

- **Repo:** letta-ai/letta (formerly MemGPT)
- **Canonical URL:** https://github.com/letta-ai/letta (live, not 404)
- **Stars:** 23,029 (gh api, 2026-05-29) · last push 2026-05-14 · not archived · Python
- **License:** Apache-2.0 (SPDX `Apache-2.0`, confirmed via `gh api .../license`)
- **Category:** agent-framework
- **Homepage/docs:** https://docs.letta.com/

## What it is
Letta is the open-source agent runtime that grew out of the **MemGPT** paper (Packer et al.,
"MemGPT: Towards LLMs as Operating Systems"). It is a *platform for building stateful agents*:
LLM agents with self-editing long-term memory, persistent state in a Postgres/SQLite-backed
ORM, a tool/function-calling subsystem, and a REST server + ADE (Agent Development Environment).
It is **not a benchmark** and exposes **no native hallucination/eval metric**. It is
infrastructure — model-agnostic (OpenAI/Anthropic/local), with MCP, Composio, and sandboxed
(E2B/Modal/local) tool execution.

## Tool-calling internals relevant to OUR paper (key finding)
Letta's tool layer is the only part directly germane to TEHR:
- `letta/helpers/tool_rule_solver.py` — `ToolRulesSolver.get_allowed_tool_names(available_tools, ...)`.
  Tool rules (`InitToolRule`, `ChildToolRule`, `ConditionalToolRule`, `TerminalToolRule`,
  `ParentToolRule`, `MaxCountPerStepToolRule`, `RequiredBeforeExitToolRule`,
  `RequiresApprovalToolRule`, `ContinueToolRule`) define a per-turn allowed-transition graph.
  Critically it computes `final_allowed_tools = set.intersection(...) & available_tools` —
  i.e. the allowed set is **intersected with the real registry before being offered to the model**.
  This is a *structural prevention* of tool-existence hallucination (the model is only ever
  shown tools that exist + are legal this turn), as opposed to our *detect-and-repair* RVR loop.
- `letta/services/tool_executor/*` — pluggable executors (core/builtin/composio/mcp/files) and
  `tool_execution_helper.py`; sandbox configs (E2B/Modal/local) in `sandbox_config.py`.
- Tool schemas live in a DB ORM (`letta/orm/tool.py`, `schemas/tool.py`) with args-schema,
  pip/npm requirements, parallel-execution flags.

## Concrete reuse verdict
- **RUN as extra benchmark:** NO. It is a runtime, not a benchmark — no tasks, no scorer, no
  TEHR. Running it would mean building our own task suite on top, which is out of scope.
- **Reuse COMPONENT in our harness:** LOW value / skip. Our harness is a lightweight
  benchmark loader + runner (`harness/bench_loaders/*.py`, MLX + API models). Letta is a
  heavyweight stateful server (Postgres, ORM, alembic migrations, REST API). Adopting any
  module would drag in the whole stack. The `tool_rule_solver` logic is small and conceptually
  reusable but we would re-implement the idea, not import the package.
- **Use as BASELINE:** POSSIBLE but secondary. Letta's `ToolRulesSolver` is a credible
  **prevention baseline** to contrast against RVR: "constrain the offered tool set so the model
  *cannot* name a nonexistent tool" vs. our "let it err, then re-prompt with the registry." If
  reviewers ask why we repair instead of constrain, citing Letta/tool-rules as the
  constrain-side alternative (and noting it presupposes a fixed, server-managed registry the
  model can't deviate from) is a clean differentiation. Implementing it as a runnable baseline
  in our harness is MED effort and arguably unnecessary; describing it suffices.
- **CITE as PRIOR ART:** YES. Cite **MemGPT (Packer et al.)** for stateful/self-editing-memory
  agents and Letta as its production lineage when situating agent frameworks and tool-governance
  approaches. Use it to frame the prevention-vs-repair axis around tool-existence errors.
- **PATTERN for paper-revision skill / reviewer personas:** MARGINAL. The transferable concept
  is the **tool-rule state machine** (allowed-transition graph intersected with the real
  registry) — a useful talking point for a reviewer persona that asks "why repair instead of
  prevent?" No code reuse for the skill itself.

## Effort & license risk
- **License risk: LOW.** Apache-2.0, permissive (patent grant included). Safe to cite and, if
  ever needed, to vendor a small reimplementation with attribution + NOTICE retention.
- **Effort: HIGH** to integrate as software (stateful server stack); **LOW** to cite as prior
  art; **MED** to stand up a constrain-the-registry baseline inspired by `tool_rule_solver`.
- **Watch-outs:** (1) Don't confuse Letta (framework) with a benchmark — it yields no comparable
  TEHR number. (2) Its tool registry is server-managed/DB-backed, so its "no hallucination
  possible" property is by construction and not a fair head-to-head with a free-form
  function-calling model on BFCL/τ-bench — disclose that asymmetry if cited as a baseline.

## Adversarial verification (2026-05-29, independent re-check)
Verified the survey's load-bearing claims from primary sources, not the summary.

- **LICENSE — CONFIRMED `Apache-2.0` (SPDX), standard/unmodified.** Two independent sources:
  (1) `gh api repos/letta-ai/letta/license` → `{"spdx":"Apache-2.0","name":"Apache License 2.0","path":"LICENSE"}`;
  (2) raw `LICENSE` file at main → standard ASF header "Apache License / Version 2.0, January 2004",
  no exceptions/modifications, copyright "Letta authors (2023)". The survey's `Apache-2.0` claim is
  ACCURATE. NOT GPL/AGPL — so vendoring a small reimplementation with attribution + NOTICE is legally
  permissible (permissive + patent grant). No copyleft contamination risk for our permissive codebase.
- **STARS — CONFIRMED order of magnitude.** `gh api repos/letta-ai/letta` → `stargazers_count: 23029`
  (~23k, 10^4). Survey's "23,029" matches exactly. Not archived (`archived:false`), not a fork,
  `pushed_at: 2026-05-14`, Python. All accurate and current.
- **TOOL-RULES INTERNALS — CONFIRMED.** `tool_rule_solver.py` does contain `ToolRulesSolver` with
  `get_allowed_tool_names`; the registry intersection `final_allowed_tools = final_allowed_tools & available_tools`
  is real and present in the rule-based pathway, plus a second `set(allowed) & available_tools` for the
  init pathway, with an `error_on_empty=True` default that raises `ValueError` on empty allowed set.
  All nine tool-rule types the survey lists are present. The "structural prevention" framing is fair.

### Where the survey is slightly OVER-OPTIMISTIC / needs caveats
1. **"Structural prevention" is conditional, not global.** The intersection only constrains the offered
   set when tool rules are actually configured for the agent. A vanilla Letta agent with no tool rules
   defined does not get this guarantee by this code path — so it is NOT a blanket "Letta cannot hallucinate
   tools" property. Disclose this if cited as a prevention baseline.
2. **A leaderboard exists (leaderboard.letta.com).** This is a model-ranking leaderboard, NOT a runnable
   eval suite shipped in-repo and NOT a TEHR-comparable benchmark. The survey's "not a benchmark / no
   native eval metric" verdict still holds, but a reviewer skimming the repo could mistake the leaderboard
   for an eval harness — name it explicitly to avoid that.

### "cite-only" pressure-test vs. our MLX+API harness
- **Can we RUN it externally?** Yes, but heavyweight: Docker + Postgres + alembic migrations + REST server.
  It is model-agnostic (OpenAI/Anthropic/local) so our API models would connect, but it is a stateful
  server, not a benchmark runner. It produces NO TEHR number. Running it buys us nothing comparable.
- **Can we VENDOR/reuse code into our harness?** License permits it (Apache-2.0), but it is the wrong
  shape: our harness is a lightweight `bench_loaders/*.py` + MLX/API runner. Importing the package drags
  the server stack; the only germane logic (`tool_rule_solver`) is ~70 lines of set algebra we would
  re-implement as a "constrain-the-registry" baseline, not import.
- **VERDICT: cite-only is the CORRECT primary call** (cite MemGPT/Packer et al. as prior art + Letta as
  its lineage; frame the prevention-vs-repair axis). Optionally implement a small constrain-the-offered-set
  baseline *inspired by* tool_rule_solver (MED effort) — but that is a re-implementation, not reuse of
  Letta itself. The license is genuinely permissive (no copyleft flag needed). Confidence: HIGH.

## Adversarial re-verification #2 (2026-05-29, independent, primary-source)
Re-ran the three load-bearing checks from primary sources (did NOT trust the prior verification block above).

- **LICENSE — CONFIRMED `Apache-2.0` (SPDX), standard & UNMODIFIED.** Two independent sources:
  (1) `gh api repos/letta-ai/letta/license` → `{"spdx":"Apache-2.0","name":"Apache License 2.0","path":"LICENSE"}`;
  (2) raw `LICENSE` at main → "Apache License / Version 2.0, January 2004", copyright "2023, Letta authors",
  no added exceptions / commercial clauses / non-standard terms. NOT GPL/AGPL — no copyleft contamination
  risk. Vendoring a small reimplementation into our permissive harness is legally fine (attribution + NOTICE).
  The survey is ACCURATE here; no over-optimism.
- **STARS — CONFIRMED ~23k (10^4).** `gh api repos/letta-ai/letta` → `stargazers_count: 23029`, matches
  survey exactly. `archived:false`, `fork:false`, `language:Python`, `pushed_at:2026-05-14T17:14:23Z`. Current.
- **TOOL-RULES INTERNALS — CONFIRMED.** `letta/helpers/tool_rule_solver.py` (raw, main) defines
  `ToolRulesSolver.get_allowed_tool_names` with `final_allowed_tools = final_allowed_tools & available_tools`
  and `error_on_empty: bool = True` raising `ValueError("No valid tools found based on tool rules.")`. All
  nine listed rule types present. "Structural prevention" framing is fair.

### Adversarial pressure on the survey's claims
- **Stars/license/usability NOT overstated.** If anything the survey is appropriately cautious: it does not
  inflate Letta into a benchmark, correctly calls it a runtime, and correctly flags the prevention asymmetry.
- **Two real caveats stand (already noted by prior block, re-affirmed):** (1) the intersection only guarantees
  "can't name a nonexistent tool" WHEN tool rules are configured — a vanilla agent with no rules does not get
  this guarantee by this path, so it is NOT a blanket property; (2) leaderboard.letta.com is a model-ranking
  leaderboard, NOT an in-repo runnable eval suite and NOT TEHR-comparable.

### "cite-only" pressure-test vs. OUR MLX+API harness — does it survive?
- **Run/reuse reality:** Letta is model-agnostic (OpenAI/Anthropic/local), so our API models WOULD connect, but
  it is a heavyweight stateful server (Postgres + alembic + REST), not a benchmark runner. It emits NO TEHR
  number on BFCL/τ-bench. Running it yields nothing head-to-head comparable. Vendoring the package would drag
  the whole server stack into a lightweight `bench_loaders/*.py` + MLX/API harness — wrong shape, even though
  the license permits it. The only germane logic is ~70 lines of set algebra we'd re-implement, not import.
- **VERDICT: cite-only is the CORRECT primary call** (cite MemGPT/Packer et al. as prior art + Letta as its
  production lineage; frame the prevention-vs-repair axis). Optional MED-effort: a "constrain-the-offered-set"
  baseline INSPIRED BY tool_rule_solver — a re-implementation, not reuse of Letta. License permissive; no
  copyleft flag. Confidence: HIGH.
