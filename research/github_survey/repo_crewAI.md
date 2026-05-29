# Repo Survey: crewAI

- **Repo:** crewAIInc/crewAI
- **URL:** https://github.com/crewAIInc/crewAI
- **Stars:** 52,416 (forks: 7,289) — verified via `gh api`, 2026-05-29
- **License:** MIT (SPDX: `MIT`), Copyright (c) 2025 crewAI, Inc. — clean, single-license, no dual/commercial twist in the OSS core
- **Language:** Python (monorepo under `lib/`: `crewai`, `crewai-core`, `crewai-tools`, `crewai-files`, `cli`, `devtools`)
- **Activity:** Actively maintained (last push 2026-05-28). PyPI `crewai`. Author João Moura.
- **Category:** agent-framework

## What it is
A lean multi-agent orchestration framework, explicitly built from scratch (independent of LangChain). Two abstractions:
- **Crews** — role/goal/backstory agents collaborating (sequential or hierarchical) with shared memory and tools.
- **Flows** — event-driven, production-oriented orchestration that can embed Crews.
Plus a commercial "AMP Suite" / Control Plane (hosted observability, integrations) — not part of the OSS repo's runtime.

## Relevance to our paper (TEHR / RVR)
The single most relevant artifact is `lib/crewai/src/crewai/tools/tool_usage.py`. crewAI ships a **production implementation of both halves of our contribution**:

1. **Tool-existence hallucination handling = our RVR intervention.** When an agent emits a tool/action name that does not exist, crewAI:
   - Tries a fuzzy rescue first: `SequenceMatcher(None, sanitized_tool, sanitized_input).ratio() > 0.85` against the registry.
   - On failure, returns an error that **re-injects the full tool registry**:
     `error = f"Action '{tool_name}' don't exist, these are the only available Actions:\n{self.tools_description}"` (and a separate "I forgot the Action name…" variant).
   This is exactly RVR — re-prompt with the tool registry on a bad call. It is a real-world, deployed instance of our intervention and a useful design point to cite/differentiate (they use a hardcoded 0.85 fuzzy threshold + retry; we measure the underlying per-call rate and intervene systematically).

2. **A structured hallucination signal.** It emits `ToolSelectionErrorEvent` (and `ToolValidateInputErrorEvent`) on the event bus with `tool_name`, `agent_role`, available-tools. This is a clean instrumentation pattern: a per-call event we could mirror in our harness to flag/log TEHR events, rather than string-matching model output.

3. `task.increment_tools_errors()` — they track tool-error counts per task, analogous to our per-call rate aggregation.

## Concrete judgments

- **RUN as an extra benchmark? NO.** crewAI is an orchestration framework, not a benchmark/dataset. There is no fixed task suite with ground-truth tool sets comparable to BFCL multi-turn or tau-bench. Building a TEHR benchmark on top of it would be net-new authoring, not "running crewAI."

- **Reuse a COMPONENT in our harness? LOW-VALUE / OPTIONAL.** Our harness already loads BFCL and tau-bench directly and drives MLX + API models; pulling in crewAI's agent loop would add a heavy dependency and obscure per-call measurement. The high-value reuse is the **pattern, not the package** (see below). One narrow option: mirror the `ToolSelectionErrorEvent` shape as our internal TEHR-event record. MIT permits copying the ~30 lines of `_select_tool` logic with attribution. Effort to vendor the whole framework: high and not worth it.

- **Reuse as a BASELINE? YES — as an RVR baseline / point of comparison.** crewAI's fuzzy-match (0.85) + registry-re-injection is a credible "naive deployed RVR" baseline to contrast against our systematic RVR. We can cite it as evidence that (a) tool-existence hallucination is a real production concern frameworks already patch, and (b) current mitigation is ad-hoc (magic threshold, no measurement). Running it head-to-head is optional and effort-heavy; citing + describing its mechanism is low effort and strong.

- **Cite as PRIOR ART? YES, strongly.** 52k-star framework whose tool-dispatch code independently implements RVR-style mitigation is excellent motivation/related-work: it shows the problem matters at scale and that existing solutions are heuristic and unmeasured — which is the gap our TEHR metric + principled RVR fills. Cite the repo + `tool_usage.py` mechanism.

