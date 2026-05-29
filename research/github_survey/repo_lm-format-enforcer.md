# Repo Survey: lm-format-enforcer

- **Repo:** noamgat/lm-format-enforcer
- **URL:** https://github.com/noamgat/lm-format-enforcer (valid, not 404)
- **Stars:** 2,015 (via `gh api`, 2026-05-29)
- **License:** MIT (SPDX: MIT) — permissive, no risk for citing/reusing
- **Archived:** No. Last push 2026-04-04 (actively maintained)
- **Category:** constrained-decoding

## What it does
Token-level constrained decoding. Enforces LM output to match a target format
(JSON Schema, schemaless JSON mode, or regex) by filtering the permissible token
set at every generation step.

Mechanism: a character-level parser builds an implicit tree of allowed next
characters for the format; a tokenizer prefix tree maps token sequences to
characters. At each step it intersects the two trees and masks logits to only
tokens valid in both. This is the same "logit-mask / guided decoding" family as
Outlines, Guidance, and vLLM guided decoding.

Backend integrations: HF Transformers, vLLM, llama.cpp, TensorRT-LLM, ExLlamaV2,
LangChain, LlamaIndex, Haystack.

## Relevance to our paper (TEHR / tool-existence hallucination, RVR intervention)

Key fact: **no tool/function-calling constraint feature is documented.** It
constrains *output format* (JSON shape, regex), not *which tool names are legal*.
Our TEHR phenomenon is the model inventing a tool that is not in the registry —
i.e. emitting a wrong `name` value, not malformed JSON. LMFE does not natively
prevent that.

HOWEVER: a JSON Schema with `"name": {"enum": [<registry tool names>]}` would, via
LMFE's token masking, make it *impossible* to decode a non-existent tool name.
That makes LMFE a **mechanistic upper bound / hard-constraint baseline** against
our soft RVR re-prompt intervention. This is the most useful framing for us.

## Concrete judgments

| Use | Verdict | Notes |
|---|---|---|
| RUN as extra benchmark | **No** | It is a decoding library, not a benchmark/dataset. Nothing to "run as a benchmark." |
| Reuse COMPONENT in harness | **Maybe (low-med effort)** | Only works on local logits → applies to our MLX/Qwen3 path, NOT the Anthropic API path (no logit access). MLX is not a listed backend; would need a custom logits-processor adapter. Skip unless we add a constrained-decoding arm. |
| Reuse as BASELINE | **Yes — strongest use** | Add a "constrained decoding" intervention arm: enum-restricted tool-name JSON Schema. Drives TEHR→0 by construction on local models, contrasting RVR (works on API + local, no logit access needed). Lets us argue RVR's value: API-only models (Anthropic 4.x already 0) and black-box settings can't use logit masking. Med effort on Qwen3/MLX only. |
| Cite as PRIOR ART | **Yes** | Canonical constrained-decoding ref alongside Outlines/Guidance/XGrammar. Cite to position RVR as a *post-hoc black-box* alternative to *white-box logit masking*, and to note logit masking is unavailable for closed API models — a core motivation for our re-prompt approach. |
| PATTERN for paper-revision skill/personas | **No** | Out of scope; nothing transferable. |

## Effort & risk
- **License risk:** none (MIT).
- **Integration effort:** Low to cite. Medium to wire as a baseline arm because
  MLX is unsupported — needs a custom logits processor, and it only covers the
  local-model half of our matrix (API models excluded by design — itself a
  paper point). The Anthropic 4.x = 0 result needs no such baseline.

## Recommendation
Cite as prior art AND add as a baseline arm on the local Qwen3/MLX models:
enum-constrained tool-name decoding as a hard-constraint upper bound vs. our
black-box RVR re-prompt. Emphasize that constrained decoding needs logit access
(impossible for closed APIs), which is exactly the gap RVR fills. Do not treat as
a runnable benchmark.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

Re-checked every load-bearing claim against primary sources (gh API, raw LICENSE,
pyproject.toml, README). The survey holds up; it was appropriately conservative,
not over-optimistic. Findings:

