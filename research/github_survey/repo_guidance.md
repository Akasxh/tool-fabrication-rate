# Repo survey: guidance

- **Repo:** guidance-ai/guidance
- **URL:** https://github.com/guidance-ai/guidance (canonical; did NOT 404)
- **Stars:** 21,484 (gh api, 2026-05-29)
- **License:** MIT (SPDX, confirmed via `gh api repos/guidance-ai/guidance`)
- **Language:** Python (repo tagged "Jupyter Notebook" by GitHub due to notebook docs)
- **Status:** Active. Last push 2026-05-21; not archived; 1,167 forks, 293 open issues.
- **Category:** constrained-decoding (NOT a benchmark — unlike the rest of this survey set)

## What it is
A library for **constraining and controlling LLM output** at generation time. Core
features:
- **Regex constraints** — force output to match a regular expression.
- **Context-free grammars (CFG)** — force output to conform to an arbitrary grammar;
  used for guaranteed-valid JSON/XML/code.
- **JSON Schema / Pydantic** — generate output validated against a Pydantic model.
- **`select()`** — constrain output to one of a fixed list of options.
- **Token fast-forwarding** — skips forward passes on tokens the grammar makes
  deterministic, cutting latency/cost.
- **Control flow** — `@guidance` decorator, loops, conditionals, interleaved
  gen + program logic; some tool-use integration in control-flow examples.

**Critical backend caveat (decisive for us):** grammar/regex constraints require
**token-level access to the backend**. They work on local backends (Transformers,
llama.cpp, vLLM). For closed API models the README only claims "supports... OpenAI,
etc." and hedges: constraints hold "so long as the backend LLM has full support for
Guidance." Anthropic Claude exposes no token-mask/logit-bias API, so guidance **cannot
enforce a grammar on Anthropic 4.x** — exactly the family that anchors our 0-event
result. No benchmarks or eval harness ship in the repo.

## Fit vs our paper
Our paper measures a **per-call Tool-Existence Hallucination Rate (TEHR)**: does the
model emit a call to a tool not in the registry? Our intervention **RVR** is a
*post-hoc, re-prompt* mechanism — detect a bad call, re-inject the tool registry, ask
again. guidance attacks the same failure mode from the **opposite end**: prevent the
bad token *during decoding* via a grammar over the allowed tool names. So guidance is
genuinely **adjacent prior art / a conceptually competing intervention**, not a
benchmark and not a baseline-in-our-current-shape.

The mismatch that blocks direct use: guidance's constraint only bites where we have
token-level control (our MLX/Qwen3 4-bit local runs), and that is *precisely* the
setting where we report nonzero TEHR (1.87% peak at 14B). On Anthropic 4.x — our 0%
setting — guidance can't apply a hard constraint at all. So it is not a drop-in
intervention across our whole model matrix; it is a method that would only function on
the local-MLX half.

## Concrete verdict per use mode

- **RUN as an extra benchmark? — NO / N/A.** guidance is a control library, not a
  benchmark. There is no dataset or scored task to run. Skip.

- **Reuse a COMPONENT in our harness? — MAYBE, low priority, MLX-only.** MLX is not a
  listed first-class backend (Transformers / llama.cpp / vLLM are), so wiring guidance
  into our MLX path is non-trivial — likely needs an llama.cpp (GGUF) re-host of Qwen3
  or a custom logits-processor bridge. Effort is medium-to-high and only covers half
  our matrix. Don't put this on the deadline path.

- **Reuse as a BASELINE? — YES, this is the strongest fit, and it sharpens the paper.**
  A "**constrained-decoding (guidance grammar over the tool-name set)**" arm is the
  obvious **upper-bound / structural baseline** against our RVR re-prompt: a grammar
  over allowed tool names drives TEHR to **0 by construction** on any backend that
  supports it. That is a compelling table row IF we frame honestly: constrained
  decoding is a *hard guarantee but needs token-level control* (so it's unavailable on
  closed APIs and on naive API tool-calling), whereas **RVR is backend-agnostic and
  works on Anthropic 4.x / any API model** — which is the regime real deployments use.
  This turns guidance from a threat into our differentiation. Recommend implementing it
  as a baseline arm on the **local-MLX/Qwen3 subset only** (via llama.cpp/vLLM rehost),
  reporting "0% TEHR but API-incompatible," and contrasting with RVR's portability.
  Scope it as a stretch experiment, not deadline-critical.

- **Cite as PRIOR ART? — YES, mandatory.** With 21k stars and MIT, guidance is the
  canonical reference for constrained/grammar-based decoding and *must* be cited (with
  outlines / llguidance / XGrammar) as the "prevent-at-decode-time" family that RVR is
  positioned against. A reviewer who knows this space will ask "why not just constrain
  decoding?" — we need the answer (API models, closed weights, MLX gaps) in the related
  work and limitations.

