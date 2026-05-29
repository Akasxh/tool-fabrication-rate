# BASELINES COVERAGE — Tool-Existence Hallucination (TEHR / Tool Fabrication Rate) vs RVR

**Purpose.** One consolidated table of every method that *reduces* tool-call fabrication (an LLM
agent naming a tool absent from the provided registry), classified into the five requested
families, with repo (stars, license), mechanism, and a **RUN-vs-CITE** decision for our harness
(`harness/intervention/` pure functions `(parsed_calls, registry) -> Action`; distractor probe
removes the real tool + injects a look-alike; per-call **TFR / TEHR** = calls naming a tool not in
the registry; MLX-local Qwen3 4-bit + Anthropic/OpenAI API tiers).

**Builds on (do not re-derive):** `synth_paper-baselines-and-priorart.md` (Parts A/B/C),
`INTEGRATION_PLAN.md` §(b) baselines + §(c) cites, `discover_constrained_decoding.md`. This file
**adds** the training-time / detection-time literature the prior synths missed (Fission-GRPO,
Relign, SimpleToolHalluBench / "Reasoning Trap", internal-representation probes, NabaOS receipts)
and resolves the final RUN list + integration sketch.

**Organizing fact (carried over, still the spine of the argument):** RVR's *mechanism* — detect a
call to an absent tool → return an error that re-lists available tools → model self-corrects —
**already ships, default-on, in production frameworks** (LangGraph `ToolNode`, smolagents, pydantic-ai,
instructor). Novelty is not the intervention; it is (1) *measuring* the per-call TFR these guardrails
silently absorb, (2) quantifying recovery across model families, (3) the **black-box-API vs
white-box-decode-time asymmetry**: constrained decoding makes TFR=0 *by construction* but needs
logit access, so it cannot touch closed Anthropic/OpenAI. **RVR is the black-box-API analog of
constrained decoding.**

---

## BASELINES COVERAGE TABLE

Legend — **Targets existence?** Y = method specifically prevents/measures calling a *nonexistent*
tool; A = adjacent (wrong-but-valid tool, params, or general execution errors). **RUN?** effort to
wire into our harness, or `cite-only`.

### Family 1 — Constrained / guided decoding (structural TFR=0 on open weights; the "upper bound")

| Method | Repo (stars, license) | Mechanism | RUN? | Comparison vs RVR | Targets existence? |
|---|---|---|---|---|---|
| **Outlines** | `dottxt-ai/outlines` (13.9k, Apache-2.0) | Automaton + precomputed token masks; constrain tool-name slot to `Literal[registry]` | **RUN — primary upper bound (med)** | Structural TFR=0 on MLX/Qwen3; `from_anthropic` *raises* on `output_type` → API-incompatible. The asymmetry IS RVR's reason to exist. | **Y** (by construction) |
| **XGrammar** | `mlc-ai/xgrammar` (~1.7k, Apache-2.0) | Byte-level pushdown automaton + adaptive mask cache; default backend of vLLM/SGLang/TRT-LLM/MLC | cite (family); optional 2nd engine | Same structural-0 point via a different engine; Apple-Silicon path exists | Y |
| **llguidance** | `guidance-ai/llguidance` (~0.8k, MIT) | Earley-parser CFG, ~50µs/token, no startup cost; core behind OpenAI Structured Outputs & Guidance | cite | "fast-forward tokens" = clean cost contrast to RVR's re-prompt overhead | Y |
| **lm-format-enforcer** | `noamgat/lm-format-enforcer` (MIT) | `CharacterLevelParser` choice/regex mask; backend-agnostic | cite (opt. 2nd engine, needs MLX logits-proc adapter) | README states verbatim it cannot be used with API solutions → reinforces asymmetry | Y |
| **guidance** | `guidance-ai/guidance` (~21k, MIT) | Grammar/regex constrained gen | **cite-only** | No MLX backend; Anthropic backend in `broken_models/` → off critical path | Y |
| **transformers-CFG** | `epfl-dlab/transformers-CFG` (~140, MIT) | EBNF grammar as drop-in HF `LogitsProcessor` | cite (lowest-friction in-harness alt to Outlines) | Cleanest "tool-registry-as-grammar" in our HF/MLX path; EMNLP-2023 backed | Y |
| **SynCode** | `uiuc-focal-lab/syncode` (~330, MIT) | Offline DFA mask store, provable soundness+completeness | cite-only | Theory anchor for "structural error cannot occur"; motivates why API models still need RVR | Y |
| **Formatron** | `Dan-wanna-M/formatron` (~240, MIT) | Pydantic/JSON-schema → low-overhead constraint, HF integ. | cite-only | Design note on not over-constraining = cost-quality-gap discussion | Y |
| **AICI** | `microsoft/aici` (~2.0k, MIT) | Wasm controllers: constrained decode + dynamic prompt editing per token | cite-only | Closest *decode-loop* analogue to RVR's "intervene + re-steer" idea | Y |