- **License = MIT — CONFIRMED (high confidence).** Verified three ways: (1) raw
  LICENSE file is the verbatim MIT text, "Copyright (c) 2023 Noam Gat"; (2)
  `pyproject.toml` `license = "MIT"` + classifier `License :: OSI Approved :: MIT
  License`; (3) gh API `license.spdx_id = "MIT"`. SPDX: **MIT**. Permissive — we
  MAY vendor/modify/redistribute into our (permissive) codebase with attribution.
  No GPL/AGPL copyleft concern. This is the favorable case the prompt asked us to
  watch for; it is genuinely clear here.
- **Stars = 2,015 — CONFIRMED (high).** gh API `stargazers_count = 2015`. Survey
  said 2,015. Order of magnitude (~2k) is correct; no inflation.
- **Maintained — CONFIRMED.** `archived = false`, `fork = false`, last push
  2026-04-04. Survey accurate.
- **Backends — CONFIRMED.** HF Transformers, vLLM, llama.cpp, TensorRT-LLM,
  ExLlamaV2, LangChain, LlamaIndex, Haystack. Survey list matches.
- **MLX NOT supported — CONFIRMED and material.** MLX appears nowhere in repo
  docs/README. Our local path is MLX/Qwen3-4bit on M5. Using LMFE as a baseline
  arm therefore requires writing a custom MLX logits-processor adapter (it exposes
  a backend-agnostic `CharacterLevelParser` + token-mask interface, so it is
  doable, but it is real glue work, not a drop-in). Survey's "medium effort"
  rating is fair.
- **API models excluded BY DESIGN — CONFIRMED, and stronger than the survey
  states.** README, verbatim: "it can not be used with OpenAI ChatGPT and similar
  API based solutions." So it cannot touch the Anthropic 4.x half of our matrix
  at all. This strengthens (not weakens) the paper framing: logit-masking is
  structurally unavailable for closed APIs → motivates black-box RVR.

### Claims-check / penalties
- **MINOR OVERSTATEMENT (one claim).** Survey asserts a JSON Schema
  `{"name":{"enum":[...]}}` baseline. README/feature-table do NOT explicitly
  document `enum`/`Literal` value-restriction; they document JSON Schema + regex +
  schemaless JSON. Enum is plausibly supported (it's standard JSON Schema and the
  lib is Pydantic-based), but it is documented-by-implication, not stated. The
  GUARANTEED-supported equivalent is a **regex constraint** `(toolA|toolB|...)`
  over the tool-name field, which achieves the identical hard upper bound. Use the
  regex form to de-risk; verify enum support empirically before relying on it.
- No other over-optimism found. The survey already correctly rejected "run as
  benchmark" (it's a library) and correctly scoped reuse to the local arm only.

### Pressure-test of "cite-only"
The prompt framed this as a cite-only candidate; that UNDER-sells it slightly.
Because the license is MIT (not GPL/AGPL), we are not restricted to
cite/run-external — we COULD vendor an adapter. Realistic recommendation:
**include-parts** — cite as canonical prior art (alongside Outlines / Guidance /
XGrammar) AND optionally implement a constrained-decoding baseline arm on the
local Qwen3/MLX models (regex tool-name mask) as a hard-constraint upper bound vs.
RVR. The baseline only covers the local half of the matrix; the API half (where
Anthropic 4.x is already TEHR=0) is structurally out of reach for any logit-mask
method — which is itself the argument for RVR. Do NOT run it as a benchmark.

**Verdict:** license MIT (confirmed, high conf); recommend include-parts;
one minor enum overstatement flagged (regex fallback de-risks it); MLX adapter
is required glue, API models permanently excluded by design.

---

## ADVERSARIAL RE-VERIFICATION #2 (2026-05-29, Opus, fully independent)

Re-pulled every load-bearing claim from primary sources (gh API, raw LICENSE,
pyproject.toml, decoded README @ v0.11.3). Confirms the survey AND corrects one
point in Verification #1.

### License — MIT, CONFIRMED THREE WAYS (high confidence)
- Raw `LICENSE` file: verbatim MIT text, "Copyright (c) 2023 Noam Gat" (full text
  decoded, includes the standard permission grant + AS-IS clause).
