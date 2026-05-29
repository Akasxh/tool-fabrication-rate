# Repo survey: dottxt-ai/outlines

- **Canonical URL:** https://github.com/dottxt-ai/outlines
- **Category:** constrained-decoding
- **Stars:** 13,902 (gh api, 2026-05-29)
- **License:** Apache-2.0 (SPDX, verified via gh api `.license.spdx_id`)
- **Activity:** active — last push 2026-05-18; latest release **v1.3.0** (2026-05-13). Not archived.
- **Homepage:** https://dottxt-ai.github.io/outlines/

## What it does
Structured-generation library: forces an LLM's decoded output to conform to a
declared shape *during* sampling (logit masking against an FSM/CFG compiled from
the constraint) rather than parsing free text afterward. Output types supported:
- **Multiple choice** via `Literal[...]` / Python enums
- **JSON Schema / Pydantic** models
- **Regex** (`outlines.Regex`)
- **Context-free grammar** (`outlines.CFG`)
- **Function-signature inference** (derive a JSON schema from a Python callable)

v1 API is uniform: `model = outlines.from_<backend>(...)`, then
`model(prompt, output_type=...)`.

## Backends (v1, first-class)
`docs/features/models/` lists: anthropic, gemini, openai, openai_compatible,
openrouter, dottxt (API); transformers, transformers_multimodal, **mlxlm**,
llamacpp (local); vllm, vllm_offline, sglang, tgi, ollama (servers).

**Critical for us:** `outlines.from_mlxlm(*mlx_lm.load("repo"))` wraps the *exact*
objects our `harness/adapters/mlx_adapter.py::_ensure_loaded` already produces
(`mlx_lm.load(model_id)` → `(model, tokenizer)`). Constrained generation is
**not** supported with `batch()`, and requires Apple-Silicon Metal — both fine
for our single-call M5 local tier.

## Concrete fit against our paper

Our TEHR metric counts per-call tool-existence hallucinations on the local tier;
the MLX adapter today does **unconstrained** greedy generation and recovers tool
calls via regex (`_TOOL_CALL_RE`, `_parse_tool_calls`), flagging `parse_ok=False`
on malformed JSON. Outlines is the canonical lever against both failure modes.

### 1. BASELINE / second intervention (PRIMARY value) — med effort
Our `harness/intervention/` already holds `rvr.py`, `naive_retry.py`,
`framework_default.py`, `decoy_list.py`. Outlines adds a *decoding-time*
intervention that RVR (a re-prompt) cannot: constrain the tool **name** field to
`Literal[<registry tool names>]`, making TEHR **structurally 0** on the local
tier. That is a strong, honest baseline contrast — "constrained decoding zeroes
TEHR but at what cost to task accuracy / what happens to the args / does it just
move the error to wrong-but-valid tool selection." This is exactly the
cost-quality-gap framing in the v3 plan. Effort: medium — you must compile the
constraint from the live registry and reconcile it with the Qwen3 chat-template
`<tool_call>{json}</tool_call>` envelope (constrain the inner JSON, or the
name slot within it). The decoding lock in ADDENDUM §D.1 (`temp=0.0`) is
compatible; outlines masks logits, sampler stays greedy.

### 2. COMPONENT reuse in harness — med effort
`outlines.from_mlxlm(*mlx_lm.load(...))` drops into `MLXAdapter._ensure_loaded`
with near-zero glue. A `ConstrainedMLXAdapter` subclass could pass
`output_type=` built from `render_for_mlx(registry)`. Risk: outlines owns the
generate loop, so our token-accounting (`tokenizer.encode` in/out) and
`finish_reason` heuristic need re-wiring to outlines' return type — non-trivial
but bounded. Keep it ADDITIVE (new adapter), do not touch the Qwen path.

