# Repo survey: storm

- **Repo:** stanford-oval/storm
- **URL:** https://github.com/stanford-oval/storm (canonical; did NOT 404)
- **Homepage / demo:** http://storm.genie.stanford.edu (live research preview, 70k+ users)
- **Stars:** 28,277 (gh api, 2026-05-29)
- **License:** MIT (SPDX, confirmed via `gh api repos/stanford-oval/storm`)
- **Language:** Python
- **Status:** Active-ish. Last push 2025-09-30; not archived. ~2,575 forks, 124 open issues.
  PyPI package `knowledge-storm` (v1.1.0, litellm integration).
- **Papers:** STORM (arXiv:2402.14207, NAACL 2024); Co-STORM (arXiv:2408.15232, EMNLP 2024 main).
- **Category:** research-automation (knowledge curation / long-form report generation — NOT a
  tool-calling or hallucination benchmark)

## What it is
STORM = *Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking*.
An LLM system that writes Wikipedia-style, citation-grounded long-form articles from scratch by
(1) a **pre-writing** stage that does Internet research and builds an outline, then (2) a
**writing** stage that drafts the full article with citations. Core trick: generate good
research questions via (a) **perspective-guided question asking** and (b) **simulated
conversations** between a "Wikipedia writer" agent and a "topic expert" agent grounded in search.

**Co-STORM** adds a **collaborative discourse protocol** with a turn-management policy over
multiple roles: LLM **experts** (answer from retrieved sources / raise follow-ups), a
**Moderator** (injects thought-provoking questions from under-used retrieved info), and a
**human user**; it maintains a dynamically updated hierarchical **mind map** of collected info.

Implementation: highly modular, built **on top of dspy**. Pluggable LM layer (any litellm
provider) and retrieval layer (`YouRM`, `BingSearch`, `VectorRM`, `SerperRM`, `BraveRM`,
`SearXNG`, `DuckDuckGoSearchRM`, `TavilySearchRM`, `GoogleSearch`, `AzureAISearch`). Entry points
are `STORMWikiRunner` and the Co-STORM runner classes.

## Fit vs our paper
Our paper measures a **per-call Tool-Existence Hallucination Rate (TEHR)** on BFCL multi-turn /
tau-bench (Anthropic 4.x = 0 events; Qwen3 4-bit non-monotonic, peak 1.87% at 14B) and proposes
**RVR** — detect a call to a tool not in the registry, re-inject the registry, re-prompt. STORM
operates in a completely different layer: open-domain web-grounded report writing. It has **no
tool registry, no function-calling task, and no hallucination metric** of the kind we measure
(its "hallucination" concern is citation/factual grounding of free-text prose, not tool-existence
in a structured call). There is **zero benchmark overlap** with TEHR.

## Concrete verdict per use mode

- **RUN as an extra benchmark? — NO / N/A.** STORM is a generation *system*, not a benchmark, and
  its task (long-form article writing) is orthogonal to tool-existence hallucination. Running it
  would produce articles, not TEHR-comparable numbers. It also requires paid search-API keys
  (You.com/Bing/Serper/Tavily) and heavy web access per topic, so it is operationally expensive
  with no payoff for our claim. Skip.

- **Reuse a COMPONENT in our harness? — NO.** Nothing in STORM maps to BFCL/tau-bench tool
  calling. Its LM/RM abstraction is just a thin dspy+litellm wrapper we don't need (our
  `harness/bench_loaders/{bfcl,tau_bench}.py` already drive MLX + API models directly). Adopting
  any of it adds a dspy dependency for no measurement benefit. Reject.

- **Reuse as a BASELINE? — NO.** It is not a tool-use agent and produces no comparable metric.
  Not a meaningful baseline for RVR or for TEHR.

