# Repo survey: Future-House/paper-qa (PaperQA2)

- **URL:** https://github.com/Future-House/paper-qa (canonical; URL did not 404)
- **Stars:** 8,576 (gh api, 2026-05-29)
- **License:** Apache-2.0 (SPDX, confirmed via `repos/.../license`) — permissive, low risk
- **Language:** Python; actively maintained (last push 2026-03-20), CalVer (v5+ = "PaperQA2")
- **Category:** research-automation

## What it does
PaperQA2 is a high-accuracy **RAG agent for scientific literature**. Given a
question, an LLM-driven agent runs a three-phase loop over a corpus of PDFs/
Office/code/HTML docs: (1) **paper search** — generate keyword queries, embed
and index candidates; (2) **gather evidence** — embed the query, rank chunks,
produce contextual scored summaries with LLM re-ranking (RCS); (3) **generate
answer** — feed top summaries into an answer prompt with inline citations. Uses
LiteLLM (OpenAI/Claude/Gemini/Ollama/local), tantivy full-text search, numpy or
Qdrant vector store, multiple PDF readers (Docling, nemotron-parse), and
metadata clients (Crossref, Semantic Scholar, Unpaywall). Ships a `pqa` CLI and
a Python API (`Docs`, `ask()`, `agent_query()`). Ships **LitQA2** eval splits
(from LAB-Bench) for which the authors report superhuman literature QA.

## Fit to our paper (TEHR / RVR on multi-turn function-calling)
Our harness grades a **per-call Tool-Existence Hallucination Rate**: tasks carry
a fixed OpenAI-shape tool `registry` (`harness/types.py:Task`), the model emits
function calls, and we flag calls naming a tool absent from the registry. paper-qa
is a different problem class entirely — closed-domain document RAG graded on
**answer correctness** (LitQA2), with a small fixed internal tool set
(paper_search/gather_evidence/gen_answer) that the agent essentially never
hallucinates around. There is no external, varied per-task tool registry to
probe for existence hallucination, so it does not map onto TEHR.

### Concrete verdicts
- **RUN as extra benchmark?** No. LitQA2 measures retrieval/answer accuracy, not
  tool-existence hallucination. It would not produce a TEHR number and does not
  exercise a varied tool registry. Adapting it would mean inventing a new metric —
  out of scope and not comparable to our BFCL/tau-bench results.
- **Reuse a COMPONENT in our harness?** No meaningful reuse. We already have our
  own adapters + LiteLLM-independent provider routing; paper-qa's value is RAG
  parsing/retrieval, which our function-calling harness has no use for. Pulling it
  in would add a heavy dependency tree (Docling, tantivy, Qdrant) for nothing.
- **Reuse as a BASELINE?** No. It is not a tool-calling hallucination baseline; no
  shared task or metric.
- **Cite as PRIOR ART?** Optional, weak. Useful only as a one-line example of a
  production scientific-RAG agent when motivating "agentic tool use is widely
  deployed." Its companion papers (Skarlinski et al., "Language agents achieve
  superhuman synthesis of scientific knowledge", 2024; LAB-Bench, Laurer et al.)
  are the citeable artifacts, not the repo. Low priority vs BFCL/tau-bench lineage.
- **Borrow a PATTERN for the paper-revision skill / reviewer personas?** Marginal.
  Its agentic "search -> gather evidence -> generate with inline citations"
  decomposition and LLM re-ranking of evidence is a clean template for a
  *citation-grounded* revision/review step (force claims to be backed by a
  retrieved source). But this is a generic RAG pattern; we would reimplement the
  idea, not vendor the code. Not load-bearing.

## Effort / risk
- License risk: **low** (Apache-2.0).
- Integration effort to do anything real: **high** for benchmark/component (new
  metric + heavy deps), and the payoff is ~zero because the task domain differs.
- Recommendation: **cite-only at most**, and even that is optional. Do not invest
  harness or benchmark integration effort here.

## Adversarial verification (2026-05-29, independent)
Re-checked every load-bearing claim against the live repo, not the survey summary.

- **LICENSE (exact SPDX, file-level):** CONFIRMED **Apache-2.0**. Did not trust the
  GitHub license detector alone. Decoded the raw `LICENSE` blob
  (`contents/LICENSE`, sha `7d89c6e2…`): it is the verbatim 201-line Apache License,
  Version 2.0 (Jan 2004) text. `pyproject.toml` independently corroborates via the
  trove classifier `License :: OSI Approved :: Apache Software License` and
  `license = {file = "LICENSE"}`. No dual-license, no GPL/AGPL surprise. Survey's
  "Apache-2.0, permissive, low risk" is ACCURATE.
- **Vendoring direction:** Survey under-stated the *good* news here. Our own harness
  (`harness/pyproject.toml`) is also `license = { text = "Apache-2.0" }`, so the
  GPL/AGPL "cite/run-external-only, cannot vendor" hazard from the review brief does
  **not** apply — Apache-into-Apache vendoring is permitted (subject to NOTICE/
  attribution). The vendoring blocker is therefore *task-fit*, not license.
- **Stars order of magnitude:** CONFIRMED. `gh api` returns `stargazers_count: 8576`
  — i.e. ~10^3 (thousands), exactly as the survey's 8,576 states. Not inflated.