### 3. PRIOR ART / RELATED WORK — must-cite
Outlines is *the* reference implementation of FSM-guided constrained decoding
(Willard & Louf, "Efficient Guided Generation for LLMs", arXiv:2307.09702). Our
related-work must position TEHR + RVR against constrained decoding: we measure a
hallucination others *prevent by construction*, and we argue (a) constrained
decoding needs the registry at decode time (white-box, local only — our API
4.x tier can't use it the same way) and (b) it can mask rather than fix the
underlying selection error. Cite alongside guidance / xgrammar / lm-format-enforcer.

### 4. RUN as a standalone benchmark — NO
Not a benchmark; it's a generation library. No datasets/tasks to run.

### 5. PATTERN for paper-revision skill / personas — low value
Nothing reusable for the skill itself beyond a "constrained-decoding reviewer"
persona prompt that asks "why not just constrain decoding?" — a likely real
reviewer question this repo helps us pre-empt. Worth seeding one persona line.

## License risk
Apache-2.0 — permissive, patent grant, compatible with research use and with
vendoring a thin adapter. Low risk. Preserve NOTICE/attribution if code is copied
rather than imported; we should `import outlines` as a dep, not vendor.

## Bottom line
**reuse-pattern → effectively a BASELINE + COMPONENT.** Highest-leverage use is a
constrained-decoding intervention that forces TEHR→0 on the MLX tier, giving a
direct cost-quality-gap contrast to RVR, plus a must-cite related-work anchor.
Medium effort, low license risk.

---

## ADVERSARIAL VERIFICATION (2026-05-29, Akash)

**Method:** independent `gh api` calls + raw LICENSE decode + read of outlines
source (`outlines/models/mlxlm.py`, default branch) + cross-check against
`harness/adapters/mlx_adapter.py`.

### License — CONFIRMED Apache-2.0 (NOT trusting summary)
- `gh api repos/dottxt-ai/outlines .license.spdx_id` → `Apache-2.0`.
- Decoded the actual `LICENSE` blob: header reads "Apache License / Version 2.0,
  January 2004". This is a genuine Apache-2.0, not a mislabeled file.
- **Vendoring verdict:** permissive, patent grant, NOTICE-preservation only.
  Safe to `import outlines` as a dependency AND (if ever needed) to vendor a thin
  adapter with attribution. This is the GOOD case — the task's GPL/AGPL caveat
  does NOT apply here. No copyleft contamination risk for our permissive codebase.

### Stars — CONFIRMED order-of-magnitude (~14k)
- `stargazers_count = 13902` (2026-05-29). Survey said 13,902 — exact match.
  Order of magnitude (10^4) is correct; no inflation.

### Activity — CONFIRMED
- `pushed_at = 2026-05-18`, latest release **1.3.0** (2026-05-13, verified via
  `releases/latest` and `tags`). `archived=false`, `fork=false`. Survey accurate.

### Reuse-pattern pressure test — MOSTLY HOLDS, with two real caveats
1. **`from_mlxlm(*mlx_lm.load(...))` — TRUE.** Source signature is
   `from_mlxlm(model: nn.Module, tokenizer: MLXTokenizer) -> MLXLM`. Our adapter
   already produces exactly `self._model, self._tokenizer = load(self.model_id)`
   (`mlx_adapter.py::_ensure_loaded`), so the unpack is real, not hand-wavy.
2. **"not supported with batch()" — TRUE, verbatim.** `MLXLM.generate_batch`
   raises `NotImplementedError("mlx-lm does not support constrained generation
   with batching")` when `output_type` is set. Fine for us — our local tier is
   single-call (`dispatch` runs one `generate`).
3. **CAVEAT A (survey under-stated the integration cost): token accounting.**
   `MLXLM.generate` returns a bare `str` — no token counts, no finish_reason.
   Our `MLXAdapter.dispatch` builds a `ProviderResponse` with prompt/completion
   token counts (re-`encode` of prompt+raw) and a `"length"` finish-reason
   heuristic keyed off `max_tokens`. A `ConstrainedMLXAdapter` would have to
   re-derive ALL of that around outlines' string return, AND we lose the raw
   text needed for our `_strip_envelopes` / `parse_ok` path unless we keep our
   own parse. The survey called this "non-trivial but bounded" — accurate, but it
   is the single biggest glue cost and should not be under-sold as "near-zero".
4. **CAVEAT B (survey imprecision): "requires Apple-Silicon Metal."** This is not
   an outlines constraint — it is just that `mlx`/`mlx_lm` only run on Apple
   Silicon. Constrained vs unconstrained makes no difference. Harmless but
   slightly misframed as if outlines added a hardware requirement.
5. **API tier (Anthropic 4.x) — outlines CANNOT give us structural TEHR=0 there.**
   Survey is correct: constrained decoding is white-box logit masking, so it only
   applies to the local MLX tier. Outlines DOES ship `from_anthropic`/`from_openai`
   backends, but those delegate to the provider's own JSON/tool-schema modes
   (server-side), NOT FSM logit masking — so the "structurally 0" mechanism does
   not transfer to our API tier. The asymmetry the survey relies on for related
   work is real.

### Claims-check summary
- License: not overstated (genuinely Apache-2.0, vendoring-safe).
- Stars: not overstated (exact).
- Usability/reuse: **mildly over-optimistic on glue cost** (token-accounting
  rewire is the real work) and **one imprecise hardware claim**. Core thesis —
  "use outlines as a decoding-time intervention/baseline that forces local-tier
  TEHR→0, contrast against RVR's re-prompt, must-cite related work" — survives.

### Verdict: include-parts
Use as (a) a **baseline intervention** on the MLX tier (constrain tool-name slot
to `Literal[registry names]` → structural TEHR=0, cost-quality contrast vs RVR)
and (b) a **must-cite related-work anchor** (Willard & Louf, arXiv:2307.09702).
Do NOT run as a benchmark (it has no datasets). Dependency import, not a vendor.
License is the easy part; budget real time for the token-accounting glue.

---

## ADVERSARIAL RE-VERIFICATION (2026-05-29, Opus agent — independent pass)

**Method:** fresh `gh api repos/dottxt-ai/outlines` (metadata + `/license` blob
decode), `WebFetch` of current `main` source for `outlines/models/mlxlm.py` and
`outlines/models/anthropic.py`, cross-read of `harness/adapters/mlx_adapter.py`,
`harness/registry.py`, `harness/intervention/`. Did NOT trust the prior block.

### License — CONFIRMED Apache-2.0 (independent)
- `.license.spdx_id = Apache-2.0`, `.license.key = apache-2.0`.
- Decoded the raw `/license` blob (base64): header is "Apache License / Version
  2.0, January 2004 / http://www.apache.org/licenses/". Genuine, not mislabeled.
- **GPL/AGPL caveat does NOT apply.** This is the permissive case: safe to
  `import outlines` as a dep; vendoring a thin adapter is also legally fine with
  NOTICE/attribution preserved. No copyleft contamination for our codebase. The
  task's "GPL/AGPL → cite/run-external only, do not vendor" warning is moot here.

### Stars — CONFIRMED, NOT inflated
- `stargazers_count = 13902` (2026-05-29). Survey said 13,902 — exact. OOM 10^4.

### Activity — CONFIRMED
- `pushed_at = 2026-05-18T07:38:26Z`; latest release `1.3.0` (2026-05-13 via
  `releases/latest`); `archived=false`, `fork=false`. All accurate.

### Reuse-pattern pressure test — HOLDS, with the prior caveats CONFIRMED + ONE
### MATERIAL CORRECTION to the prior block.
1. **`from_mlxlm(model, tokenizer) -> MLXLM` — CONFIRMED from current source.**
   Our `mlx_adapter.py::_ensure_loaded` does `self._model, self._tokenizer =
   load(self.model_id)` (line 114), so `from_mlxlm(*mlx_lm.load(...))` unpacks
   cleanly. Real, not hand-wavy.
2. **`generate` returns a bare `str` — CONFIRMED** (docstring: "Returns: str").
   So CAVEAT A from the prior block stands and is the dominant glue cost: a
   `ConstrainedMLXAdapter` must re-derive `tokens_in/tokens_out` (currently
   `len(tokenizer.encode(prompt))` / `encode(raw)`, lines 341-342), the
   `_classify_finish` "length" heuristic (lines 361-370), AND keep our
   `_parse_tool_calls`/`_strip_envelopes` path because outlines returns only the
   constrained string. NOT "near-zero glue." Survey §2's "near-zero" wording is
   over-optimistic; the prior block's downgrade to "biggest glue cost" is correct.
3. **`generate_batch` raises `NotImplementedError` under `output_type` —
   CONFIRMED** ("mlx-lm does not support constrained generation with batching").
   Fine: our local tier is single-call.
4. **CORRECTION to prior block caveat #5 (the prior verifier got the mechanism
   wrong).** Prior block claimed outlines' `from_anthropic`/`from_openai` backends
   "delegate to the provider's own JSON/tool-schema modes (server-side)." That is
   FALSE for Anthropic in current `main`. `outlines/models/anthropic.py` raises on
   ANY non-None `output_type`: `AnthropicTypeAdapter.format_output_type` and both
   `generate`/`generate_stream` raise "The output type ... is not available with
   Anthropic"; docstring: "structured generation is not supported by Anthropic ...
   output_type must be None." So outlines provides NO structured-output path on the
   Anthropic tier at all — not even server-side delegation. This makes the
   API-vs-local **asymmetry SHARPER, not weaker**: outlines literally cannot touch
   our Anthropic 4.x tier's TEHR. The survey's related-work thesis is therefore
   strengthened, but anyone citing "outlines structures Anthropic output" would be
   wrong — do not write that.
