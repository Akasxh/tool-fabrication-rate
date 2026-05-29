# AutoGPT — GitHub Survey

- Repo: Significant-Gravitas/AutoGPT
- URL: https://github.com/Significant-Gravitas/AutoGPT (URL valid, not 404)
- Stars: 184,630 | Forks: 46,204 | Open issues: 428
- Language: Python | Archived: no | Last push: 2026-05-29 (actively maintained)
- Category: agent-framework

## License (verified from LICENSE file — gh API reports NOASSERTION because it is dual)
Split license:
- **MIT** for everything OUTSIDE `autogpt_platform/` — includes the classic standalone
  AutoGPT agent, `classic/forge`, the benchmark (`classic/direct_benchmark`, formerly
  AGBenchmark), and the classic GUI. `CITATION.cff` declares `license: MIT`.
- **Polyform Shield License** for everything inside `autogpt_platform/` (the new visual
  low-code agent-builder platform). Polyform Shield is a source-available NON-COMPETE
  license: usage is fine but you may not use it to build a competing product. NOT
  OSI-approved, NOT a free/open license.

Risk: LOW for the MIT classic/benchmark/forge code; AVOID the `autogpt_platform/` tree
(non-compete clause is incompatible with permissive reuse and ICML artifact norms).

## What it is
Two things under one repo:
1. **AutoGPT Classic** (MIT): the original 2023 "make GPT-4 fully autonomous" loop —
   an LLM agent with memory, web access, file ops, and tool use that decomposes goals
   into steps. `classic/forge` is an agent-building toolkit; `classic/direct_benchmark`
   holds the agent challenge suite (file retrieval, web navigation, coding, reasoning
   challenges with a `challenges_already_beaten.json` ledger and `analyze_*.py` scorers).
2. **AutoGPT Platform** (Polyform): a visual block-based builder + backend for deploying
   persistent autonomous agents. The bulk of current development; non-compete licensed.

It is an end-to-end autonomous-agent product, not a tool-calling correctness benchmark.

## Concrete judgement for our TEHR / RVR paper

- **RUN as an extra benchmark? NO (skip).** `classic/direct_benchmark` measures whole-task
  agent success on open-ended GPT-4-era challenges (web/file/coding goals). It is not a
  structured tool-calling benchmark with a fixed tool registry per turn, so it gives us no
  clean per-call denominator for a Tool-Existence Hallucination Rate. It is GPT-4/agent-loop
  shaped, heavy to stand up, and orthogonal to BFCL/tau-bench multi-turn tool-call schemas.
  Adapting it into our `harness/bench_loaders/` would be a large effort for a metric mismatch.

- **Reuse a COMPONENT in our harness? NO.** The agent loop and Forge toolkit are tied to the
  classic agent's own scaffolding; nothing maps onto our adapters/runner/intervention design
  better than what we already have (BFCL + tau-bench loaders, MLX + API model adapters).

- **Reuse as a BASELINE? NO.** AutoGPT is an agent scaffold, not a model or an intervention
  comparable to RVR. There is no apples-to-apples baseline here.

- **Cite as PRIOR ART? YES (cite-only, low effort).** AutoGPT is THE canonical reference for
  autonomous LLM tool-using agents and motivates why tool-existence hallucination matters
  (agents that invent tools/actions in a long autonomy loop). Cite in related work to frame
  the real-world stakes of TEHR. Use `CITATION.cff` (Significant Gravitas, MIT). 184k stars
  makes it a strong motivating citation; differentiate by noting it has no per-call
  tool-existence metric or registry-reprompt intervention.

- **Borrow a PATTERN for the paper-revision skill / reviewer personas? MARGINAL.** Nothing
  directly. The challenge-ledger idea (`challenges_already_beaten.json` + `analyze_failures.py`
  as a regression scoreboard) is a mildly interesting pattern for tracking which review
  findings are resolved across revisions, but it is generic and not worth importing.

## Bottom line
Cite-only prior art. Do not run, do not vendor, do not baseline. The MIT portions are
license-safe to read/cite; never pull from `autogpt_platform/` (Polyform Shield non-compete).

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verified against live GitHub (`gh api`) + raw LICENSE fetch. Verdict: survey is ACCURATE, not over-optimistic. No claims downgraded.

**License — CONFIRMED dual, NOT a single SPDX.**
- `gh api` reports `spdx_id: NOASSERTION`, `license.key: other` (as the survey correctly noted — this is because the repo is dual-licensed, not because the license is unknown).
- Raw `LICENSE` file (master) verbatim: "All portions of this repository are under one of two licenses. Everything inside the autogpt_platform folder is under the **Polyform Shield License**. Everything outside ... is under the **MIT License**." Full PolyForm Shield License 1.0.0 text + full MIT text are embedded in the file.
- `CITATION.cff` confirmed `license: MIT`, author `Significant Gravitas`.
- SPDX call: effective = `MIT AND LicenseRef-PolyForm-Shield-1.0.0`. The MIT subtree (classic agent / Forge / classic GUI / `classic/direct_benchmark`) is SPDX `MIT`. The `autogpt_platform/` subtree is `LicenseRef-PolyForm-Shield-1.0.0` (source-available, NON-OSI, non-compete).
- **VENDOR FLAG (per instructions):** PolyForm Shield is NOT GPL/AGPL — it is a non-compete source-available license, which is arguably *more* restrictive for our purposes than copyleft. We MUST NOT vendor `autogpt_platform/` into our (permissive) codebase. The MIT subtree IS safe to vendor/cite. Net effect matches the instruction's spirit: external-cite OK, selective-vendor of MIT parts OK, no blanket vendoring.