- **Borrow a PATTERN for the paper-revision skill / reviewer personas? — YES, small but
  real.** Add a reviewer-persona check: *"Did the authors address constrained-decoding
  baselines (guidance/outlines/XGrammar) and justify why a re-prompt intervention is
  needed instead of a grammar?"* This is a predictable ICML reviewer objection; baking
  it into the persona forces the rebuttal pre-emptively.

## Effort & license risk
- **License risk: NONE.** MIT — permissive, attribution only; safe to vendor code,
  borrow patterns, or run as a baseline.
- **Effort:**
  - Cite as prior art — trivial.
  - Add reviewer-persona prompt — trivial.
  - Baseline arm (MLX-only, via llama.cpp/vLLM rehost of Qwen3 + grammar over tool
    names) — **medium-to-high**; off the critical path; recommend as stretch.
  - Harness component reuse — medium-high, low value; skip.

## Bottom line
Not a benchmark. Best value is (1) **cite as prior art** (mandatory) and (2) a
**constrained-decoding baseline arm** on the local-MLX subset that makes RVR's
backend-agnostic, API-compatible re-prompt design look deliberate rather than naive.
Plus a cheap reviewer-persona addition. License is clean (MIT).

---

## ADVERSARIAL VERIFICATION (appended 2026-05-29, independent re-check)

Re-verified every load-bearing claim against the live repo via `gh api` + raw file
reads + a second-source web fetch. Verdict: **survey is accurate and, if anything,
slightly UNDERSTATES the backend problem in our favor.** No over-optimism penalty
warranted; one factual sharpening below.

**License — CONFIRMED MIT (SPDX: MIT).** Did not trust the GitHub classifier summary.
Read raw `LICENSE.md`: verbatim canonical MIT text, "Copyright (c) The Guidance
Contributors". Single license file (no COPYING/NOTICE, no dual-license, no GPL/AGPL
contamination anywhere in the tree). `pyproject.toml` points `license = {file =
"LICENSE.md"}` at that same file. **No GPL/AGPL risk** — safe to vendor, borrow
patterns, and run as a baseline with attribution only. The "License risk: NONE" claim
holds.

**Stars — CONFIRMED, correct order of magnitude.** `gh api` = 21,484; web page = 21.5k.
~10^4, low-twenties-thousands. Survey's "21k stars" is accurate.

**Status — CONFIRMED active.** Not archived; last push 2026-05-21; 1,167 forks; 293 open
issues. Matches survey.

**Backend claims — CONFIRMED and STRENGTHENED.** Inspected `guidance/models/`:
- Core backends present: `_transformers.py`, `_llama_cpp.py`, `_openai.py`,
  `_azureai.py`, `_onnxruntime.py`. vLLM + sglang + litellm live in `experimental/`.
- **No `_mlx.py` anywhere.** MLX is not a backend at all (not core, not experimental).
  Survey's "MLX-only reuse is medium-to-high effort, needs a GGUF/llama.cpp rehost of
  Qwen3" is correct and remains the only viable local path for us.