- **Borrow a PATTERN for the paper-revision skill / reviewer personas? PARTIAL / INDIRECT.** crewAI's Crew = role + goal + backstory + collaboration is a clean template for structuring reviewer personas as role-conditioned agents (e.g., "Skeptic reviewer: goal=find unsupported claims, backstory=ICML AC"). It also ships a Claude Code skills plugin (`crewAIInc/skills`) — worth a glance as a packaging reference, not content. Not load-bearing for the metric, but a tidy organizing pattern for multi-persona review.

## Effort & risk
- **License risk: LOW.** Plain MIT. Copying small code snippets or borrowing the RVR/event pattern is safe with attribution. Note: the **AMP/Control Plane is commercial/hosted** and out of scope — stay in the OSS `lib/` tree.
- **Effort: LOW to cite/baseline-describe; HIGH to run head-to-head or vendor the framework.**

## Bottom line
Best value = **prior-art citation + RVR baseline reference**, anchored on `lib/crewai/src/crewai/tools/tool_usage.py` (lines ~740–800), which independently implements our exact intervention as an ad-hoc heuristic. It motivates our work and gives a concrete comparison point. Do not run it as a benchmark; do not vendor it into the harness. Secondary: borrow the role/goal/backstory Crew pattern to structure reviewer personas.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verifier: Claude Code agent. Method: `gh api` for metadata, raw.githubusercontent fetch of `LICENSE` + `tool_usage.py`, `grep -n` on the raw source. Goal: penalize over-optimistic claims and confirm the cite-only recommendation under our MLX+API harness + likely-permissive codebase.

**License — CONFIRMED MIT (SPDX `MIT`).** Read the actual `LICENSE` file verbatim: standard MIT, "Copyright (c) 2025 crewAI, Inc." `gh api ... .license.spdx_id` also returns `MIT`. No GPL/AGPL, no dual-license or commercial twist in the OSS core. The user's copyleft concern does NOT apply: vendoring small snippets (e.g. the ~30-line `_select_tool` logic) into our permissive codebase is permitted with attribution. (Caveat unchanged: the AMP Suite / Crew Control Plane is a separate commercial/hosted product, confirmed in README — stay in the OSS `lib/` tree.)

**Stars — CONFIRMED order-of-magnitude (tens of thousands).** `gh api` returns `stargazers_count: 52416`, `forks_count: 7289`, `archived: false`, `pushed_at: 2026-05-28`. Matches the survey's figures exactly. "~52k-star, actively maintained" stands.

**Code claims — CONFIRMED, all four.** `grep -n` on the live raw source:
- `SequenceMatcher(...).ratio() > 0.85` fuzzy threshold — line 745.
- Registry re-injection error `"Action '{tool_name}' don't exist, these are the only available Actions:\n{self.tools_description}"` — line 758; the empty-name variant `"I forgot the Action name..."` — line 767.
- `ToolSelectionErrorEvent` emitted — lines 761, 770 (imported line 18).
- `increment_tools_errors()` — pervasive, incl. lines 749 in `_select_tool`.
- `_select_tool` defined at line 732; `_validate_tool_input` (where `ToolValidateInputErrorEvent` lives) at line 857. The survey's "lines ~740–800" citation is ACCURATE. Minor survey nuance held up: `ToolValidateInputErrorEvent` is in the input-validation path, not the selection-failure path — the survey correctly attributes it as a separate event.

**Pressure-test of "cite-only / don't run / don't vendor":** Holds up, arguably stronger than stated.
- *Run as benchmark:* CONFIRMED not viable. README/docs show no task suite with ground-truth tool sets; it is an orchestration framework. Nothing to "run" comparable to BFCL/tau-bench.
- *MLX+API harness fit:* crewAI routes LLM calls through LiteLLM. API models (OpenAI/Anthropic) work; local is via Ollama/LM Studio, NOT native MLX. So even if we wanted to drive our MLX models through it, there is an integration gap — additional reason not to run it. Our harness already drives MLX + API directly; crewAI's agent loop would add a heavy dependency and obscure per-call TEHR measurement. Don't-run / don't-vendor-the-framework recommendation is correct.
- *Vendor a component:* Legally fine under MIT (no copyleft block). Value is the PATTERN (the `ToolSelectionErrorEvent` shape + registry-re-injection), not the package. Survey already says this; concur.

