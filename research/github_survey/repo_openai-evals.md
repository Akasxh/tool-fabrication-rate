# Repo Survey: openai/evals

- **URL**: https://github.com/openai/evals
- **Category**: eval-harness
- **Stars**: 18,556 (live via `gh api`, 2026-05-29)
- **Forks**: 2,970 | **Open issues**: 206
- **License**: **MIT** (code). GitHub reports `NOASSERTION` only because `LICENSE.md`
  appends per-dataset license terms after the MIT block. Code is unambiguously MIT;
  the registry **datasets** carry their own licenses (C4 ODC-BY, OpenWebText CC0,
  Wikipedia CC BY-SA/GFDL, plus many others) — must be checked individually if we
  reuse any specific dataset.
- **Activity**: Effectively maintenance-only. Substantive eval work stopped ~late 2024;
  2025–2026 commits are CI/pre-commit pinning and dependency cleanup. README now steers
  users to OpenAI's hosted Dashboard Evals product. Not archived, but not actively
  developed as an OSS harness.

## What it is
A framework + open registry for evaluating LLMs. Core abstractions:
- `completion_fns/` — pluggable model callers (OpenAI, LangChain, CoT, retrieval).
- `solvers/` — newer abstraction layer (providers, memory, postprocessors, nested solvers).
- `elsuite/` — ~30 hand-built evals, several model-graded / multi-turn agentic.
- `registry/` — YAML eval specs + Git-LFS data.
- CLI: `oaieval <solver> <eval>`, `oaievalset`.

## Directly relevant prior art (the valuable part for us)
Several `elsuite` evals are squarely in our tool-use / tool-existence-hallucination lane:
- **`bugged_tools`** — model must complete a task using a tool that may be buggy, and flag
  `(@Bugged: NAME)` when it detects misbehavior. Metric = accuracy of bug detection.
  This is the closest existing analogue to TEHR: it probes whether a model correctly
  reasons about the *state/validity of its tools* during multi-turn use. Strong
  differentiation + cite target: they measure bug-detection accuracy via a custom
  parenthetical flag protocol; we measure an objective per-call existence violation rate
  (TEHR) on a real benchmark (BFCL multi-turn) with no model self-report.
- **`cant_do_that_anymore`** — tests whether a model follows *new* rules that forbid an
  ordinarily-legal action (chess variant: bishops move like knights), counting how often
  it still emits the now-illegal move it was biased toward. Conceptually parallel to
  "calling a tool that isn't in the registry" — a prior-bias-vs-current-constraint probe.
  Good framing citation for why models hallucinate unavailable affordances.
- **`error_recovery`** — multi-turn recovery after an injected error; relevant to our RVR
  intervention framing (re-prompt-after-bad-call). Useful as related work / baseline idea.
- **`solver_tools_convo.py`** — a generic multi-turn tool-conversation solver harness.

## Concrete judgment for our paper/harness

### Run as an extra benchmark? — NO (low value, high friction)
- `oaieval` is hardwired to OpenAI/solver completion_fns and a flag-based text protocol,
  NOT native tool/function-calling. Our story is per-call function-calling on Anthropic 4.x
  + MLX Qwen3; their protocol is incompatible with how we elicit/score tool calls.
- Git-LFS data pull, model-graded scoring, and the deprecated/hosted-redirect status make
  it a poor fit as a clean reproducible benchmark in a main-track table.
- `bugged_tools` is the only tempting candidate, but its metric (self-reported bug flag)
  is a different construct than TEHR; porting it would be a re-implementation, not a run.

### Reuse a component in our harness? — NO
- We already have a clean `bench_loaders/*` + `adapters/*` design with canonical OpenAI
  schema normalization (see `harness/bench_loaders/bfcl.py`). Their `completion_fns`/
  `solvers` layer is heavier and OpenAI-centric; adopting it would be a regression vs our
  existing typed `Task`/adapter abstraction. No component worth vendoring. MIT would permit
  it if we ever wanted to, with attribution.

### Reuse as a baseline? — WEAK / NO as-run; YES as conceptual baseline
- Can't run their numbers head-to-head against TEHR (different metric + protocol).
- But `bugged_tools` accuracy is a legitimate *related metric* to contrast: "prior work
  scores model self-detection of tool bugs; we report an objective existence-violation rate."