- **`_anthropic.py` exists ONLY in `guidance/models/broken_models/`.** That dir's README
  states these files "use an older version of guidance's internal API... cannot and
  should not be imported from this repository." So Anthropic support is **dead/broken,
  not merely unconstrainable.** The survey was slightly generous ("README claims supports
  OpenAI etc."); the real situation is worse for any Anthropic path — there is no working
  Anthropic backend at all. This makes our differentiation argument STRONGER: guidance
  literally cannot touch Anthropic 4.x (our 0-event family), broken or constrained.
- OpenAI backend exposes only `RegexMixin` + `JSONMixin` (structured-output-style
  constraints via OpenAI's API), **not** arbitrary CFG. Arbitrary grammar / token
  fast-forwarding only fully works on token-level local backends (Transformers,
  llama.cpp). Confirms the "needs token-level control" thesis.

**Pressure-testing the recommendations:**
- "Cite-only / cite as prior art = mandatory" — UPHELD. Canonical constrained-decoding
  reference, MIT, 21k stars, actively maintained. A reviewer will ask "why not just
  constrain decoding?"; we need this in related work + limitations.
- "Baseline arm on local-MLX/Qwen3 subset via llama.cpp rehost" — UPHELD as a *stretch*,
  off critical path. Confirmed feasible (llama.cpp is a first-class backend; GGUF Qwen3
  exists) but non-trivial and covers only half our model matrix. Do NOT put on the
  2026-04-28 deadline path.
- "Reviewer-persona addition" — UPHELD, trivial, high value.
- "Run as benchmark = NO" — UPHELD. No dataset, no scored task ships. It is a library.

**Could we ACTUALLY run/reuse it given MLX+API harness + license?**
- License: yes, no blocker (MIT).
- API half of our harness (Anthropic 4.x): **NO** — no working Anthropic backend; grammar
  enforcement impossible on Claude regardless. This is exactly why RVR (re-prompt,
  backend-agnostic) is our differentiator.
- MLX half (Qwen3 4-bit): not directly — MLX unsupported; requires a llama.cpp/GGUF or
  vLLM rehost of Qwen3 plus a logits-processor bridge. Medium-to-high effort.
- Net: reusable as an *external/rehosted baseline*, NOT as a drop-in across our matrix.

**RECOMMENDATION: cite-only** (mandatory prior-art citation) **as the primary action**,
with an optional stretch "constrained-decoding baseline" arm on the MLX/Qwen3 subset
only (rehosted via llama.cpp) if schedule permits. Not a benchmark. License clean.
**Confidence: HIGH.** All claims verified against live repo source, two sources for stars,
raw LICENSE text read directly.

---

## SECOND INDEPENDENT ADVERSARIAL RE-CHECK (appended 2026-05-29, reviewer Akash/Opus)

Re-ran the verification from scratch against the live repo (`gh api` + raw base64 file
reads + harness source inspection). I did NOT trust either the survey body or the first
appended block. Verdict: **survey claims hold; no over-optimism penalty. One claim is
actually MORE favorable to us than written (vendoring is legal here), and one nuance
worth flagging.**

**LICENSE — CONFIRMED MIT (SPDX: MIT).** Read the raw decoded LICENSE.md, not the
classifier badge: canonical MIT text, "Copyright (c) The Guidance Contributors". GitHub
license endpoint reports path `LICENSE.md`, spdx `MIT`. `pyproject.toml` declares
`license = {file = "LICENSE.md"}` pointing at that same file. No COPYING/NOTICE, no
GPL/AGPL anywhere. **The task's GPL/AGPL veto does NOT trigger — this is MIT, fully
permissive.**

**VENDORING — EXPLICITLY CLEAR (sharper than survey).** Our own harness is licensed
**Apache-2.0** (`harness/pyproject.toml`: `license = { text = "Apache-2.0" }`). MIT is
inbound-compatible with Apache-2.0, so we may legally vendor guidance code into our
tree (with attribution), not merely cite/run-externally. The survey's "License risk:
NONE / safe to vendor" is correct and now confirmed against OUR specific license.

**STARS — CONFIRMED order of magnitude.** `gh api` = 21,484 (10^4, low-twenties-k).
Matches survey "21k".

**STATUS — CONFIRMED active.** archived=false, pushed_at 2026-05-21, 1,167 forks, 293
open issues. Matches.

**BACKEND / RUNNABILITY — CONFIRMED, and the Anthropic situation is genuinely worse
than the survey body's softer framing (the first appendix already caught this; I
re-verified it):**
- `guidance/models/` core backends: `_transformers.py`, `_llama_cpp.py`, `_openai.py`,
  `_azureai.py`, `_onnxruntime.py`. `experimental/`: `_vllm.py`, `_sglang.py`,
  `_litellm.py`.
- **No `_mlx.py` exists.** The only repo-wide "mlx" search hit is a coincidental
  substring inside `client/graphpaper-inline/package-lock.json` (an npm lockfile) — NOT
  a backend. Confirmed there is zero MLX support.
- Our local path uses `mlx_lm.load` / `mlx_lm.generate` directly (`harness/adapters/
  mlx_adapter.py`). guidance cannot bind to that without a GGUF/llama.cpp or vLLM
  rehost of Qwen3 + a logits-processor bridge. Medium-to-high effort, MLX-only, off
  critical path — survey is right.
- `_anthropic.py` lives ONLY in `guidance/models/broken_models/`; that dir's README
  states verbatim the files "cannot and should not be imported from this repository."
  So on Anthropic 4.x (our 0-event family) guidance is not merely "unconstrainable" —
  there is **no working backend at all**. Strengthens our differentiation, not weakens
  it.

**PRESSURE-TEST OF "CITE-ONLY":** Upheld as the correct PRIMARY recommendation. Given
MLX is unsupported and Anthropic is broken, we cannot drop guidance into our matrix; a
real reuse requires re-hosting Qwen3 on llama.cpp/vLLM — that is a build, not a reuse,
and it covers only half the model matrix. So "run/reuse as-is across our harness" is
NOT actually feasible; cite-only is honest. The optional constrained-decoding baseline
arm (MLX subset, rehosted) remains a legitimate STRETCH experiment, explicitly off the
2026-04-28 deadline path. Run-as-benchmark: NO (no dataset ships).

**Could we ACTUALLY run/reuse it given MLX+API harness + license?** License: yes (MIT,
compatible with our Apache-2.0; vendoring legal). Technically: NO as a drop-in — API
half (Anthropic) has no working backend; MLX half needs a rehost. Reusable only as an
external/rehosted baseline.

**FINAL: recommend = cite-only.** License MIT confirmed, vendor-safe into our Apache-2.0
tree. Not a benchmark. Optional stretch baseline on MLX/Qwen3 subset via llama.cpp
rehost. **Confidence: HIGH** — every load-bearing claim re-verified against live repo
source and our own harness license.