5. **Hardware framing (prior caveat B) — stands.** Apple-Silicon requirement is an
   `mlx`/`mlx_lm` property, not an outlines one. Cosmetic.
6. **Install state:** `outlines` is NOT currently in the env (no `python`/`pip` on
   PATH — uv-managed project). Adding it is a new dependency; verify it pins a
   compatible `mlx-lm` (our adapter targets `mlx-lm>=0.31.0`). Low risk, just not
   "already available."

### Claims-check summary (this pass)
- License: NOT overstated — genuinely Apache-2.0, vendoring-safe.
- Stars: NOT overstated — exact (13,902).
- Usability/reuse: survey §2 "near-zero glue" is **over-optimistic** (token-
  accounting + parse re-wire is real work). Prior block's Anthropic-backend
  mechanism claim was **wrong** (it raises, doesn't delegate) — corrected above;
  the correction makes the paper's local-vs-API asymmetry argument stronger.
- Core thesis survives on all counts: constrained-decoding baseline that forces
  local-tier TEHR→0 + must-cite related work; no benchmark datasets.

### Verdict: include-parts (CONFIRMED)
(a) Baseline intervention on the MLX tier only — constrain the tool-name slot to
`Literal[registry names]` (built from `harness/registry.py::render_for_mlx`) for
structural TEHR=0; cost-quality contrast vs RVR (`harness/intervention/rvr.py`).
(b) Must-cite related-work anchor (Willard & Louf, arXiv:2307.09702). NOT a
benchmark. Import as a dependency (Apache-2.0, vendoring also permitted), do not
claim it constrains the Anthropic tier. Budget the token-accounting glue, not the
license, as the real cost.
