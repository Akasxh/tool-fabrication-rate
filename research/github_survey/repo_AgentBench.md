# Repo survey: AgentBench

- **Repo:** THUDM/AgentBench
- **URL:** https://github.com/THUDM/AgentBench (canonical; did NOT 404)
- **Stars:** 3,458 (gh api, 2026-05-29)
- **License:** Apache-2.0 (SPDX, confirmed via `gh api .../license`)
- **Language:** Python
- **Status:** Active. Last push 2026-02-08; not archived. ICLR'24 paper (arXiv 2308.03688).
- **Category:** benchmark

## What it is
First broad "LLM-as-Agent" benchmark across **8 interactive environments**: Operating
System, Database (DBBench), Knowledge Graph, Digital Card Game (Avalon), Lateral
Thinking Puzzles, plus recompiled ALFWorld (house-holding), WebShop (web shopping),
Mind2Web (web browsing). Current `main` is **AgentBench FC (Function Calling)** —
rebuilt on AgentRL, function-calling-style prompts, fully **containerized**: tasks run
as Docker workers behind an AgentRL Controller + Redis allocator (`docker compose -f
extra/docker-compose.yml up`). Older `v0.1`/`v0.2` tags retain the original
controller/worker (`src/server`, `src/client`, `src/assigner.py`) architecture.

Resource reality: WebShop env needs ~16GB RAM; ALFWorld worker leaks memory/disk; KG
needs a Freebase Virtuoso DB dump; MySQL image for DBBench. Heavy infra.

## Fit vs our paper
Our paper measures a **per-call Tool-Existence Hallucination Rate (TEHR)** on **static
tool registries** (BFCL multi-turn, tau-bench) — does the model call a tool not in the
registry. Our harness `Task` (harness/types.py) is a flat `{registry, initial_prompt,
turns_max, expected_outcome}` over canonical-OpenAI tool schemas; loaders parse
JSON/JSONL into that shape (harness/bench_loaders/bfcl.py). AgentBench is the opposite
shape: stateful, environment-grounded, Docker-backed *task success* scoring, not
per-call tool-name hallucination.

## Concrete verdict per use mode

- **RUN it as an extra benchmark? — NO (skip for the deadline).** Mismatch on two
  axes. (1) Infra: containerized controller/worker + Redis + MySQL + 16GB WebShop +
  Freebase dump is far outside our `bench_loaders/*.py` "parse a file into `Task`"
  pattern and our MLX-on-a-32GB-Mac + API setup. (2) Metric: AgentBench scores
  end-to-end task success in live environments; it does NOT expose a per-call
  tool-existence signal. To get TEHR we'd need a *fixed* tool registry per task and
  to classify each call against it — AgentBench's tools are environment-coupled, not a
  static registry we control. Adapting it ~= reimplementing the env. Not worth it before
  2026-04-28. (If breadth demands a 3rd loader, prefer something registry-shaped.)

- **Reuse a COMPONENT in our harness? — NO.** Controller/worker + Docker-Compose
  orchestration (`src/server`, `src/client`, AgentRL) is the wrong abstraction for our
  in-process adapter→runner loop. Their tool-call parsing is tied to AgentRL, not
  reusable standalone. Nothing drops cleanly into `harness/`.

- **Reuse as a BASELINE? — NO (not an intervention baseline).** AgentBench is a task
  suite, not a hallucination-mitigation method. It is not comparable to RVR (our
  re-prompt-with-registry intervention). Our baselines are the C0/C0.5/C0.7/C1
  conditions, not AgentBench.

