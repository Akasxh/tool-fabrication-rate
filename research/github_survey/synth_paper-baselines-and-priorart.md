# Synthesis: RVR Baselines + Prior Art — Citation & Comparison Plan

**Scope:** For the SCALE / TEHR paper (per-call Tool-Existence Hallucination Rate on BFCL
multi-turn; Anthropic 4.x = 0 events, Qwen3 4-bit non-monotonic peak 1.87% @ 14B; intervention
= **RVR** = re-prompt with the tool registry on a bad call). This synthesizes the verified
`repo_*.md` + `discover_*.md` surveys into (A) **baselines** to compare RVR against and (B)
**prior art** to cite/differentiate. Every entry cites a specific repo + verified license.
Source files referenced inline as `repo_X.md` / `discover_Y.md` under
`/Users/cero/Desktop/PROJECTS/icml/research/github_survey/`.

**One framing fact that organizes everything below:** RVR's *mechanism* (detect a call to a
tool not in the registry → return an error that re-lists the available tools → model
self-corrects) is **already shipped, default-on, in production frameworks** (LangGraph
`ToolNode`, smolagents `execute_tool_call`, pydantic-ai `ModelRetry`, instructor reask). So the
paper's novelty is **not the intervention** — it is (1) *measuring* the per-call TEHR these
guardrails silently absorb, (2) quantifying RVR's recovery across model families, and (3)
contrasting RVR (black-box, API-compatible, post-hoc) against the constrained-decoding family
(white-box, logit-masking, structurally guarantees TEHR=0 but cannot touch closed APIs). Both
the baseline matrix and the related-work narrative must be built around this.

---

## PART A — BASELINES (intervention arms to compare RVR against)

These are *interventions on a bad/hallucinated tool call*, implemented as sibling functions in
`harness/intervention/` (existing files: `rvr.py`, `naive_retry.py`, `decoy_list.py`,
`framework_default.py`, all pure `(parsed_calls, registry) -> Action`). The comparison axis is:
does the arm reduce TEHR, at what cost (extra calls/tokens = the cost-quality-gap), and on
which tiers (API vs local-MLX) is it even applicable?

Ranked by **value-to-effort** for the ICML main-track table.

### Tier 1 — implement in our own harness (clean-room, no vendoring). Deadline-critical.

| # | Baseline arm | Source / prior art repo | License | Effort | Why it's the right comparison |
|---|---|---|---|---|---|
| **A1** | **Naïve generic reask** ("that was invalid, try again", NO registry) | instructor `567-labs/instructor` (`repo_instructor.md`); also the generic form of LangGraph/smolagents | MIT | trivial (already exists as `naive_retry.py`) | The control that isolates RVR's active ingredient: is it the *retry* or the *registry grounding* that fixes TEHR? Without this arm, a reviewer says "RVR just = retry." |
| **A2** | **Reflexion-style ungrounded self-reflection** (model self-critiques its failed call in free text, then retries — no registry injected) | noahshinn/reflexion (`repo_reflexion.md`, `discover_self_correction___re.md`) | MIT | **<1 hr** (~25-line sibling returning `Action.RE_PROMPT` with a self-reflection prompt) | The *intrinsic*-correction baseline. RVR = grounded reflection; Reflexion-style = ungrounded reflection. Head-to-head on TEHR sharpens the "verifiable feedback beats self-generated lesson" claim. **Do NOT run their repo** (OpenAI-locked, submodules, wrong axis); reimplement the prompt idea natively. |
| **A3** | **Self-Refine-style intrinsic refine** (no external feedback at all) | madaan/self-refine (`discover_self_correction___re.md`) | Apache-2.0 | low | Predicts it should *not* fix tool-existence errors (no registry signal) → motivates why grounding is necessary. Cheap, strengthens the ablation ladder A1→A2→A3→RVR. |
| **A4** | **Decoy-list / distractor-registry** (already present) | our `decoy_list.py` | n/a | exists | Robustness arm: inject near-miss tool names to stress whether RVR's grounding survives registry noise. Pairs with RoTBench (see B-benchmarks). |

> **Ablation ladder for the headline table:** No-intervention → A1 generic reask → A2 ungrounded
> reflection → A3 intrinsic refine → **RVR (grounded reask)** → A5 constrained decoding
> (upper bound, local-only). This single ladder answers every "is RVR just X?" reviewer question.

### Tier 2 — constrained-decoding upper bound (local-MLX/Qwen3 tier ONLY). High value, real glue.

The constrained-decoding family forces TEHR=**0 by construction** (mask the tool-name slot to
`Literal[<registry names>]` / a regex `(toolA|toolB|...)` over the name field). This is the
**structural upper bound** RVR is benchmarked against — but it needs token-level logit access,
so it is **inapplicable to the Anthropic 4.x API tier** (which is already TEHR=0 anyway). That
asymmetry IS the paper's argument for a black-box re-prompt method.