- **Cite as PRIOR ART? — MAYBE, weak / context-only.** Worth citing only if our related-work or
  paper-revision narrative touches multi-agent LLM research automation, simulated
  expert/moderator discourse, or grounded long-form generation. It is NOT prior art for
  tool-existence hallucination or for failure-detect-and-reprompt interventions. If cited, frame
  it as a high-profile example of *role-structured multi-agent LLM systems* (Co-STORM
  expert/moderator protocol), differentiated sharply from our structured tool-call measurement.

- **Borrow a PATTERN for the paper-revision skill / reviewer personas? — YES (the one real win).**
  Co-STORM's **role-structured discourse** is a clean, citable template for our reviewer
  personas:
  1. **Moderator role** — Co-STORM's Moderator surfaces *under-used* information (questions the
     experts haven't engaged). Mirror this in the paper-revision skill: a "moderator" pass that
     flags claims/evidence in our results the draft under-discusses, or reviewer objections not
     yet pre-empted. This complements the existing skeptic/adversary personas with a
     coverage-gap-finder rather than another attacker.
  2. **Expert + simulated-conversation pattern** — generating good *questions* (not just answers)
     to drive depth is exactly what a strong reviewer persona should do against our draft. The
     perspective-guided question asking is a reusable rubric idea: enumerate distinct reviewer
     perspectives (measurement-validity, baseline-fairness, generalization-across-families) and
     ask sharp questions from each, then revise.
  This is a *pattern borrow only* — no code, no dependency.

## Effort & license risk
- **License risk: NONE.** MIT — permissive, attribution only. Safe to vendor code, borrow
  patterns, or cite.
- **Effort:**
  - Cite as (weak) prior art — trivial.
  - Borrow the moderator/expert discourse pattern for reviewer personas + revision skill — low.
  - Run it / reuse a component / baseline — not worth it (off-task, needs paid search APIs).

## Bottom line
Big, clean (MIT), well-known dspy-based research-automation system — but on a different axis from
our tool-existence-hallucination work. It is **not** a benchmark we can run, **not** a harness
component, and **not** a baseline; cite it at most as weak context for multi-agent research
automation. The single concrete payoff is **borrowing Co-STORM's role-structured discourse
(Moderator + Expert / perspective-guided question asking) as a pattern for our reviewer personas
and the paper-revision skill** — adding a coverage-gap "moderator" persona alongside the existing
skeptic/adversary roles.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verified against the live repo, not the survey summary. Method: `gh api`, raw LICENSE bytes,
setup.py + requirements.txt.

### License — CONFIRMED MIT (SPDX: MIT), no copyleft risk
- Pulled the raw `LICENSE` file bytes directly (not GitHub's auto-detector, which can be fooled by
  a renamed/modified file). It is the **verbatim canonical MIT text** (172 words, standard
  permission grant + warranty disclaimer), header line `MIT License`, copyright
  `(c) 2024 Stanford Open Virtual Assistant Lab`. No GPL/AGPL/BSD/Apache strings present.
- Cross-checked package metadata: `setup.py` declares `license="MIT License"` and the OSI
  classifier `License :: OSI Approved :: MIT License`. GitHub API `spdx_id` = `MIT`. **Three
  independent sources agree.**
- Verdict: the survey's MIT claim is **accurate and not over-optimistic**. This is NOT a
  GPL/AGPL situation; vendoring STORM code into our (permissive) codebase is license-safe
  (attribution only). Transitive deps are mainstream-permissive (dspy/langchain/litellm/qdrant);
  no copyleft dependency surfaced in `requirements.txt`.

### Stars — CONFIRMED order-of-magnitude (tens of thousands)
- `gh api` 2026-05-29: **28,277 stars**, 2,575 forks, 124 open issues, not archived, not a fork,
  not a mirror, created 2024-03-24, last push 2025-09-30. Matches the survey exactly. Order of
  magnitude (10^4) is correct and the repo is the canonical Stanford one.