### Cite as prior art? — YES (recommended, primary use)
- Cite `evals` as the canonical OpenAI eval framework, and specifically `bugged_tools` and
  `cant_do_that_anymore` as the nearest prior art on tool-reliability / constraint-violation
  in agentic settings. This sharpens our novelty claim (objective per-call TEHR on a
  standard multi-turn function-calling benchmark, across API + local-quantized families).

### Borrow a pattern for the paper-revision skill / reviewer personas? — YES (modest)
- The **model-graded eval** pattern (`elsuite/modelgraded/`, eval-templates docs) is a
  reusable rubric/grader pattern for an automated reviewer persona: structured grading
  prompts + classification templates. Worth mirroring the *rubric structure*, not the code.

## Effort & risk
- **Effort to RUN as benchmark**: HIGH and not worthwhile (protocol mismatch, LFS, deprecation).
- **Effort to CITE / borrow framing**: LOW — primary recommended path.
- **License risk**: LOW for code (MIT). MEDIUM/per-dataset if we ever ingest a specific
  registry dataset — each has its own license; verify before use.

## Bottom line
Treat as **cite-only** prior art. `bugged_tools` + `cant_do_that_anymore` are the key
references to position TEHR against. Do not run it as a benchmark and do not vendor its
components — our harness is already cleaner for our use case. Optionally borrow the
model-graded grading-template *pattern* for reviewer personas.

---

## Adversarial verification (2026-05-29, independent re-check)

**Method**: Pulled raw `LICENSE.md` and `README.md` from `main` and queried the GitHub
API directly (`gh api repos/openai/evals`). Did not trust the survey summary.

### License — CONFIRMED, with a sharper caveat
- **Code SPDX: `MIT`** — verified by reading the actual `LICENSE.md`: "MIT License /
  Copyright (c) 2023 OpenAI" followed by the standard MIT grant verbatim. The survey's
  claim is accurate.
- **GitHub reports `NOASSERTION` / `spdx_id: "NOASSERTION"`** (confirmed via API). The
  cause is exactly as the survey states: `LICENSE.md` appends a "### Dataset Licenses"
  section after the MIT block, so the GitHub license classifier refuses to assert a single
  SPDX. This is a packaging artifact, not a copyleft contamination of the code.
- **STRONGER WARNING than the survey gave on datasets**: the appended per-dataset terms
  include genuinely restrictive licenses, not just attribution ones:
  - **`PiC/phrase_similarity` → CC BY-NC 4.0 (NonCommercial)** — used in the
    `steganography` registry data.
  - **Wikipedia → CC BY-SA 3.0 / GFDL (copyleft, share-alike)** — used in `text_compression`
    and `steganography`.
  - Plus C4 (ODC-BY), several CC0, CC BY 4.0, and MIT datasets.
  Implication: the **code** is safely MIT (vendor-OK with attribution into our permissive
  harness), but **do not ingest the NC or SA datasets** — NC is incompatible with most
  research-artifact redistribution and SA would force share-alike on any derived data we
  release. Since our verdict is cite-only / no-dataset-reuse, this does not bite us, but it
  must be flagged: the survey under-stated this by lumping everything as "attribution-ish."

### Stars — CONFIRMED
- API returns `stars: 18556` — matches the survey's 18,556 exactly. Order of magnitude
  (~18.5k, low tens-of-thousands) confirmed. Forks 2,970 and open issues 206 also match.
  No inflation.

### Activity / deprecation — CONFIRMED (not over-stated; arguably under-stated)
- `archived: false`, but `pushed_at: 2026-04-14`. Recent commit subjects are all hygiene:
  "Pin pre-commit hook revisions to immutable commits", "Pin GitHub Actions workflow
  references", "Remove incontext_rl suite with defunct dependencies". No new evals. The
  README leads with a banner steering users to the hosted OpenAI Dashboard Evals product.
  Survey's "maintenance-only" is fair.