| # | Engine | Repo | License | Effort | Recommendation |
|---|---|---|---|---|---|
| **A5 (primary)** | **Outlines** | dottxt-ai/outlines (`repo_outlines.md`) | Apache-2.0 | **medium** | **Best fit.** `from_mlxlm(*mlx_lm.load(...))` wraps the exact objects our `mlx_adapter.py::_ensure_loaded` already produces. Real cost = re-deriving token accounting + finish_reason + keeping our parse path around outlines' bare-`str` return (the surveys flag "near-zero glue" as over-optimistic — budget this). Import as a dep, do NOT vendor. **Note:** outlines `from_anthropic` *raises* on any `output_type` — it provides NO structured path on the Anthropic tier, which *sharpens* the API-vs-local asymmetry; never claim it constrains Anthropic. |
| A5-alt | lm-format-enforcer | noamgat/lm-format-enforcer (`repo_lm-format-enforcer.md`) | MIT | medium | Backend-agnostic `CharacterLevelParser` + regex/choice mask; no MLX backend → needs a custom MLX logits-processor adapter. README states verbatim it "can not be used with OpenAI ChatGPT and similar API based solutions" → reinforces the asymmetry. Use as the secondary engine if we want a second decode-time data point. |
| A5-alt | guidance | guidance-ai/guidance (`repo_guidance.md`) | MIT | med-high | 21k-star canonical reference, but **no MLX backend and Anthropic backend is in `broken_models/`** → only usable via a llama.cpp/GGUF or vLLM rehost of Qwen3. Off critical path; prefer Outlines for the actual arm, cite guidance in related work. |

> **Pick ONE engine to actually run (Outlines), report its result as "constrained decoding zeroes
> TEHR on the local tier but is API-incompatible and can mask rather than fix the underlying
> wrong-but-valid selection error," and cite the rest (lm-format-enforcer, guidance, XGrammar,
> llguidance, SynCode, AICI) as the family.** Do not burn deadline time wiring three engines.

### Tier 3 — framework "tool-not-found" handling (run as a real-world reference, optional).

These ship the RVR pattern as production defaults. Highest value is as **prior-art citations**
(Part B), but each can optionally be run as an "off-the-shelf guardrail" reference row. Generally
**not worth running** — RVR already *is* this pattern, so a separate run adds little; cite them
as the named real-world instantiation instead.

| Framework | Repo | License | The exact prior-art code | Action |
|---|---|---|---|---|
| LangGraph `ToolNode` | langchain-ai/langgraph (`repo_langgraph.md`) | MIT | `INVALID_TOOL_NAME_ERROR_TEMPLATE` + `_validate_tool_call` (`libs/prebuilt/.../tool_node.py`, verbatim "is not a valid tool, try one of [...]") | **cite-only** (strongest single prior-art for RVR mechanism) |
| smolagents | huggingface/smolagents (`repo_smolagents.md`) | Apache-2.0 | `execute_tool_call`: `raise AgentToolExecutionError(f"Unknown tool {tool_name}, should be one of: {...}")` | **cite-only**; optional scaffold-robustness ablation is **medium-HIGH effort + measurement-validity confound** (MLX path text-parses tool calls → parse misses contaminate TEHR). API-models-first if ever pursued. |
| pydantic-ai | pydantic/pydantic-ai (`discover_agent_frameworks_and.md`) | MIT | first-class `ModelRetry` exception + typed tool registry | **cite-only** (canonical reference impl of the RVR loop) |
| instructor | 567-labs/instructor (`repo_instructor.md`) | MIT | validate→reask→retry loop (`v2/core/retry.py`), re-prompts with the ValidationError | **cite-only** + pattern source for the paper-revision skill; keep OUT of the measurement path (its auto-reask would *suppress* the TEHR events we count). |

---

## PART B — PRIOR ART (cite & differentiate)

### B1. Tool-existence / tool-hallucination measurement — the closest constructs (MUST cite + differentiate)

This is where reviewers will look hardest. We must show TEHR is a *distinct, sharper* construct.