### "Reuse-pattern" claim — PRESSURE-TESTED, holds but with a correction
- The survey's two negative reuse verdicts (not a benchmark, not a harness component, not a
  baseline) are **correct and if anything UNDERSTATE the integration cost**. The dependency is
  `dspy_ai==2.4.9` — a *hard-pinned, ~Feb-2024-era* dspy plus langchain-text-splitters,
  langchain-huggingface, langchain-qdrant, qdrant-client, sentence-transformers, trafilatura.
  Calling it "a thin dspy+litellm wrapper we don't need" slightly *undersells* the mess: pulling
  any STORM component drags in a pinned-old dspy + langchain + a vector DB client, which would
  conflict with / bloat our MLX+API harness. So the survey's REJECT-the-component conclusion is
  right, and the real reason is even stronger than stated.
- The **pattern-borrow** claim (Co-STORM Moderator/Expert role-structured discourse → reviewer
  personas) survives scrutiny: it is genuinely a code-free, dependency-free idea transplant, so
  the pinned-dep problem does not touch it. This is the one defensible "reuse" and it is honestly
  scoped (pattern only, not code).
- **Run-externally feasibility:** STORM *can* be run (MIT, pip-installable `knowledge-storm`), but
  it needs paid search-API keys and produces long-form articles, not TEHR numbers. The survey's
  "skip running it" is correct; there is no tool-existence-hallucination signal to extract.

### Over-optimism penalty
- Net: the survey did **not** overstate license, stars, or usability. If anything it was mildly
  *generous* in describing the dspy coupling as "thin." No correction needed to its bottom-line
  recommendation. The headline payoff (cite-only + borrow the moderator/expert persona pattern)
  is the right call.

### Final verdict
- License: **MIT** (SPDX `MIT`), confirmed from raw LICENSE + setup.py + API. Safe to vendor; no
  copyleft flag needed.
- Recommend: **cite-only** for our paper (weak prior art for role-structured multi-agent LLM
  systems) PLUS borrow the Co-STORM Moderator/Expert discourse pattern for reviewer personas /
  revision skill (pattern, not code). Do NOT run as a benchmark, do NOT vendor components.
- Confidence: **high** (license + stars triple-verified; reuse claim stress-tested against actual
  pinned deps).

---

## INDEPENDENT RE-CONFIRMATION (2026-05-29, second adversarial pass)

Re-ran the checks against the live repo from scratch (not trusting the section above):
- **License = MIT (SPDX `MIT`)** — pulled raw `LICENSE` bytes via `gh api .../contents/LICENSE`:
  verbatim canonical MIT (172-word grant + disclaimer), `Copyright (c) 2024 Stanford Open Virtual
  Assistant Lab`. `setup.py` independently declares `license="MIT License"` + OSI classifier
  `License :: OSI Approved :: MIT License`. API `spdx_id` = `MIT`. **Not GPL/AGPL** — vendoring is
  license-safe (attribution only); no copyleft flag warranted. Confirmed.
- **Stars = 28,277** (10^4 magnitude), forks 2,575, open issues 124, not archived, not a fork,
  created 2024-03-24, last push 2025-09-30. Matches. Confirmed.
- **Reuse pattern** — `requirements.txt` confirms the hard pin `dspy_ai==2.4.9` plus
  langchain-text-splitters / langchain-huggingface / langchain-qdrant, qdrant-client,
  sentence-transformers, trafilatura, litellm. Adopting any STORM *component* drags in a
  pinned-old dspy + langchain + vector-DB client → conflicts with / bloats our MLX+API harness.
  REJECT-component verdict holds and is, if anything, understated. The Co-STORM Moderator/Expert
  discourse **pattern borrow** is code-free/dependency-free and survives. Confirmed.
- **Nit:** `setup.py` now reads `knowledge-storm` v**1.1.1** (survey body said PyPI 1.1.0);
  immaterial to any verdict.
- **Over-optimism check:** survey did NOT overstate license/stars/usability; mildly *generous* in
  calling the dspy coupling "thin." No correction to the bottom line.
- **Net recommend: cite-only** (weak prior art for role-structured multi-agent LLM systems) +
  borrow Co-STORM Moderator/Expert persona pattern. Do NOT run as benchmark, do NOT vendor.