**Over-optimism check:** No material overstatement found. Stars/license/activity are accurate, not inflated. The strongest claim — that `tool_usage.py` "independently implements our exact intervention" — is fair but should be framed precisely in the paper: it is a *heuristic, unmeasured* mitigation (hardcoded 0.85 fuzzy match + registry re-prompt with retry), which is exactly the gap our measured TEHR + principled RVR fills. That framing is already in the survey. The `crewAIInc/skills` reference: repo exists but `license: null` (no LICENSE) — treat strictly as a packaging-reference glance, do NOT copy content from it (no license grant). Survey already scoped it as "reference, not content"; fine.

**VERDICT: cite-only (as prior-art + naive-RVR baseline reference). CONFIRMED. license_confirmed=true, MIT. confidence=high.** Recommendation unchanged from survey; the cite-only call is well-supported and the license poses no vendoring risk should we want the ~30-line pattern later.

---

## ADVERSARIAL VERIFICATION #2 (2026-05-29, second independent re-check)

Verifier: Claude Code agent (fresh, did not trust prior sections). Method: `gh api` metadata, raw `LICENSE` verbatim, `grep -n` on live `tool_usage.py`, WebFetch of README, `pyproject.toml` dependency inspection.

**License — CONFIRMED MIT (SPDX `MIT`), no copyleft.** Read `LICENSE` verbatim: standard MIT text, "Copyright (c) 2025 crewAI, Inc." `gh api .license.spdx_id` = `MIT`, `.license.name` = "MIT License". There is NO GPL/AGPL. The user's copyleft scenario does not apply — vendoring the ~30-line `_select_tool` pattern into our permissive codebase is permitted with attribution. (AMP Suite / Crew Control Plane is a separate commercial/hosted product, confirmed in README — out of scope; stay in OSS `lib/` tree.)

**Stars — CONFIRMED order-of-magnitude (tens of thousands).** `gh api` returns 52,416 stars, 7,289 forks, `archived: false`, `pushed_at: 2026-05-28`. Order-of-magnitude (10^4) and "actively maintained" both hold.

**Code claims — CONFIRMED, all load-bearing lines independently re-grepped:** `SequenceMatcher(...).ratio() > 0.85` (line 745), registry re-injection `"Action '{tool_name}' don't exist, these are the only available Actions:\n{self.tools_description}"` (758), empty-name variant `"I forgot the Action name..."` (767), `ToolSelectionErrorEvent` (761, 770), `ToolValidateInputErrorEvent` in the separate input-validation path (920, `_validate_tool_input` at 857), `increment_tools_errors()` pervasive (incl. 749), `_select_tool` at 732. Survey's "~740-800" citation is accurate.

**MLX+API harness fit — CONFIRMED gap, stronger than survey stated.** Independently checked `lib/crewai/pyproject.toml`: LLM routing goes through LiteLLM (`litellm>=1.83.7,<1.84`, as an optional extra); README FAQ lists Ollama/LM Studio for local models. There is NO `mlx` dependency and no native MLX backend. To drive our MLX models through crewAI we would need to bridge MLX behind a LiteLLM-compatible endpoint — net-new integration work that would also obscure per-call TEHR measurement. Reinforces don't-run / don't-vendor-the-framework.

**Run-as-benchmark — CONFIRMED not viable.** No ground-truth tool-set task suite in repo/README; it is an orchestration framework, not a benchmark comparable to BFCL multi-turn or tau-bench.

**Over-optimism audit — NONE found.** Stars, license, activity, and every code citation are accurate, not inflated. The strongest narrative claim (that `tool_usage.py` "independently implements our exact intervention") is fair AND is already correctly framed as a *heuristic, unmeasured* mitigation (hardcoded 0.85 fuzzy threshold + registry re-prompt) — i.e. the gap our measured TEHR + principled RVR fills. The `crewAIInc/skills` repo aside is correctly scoped as packaging-reference-only (no license grant). No survey claim required downgrading.

**VERDICT #2: cite-only. CONFIRMED. license_confirmed=true, SPDX=MIT, confidence=high.** Both the survey and the first adversarial section hold up under independent re-verification. Cite as prior-art + naive-RVR baseline; do not run as a benchmark; do not vendor the framework (MLX integration gap + heavy dependency). Vendoring the ~30-line registry-re-injection pattern later is legally clean under MIT with attribution.
