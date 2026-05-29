# Repo Survey: ToolBeHonest

- **Repo:** https://github.com/ToolBeHonest/ToolBeHonest
- **Stars:** 21 (real, via `gh api`, 2026-05-29)
- **License:** MIT (SPDX: `MIT`) — permissive, low risk. Copyright (c) 2024 Yuxiang Zhang.
- **Language:** Python. Last push 2024-09-23 (stale; 0 open issues, 0 forks).
- **Venue:** EMNLP 2024 main conference. Paper: arXiv 2406.20015 / ACL Anthology 2024.emnlp-main.637.
- **Dataset:** HuggingFace `Joelzhang/ToolBeHonest` (the repo's `./data/*.json` is NOT committed; `main.py` defaults to `./data/test_en.json` and calls `convert_hf_data()`, so data must be pulled from HF).
- **Category:** benchmark

## What it does

A **multi-level hallucination diagnostic benchmark** for tool-augmented LLMs. 700 manually
annotated samples across seven tasks, English + Chinese. Built around two axes:

- **Depth (3 inference levels):** (1) solvability detection, (2) solution planning,
  (3) missing-tool analysis.
- **Breadth (3 hallucination-inducing scenarios):** MNT = missing necessary tools,
  PT = potentially-available tool misuse, LFT = limited-functionality tool misuse.

Metrics (in `utils/calculate_metrics.py`): per-subtask `unsolvable` exact-match,
`progress_rate`, and `scorers` (a matching score, mean over instances); aggregated by group
(MNT/PT/LFT/overall) via `np.mean`. A separate `calculate_hallu_analysis` counts six error
categories per group/level: **`non_existent_tools`**, `solvability_hallu`, `wrong_tools`,
`correct`, `wrong_unsolvable_index`, `wrong_reasoning`.

Headline result: Gemini-1.5-Pro 45.3 and GPT-4o 37.0 (out of 100); main error source is
assessing task solvability.

Backends: OpenAI API, Gemini API, and local vLLM server (`http://localhost:8000/v1/chat/completions`).
Deps: `vllm, openai, google-generativeai, scikit-learn, numpy, sentence-transformers`
(sentence-transformers used for the embedding-based `scorers` matching score).

## Relevance to our paper (TEHR / RVR on tool-existence hallucination)

This is the **closest prior art to our core construct**. Critical distinction to draw:

- **Their `non_existent_tools`** = the model *recommends/invents a tool that does not exist*
  when reasoning about how to solve an (often unsolvable) task. It is scored as a **per-sample
  error category, raw counts, in a curated diagnostic of 700 hand-annotated items**, mostly
  single-turn reasoning about tool availability.
- **Our TEHR** = a **per-call rate** measured on **executed multi-turn agentic trajectories**
  (BFCL multi-turn), counting calls that invoke a tool absent from the live registry. Different
  unit of analysis (per-call vs per-sample), different setting (live multi-turn execution vs
  static diagnostic), and we add an **intervention (RVR)**, which ToolBeHonest has none of.

So it is prior art to **cite and differentiate**, not a competing metric we lose to.

## Concrete verdict per use

- **RUN as an extra benchmark?** Possible but **medium-high effort, low fit.** Data lives on
  HF (`Joelzhang/ToolBeHonest`), not the repo, so add a loader that pulls + `convert_hf_data`.
  Backends already include vLLM (adaptable to our MLX/API runners) and OpenAI; would need an
  Anthropic adapter. BUT its outputs are scenario/subtask scores and *raw counts*, not a
  per-call rate, and it is single-/low-turn — it does **not** plug into our per-call TEHR
  pipeline. Running it would give a *second, differently-defined* hallucination number, useful
  as a breadth data point but requiring you to reconcile two definitions. Treat as optional
  breadth, not a primary add. Effort: med-high.
- **Reuse a COMPONENT in our harness?** Marginal. The `scorers` embedding-match
  (sentence-transformers) and the `calculate_hallu_analysis` error-taxonomy bucketing are the
  only reusable bits; both are small and easy to reimplement. Not worth importing the package.
- **Reuse as a BASELINE?** Yes, conceptually: their per-model `non_existent_tools` counts and
  overall scores (GPT-4o 37.0, Gemini-1.5-Pro 45.3) are a **baseline/anchor** showing
  frontier-2024 models DO fabricate tools in their setting — useful contrast to our finding
  that Anthropic 4.x = 0 TEHR events on BFCL multi-turn. Cite their numbers; do not re-run just
  for this.
- **Cite as PRIOR ART?** **Strong yes — required.** It is the canonical EMNLP-2024 reference
  that names tool-existence/`non_existent_tools` hallucination. Our related-work + metric-
  definition sections must position TEHR against it (per-call live rate vs per-sample static
  count; + intervention).
- **Borrow a PATTERN for the paper-revision skill / reviewer personas?** Yes, lightly. Their
  six-way error taxonomy (`non_existent_tools`, `wrong_tools`, `solvability_hallu`,
  `wrong_reasoning`, etc.) is a clean **failure-mode rubric** a reviewer persona can use to
  press us: "you only measure non-existent-tool calls; what about wrong-tool / wrong-reasoning
  errors?" Good adversarial-reviewer prompt material and a checklist for our error analysis.

## Bottom line

`integration_class = cite-only` (with a baseline-anchor citation). MIT license = no risk.
Highest value is as **differentiated prior art + a reviewer-rubric pattern**, not as a
benchmark we run. Running it is feasible but med-high effort and yields a differently-defined
metric, so deprioritize unless a reviewer demands cross-benchmark breadth.

## Sources
- https://github.com/ToolBeHonest/ToolBeHonest
- https://huggingface.co/datasets/Joelzhang/ToolBeHonest
- https://aclanthology.org/2024.emnlp-main.637/
- https://arxiv.org/html/2406.20015

---

## Adversarial verification (2026-05-29, independent)

Re-checked the survey's load-bearing claims directly against the GitHub API and the raw repo,
not summaries. **All three primary survey claims hold; no over-statement found.**

- **LICENSE — CONFIRMED `MIT`.** Read the verbatim `LICENSE` file via
  `gh api repos/ToolBeHonest/ToolBeHonest/license` (base64-decoded): full canonical MIT text,
  "Copyright (c) 2024 Yuxiang Zhang". GitHub's classifier and the actual file agree
  (`spdx_id: MIT`). This is NOT a GPL/AGPL trap — **safe to vendor** into our permissive
  codebase, modify, and redistribute with attribution. The survey's "MIT / low risk" is accurate.
  The HF dataset `Joelzhang/ToolBeHonest` is also stated MIT (700-row `test` split, EN+ZH).
- **STARS — CONFIRMED 21** (`stargazers_count: 21`, 0 forks, 0 open issues, not archived,
  last push 2024-09-23). Order of magnitude = tens, i.e. a research-artifact repo with
  negligible community adoption. Survey's "21" is exact.
- **RUNNABILITY / "cite-only" — UPHELD, with one nuance.** Repo tree confirms NO `data/` dir is
  committed (only `LICENSE README __init__.py main.py requirements.txt scripts/ utils/`); data
  must be pulled from HF and run through `convert_hf_data()` — survey correct. `main.py` exposes
  OpenAI, Gemini, vLLM backends and **no Anthropic backend** (survey correct; we'd have to add
  one for our 4.x models). requirements = `vllm, openai, google-generativeai, scikit-learn,
  numpy, sentence-transformers` (survey correct).
  - Nuance the survey slightly under-states in our favor: the vLLM backend talks to an
    **OpenAI-compatible `/v1/chat/completions` endpoint**, so our MLX models served behind an
    OpenAI-compatible shim (or routed through our API runner) could be pointed at it with low
    plumbing effort — backend integration is EASIER than "med-high" implies.
  - BUT the survey is RIGHT about the real blocker, which is conceptual not mechanical: it is a
    **per-sample static reasoning diagnostic** (700 hand-annotated items, solvability/planning/
    missing-tool analysis), NOT per-call live multi-turn trajectory execution. Its `non_existent_tools`
    is a raw error-category count per sample, not a per-call TEHR. It does **not** plug into our
    per-call BFCL/tau-bench harness; running it yields a second, differently-defined number to
    reconcile. So "run-as-benchmark" remains optional breadth, and **cite-only is the right call.**

**Verdict: `cite-only` (baseline-anchor + differentiated prior art).** Survey did NOT overstate
stars, license, or usability — if anything it was conservative on backend-adaptation effort. The
only correction is directional and minor (vLLM=OpenAI-compatible eases wiring). License is
genuinely permissive (MIT), so the GPL/AGPL vendoring caveat does NOT apply here.

---

## Adversarial verification PASS 2 (2026-05-29, fully independent re-check)

Re-ran every load-bearing claim against primary sources (GitHub API + raw file bytes + HF
dataset page), ignoring both the survey body and the earlier verification section. **All claims
hold. No over-statement detected.**

- **LICENSE = `MIT` — CONFIRMED (verbatim).** `gh api .../license` → `spdx_id: MIT`,
  `path: LICENSE`. Base64-decoded the actual `LICENSE` file: canonical MIT text,
  "Copyright (c) 2024 Yuxiang Zhang". Not GPL/AGPL — the copyleft vendoring caveat does NOT
  apply. **Permissive → safe to vendor, modify, redistribute with attribution** into our
  (permissive) harness. HF dataset `Joelzhang/ToolBeHonest` also states **MIT**, 700 rows,
  single `test` split, EN+ZH. License is genuinely permissive end-to-end (code + data).
- **STARS = 21 — CONFIRMED exact** (`stargazers_count: 21`). Forks 0, open_issues 0,
  archived false, last push 2024-09-23. Order of magnitude = tens; negligible adoption,
  consistent with a one-author research artifact. Survey not inflated.
- **RUNNABILITY / "cite-only" — UPHELD.** Root tree (API): `LICENSE README.md __init__.py
  assets main.py requirements.txt scripts utils` — **no `data/` committed** (survey correct;
  data pulled from HF + `convert_hf_data()`, called unconditionally at main.py:85).
  `requirements.txt` = exactly `vllm, openai, google-generativeai, scikit-learn, numpy,
  sentence-transformers` (survey correct). Backends in main.py: gemini / openai / vllm only —
  **no Anthropic backend** (survey correct; we'd add one for 4.x). The earlier note's nuance is
  verified at source: `VllmGeneration.generation_vllm` is a bare
  `requests.post(api_url, json={'messages':[...]})` to `http://localhost:8000/v1/chat/completions`
  — i.e. an OpenAI-compatible endpoint, so an MLX model behind an OpenAI-compatible shim wires in
  with low effort. Six-way error taxonomy incl. `non_existent_tools`, `solvability_hallu`,
  `wrong_tools` confirmed in `utils/calculate_metrics.py` (line ~75).
- **CONCEPTUAL BLOCKER stands.** It is a per-sample static reasoning diagnostic (700 hand-
  annotated items; solvability / planning / missing-tool analysis), NOT per-call live multi-turn
  trajectory execution. `non_existent_tools` is a raw per-sample error-category count, not a
  per-call TEHR. It does not plug into our per-call BFCL/tau-bench harness; running it yields a
  second, differently-defined hallucination number to reconcile. Mechanical wiring is easy
  (OpenAI-compat), but fit is low.

**VERDICT (independent): `cite-only`** — differentiated prior art + a baseline anchor
(GPT-4o 37.0, Gemini-1.5-Pro 45.3) showing frontier-2024 models DO fabricate tools, contrasting
our Anthropic-4.x = 0 TEHR. Optionally `include-parts` as a reviewer-rubric pattern (six-way
failure taxonomy). License MIT = no vendoring risk; GPL/AGPL caveat N/A. Confidence: HIGH.
The survey did not overstate stars, license, or usability.
