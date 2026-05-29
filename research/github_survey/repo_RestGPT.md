# Repo Survey: RestGPT

- **Repo:** Yifan-Song793/RestGPT
- **URL:** https://github.com/Yifan-Song793/RestGPT
- **Stars:** 1,398 (gh api, 2026-05-29)
- **License:** MIT (SPDX: MIT) — permissive, no copyleft risk
- **Last push:** 2024-06-07 (effectively unmaintained; ~2 yrs stale)
- **Paper:** "RestGPT: Connecting Large Language Models with Real-World RESTful APIs" arXiv:2306.06624 (2023). Project page: https://restgpt.github.io/
- **Category:** benchmark

## What it is
An LLM-based autonomous agent that drives real-world RESTful APIs (TMDB movie DB, Spotify). Coarse-to-fine online planning split into four modules: **Planner** (NL sub-tasks) → **API Selector** (pick endpoint) → **Caller** (formulate params from OpenAPI docs) → **Parser** (Python code to read responses). Ships **RestBench**, a human-annotated benchmark:

| Scenario | # APIs | # Tasks | Avg path len |
|----------|--------|---------|--------------|
| TMDB     | 54     | 100     | 2.3          |
| Spotify  | 40     | 57      | 2.6          |

Each RestBench instance = NL instruction + gold solution path (ordered list of API calls). Metrics in the paper: **Correct Path Rate** and **Success Rate** (human/automatic check that the executed API sequence satisfies the instruction). Stack: langchain + openai + spotipy + tiktoken. Hard-wired to OpenAI (GPT-3.5/GPT-4 in the paper); no first-class local/MLX or Anthropic support.

## Concrete assessment for our paper (TEHR + RVR on tool-existence hallucination)

**Run it as an extra benchmark? Mostly no.** Running RestGPT *as-is* is high effort and a poor fit:
- It is an *agent framework*, not a clean eval harness. Execution requires live TMDB + Spotify API keys (Spotify needs OAuth + manual playlist setup), so runs are non-hermetic, rate-limited, and non-reproducible — bad for a measurement paper.
- It is langchain/OpenAI-coupled; routing through our Anthropic/MLX adapters means rewriting the planner/selector/caller loop.
- Only 157 tasks total, English-only, two domains.