| Repo | License | What they measure | How we differentiate TEHR | Action |
|---|---|---|---|---|
| **ToolBeHonest** (ToolBeHonest/ToolBeHonest, EMNLP 2024) (`repo_ToolBeHonest.md`) | MIT | `non_existent_tools` as a **per-sample raw count** in a 700-item **static** reasoning diagnostic | TEHR = **per-call rate** on **live multi-turn executed** trajectories, **+ an intervention (RVR)** they lack | **cite-only**, baseline-anchor (their GPT-4o 37.0 / Gemini-1.5-Pro 45.3 show frontier-2024 models *do* fabricate tools, contrasting our Anthropic-4.x = 0). Borrow their 6-way error taxonomy as a reviewer-persona rubric. |
| **When2Call** (NVIDIA/When2Call, NAACL 2025) (`discover_tool_function_callin.md`) | Apache-2.0 | "when NOT to call," incl. tool-doesn't-exist; 4-way MCQ (call / ask / can't-answer / hallucinate) | We measure the realized per-call rate in execution, not MCQ choice; we add recovery | **cite + strongly consider run** (closest published analog to our axis; permissive; ships DPO-style negative-example data). |
| **mirage-bench** (sunblaze-ucb, arXiv 2507.21017) (`discover_tool_function_callin.md`) | Apache-2.0 | unified **agentic hallucination** taxonomy (unfaithful to instructions/history/observations) | Frames TEHR as one instance of a broader taxonomy | **cite** for positioning; optionally borrow their snapshot/decision-point isolation idea. |
| **FacTool** / **SelfCheckGPT** (`discover_self_correction___re.md`) | Apache-2.0 / MIT | tool-grounded factuality detection / consistency-based hallucination detection | We detect *tool-existence* errors, not factual claims | **cite** to pre-empt "did you compare against consistency/factuality detectors?" |

### B2. Self-correction / reflection family (cite to position RVR as grounded reflection)

| Repo | License | Role | Action |
|---|---|---|---|
| **Reflexion** (noahshinn/reflexion, NeurIPS 2023, arXiv:2303.11366) (`repo_reflexion.md`) | MIT | canonical verbal-RL / cross-episode reflection | **mandatory cite**; also the source for baseline A2 (reimplemented). |
| **CRITIC** (microsoft/ProphetNet/CRITIC, ICLR 2024) (`discover_self_correction___re.md`) | MIT | "tool-interactive critiquing" — the generic method RVR specializes | **mandatory cite** — closest published analogue; RVR = tool-interactive critiquing specialized to tool-existence errors. |
| **Self-Refine** (madaan/self-refine) (`discover_self_correction___re.md`) | Apache-2.0 | canonical *intrinsic* (no-feedback) correction | cite + baseline A3 (intrinsic vs grounded contrast). |
| **TextGrad** (zou-group/textgrad) (`discover_self_correction___re.md`) | MIT | textual-gradient feedback-driven revision | cite as recent high-star self-correction framework. |
| **ToRA** (microsoft/ToRA) (`discover_self_correction___re.md`) | MIT | tool-integrated reasoning w/ execution-feedback rectification | cite as tool-use-family member (execute→observe→correct). |

### B3. Constrained / guided decoding family (cite as the "prevent-at-decode-time" alternative)

Cite as a cluster to answer the inevitable "why not just constrain decoding?" — answer: needs
white-box logit access, unavailable on closed APIs (Anthropic 4.x), can mask rather than fix the
underlying selection error.