**Stars — CONFIRMED.** 184,630 stars (forks 46,204, open issues 427). Order of magnitude 10^5. Survey's 184,630 is exact-match to live API. Not inflated.

**Maintenance — CONFIRMED.** `archived: false`, `pushed_at: 2026-05-29` (same-day), `language: Python`. Actively maintained.

**"Cite-only / skip-as-benchmark" — PRESSURE-TESTED, HOLDS.**
- The benchmark path: LICENSE text says `classic/benchmark` but that path 404s; the actual live dir is `classic/direct_benchmark` (survey used the correct current path — good catch). It is a "Direct Benchmark Harness" that *directly instantiates AutoGPT agents* (strategies: one_shot, rewoo; models: claude/openai) and scores whole-task success on challenge categories `abilities / alignment / library / verticals` (e.g. ReadFile, web nav, coding goals). Confirmed via README + dir listing.
- This is a full agent-loop task-success harness, NOT a structured per-call tool-calling benchmark with a fixed per-turn tool registry. There is NO clean per-call denominator for TEHR, and no tool-existence-hallucination signal exposed per call. Adapting it to `harness/bench_loaders/` = large effort for a metric mismatch. Confirmed SKIP-as-benchmark.
- Could we *run* it given MLX+API? It supports `--models claude,openai` (API), so API runs are technically possible, but it has NO MLX path and is built around poetry + AutoGPT's own agent scaffolding. Even if run, output is task-success %, not TEHR. So "runnable" technically-yes-via-API but USELESS for our metric → does not change the verdict.
- Cite-only as canonical autonomous-agent prior art: justified by 184k stars + MIT CITATION.cff. HOLDS.

**One nit (not a downgrade):** the `challenges_already_beaten.json` + `analyze_failures.py` regression-ledger pattern the survey flagged as "marginal" for the reviewer-persona/revision skill is real and present in the tree, but remains generic; agree it is not worth importing.

**FINAL:** recommend = cite-only. license_spdx = `MIT AND LicenseRef-PolyForm-Shield-1.0.0` (MIT subtree only is reusable/vendorable; autogpt_platform/ non-compete = do NOT vendor). license_confirmed = true. confidence = high.

---

## INDEPENDENT RE-VERIFICATION #2 (2026-05-29, Akash adversarial pass)

Re-checked all load-bearing claims against live sources rather than trusting the prior append. Everything HOLDS; survey is NOT over-optimistic.

**License — CONFIRMED dual, independently fetched raw LICENSE.** Verbatim opening: "All portions of this repository are under one of two licenses. Everything inside the autogpt_platform folder is under the Polyform Shield License. Everything outside ... is under the MIT License." `gh api` returns `spdx_id=NOASSERTION`, `license.key=other` — correctly explained by the dual structure, NOT an unknown license.
- SPDX (effective): `MIT AND LicenseRef-PolyForm-Shield-1.0.0`.
- VENDOR FLAG: Polyform Shield is a source-available NON-COMPETE license (not GPL/AGPL, but arguably *stricter* for our purposes). Per the GPL/AGPL spirit of the instruction: external cite/run OK, but DO NOT vendor `autogpt_platform/` into our permissive codebase. The MIT subtree (classic agent / Forge / classic GUI / `classic/direct_benchmark`) IS safe to read/cite/vendor.

**Stars — CONFIRMED.** Live `gh api`: 184,630 stars, 46,204 forks, 427 open issues. Order of magnitude 10^5. Exact match to the survey's number. Not inflated.

**Maintenance — CONFIRMED.** `archived=false`, `pushed_at=2026-05-29T09:22:54Z` (same day), `language=Python`. Active.

**"cite-only / skip-as-benchmark" — PRESSURE-TESTED, HOLDS.**
- Benchmark path verified: `classic/benchmark` 404s; live path is `classic/direct_benchmark` (survey's correction confirmed). Tree contains `analyze_failures.py`, `analyze_reports.py`, `challenges/`, `challenges_already_beaten.json`, `direct_benchmark/`.
- README confirms it measures whole-task / challenge-level agent success across strategies (one_shot, rewoo, plan_execute, reflexion, tree_of_thoughts). Models are API-only (Claude + OpenAI families, incl. extended-thinking/reasoning modes). NO MLX path. NO fixed per-turn tool registry. NO tool-hallucination / tool-existence metric exposed — README explicitly has nothing of the kind.
- RUNNABLE given our MLX+API harness? Only partially: API runs are technically possible, but there is no MLX backend and the scaffolding is AutoGPT's own poetry-based agent loop. More importantly, even a successful run yields task-success %, NOT a per-call TEHR denominator — so it is USELESS for our metric. "Could run via API" does NOT upgrade it past cite-only.
- The MIT `CITATION.cff` (author: Significant Gravitas) + 184k stars justify it as canonical autonomous-agent prior art for related work.

**VERDICT: survey accurate, no downgrades. recommend=cite-only, confidence=high, license_confirmed=true.**
