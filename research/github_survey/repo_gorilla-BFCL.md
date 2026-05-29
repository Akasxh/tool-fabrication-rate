# Repo survey: gorilla-BFCL (Berkeley Function-Calling Leaderboard)

- **Repo:** ShishirPatil/gorilla
- **Canonical URL:** https://github.com/ShishirPatil/gorilla
- **Stars:** 12,876 (gh api, 2026-05-29)
- **License:** Apache-2.0 (SPDX, confirmed from LICENSE file header) — permissive, no copyleft risk
- **Active:** yes — last push 2026-04-13; tags v1.1/v1.2/v1.3
- **Category:** benchmark

## What it is
The Gorilla monorepo. Function/tool-calling research from UC Berkeley. The piece
that matters for us lives at `berkeley-function-call-leaderboard/` (BFCL), the
benchmark our paper already uses. BFCL ships:
- `bfcl_eval/data/` — task files + tool docs + ground truth (incl. the four
  `BFCL_v4_multi_turn_*` splits: base, long_context, miss_func, miss_param —
  exactly the splits our harness loads).
- `bfcl_eval/eval_checker/` — scoring: `ast_eval/`, `multi_turn_eval/`,
  `agentic_eval/`, `eval_runner.py`. State-based + AST checking for multi-turn.
- `bfcl_eval/model_handler/` — `base_handler.py`, `api_inference/`,
  `local_inference/`, `parser/`: per-family adapters that turn model output into
  comparable tool calls (this is the part that encodes family-specific quirks).
- CLI entrypoint `bfcl` (`bfcl_eval.__main__:cli`), `TEST_CATEGORIES.md`,
  `SUPPORTED_MODELS.md`.

## Relationship to our harness
We already **vendor the BFCL v4 data** (`harness/data/bfcl_v4/repo/berkeley-function-call-leaderboard`)
and **reimplement the loader** in `harness/bench_loaders/bfcl.py`. That loader
deliberately does NOT import the upstream package — it re-vendors the
`_CLASS_TO_DOC_FILENAME` mapping and normalizes schemas itself to keep BFCL off
the import path. So BFCL is already integrated as a data source; the open
questions are about the *evaluation/scoring* and *model-handler* layers we did
not adopt.

## Concrete judgments

### RUN as an extra benchmark? — Already in; partial expansion possible
We run the multi-turn splits. The breadth win is **adding the single-turn AST
categories** (simple / parallel / multiple / parallel_multiple, plus the
`irrelevance` and `live` relevance categories). Those single-turn categories are
the canonical place a Tool-Existence Hallucination Rate signal shows up cheaply,
and `irrelevance`/relevance detection is conceptually adjacent to TEHR. Effort:
LOW-MED — same repo we already vendor; just point the loader at the
single-turn task files and reuse our normalization. No new license issue.

### Reuse a COMPONENT in our harness? — Yes, the eval_checker is the prize
`eval_checker/multi_turn_eval/` and `ast_eval/` are the upstream's *official*
scoring logic. Our harness computes TEHR (a per-call existence check we own),
but if a reviewer asks "does your re-prompt intervention hurt task accuracy?",
the credible answer is upstream BFCL accuracy. Vendoring `eval_checker` as an
optional scorer lets us report standard BFCL accuracy alongside TEHR/RVR with
the community-accepted metric rather than a homegrown one. Apache-2.0 makes
vendoring clean (keep NOTICE/attribution). Effort: MED — the checker pulls a
heavy dep tail (tree_sitter, faiss-cpu, sentence-transformers, qwen-agent,
networkx, vendor SDKs); isolate it behind an optional extra / subprocess rather
than into our core env.

### Reuse as a BASELINE? — Yes, strongly, via the public leaderboard
BFCL maintains a public leaderboard with per-model, per-category accuracy across
many families (Anthropic, OpenAI, Qwen, Mistral, Cohere, Llama, ...). That is a
ready-made external baseline table to position our family coverage and to
cross-check that our harness's accuracy is in line with the official numbers
(sanity gate against silent harness bugs). The `model_handler/` family adapters
also document the canonical per-family tool-call parsing — useful prior art when
defending our Qwen3 4-bit vs Anthropic 4.x comparison against "your harness
mis-parsed family X" reviewer attacks.

### Cite as PRIOR ART? — Mandatory
This is the benchmark our headline result is measured on; it must be cited and
differentiated. Differentiation: BFCL scores *task accuracy / call correctness*;
we introduce **TEHR (per-call tool-existence hallucination)** as an orthogonal
error mode BFCL's aggregate accuracy does not isolate, plus the **RVR**
intervention. Frame TEHR as a finer-grained diagnostic on top of BFCL's
substrate.