- **Outlines** (Apache-2.0) — Willard & Louf, arXiv:2307.09702 (`repo_outlines.md`). *Also baseline A5.*
- **guidance** (MIT, 21k★) (`repo_guidance.md`)
- **lm-format-enforcer** (MIT) (`repo_lm-format-enforcer.md`)
- **XGrammar** (mlc-ai, Apache-2.0), **llguidance** (guidance-ai, MIT), **SynCode** (uiuc-focal-lab, MIT, soundness/completeness), **AICI** (microsoft, MIT, token-level prompt-editing — closest decode-loop analogue to RVR's re-steer idea) — all from `discover_constrained_decoding.md`.
- **jsonformer** (MIT), **instructor** (MIT) — structured-output (schema, not tool-existence) prior art.

### B4. Benchmarks & eval harnesses we measure on / differentiate from (context citations)

- **gorilla-BFCL** (Apache-2.0) — primary benchmark; cite + run (`repo_gorilla-BFCL.md`). Its `irrelevance_match`/`relevance_match` measure abstention/over-calling, **not** tool-existence — cite as the closest prior metric we differentiate from.
- **tau-bench** (MIT) — primary benchmark; cite + run (`repo_tau-bench.md`).
- **inspect_ai / inspect_evals** (MIT, UK AISI) (`repo_inspect_ai.md`) — already ships a full BFCL port (5-B, 4,981 samples, our exact multi-turn splits incl. `multi_turn_miss_func`) + a tau2 eval under one MIT harness. **Cleanest path to main-track breadth**: run our families through it and overlay our own TEHR computation on the call trace (its `multi_turn_match` is state-based and won't give TEHR for free). Cite + strongly consider as the runner.
- **Run-as-benchmark breadth targets** (per the recommendation table, all permissive): **Seal-Tools** (Apache-2.0), **ToolSandbox** (NOASSERTION — confirm before redistribution), **StableToolBench** (Apache-2.0 — run a cheap **TEHR-only variant**: drive models over its large tool registries, log calls, skip the costly GPT-4 judge + virtual API server; `repo_StableToolBench.md`), **RestGPT** (MIT). Plus optional harder/executable axes from `discover_tool_function_callin.md`: **NESTFUL** (Apache-2.0, nested calls), **ComplexFuncBench** (NO license — cite-only, do not redistribute), **RoTBench** (Apache-2.0, controlled noise levels → natural RVR robustness ablation, pairs with decoy arm A4).
- **Cite-only benchmark context:** ToolBench, API-Bank, MetaTool, AgentBench, ToolEmu, AppWorld, NexusRaven (note: data is CC-BY-NC-4.0 — cite only, never vendor data), ToolACE.
- **Eval-harness context cites:** lm-evaluation-harness, helm, openai-evals, deepeval, promptfoo (`repo_promptfoo.md` — TS/Node, single-prompt assertions, no tool-registry/multi-turn notion → not runnable for our headline; cite-only).

---

## PART C — RECOMMENDED ACTION PLAN (ranked, deadline-aware; 2026-04-28 AoE)

**Deadline-critical (do first):**
1. **Build the intervention ablation ladder** (A1 generic reask, A2 Reflexion-style, A3 Self-Refine-style) as clean-room sibling functions in `harness/intervention/`. Total ~1 day; A2 is <1 hr. Zero vendoring, zero license risk (all MIT/Apache-2.0, reimplemented). This is the single highest-leverage add — it answers "is RVR just retry?" for every reviewer.
2. **Wire ONE constrained-decoding upper bound (A5 = Outlines)** on the local-MLX/Qwen3 tier only. Budget the token-accounting/parse glue (the real cost; surveys flag "near-zero" as over-optimistic). Report TEHR=0 structurally + cost-quality contrast vs RVR + API-incompatibility.
3. **Add ≥1 breadth benchmark beyond BFCL/tau-bench.** Cheapest high-value: **When2Call** (direct unavailable-tool axis, Apache-2.0, ships negative data) and/or a **StableToolBench TEHR-only variant** (large registries = where TEHR should rise; skip the GPT-4 judge). Consider adopting **inspect_evals** as the runner to get BFCL + tau2 + agentic evals under one MIT harness.

**High-value, lower-effort (do in parallel):**
4. Write the **related-work clusters** (B1 measurement, B2 self-correction, B3 constrained decoding, B4 benchmarks). Mandatory cites: ToolBeHonest, Reflexion, CRITIC, Outlines, guidance, LangGraph `ToolNode`, pydantic-ai, instructor.
5. Frame the **novelty pivot** explicitly: RVR's mechanism is industry-standard (LangGraph/smolagents/pydantic-ai ship it); our contribution is *measuring* TEHR + quantifying recovery across families + the API-vs-decode-time asymmetry.
6. Seed **reviewer personas**: (a) "why not just constrain decoding?" (answer: API/black-box, masks selection error); (b) "RVR is just LangGraph `ToolNode`" (answer: yes — we measure what it papers over); (c) ToolBeHonest's 6-way error taxonomy as an adversarial rubric ("you only count non-existent-tool calls; what about wrong-tool/wrong-reasoning?").

**Optional / stretch (only if schedule permits):**
7. Second constrained-decoding engine (lm-format-enforcer) for a 2nd decode-time data point.
8. smolagents/scaffold-robustness ablation — **API-models-first**, with an MLX parser-error audit (MLX text-parsing confounds TEHR). Off critical path.
9. RoTBench noise-level ablation paired with the decoy arm (A4) for an RVR-robustness curve.
10. guidance baseline via llama.cpp/GGUF rehost of Qwen3 — explicitly off the deadline path.

## Licensing guardrails (verified across surveys)
- **Safe to vendor/import (permissive):** all Tier-1/Tier-2 baseline sources and framework prior
  art are MIT or Apache-2.0 (Reflexion, Self-Refine, instructor, LangGraph, smolagents,
  pydantic-ai, Outlines, lm-format-enforcer, guidance) — but our recommendation is **import as
  deps or reimplement, do NOT vendor** (architecture/cleanliness, not license).
- **Cite-only, do NOT redistribute data/code (license gaps):** ComplexFuncBench & mcp-bench (NO
  LICENSE = all-rights-reserved), ToolSandbox (NOASSERTION — confirm), NexusRaven **data**
  (CC-BY-NC-4.0 — non-commercial, never vendor the data).
- The GPL/AGPL copyleft worry raised in the brief **does not trigger anywhere** in the baseline or
  prior-art set — every load-bearing repo verified permissive against its raw LICENSE file.