**But the RestBench *data* is genuinely useful (this is the real value).** RestBench gives a **bounded, explicit API registry per scenario** (54 / 40 endpoints with OpenAPI specs) plus gold call sequences. That is exactly the substrate TEHR needs: a closed tool set against which any model-emitted API call can be checked for existence. We can:
- Write a `bench_loaders/restbench.py` that yields our `Task` objects — map each scenario's OpenAPI endpoint list into the normalized `registry` (same OpenAI-tool shape our BFCL loader produces), and carry the gold path in `expected_outcome`. Then compute **per-call TEHR** = fraction of emitted calls naming an endpoint not in the registry. This needs **no live API keys** if we stub execution (we only need to detect hallucinated tool *names*, not actually call TMDB/Spotify). Effort: ~moderate, comparable to the existing BFCL loader; the OpenAPI → registry normalization is the main work.
- This adds a **second tool-existence domain beyond BFCL** (real REST APIs vs BFCL's synthetic Python tools) — directly serves the "more benchmarks/families" main-track breadth goal, and is a different distribution (larger, OpenAPI-typed registries) that could surface non-monotonic Qwen3 behavior in a new setting.

**Reuse a component in our harness? Marginal.** The planner/caller code is langchain-bound and not worth vendoring. The OpenAPI spec files and the `api_selector` prompt design are the only reusable artifacts, and even those we'd likely reimplement.

**Reuse as a baseline? Yes, citationally / optionally functionally.** RestGPT is a natural *baseline agent* on RestBench: if we run RVR vs a plain tool-calling loop on RestBench, RestGPT's reported Success/Correct-Path numbers give a reference point, and its API-Selector is itself a "constrain the model to the registry" mechanism — a prior-art comparator for our RVR re-prompt-with-registry intervention.

**Cite as prior art? Yes — and we should.** RestGPT/RestBench is canonical prior work on (a) grounding LLMs in a fixed real-API registry and (b) the failure mode of selecting non-existent/wrong APIs. Its API Selector is a design point we should *differentiate RVR from*: RestGPT constrains selection up-front via a planning module; RVR is a *reactive* correction that re-injects the registry only after a bad call. Good related-work + motivation citation for tool-existence hallucination.

**Pattern for the paper-revision skill / reviewer personas? Low.** Nothing methodological to borrow for the skill itself. At most, RestBench's human-annotated "gold solution path" framing is a reminder that a reviewer persona may demand human-verified ground truth for any new benchmark we add — worth flagging in the "anticipate reviewer asks" rubric, but not a reusable pattern.

## Honest effort / risk
- **License:** MIT — clean. Safe to vendor RestBench data + cite. Attribute in repo.
- **Effort to use the data (recommended path):** moderate (~1 loader + OpenAPI→registry normalizer + name-existence checker; no live keys needed).
- **Effort to run the full agent (not recommended):** high (live API keys, OAuth, langchain/OpenAI rewrite, non-hermetic, only 157 tasks).
- **Staleness risk:** repo last touched 2024-06; TMDB/Spotify live endpoints may have drifted, but for *name-existence* TEHR we use the frozen OpenAPI specs in-repo, not live calls — so drift is a non-issue for our metric.

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

Independently re-checked every load-bearing claim against the live repo (gh API + raw file fetch + parsing the actual data/spec files). Verdict: survey is **accurate and in places understated** the negatives. No over-optimism penalty on the core facts; one minor effort-framing nuance below.

**License — CONFIRMED MIT (SPDX: MIT).** Did NOT trust the summary: decoded the raw `LICENSE` blob. It is the verbatim MIT text, "Copyright (c) 2023 Yifan Song", with the full grant ("use, copy, modify, merge, publish, distribute, sublicense, and/or sell"). No GPL/AGPL/copyleft. `gh api .../license` also returns `spdx_id: MIT`. **Vendoring RestBench data into our (permissive) codebase is legally fine** — attribute + retain the MIT notice. (The GPL/AGPL no-vendor concern does not apply here.)

**Stars — CONFIRMED 1,398** (`gh api`, 2026-05-29). Order of magnitude ~1.4k correct.

**Last push — CONFIRMED 2024-06-07**, `archived: false`, `fork: false`. ~2 yr stale, as stated.

**Data counts — ALL CONFIRMED by parsing the files directly:**
- `datasets/tmdb.json` = 100 tasks; `datasets/spotify.json` = 57 tasks (157 total). Each item = `{"query": <NL>, "solution": [<ordered API calls>]}`, e.g. `"give me the number of movies directed by Sofia Coppola" -> ["GET /search/person", "GET /person/{person_id}/movie_credits"]`. This is exactly the gold-path substrate the survey describes.
- `specs/tmdb_oas.json` = OpenAPI 3.0.0, 54 operations (matches "54 APIs"). `specs/spotify_oas.json` = OpenAPI 3.0.3, 40 operations (matches "40 APIs"). Frozen specs in-repo, no live calls needed to enumerate the registry.

**"Run-as-benchmark" pressure test — survey's "mostly no" is CORRECT and UNDERSTATED.** Hard evidence the full agent will NOT run with our MLX+API harness, or honestly anyone's, without surgery:
- Entry points (`run.py`) hard-wire `llm = OpenAI(model_name="text-davinci-003", temperature=0.0, max_tokens=700)`. **text-davinci-003 was shut down by OpenAI in Jan 2024** — the default config is dead on arrival even with a valid OpenAI key. No Anthropic/MLX path exists; routing our adapters requires a langchain `BaseLLM` shim and rewriting the planner/selector/caller/parser loop.
- Pinned to **pre-0.1 langchain** internals: `from langchain import OpenAI`, `from langchain.llms.base import BaseLLM`, `langchain.requests`, `langchain.chains.base.Chain` across all five modules. These import paths are removed in modern langchain.
- **No `requirements.txt`/lockfile** in the repo — install is a loose README line `pip install langchain colorama tiktoken spotipy openai` with zero version pins. Classic dependency-rot: a fresh resolve pulls modern langchain/openai and the imports break immediately.
- Live creds required to actually execute: `config.yaml` needs `openai_api_key`, `tmdb_access_token`, and Spotify `client_id`/`client_secret`/`redirect_uri` (OAuth + `init_spotify.py` playlist setup). Non-hermetic, rate-limited, non-reproducible — wrong for a measurement paper.

**One effort-framing nuance (mild correction):** the survey rates the data-reuse loader "moderate ... comparable to the BFCL loader." Agreed, but be precise about *what* is moderate: the JSON is trivially parseable (`query` + `solution` + OpenAPI specs); the only real work is OpenAPI->registry normalization on OUR side. We reuse the **data + specs only** (MIT-clean), and write zero lines that touch their langchain/OpenAI code. Do not let "moderate" leak into any implication that running their agent is moderate — running the agent is high/borderline-broken.

**Net for our harness:** include the RestBench *data* (datasets + specs) as a second tool-existence domain via a new `bench_loaders/restbench.py`; compute per-call TEHR against the frozen 54/40-endpoint registries with stubbed execution (no keys). Do NOT vendor or run the agent. Cite RestGPT as prior art and contrast its up-front API-Selector with our reactive RVR.

## ADVERSARIAL VERIFICATION #2 — independent re-check (2026-05-29)

Second independent pass, re-running every load-bearing fact from scratch (gh API + raw file fetch + Python parsing of the actual JSON/spec files). I did NOT trust the prior verification section. All core claims reproduce. No over-optimism penalty warranted on the facts; the survey is accurate and appropriately pessimistic on the run-as-benchmark question.

- **License — CONFIRMED MIT (SPDX: MIT).** Decoded the raw `LICENSE` blob (not just `gh api .../license` summary): verbatim MIT text, "Copyright (c) 2023 Yifan Song", full grant incl. "modify, merge, publish, distribute, sublicense, and/or sell". `gh api` `license_key=mit`, `spdx_id=MIT`. No copyleft. Permissive — vendoring the RestBench **data + specs** into our codebase is legally clean (retain MIT notice + attribute). The GPL/AGPL no-vendor warning does NOT apply to this repo.
- **Stars — CONFIRMED 1,398** (gh api, 2026-05-29). Order of magnitude ~1.4k is correct.
- **Maintenance — CONFIRMED** `pushed_at=2024-06-07`, `archived=false`, `fork=false`. ~2 yr stale.
- **Data counts — CONFIRMED by parsing files:** `datasets/tmdb.json` is a list of 100 items; `datasets/spotify.json` is 57 (157 total). Schema is exactly `{"query": <NL>, "solution": [<ordered REST calls>]}` (verified first TMDB item: Sofia Coppola -> `["GET /search/person", "GET /person/{person_id}/movie_credits"]`). `specs/tmdb_oas.json` = OpenAPI 3.0.0 with **54** operations; `specs/spotify_oas.json` = OpenAPI 3.0.3 with **40** operations. All four numbers (100/57/54/40) match the survey table exactly.
- **Run-as-benchmark pressure test — survey's "mostly no" CONFIRMED and correctly understated.** `run.py` hard-wires `llm = OpenAI(model_name="text-davinci-003", ...)` (line 61) — a model OpenAI retired Jan 2024, so the default is dead on arrival. Imports are pre-0.1 langchain (`from langchain import OpenAI`, `from langchain.requests import Requests`) that are removed in modern langchain. Root listing has **no** requirements.txt / setup.py / pyproject / lockfile (confirmed: only loose README pip line). `config.yaml` requires `openai_api_key` + `tmdb_access_token` + Spotify `client_id`/`client_secret`/`redirect_uri` (OAuth, non-hermetic). Running the agent through our MLX+API harness is high-effort and partially broken; it is not a drop-in benchmark.

**My verdict matches the survey's recommendation:** do NOT run/vendor the agent. DO reuse the RestBench **data + frozen OpenAPI specs only** (MIT-clean) as a second tool-existence domain via a new `bench_loaders/restbench.py` — the 54/40-endpoint registries + gold paths make per-call TEHR computable with stubbed execution and zero live keys. Cite RestGPT as prior art; contrast its up-front API Selector with our reactive RVR. Classifying this as "run-as-benchmark" would be over-optimistic; the honest recommendation is **include-parts** (the data, not the code).

## Bottom line
Don't run RestGPT the agent. **Do** vendor RestBench (MIT) as a second tool-existence benchmark via a new `bench_loaders/restbench.py` — bounded OpenAPI registries + gold paths make per-call TEHR computable without live keys, adding a real-REST-API domain beyond BFCL. Cite RestGPT as prior art and position its up-front API Selector as the contrast for our reactive RVR intervention; optionally use its reported numbers as a baseline.