- **Cite as PRIOR ART? — YES (primary recommended use).** Cite as the canonical
  LLM-as-agent multi-environment benchmark (ICLR'24) and **differentiate**: AgentBench
  measures coarse end-to-end task success across live environments; we isolate and
  quantify a specific *per-call* failure mode (tool-existence hallucination) on static
  registries with a targeted intervention (RVR). Useful in Related Work to position our
  narrow-but-deep contribution against broad-but-shallow agent benchmarks, and to
  motivate "task-success metrics hide tool-existence hallucinations." Note the FC
  function-calling variant is directly topical to our tool-call framing.

- **Borrow a PATTERN for paper-revision skill / reviewer personas? — WEAK / optional.**
  The 8-environment taxonomy and per-env success-rate reporting are a useful template
  for a reviewer persona that asks "where's your breadth across agent settings?" — i.e.
  arm the skeptic persona to push for environment diversity and to anticipate the
  "why only BFCL/tau-bench?" critique. No code to borrow; only the framing.

## License risk
Apache-2.0 — permissive, patent grant, attribution + NOTICE retention only. No copyleft.
Safe to vendor code/snippets or cite. Note recompiled sub-datasets (ALFWorld/WebShop/
Mind2Web) carry their own upstream licenses if their *data* were ever pulled in — not
relevant for cite-only use.

## Effort
- Cite-only: ~trivial (one bib entry + one Related-Work sentence + differentiation).
- Run-as-benchmark: high (Docker/AgentRL infra) AND blocked by metric mismatch — not
  recommended.

## Bottom line
**cite-only.** Strong prior-art citation and differentiation target; not a benchmark we
can run, a component we can reuse, or a baseline we can compare against. Optionally seed
a reviewer-persona "breadth" prompt from its environment taxonomy.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

Method: did not trust the summary. Verified each load-bearing claim against GitHub directly.

- **LICENSE — CONFIRMED Apache-2.0 (SPDX).** Fetched and decoded raw `/LICENSE`
  (`gh api repos/THUDM/AgentBench/contents/LICENSE` → base64 decode): file begins
  "Apache License / Version 2.0, January 2004" — genuine Apache 2.0 text, NOT a misnamed
  file fooling the API. `gh api .../license` independently reports
  `spdx_id=Apache-2.0`, `name="Apache License 2.0"`, `path=LICENSE`. Only one
  license/notice file in repo root tree (no COPYING, no second LICENSE). No GPL/AGPL.
  → **Permissive. We CAN vendor snippets, run externally, and cite. No copyleft trap.**
  Caveat unchanged: recompiled sub-datasets (ALFWorld/WebShop/Mind2Web) carry their own
  upstream data licenses — irrelevant for cite-only, would matter only if data ingested.

- **Stars — CONFIRMED order-of-magnitude.** `gh api` → `stargazers_count=3458`
  (GitHub web rounds to "3.5k"). Survey's 3,458 is exact and correct. ~10^3.5, mid-thousands.

- **Active — CONFIRMED.** `archived=false`, `pushed_at=2026-02-08`, `default_branch=main`,
  `language=Python`. Matches survey.

- **FC/Docker rebuild — CONFIRMED, with a minor correction.** Current `main` IS the
  function-calling rebuild on AgentRL, Docker-required. README lists **5** containerized
  FC environments (OS, DBBench, KnowledgeGraph, WebShop, ALFWorld); the original
  **8-environment** taxonomy (adds Avalon card game, Lateral Thinking Puzzles, Mind2Web)
  is the older v0.2. The survey's "8 environments" describes v0.2 and it did flag the FC
  variant separately — not an overstatement, but readers should note FC main = 5 envs.

- **"cite-only" claim — PRESSURE-TESTED, HOLDS.** Checked our harness directly
  (`harness/types.py` `Task`: flat `{id, benchmark, registry, initial_prompt, turns_max,
  expected_outcome}`; loaders `harness/bench_loaders/{bfcl,tau_bench}.py` parse a
  file into that shape). AgentBench FC is architecturally orthogonal on BOTH axes the
  survey claimed: (1) **Infra** — Docker workers + AgentRL Controller + Redis allocator +
  per-env images (MySQL, 16GB WebShop, Freebase/Virtuoso for KG) cannot be expressed as a
  file→`Task` loader and is hostile to our MLX-on-32GB-Mac + API runner. (2) **Metric** —
  scores end-to-end *task success* in live envs; tools are environment-coupled, so there
  is NO static per-call tool registry to classify calls against → cannot yield TEHR
  without re-implementing each env. Not a hallucination-mitigation method, so not an RVR
  baseline either. **We would NOT actually be able to run/reuse it for our purpose under
  the deadline; cite-only is the honest call (not over-optimistic — if anything the
  survey was generous in even sketching a run-as-benchmark path).**

**Verifier verdict: cite-only. License Apache-2.0 confirmed (permissive, vendor-safe).
No survey claims overstated; one clarification (FC main = 5 envs vs v0.2 = 8). Confidence: high.**

---

## INDEPENDENT ADVERSARIAL RE-VERIFICATION (2026-05-29, second pass)

Re-ran every load-bearing check from scratch via `gh api` + raw file fetch; did not
trust the summary OR the prior verification block.

- **LICENSE = Apache-2.0 (SPDX) — CONFIRMED, not over-claimed.** `gh api .../license`
  → `spdx_id=Apache-2.0`, `name="Apache License 2.0"`, `path=LICENSE`. Decoded raw
  `/LICENSE` content begins literally "Apache License / Version 2.0, January 2004 /
  http://www.apache.org/licenses/ / TERMS AND CONDITIONS..." — genuine Apache-2.0 text,
  not a misnamed file fooling the API classifier. Only one license file in the repo
  root (no COPYING/NOTICE/second LICENSE; grep for licen|copying|notice → just LICENSE).
  → **Permissive. NOT GPL/AGPL. No copyleft trap. We may vendor snippets, run
  externally, and cite freely.** Standing caveat: recompiled sub-datasets
  (ALFWorld/WebShop/Mind2Web/KG-Freebase) carry their own upstream DATA licenses —
  irrelevant for cite-only; would matter only if their data were ingested.

- **Stars order-of-magnitude — CONFIRMED.** `stargazers_count=3458` (~10^3.5,
  mid-thousands; GitHub web rounds to "3.5k"). Survey's 3,458 is exact. Not inflated.

- **Active — CONFIRMED.** `archived=false`, `pushed_at=2026-02-08`, `default_branch=main`,
  `language=Python`.

- **Environment count nuance — survey NOT overstated, one clarification stands.**
  Fetched `main/README.md`: current main (AgentBench FC) ships **5** containerized,
  function-calling environments (alfworld/AF, dbbench/DB, knowledgegraph/KG,
  os_interaction/OS, webshop/WS) via Docker Compose. The "8 environments" figure is the
  original v0.2 taxonomy (adds Avalon, Lateral Thinking Puzzles, Mind2Web). The survey
  described v0.2's 8 AND separately flagged the FC variant — accurate, with the caveat
  that FC main = 5 envs. Not an over-optimistic claim.

- **"cite-only" — PRESSURE-TESTED AGAINST OUR HARNESS, HOLDS HARD.** Read
  `harness/types.py` (`Task` = flat `{id, benchmark, registry, initial_prompt,
  turns_max, expected_outcome}`, registry in canonical-OpenAI shape) and confirmed
  `harness/bench_loaders/` contains only `bfcl.py` + `tau_bench.py` (file→Task parsers).
  AgentBench FC is orthogonal on BOTH axes: (1) INFRA — Docker workers + AgentRL
  Controller + Redis allocator + per-env images (MySQL, ~16GB WebShop, Freebase/Virtuoso
  for KG) is a live-service architecture that cannot be expressed as a file→`Task`
  loader and is hostile to our MLX-on-32GB-Mac + API runner; (2) METRIC — scores
  end-to-end task success in live envs with environment-coupled tools, so there is NO
  static per-call tool registry to classify each call against → it cannot yield TEHR
  without re-implementing each environment. Also not a hallucination-mitigation method,
  so not an RVR baseline. **We could NOT realistically run or reuse it for our purpose
  before 2026-04-28.** If anything the survey was generous in sketching a
  run-as-benchmark path at all; cite-only is the honest, slightly-conservative call.

**Second-verifier verdict: cite-only. License Apache-2.0 CONFIRMED (permissive,
vendor-safe, no copyleft). No survey claims overstated; sole clarification = FC main
ships 5 envs, the "8" is v0.2. Stars/activity exact. Confidence: high.**