- `pyproject.toml`: `license = "MIT"` and classifier `License :: OSI Approved ::
  MIT License`.
- `gh api`: `license.spdx_id = "MIT"`, `license.name = "MIT License"`.
- SPDX: **MIT**. Permissive. We MAY vendor/modify/redistribute into our permissive
  codebase with attribution. NO GPL/AGPL copyleft — the favorable case the prompt
  warned to watch for is genuinely present here. license_confirmed = true.

### Stars / maintenance — CONFIRMED
- `stargazers_count = 2015` (matches survey "2,015"; order of magnitude ~2k correct,
  no inflation). `archived = false`, `fork = false`, `pushed_at = 2026-04-04`,
  `updated_at = 2026-05-27`. Actively maintained. Current version 0.11.3.

### API models excluded — CONFIRMED, verbatim
- README line 213: "LM Format Enforcer requires a python API to process the output
  logits of the language model. ... it can not be used with OpenAI ChatGPT and
  similar API based solutions." => structurally cannot touch our Anthropic 4.x
  half of the matrix. Reinforces RVR motivation (black-box, no logit access).

### MLX — CONFIRMED ABSENT
- Documented backends (README line 61): transformers, LangChain, LlamaIndex,
  llama.cpp, vLLM, Haystack, TensorRT-LLM, ExLlamaV2. No MLX. Our local path is
  MLX/Qwen3-4bit on M5 => a baseline arm needs a custom MLX logits-processor
  adapter. It exposes a backend-agnostic prefix-allowed-tokens / CharacterLevelParser
  interface (line 48, `build_transformers_prefix_allowed_tokens_fn`), so doable but
  real glue work. Survey "medium effort" is fair.

### CORRECTION to Verification #1 re: enum / hard-constraint baseline
Verification #1 said enum value-restriction is "not documented" and recommended
falling back to regex. Pulling the actual README, BOTH paths are in fact documented:
- **Choice/regex decoding is explicitly first-class**: README line 119
  `"guided_regex": "[Pp]ositive|[Nn]egative"` and line 124 documents `guided_choice`
  (vLLM) — i.e. restricting output to a fixed set of strings is a documented feature,
  not an inference. A tool-name mask `(toolA|toolB|...)` is squarely supported.
- **enum IS referenced for JsonSchemaParser**: README line 202 mentions configuring
  the alphabet so characters "appear as json keys or enum values in JsonSchemaParser"
  — so JSON-Schema enum value-restriction is acknowledged in docs, not pure
  implication. Verification #1's penalty was slightly too harsh; the enum baseline is
  better-supported than it claimed.
- Net: the "hard-constraint upper bound" baseline (force tool name into the registry
  set via regex/choice or schema enum) is solidly supported on local models. No
  meaningful overstatement remains on this point.

### Minor caveat (new, from line 215)
RegexParser "can only generate characters that exist in the tokenizer vocabulary"
(open GH issue #13). Irrelevant for ASCII tool names, but note it if any registry
tool name contained exotic characters. Not load-bearing for us.

### Pressure-test of "cite-only" framing
"cite-only" UNDER-sells it. MIT license => not restricted to cite/run-external; we
COULD vendor. Realistic recommendation: **include-parts** —
1. Cite as canonical constrained-/guided-decoding prior art (with Outlines, Guidance,
   XGrammar) to position RVR as a post-hoc BLACK-BOX alternative to white-box logit
   masking.
2. Optionally implement a constrained-decoding baseline arm on local Qwen3/MLX
   (regex/choice tool-name mask) as a hard-constraint TEHR->0 upper bound vs RVR.
The baseline covers ONLY the local half of the matrix; the API half (Anthropic 4.x
already TEHR=0) is permanently out of reach for ANY logit-mask method — which is
itself the core argument for RVR. Do NOT run it as a benchmark (it is a decoding
library, not a dataset/benchmark).

**Verdict #2:** license MIT (confirmed 3 ways, high conf); recommend include-parts;
Verification #1's enum penalty was overcautious — regex/choice baseline is explicitly
documented and enum is referenced; MLX adapter is required glue; API models excluded
by design (confirmed verbatim). No over-optimism remaining; if anything the survey was
slightly conservative.