- **Maintained / not archived:** CONFIRMED `archived:false`, `fork:false`,
  `pushed_at 2026-03-20`. Survey accurate.
- **"cite-only" usability pressure-test (our MLX + API harness):**
  - API models: paper-qa routes LLMs through **LiteLLM** (`litellm>=1.81.14`, via
    `fhlmi>=0.45.0`), which speaks the Anthropic API — so our 4.x API models *would*
    drive it. That part of "could we run it" is real.
  - **MLX models: NOT supported.** The survey did not claim MLX support, but I
    pressure-tested it because our local stack is MLX. A code search for `mlx`
    returns 13 hits, **all in `tests/cassettes/*.yaml` HTTP fixtures** (recorded
    DOIs/strings), zero in source. Local inference is Ollama/LiteLLM-only. Our
    MLX-served Qwen3 4-bit models would need an OpenAI-compatible shim to even feed
    paper-qa — extra glue, not native.
  - This does **not** rescue any use case: even with API models wired in, paper-qa
    runs **LitQA2 document-RAG answer-correctness**, which yields no per-call TEHR
    number and exercises no varied external tool registry. So "run it" is
    *technically possible for the API half, pointless for our metric.*
- **Over-optimism check:** The survey is, if anything, *conservative* — it does not
  overstate stars, license, or fit, and it correctly lands on cite-only/skip-for-
  integration. The one omission I'd flag is that it leaves "cite-only" slightly
  generous: the citeable artifact is the **companion papers** (Skarlinski et al.
  2024; LAB-Bench), not the repo itself, and the citation is only weakly relevant
  to a tool-existence-hallucination paper. Net: prefer **cite-only** treated as
  optional, leaning toward **skip** for any harness/benchmark work.

**Verdict:** Apache-2.0 confirmed at file level; stars/maintenance accurate; no
license-vendoring blocker (both sides Apache), but no task-fit and no MLX path.
Cite-only at most, optional. Do not integrate.

## Independent re-verification #2 (2026-05-29, second adversarial pass)
Re-ran every load-bearing check against the live repo from scratch (not trusting the
summary or the prior verification block). All findings reproduce.

- **LICENSE (exact SPDX, file-level, not the detector):** CONFIRMED **Apache-2.0**.
  - `gh api .../license` reports `spdx_id: Apache-2.0`, `path: LICENSE`,
    `sha: 7d89c6e2d7dea1388df7efe33222068cdd784f8b`.
  - Decoded the raw `contents/LICENSE` blob (base64 → text): verbatim
    "Apache License / Version 2.0, January 2004", **201 lines**, standard
    TERMS AND CONDITIONS. No dual-license header, no GPL/AGPL clause.
  - `pyproject.toml` corroborates twice: trove classifier
    `License :: OSI Approved :: Apache Software License` and `license = {file = "LICENSE"}`.
  - **license_confirmed = true; license_spdx = Apache-2.0.** The brief's GPL/AGPL
    no-vendor hazard does NOT apply here — this is permissive.
- **Stars order-of-magnitude:** CONFIRMED `stargazers_count = 8576` (~10^3, low-five-
  figures). Survey's "8,576" is exact, not inflated.
- **Maintained:** CONFIRMED `archived:false`, `fork:false`, `pushed_at 2026-03-20`,
  `language Python`. Survey accurate.
- **Vendoring direction (re-checked our side):** our harness
  `harness/pyproject.toml` is `license = { text = "Apache-2.0" }`. Apache→Apache,
  so vendoring is legally permitted (NOTICE/attribution aside). The blocker is
  task-fit, not license — confirms prior block.
- **"cite-only" usability pressure-test (MLX + API harness):**
  - API/Anthropic: real. Core dep `fhlmi>=0.45.0` wraps LiteLLM, and local/dev extras
    pin `litellm>=1.81.14` *specifically* for an Anthropic fix — our 4.x API models
    could drive it.
  - **MLX: NOT supported in source.** Code search for `mlx` returns hits ONLY in
    `tests/cassettes/*.yaml` HTTP fixtures (13 files, recorded DOI/string matches),
    zero in `src/`. Local inference is Ollama/LiteLLM-only; MLX-served Qwen3 would
    need an OpenAI-compatible shim. Confirms prior block.
  - Even with API models wired in, paper-qa runs LitQA2 document-RAG answer-
    correctness — it produces NO per-call TEHR number and exercises NO varied external
    tool registry (its internal tool set is fixed: paper_search/gather_evidence/
    gen_answer). "Run it" is technically possible for the API half, useless for our metric.
  - Heavy dep tree confirmed (tantivy core; Docling/Qdrant/nemotron opt-in) — pulling
    it into a function-calling harness buys nothing.
- **Over-optimism audit:** The survey does NOT overstate stars, license, or fit. If
  anything it is conservative and lands correctly on cite-only/skip. The only slack is
  that the citeable artifact is the companion papers (Skarlinski et al. 2024; LAB-Bench),
  not the repo, and even that citation is only weakly relevant to a tool-existence-
  hallucination paper. Treat cite-only as optional, leaning skip for any integration.

**Second-pass verdict:** All claims reproduce. Apache-2.0 (file-level), ~8.6k stars,
actively maintained. No license blocker but no task-fit and no native MLX path.
**cite-only at most (optional); do NOT run as benchmark, vendor, or use as baseline.**