### Borrow a PATTERN for the paper-revision skill / personas? — Minor
`TEST_CATEGORIES.md` + the irrelevance/relevance split encode a useful reviewer
persona: "you report one aggregate number; break it down by category and show
the failure is not just a relevance-detection artifact." Low-value compared to
the technical reuse above; treat as a reviewer-prompt seed, not a real pattern.

## Effort & risk summary
- **License risk:** LOW. Apache-2.0 throughout; vendoring requires only
  attribution/NOTICE. No GPL contamination.
- **Effort to expand benchmark coverage (single-turn categories):** LOW-MED.
- **Effort to vendor eval_checker as official scorer:** MED (heavy, conflicting
  pinned deps — numpy==1.26.4, faiss-cpu==1.11.0, tree_sitter==0.21.3; isolate).
- **Biggest immediate wins:** (1) cite + differentiate as prior art [required];
  (2) pull BFCL leaderboard numbers as an external baseline table [LOW];
  (3) add single-turn + irrelevance categories for breadth [LOW-MED].

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

**Method:** GitHub API + raw LICENSE/pyproject/README fetches; cross-checked against local vendored copy.

### License — CONFIRMED, survey accurate
- Top-level `LICENSE` = **Apache-2.0** (verified header: "Apache License, Version 2.0, January 2004"; SPDX `Apache-2.0` via `gh api`).
- No subdir LICENSE under `berkeley-function-call-leaderboard/` (404) → inherits top-level Apache-2.0.
- `pyproject.toml` declares `license = { "text" = "Apache 2.0" }`; README states data + leaderboard stats also Apache-2.0.
- **No copyleft anywhere.** Survey's "no GPL contamination / vendoring clean with NOTICE" claim is CORRECT. Vendoring into our permissive codebase is legitimate (retain NOTICE/attribution per Apache §4).

### Stars — CONFIRMED
- 12,876 (gh api, 2026-05-29). Order-of-magnitude (~13k / 10^4) correct. Active: pushed 2026-04-13, not archived.

### "Run-as-benchmark" / reuse claims — PARTIALLY OVER-OPTIMISTIC, two flags

1. **No MLX backend. This is the load-bearing omission.** Upstream BFCL local inference supports **vLLM and sglang only** (`vllm==0.8.5` optional, `sglang[all]` optional). There is **zero MLX / Apple-Silicon support** in pyproject or README. Our harness runs MLX locally (M5 32GB). Therefore:
   - We CANNOT "just run upstream BFCL" against our MLX models. The model_handler/local_inference layer assumes vLLM/sglang servers.
   - The OpenAI-compatible-endpoint path (`--skip-server-setup`) is the only realistic bridge: stand up an OpenAI-compatible shim over MLX, then point BFCL at it. That is real integration work, not a drop-in. The survey's "RUN as extra benchmark — LOW-MED effort, just point the loader at single-turn task files" is only true because **we already reimplemented the loader ourselves** — it is NOT true of upstream's runner. Adjusting: expanding *our* loader to single-turn categories is LOW-MED (survey right); running *upstream's* harness end-to-end on MLX is MED-HIGH and was glossed over.

2. **eval_checker dep tail is heavier/more conflict-prone than implied, but survey flagged it.** Confirmed pins: `numpy==1.26.4`, `tree_sitter==0.21.3`, `faiss-cpu==1.11.0`, `networkx==3.3`, plus `sentence-transformers`, `qwen-agent` (unpinned), vendor SDKs (mistralai, cohere, anthropic, openai). Hard pins (esp. numpy 1.26.4, tree_sitter 0.21.3) WILL conflict with a modern uv-managed env. Survey correctly says "isolate behind optional extra / subprocess" — endorsed. Keep it out of core env. This part of the survey is honest.

3. **Baseline-via-leaderboard claim — sound, no license issue.** Pulling published per-model/per-category numbers as an external baseline table is fine (stats are Apache-2.0; even absent that, reporting third-party benchmark numbers with citation is standard). Lowest-risk, highest-value reuse. Survey correct.

### Corrected verdict
- **License:** Apache-2.0, fully confirmed. Vendoring permitted; no copyleft flag needed. (This is the one thing the survey nailed without caveat.)
- **Recommendation:** `include-parts` — cite as mandatory prior art; vendor `eval_checker` as an *isolated optional scorer* (subprocess/extra, NOT core env); pull leaderboard as external baseline. Do **NOT** plan on running upstream's runner against MLX without building an OpenAI-compatible shim first (MED-HIGH, the survey under-scoped this).
- **Penalty applied:** survey conflated "we already vendored the data + wrote our own loader" with "upstream is easy to run on our stack." It is not — upstream has no MLX path. Confidence: HIGH on license/stars; HIGH that MLX gap is real.