### Pressure-test of "cite-only": would we ACTUALLY be able to run/reuse it? — HOLDS
- **Run as a benchmark in our MLX+API harness**: NOT practically. README confirms the
  setup path is OpenAI-`OPENAI_API_KEY`-centric and the registry data is gated behind
  **Git-LFS** (`git lfs fetch --all` / per-eval pulls of pointer files). Our harness elicits
  native function-calling on Anthropic 4.x + MLX Qwen3; `oaieval`'s completion_fn/solver
  protocol and text-flag scoring (e.g. `bugged_tools`' `(@Bugged: NAME)` convention) are a
  different construct than per-call TEHR. Porting would be a re-implementation, not a run.
  The survey's NO-as-benchmark verdict survives scrutiny.
- **License does NOT block vendoring** (this is the one place a GPL/AGPL repo would have
  killed reuse): MIT permits vendoring code components into our permissive codebase with
  attribution. So "cite-only" here is driven by **engineering fit + protocol mismatch +
  deprecation**, NOT by a license restriction. (Contrast: had this been GPL/AGPL we could
  only cite or run it as an external black box, never vendor — not the case here.)
- **Net**: cite-only is the right call, but for fit reasons, not legal ones. If we ever did
  want a snippet (e.g. the model-graded rubric template), MIT + attribution makes that legal;
  just never pull the NC/SA registry datasets.

### Verdict
`recommend: cite-only`. License SPDX `MIT` (code) confirmed by file inspection;
`NOASSERTION` on GitHub is a dataset-appendix artifact. Stars/activity claims accurate, not
over-optimistic. The only correction to the survey: the embedded dataset licenses include
**CC BY-NC (NonCommercial) and CC BY-SA (copyleft)**, which are more restrictive than the
survey implied — irrelevant under cite-only, but a hard "do not vendor those datasets" flag.
Confidence: **high** (primary claims verified against source files + API).

---

## Second independent adversarial pass (2026-05-29, fresh re-check)

Re-verified from scratch, not trusting the section above. All load-bearing claims hold.

- **License — CONFIRMED `MIT` (code).** Fetched raw `LICENSE.md`: verbatim "MIT License /
  Copyright (c) 2023 OpenAI" + standard grant. `gh api` returns `license.key: "other"`,
  `spdx_id: "NOASSERTION"` — confirmed this is the dataset-appendix artifact, NOT copyleft
  on the code. MIT code is vendor-safe into our permissive harness with attribution.
- **Restrictive embedded datasets — CONFIRMED and even broader than first pass.** NC:
  `PiC/phrase_similarity`, `vicgalle/alpaca-gpt4`, `ToMi` (all CC BY-NC 4.0). SA/copyleft:
  Wikipedia (CC BY-SA 3.0 + GFDL). Hard "do not vendor these datasets" flag stands;
  irrelevant under cite-only.
- **Stars — CONFIRMED 18,556** (forks 2,970, issues 206). No inflation; ~18.5k order of mag.
- **Activity — CONFIRMED maintenance-only.** `archived: false`, `pushed_at: 2026-04-14`;
  last commits are pin-pre-commit / pin-Actions / remove-defunct-suite hygiene. No new evals.
- **One MILD survey over-statement (correction):** the README banner reads "You can now
  configure and run Evals directly in the OpenAI Dashboard" — it presents a hosted
  *alternative*, it does not explicitly deprecate or steer users *away* from the OSS repo.
  The survey's "steers users to the Dashboard / redirect" framing is slightly stronger than
  the literal banner. Substance (de-facto maintenance mode) is still correct; the
  characterization is just marginally over-egged. Does not change the verdict.
- **cite-only pressure-test — HOLDS.** elsuite still ships `bugged_tools`,
  `cant_do_that_anymore`, `error_recovery` (confirmed via API). But running it in our
  MLX+API harness is impractical: setup is `OPENAI_API_KEY`-centric, registry data is
  Git-LFS-gated, and the scoring protocol (text-flag e.g. `(@Bugged: NAME)`, model-graded)
  is a different construct from per-call TEHR. cite-only is driven by engineering/protocol
  fit + maintenance status, NOT by license — MIT would permit vendoring code snippets if
  ever wanted.

Verdict unchanged: `recommend: cite-only`, SPDX `MIT` (code), confidence **high**.