### Family 2 — Self-correction / reflection (re-prompt-style; closest method-class to RVR)

| Method | Repo (stars, license) | Mechanism | RUN? | Comparison vs RVR | Targets existence? |
|---|---|---|---|---|---|
| **Reflexion** | `noahshinn/reflexion` (NeurIPS'23, MIT) | Verbal self-reflection on failure, stored as memory, retry | **RUN — A2 (reimplement, <1 hr)** | *Ungrounded* reflection (no registry) vs RVR *grounded* reask → "verifiable feedback beats self-generated lesson". Don't run their repo (OpenAI-locked); reimplement prompt. | A |
| **Self-Refine** | `madaan/self-refine` (Apache-2.0) | Intrinsic feedback→refine, no external signal | RUN — A3 (low) | Predicts it should *not* fix existence errors (no registry signal) → motivates grounding | A |
| **CRITIC** | `microsoft/ProphetNet/CRITIC` (ICLR'24, MIT) | Tool-interactive critiquing — model verifies via external tools | **cite (mandatory)** | RVR = tool-interactive critiquing specialized to tool-existence | A |
| **ToRA** | `microsoft/ToRA` (MIT) | Tool-integrated reasoning w/ execution-feedback rectification | cite-only | Execute→observe→correct family member | A |
| **TextGrad** | `zou-group/textgrad` (MIT) | Textual-gradient feedback-driven revision | cite-only | Recent high-star self-correction framework | A |

### Family 3 — Framework-level tool-not-found handling (RVR mechanism already in production)

| Method | Repo (stars, license) | Mechanism (the exact prior-art code) | RUN? | Comparison vs RVR | Targets existence? |
|---|---|---|---|---|---|
| **LangGraph `ToolNode`** | `langchain-ai/langgraph` (MIT) | `INVALID_TOOL_NAME_ERROR_TEMPLATE` + `_validate_tool_call`: verbatim "is not a valid tool, try one of [...]" | **cite (strongest single prior-art)** + RUN as C0.7 approx | This *is* RVR; we measure what it papers over. Our `framework_default.py` (C0.7) approximates its structured-error path (no registry list). | **Y** |
| **smolagents** | `huggingface/smolagents` (Apache-2.0) | `execute_tool_call`: `raise AgentToolExecutionError(f"Unknown tool {name}, should be one of: {...}")` | cite-only | Off-the-shelf guardrail; MLX text-parse confounds TFR if run as scaffold | **Y** |
| **pydantic-ai** | `pydantic/pydantic-ai` (MIT) | First-class `ModelRetry` exception + typed tool registry | cite-only | Canonical reference impl of the RVR loop | **Y** |
| **instructor** | `567-labs/instructor` (MIT) | validate→reask→retry (`v2/core/retry.py`) re-prompts with `ValidationError` | cite + pattern source for A1 | Keep OUT of measurement path (auto-reask would suppress the TFR events we count) | A (schema) |

> C0.7 (`framework_default.py`) already exists and approximates the LangGraph structured-error
> path. Running it as a real arm is **low-cost and high-value**: it isolates "structured error
> *without* the registry list" between C0.5 naive-retry and C1 RVR — the cleanest evidence that the
> *registry render*, not merely a structured error envelope, is RVR's active ingredient.

### Family 4 — Retrieval / grounding-based tool selection

| Method | Repo (stars, license) | Mechanism | RUN? | Comparison vs RVR | Targets existence? |
|---|---|---|---|---|---|
| **Tool retrieval / RAG-for-tools** (ToolBench API-Retriever, Gorilla retriever-aug, Seal-Tools retrieval) | various (Apache-2.0 / cite-only data) | Retrieve a small candidate tool set per query → model only sees valid names | cite (positioning) | Orthogonal *prevention*: shrink the registry so fabrication is less likely. RVR is *post-hoc correction* and composes with it. Note: Seal-Tools per-query-candidate vs full-registry is already our planned registry-size ablation (does registry size drive TFR?). | A (reduces, not eliminates) |
| **Relign indecisive actions (`ChangeTools`)** | `X-LANCE/ToolHallucination` (see Family 5) | Adds an explicit "switch/defer tool" action to the action space | cite | Grounding-by-abstention; RVR grounds by re-listing | Y (selection) |

### Family 5 — Training-time methods (orthogonal; cite, do NOT run)

| Method | Repo (stars, license) | Mechanism | RUN? | Comparison vs RVR | Targets existence? |
|---|---|---|---|---|---|
| **Fission-GRPO** (ACL 2026, arXiv:2601.15625) | no public repo at survey time; paper CC-BY-4.0 | RL: "fission" each failed trajectory into a new training instance w/ Error-Simulator diagnostic feedback; fixes GRPO zero-variance gradients | **cite (NEAR-TWIN — high priority)** | **Same axis as us:** BFCL v4 Multi-Turn + tau-bench + tau2, **Qwen3-8B**, recovery-rate metric, explicitly contrasts **Claude Sonnet 4 ~50% recovery vs Qwen3-8B ~20%**. Train-time vs our inference-time RVR. Must position: RVR is the *zero-training, API-compatible, black-box* recovery method; Fission-GRPO is the weights-side counterpart. | A (execution errors, incl. recovery) |
| **Relign / RelyToolBench** (ICML 2025, arXiv:2412.04141) | `X-LANCE/ToolHallucination` (Apache-2.0) | SFT+DPO over an expanded action space (`ChangeTools`, `TalkToUser`); RelyToolBench scores hallucination-aware success | **cite (mandatory — canonical reliability-alignment)** | Splits hallucination into *selection* vs *usage*; we measure *existence* per-call + add a black-box fix. Their RelyToolBench metrics = a related but training-coupled construct. | **Y** (tool selection) |
| **"The Reasoning Trap" / SimpleToolHalluBench** (arXiv:2510.22977) | benchmark; check repo on publication | Shows RL/SFT reasoning gains *amplify* tool hallucination; diagnostic bench with "(i) no tool available, (ii) only distractor tools available" | **cite (HIGHLY relevant) + consider as breadth bench** | Its two conditions are **exactly our distractor probe** (real tool removed / look-alike injected). Finding "reducing hallucination degrades utility" is precisely our cost-quality-gap. Strong external validation of the phenomenon. | **Y** |
| **Internal-representation probes** (arXiv:2601.05214) | research code on publication | White-box: probe internal activations to predict tool-selection hallucination *before* the call | cite-only | White-box *detector* (needs activations) vs RVR black-box *corrector*; same family-asymmetry argument as constrained decoding | **Y** |
| **NabaOS / Tool-Receipts** (arXiv:2603.10060, Mar 2026) | Rust impl + NyayaVerifyBench, "to be released" (URL withheld for anon review) | Execution-side HMAC-signed tool receipts; unforgeable; flags references to nonexistent calls (94.2% detection) | cite-only | Cryptographic *post-execution* fabrication *detection* (claims about calls), not pre-call existence correction; complementary | **Y** (fabricated references) |
| **ToolACE** (arXiv:2409.00920) | `Team-ACE/ToolACE` (Apache-2.0; data Apache) | Self-evolving synthesis + dual-layer verification for FC training data | cite-only | In-distribution FC specialist; ToolACE-2-8B optionally an inference-only model baseline (BFCL ships its handler) but near-zero BFCL TFR is partly in-distribution | A |

### Measurement prior-art anchors (not interventions; cite to differentiate the metric)

| Bench | Repo (license) | What it measures | Differentiation |
|---|---|---|---|
| **ToolBeHonest** | `ToolBeHonest/ToolBeHonest` (EMNLP'24, MIT) | `non_existent_tools` as per-sample raw count, 700-item **static** diagnostic; GPT-4o 37.0 / Gemini-1.5-Pro 45.3 | We do **per-call rate** on **live multi-turn executed** trajectories + an intervention; baseline-anchor showing frontier-2024 models DO fabricate vs our Anthropic-4.x = 0 |
| **When2Call** | `NVIDIA/When2Call` (NAACL'25, Apache-2.0) | 4-way MCQ incl. tool-doesn't-exist; ships DPO negative data | We measure realized per-call rate in execution, add recovery; **+consider run** |
| **mirage-bench** | `sunblaze-ucb` (arXiv:2507.21017, Apache-2.0) | Unified agentic-hallucination taxonomy | Frames TFR as one instance of a broader taxonomy |

---

## RECOMMENDED RUN LIST (3–5 to actually run as baselines)

The harness already has `rvr.py` (C1), `naive_retry.py` (C0.5), `framework_default.py` (C0.7),
`decoy_list.py` (A4). The ablation ladder to report:

> **No-intervention → C0.5 naive reask → C0.7 framework-default structured error → A2 ungrounded
> reflection → A3 intrinsic refine → C1 RVR (grounded reask) → A5 constrained decoding (structural
> upper bound, MLX-only).**

**RUN these:**

1. **C0.5 naive reask** — *exists* (`naive_retry.py`). Isolates retry-alone. Keep.
2. **C0.7 framework-default structured error** — *exists* (`framework_default.py`). The
   LangGraph `ToolNode` analog: structured `tool_not_found` envelope **without** the registry list.
   Sits between naive-retry and RVR; the single cleanest control proving the *registry render* is the
   active ingredient, not the envelope. **Run as a first-class arm.**
3. **A2 Reflexion-style ungrounded reflection** — **new sibling, <1 hr.** RVR = grounded reflection;
   A2 = ungrounded. Head-to-head sharpens the headline claim.
4. **A3 Self-Refine-style intrinsic refine** — **new sibling, low.** No external feedback; predicted
   to *not* fix existence errors → motivates grounding. (Optional if schedule tight; A2 carries the
   reflection contrast.)
5. **A5 Outlines constrained decoding** — **new adapter, med, MLX/Qwen3 ONLY.** Structural TFR=0
   upper bound. Report: zeroes TFR locally, API-incompatible, can *mask* rather than *fix* the
   underlying wrong-but-valid selection. **Honest framing: RVR is the black-box-API analog of this.**

If forced to 3: **C0.7, A2, A5** (each answers a distinct reviewer: "registry vs envelope?",
"is RVR just reflection?", "why not constrain decoding?"). C0.5 is free (exists).

### Integration sketch — new sibling pure functions in `harness/intervention/`

All match the existing signature `(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action`
and reuse `Action / ActionKind / ToolCall` from `harness.types`. A2/A3 differ from RVR/C0.7 only in
the feedback string (no registry list rendered) — same control-flow skeleton as `rvr.py`.

```python
# harness/intervention/reflexion_style.py   (A2 — ungrounded self-reflection)
"""Reflexion-style ungrounded reflection (A2). Clean-room reimpl of the
verbal-self-reflection prompt idea (Shinn et al. 2023); NO registry rendered.
Contrast arm: RVR = grounded reflection, A2 = ungrounded."""
from harness.types import Action, ActionKind, ToolCall

_REFLEXION_FEEDBACK = (
    "Your previous tool call did not succeed. Reflect on what went wrong "
    "in your reasoning, write a short self-critique, then choose your next "
    "action."
)  # deliberately omits the registry — that omission is the experiment

def reflexion_style(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action:
    if not parsed_calls:
        return Action(kind=ActionKind.EXECUTE, tool_call=None)
    for call in parsed_calls:
        if call.name not in registry:
            return Action(kind=ActionKind.RE_PROMPT, feedback=_REFLEXION_FEEDBACK)
    return Action(kind=ActionKind.EXECUTE, tool_call=parsed_calls[0])
```

```python
# harness/intervention/self_refine.py   (A3 — intrinsic refine, no external signal)
_SELF_REFINE_FEEDBACK = (
    "Review your previous tool call. Identify any problem with it and produce "
    "an improved version."
)  # no failure label, no registry — pure intrinsic refinement
# ...identical skeleton; RE_PROMPT with _SELF_REFINE_FEEDBACK on absent name.
```

```python
# harness/intervention/constrained.py   (A5 — Outlines, MLX/Qwen3 only)
# NOT a (parsed_calls, registry)->Action arm — it acts at *decode time*, so it
# lives in the adapter layer, not as a post-hoc Action. Wire a
# ConstrainedMLXAdapter that wraps outlines.from_mlxlm(*mlx_lm.load(...)) and
# constrains the tool-name field to Literal[*sorted(registry)] (or regex
# (toolA|toolB|...)). By construction call.name in registry always holds → TFR=0.
#
# REAL COST (under-stated in prior synths): outlines MLXLM.generate returns a
# bare str — re-derive tokens_in/out via tokenizer.encode, a length-based
# finish_reason heuristic, and keep the existing _parse_tool_calls path. Keep
# ADDITIVE: do NOT touch the Qwen3 path that produced the published numbers.
# from_anthropic raises on any output_type → no API tier (that is the point).
```

Register A2/A3 in the intervention dispatch exactly like `rvr`/`naive_retry`; A5 is selected as an
adapter variant on the MLX tier. Rerun **RVR + the full ladder on every new benchmark split** so the
claim generalizes beyond BFCL multi-turn.

---

## METHODS THAT WOULD BEAT (OR OUT-SCOPE) RVR — honest flags

- **Constrained decoding (Outlines/XGrammar/llguidance/SynCode) → structural TFR = 0 on open
  weights.** This strictly beats RVR's empirical reduction *on the local tier*. The honest framing
  (already the paper's spine): it requires token-level logit access, so it is **unavailable on closed
  Anthropic/OpenAI APIs** — where, notably, Anthropic 4.x is already TFR≈0 without it. **RVR is the
  black-box-API analog of constrained decoding**: same goal (only-valid names), achievable without
  logits. Report A5 as the upper bound and own that it dominates locally; the contribution is the
  API-compatible regime + the measurement.
- **Internal-representation probes (2601.05214)** can *detect* fabrication before the call, but are
  white-box (need activations) — same asymmetry; complementary detector, not a black-box corrector.
- **NabaOS receipts (2603.10060)** detect 94.2% of fabricated tool *references* cryptographically,
  but post-execution and execution-side — a detector for a different surface (claims about calls), not
  a pre-call existence fix. Does not beat RVR on our axis; cite as complementary.
- **Fission-GRPO / Relign** improve the *base model's* recovery via training; on a model so trained,
  the residual TFR (and thus RVR's headroom) shrinks. They are orthogonal (weights-side) and require
  training we explicitly do not do — cite as the training-time counterparts, do not run.

---

## CITE-ONLY LIST (coverage, no run)

- **Constrained decoding family:** guidance, XGrammar, llguidance, lm-format-enforcer,
  transformers-CFG, SynCode, Formatron, AICI, jsonformer.
- **Self-correction family:** CRITIC (mandatory), ToRA, TextGrad, Self-Refine (cite + optional A3).
- **Framework prior art:** LangGraph `ToolNode` (mandatory, strongest single prior-art), smolagents,
  pydantic-ai, instructor.
- **Training-time / detection (NEW this pass):** Fission-GRPO (ACL'26 — near-twin, mandatory cite),
  Relign / RelyToolBench (ICML'25 — mandatory), "Reasoning Trap"/SimpleToolHalluBench (2510.22977 —
  highly relevant, consider as breadth bench), internal-representation probes (2601.05214), NabaOS /
  Tool-Receipts (2603.10060), ToolACE.
- **Measurement anchors:** ToolBeHonest (mandatory differentiation), When2Call (+consider run),
  mirage-bench, FacTool, SelfCheckGPT.
- **Retrieval/grounding:** tool-retrieval / RAG-for-tools (ToolBench retriever, Gorilla retriever-aug,
  Seal-Tools candidate-set) — cite as orthogonal prevention; Seal-Tools candidate-vs-full registry is
  our registry-size ablation.

## LICENSING (all RUN/vendor candidates verified permissive)

- **Vendor/import safe (MIT/Apache-2.0):** Outlines (Apache-2.0), all reflection arms reimplemented
  clean-room (Reflexion MIT, Self-Refine Apache-2.0). C0.5/C0.7 are our own code. No GPL/AGPL/NC
  anywhere in the RUN set.
- **Import-as-dep only (do not vendor source):** outlines + mlx_lm.
- **Cite-only, never vendor data/code:** Fission-GRPO (no repo yet; paper CC-BY-4.0 — cite fine),
  NabaOS (repo withheld), NexusRaven data (CC-BY-NC-4.0), ComplexFuncBench/mcp-bench (no license).
- Relign code (`X-LANCE/ToolHallucination`, Apache-2.0) is vendorable if we ever want its
  RelyToolBench splits, but recommendation is **cite-only** (training-coupled construct).

**Confidence:** HIGH on the existing-survey content (licenses read from raw files in prior passes);
MEDIUM on the four new arXiv items' repo/license (papers very recent; no public repos confirmed at
survey time — flagged cite-only for that reason).
