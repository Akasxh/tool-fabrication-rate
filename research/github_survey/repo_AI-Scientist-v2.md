# Repo Survey: AI-Scientist-v2

- **Repo:** SakanaAI/AI-Scientist-v2
- **URL:** https://github.com/SakanaAI/AI-Scientist-v2 (canonical; resolves fine, no 404)
- **Stars:** 6,395 | **Forks:** 856 | **Open issues:** 68 | **Lang:** Python | **Last push:** 2025-12-19 (active)
- **License:** "The AI Scientist Source Code License v1.0" (Dec 2025), based on Responsible AI Source Code License v1.1. GitHub reports `NOASSERTION` (i.e. NOT an OSI/SPDX-recognized license). **This is a use-restricted, non-OSS license.**
- **Category:** research-automation

## What it does
End-to-end autonomous ML research agent. Generates hypotheses, runs experiments via a progressive **agentic tree search** (managed by an "experiment manager" agent), produces plots, and writes full LaTeX manuscripts (ICML/ICBINB templates). Famous for producing the first fully-AI-authored paper accepted at a peer-reviewed workshop. Requires Linux + NVIDIA CUDA GPUs. Executes LLM-written code (sandbox/Docker strongly advised). Models via OpenAI / Gemini / Claude-on-Bedrock; optional Semantic Scholar for novelty/citations.

### Components
- `ai_scientist/perform_llm_review.py` — **automated NeurIPS-style reviewer** with a full rubric (Summary/Strengths/Weaknesses; Originality/Quality/Clarity/Significance 1-4; Soundness/Presentation/Contribution 1-4; Overall 1-10; Confidence 1-5; Decision Accept/Reject). Supports `num_reflections` (self-refine) and few-shot examples, plus deliberately biased `reviewer_system_prompt_neg`/`_pos` personas.
- `perform_vlm_review.py` — vision-language review of figures.
- `perform_writeup.py` / `perform_icbinb_writeup.py` — LaTeX manuscript generation.
- `perform_ideation_temp_free.py` — idea generation with S2 novelty checks.
- `treesearch/` — agentic tree-search experiment loop. `tools/`, `utils/`, `llm.py`, `vlm.py`.

## Concrete judgment for our paper (TEHR / RVR on BFCL+tau-bench)

**Run it as an extra benchmark?** No. It is a paper-generation pipeline, not a tool-calling benchmark. It has no notion of a tool registry or per-call tool-existence hallucination. No measurable overlap with TEHR. Also CUDA/Linux-only and runs arbitrary LLM code — wrong fit for our MLX + API harness. **integration_class: skip for benchmarking.**

**Reuse a component in our harness?** No, blocked by license. The license forbids... (well, it grants derivative rights but) carries RAIL use-restrictions + a mandatory "machine-generated" disclosure clause and full-license-redistribution requirement. Vendoring code into our harness imports those obligations. Not worth it for the small amount of code we'd want.

**Baseline?** No. There is no competing method to TEHR/RVR here.

**Cite as prior art?** Yes — this is the strongest concrete use. Cite as a flagship example of autonomous-agent / agentic-tree-search research systems and of **LLM-as-reviewer automation**, to motivate why reliable tool use (and detecting tool-existence hallucination) matters for agentic pipelines that call tools. Differentiate: we measure and intervene on a specific failure mode (TEHR + RVR), they build an open-ended discovery loop. effort: trivial (BibTeX from their `pub.sakana.ai` paper).

**Borrow a pattern for the paper-revision skill / reviewer personas?** Yes — **highest-value takeaway.** `perform_llm_review.py` is a clean, battle-tested template for:
  1. A structured ICML/NeurIPS reviewer rubric (the exact 1-10 Overall scale + Soundness/Presentation/Contribution + Confidence + Accept/Reject) we can mirror in our reviewer personas.
  2. The `num_reflections` self-refinement loop and few-shot-example conditioning for higher-quality reviews.
  3. Adversarial **positive vs. negative reviewer personas** (`reviewer_system_prompt_pos`/`_neg`) — directly maps to our skeptic/adversary reviewer-persona idea.
  Reimplement the *pattern* (prompt structure + reflection loop) from scratch rather than copying their file, to stay clear of the license. effort: low.

## License risk
**Medium-high if vendoring code; negligible if only citing or re-implementing patterns.** Custom RAIL-derivative with field-of-use restrictions (no surveillance, no undisclosed synthetic media/manuscripts, etc.), a mandatory machine-generated-content disclosure clause, and a requirement to ship the full license with any distribution of "Contribution or derivative works." Not OSI-approved; treat as proprietary-with-permissions. Safe path: cite + independently re-implement the reviewer-rubric/reflection pattern.

## Recommendation
- **cite-only** as the integration class for the paper.
- Independently re-implement the structured-reviewer-rubric + reflection + pos/neg-persona pattern for our paper-revision skill and reviewer personas (do not vendor their source).

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verified against the live repo via `gh api` and raw file fetches. Survey holds up well; corrections and sharpened caveats below.

### Confirmed
- **Stars: 6,395** (forks 857, open issues 68, lang Python, last push 2025-12-19, not archived). Order-of-magnitude (~6.4k) CONFIRMED via GitHub API.
- **License = NOASSERTION** confirmed three ways (repo `.license.spdx_id`, `/license` endpoint, `.license.key=other`). GitHub does NOT recognize it as OSI/SPDX. **SPDX: `LicenseRef-AIScientist-SourceCodeLicense-1.0` (NOT a registered SPDX id; effectively `NOASSERTION`).**
- **License text read directly** (`LICENSE`, 4256 bytes): "The AI Scientist Source Code License, Version 1.0, December 2025", explicitly "based on the Responsible AI Source Code License v1.1 (http://licenses.ai/)". Grant of Rights (Sec. 2) DOES permit reproduce / prepare derivative works / distribute, royalty-free. RAIL field-of-use restrictions confirmed (surveillance, undisclosed synthetic media, medical, criminal-risk-by-face, and the "AI Scientist" clause requiring machine-generated disclosure in abstract/Methods). Redistribution requires shipping a complete copy of the License. **Sec. 3.3 propagates the use-restrictions to all downstream recipients** (downstream agreements must contain the same restrictions). Survey's characterization is ACCURATE.
- **Runtime: Linux + NVIDIA CUDA + PyTorch confirmed** from README verbatim: "This code is designed to run on Linux with NVIDIA GPUs using CUDA and PyTorch." Executes LLM-written code; README explicitly warns to run inside a Docker sandbox. Providers: OpenAI, Gemini, Claude-via-AWS-Bedrock (requirements.txt confirms `anthropic` + `openai`; no `mlx`).
- **`perform_llm_review.py` exists** in `ai_scientist/` alongside `perform_vlm_review.py`, `perform_writeup.py`, `perform_icbinb_writeup.py`, `perform_ideation_temp_free.py`, `treesearch/`, `tools/`, `utils/`, `llm.py`, `vlm.py`. Reviewer-component claim CONFIRMED.

### Corrections / sharpened caveats
1. **It is NOT GPL/AGPL and NOT copyleft.** The task framed the worst case as "GPL/AGPL." Reality is different in mechanism but lands in a similar place for us: this is a **use-restricted RAIL-derivative**, not a reciprocal/viral license. The danger to us is NOT source-disclosure (copyleft) — it is that **vendoring imports RAIL field-of-use restrictions + a mandatory machine-generated-disclosure obligation + Sec 3.3 downstream-propagation** into our codebase, which we intend to release under a permissive license (MIT/Apache). That is a license-INCOMPATIBILITY for a permissive repo. So the practical conclusion ("can cite/run-externally, do NOT vendor into our permissive codebase") is CORRECT, just for RAIL-restriction reasons rather than copyleft reasons.
2. **"cite-only" pressure-test = HOLDS.** We genuinely cannot run it inside our harness: it is CUDA/Linux/PyTorch-only and our harness is MLX (Apple Silicon) + API. It is a paper-generation pipeline with no tool registry / function-calling / per-call tool-existence notion, so zero overlap with TEHR and useless as a TEHR benchmark or RVR baseline. Running it "externally" is technically possible only on rented Linux+NVIDIA (YC API credits don't supply GPUs; M5/MLX can't run it), so even external reproduction is a non-trivial infra lift with no payoff for our claims. **cite-only is the right call; do not even budget time to run it.**
3. **The only real value is the reviewer-rubric / reflection / pos-neg-persona PATTERN.** This is an IDEA we re-implement from scratch (the rubric structure is not itself copyrightable; copying their .py would import the license). Keep this as "borrow pattern, re-implement clean" — NOT a vendored dependency.

### Verdict
- **recommend: cite-only.** Cite as flagship autonomous-research-agent + LLM-as-reviewer prior art motivating reliable tool use. Re-implement (do not vendor) the structured-reviewer-rubric + `num_reflections` reflection loop + positive/negative reviewer personas for our paper-revision skill & reviewer personas.
- **license_confirmed: true** — read LICENSE file directly; custom RAIL-derivative, NOASSERTION/non-SPDX, use-restricted, downstream-propagating. NOT vendorable into a permissive repo.
- **No over-optimism penalty needed beyond the GPL-vs-RAIL framing fix** — original survey did not overstate stars, license openness, or usability.

---

## ADVERSARIAL VERIFICATION #2 (2026-05-29, second independent re-check)

Re-ran every load-bearing claim from scratch against the live repo (`gh api`, raw LICENSE/README/source decode). Findings below are my own, not inherited from the section above.

### Independently confirmed (this pass)
- **Stars 6,395 / forks 857 / open issues 68 / Python / pushed 2025-12-19 / not archived.** Order-of-magnitude ~6.4k CONFIRMED.
- **License = NOASSERTION** (`license.key=other`, `license.spdx_id=NOASSERTION`, `name=Other`). Confirmed via both the repo endpoint and the `/license` endpoint. There is **no valid registered SPDX identifier** — `NOASSERTION` is the correct machine value. Any `LicenseRef-*` string is a local convention, not a recognized SPDX id.
- **LICENSE text read in full (decoded from base64), all 8 sections.** "The AI Scientist Source Code License, Version 1.0, December 2025," explicitly based on Responsible AI Source Code License v1.1. Verified verbatim:
  - **Sec. 2 Grant**: non-exclusive, worldwide, royalty-free copyright license to reproduce / prepare derivative works / distribute. (So it is permissive-ish in the COPYRIGHT grant — NOT copyleft, NOT viral.)
  - **Sec. 3.1**: redistribution of any portion must ship a complete copy of the License.
  - **Sec. 3.2**: RAIL field-of-use restrictions confirmed — (a) surveillance/protected-class inference, (b) undisclosed synthetic audio/video media, (c) healthcare claim-prediction & unsupervised diagnosis, (d) criminal/face-based prediction, and **(e) the "AI Scientist" clause**: cannot generate/disseminate manuscripts without a prominent machine-generated disclosure (abstract / Methods / Disclosure section).
  - **Sec. 3.3**: those use-restrictions MUST be propagated as enforceable provisions into any downstream legal agreement governing use/distribution. (Downstream-propagation CONFIRMED — this is the real poison pill for vendoring.)
  - **Sec. 4 Termination**: licensor may terminate + demand destruction of all copies on any restricted use.
- **Runtime CUDA/Linux/PyTorch CONFIRMED verbatim** from README: "This code is designed to run on Linux with NVIDIA GPUs using CUDA and PyTorch," plus a conda `pytorch-cuda=12.4` install line and a "CUDA Out of Memory" FAQ. README explicitly warns it executes LLM-written code and must be run in a Docker sandbox.
- **No MLX.** `requirements.txt` lists `anthropic`, `openai`, `botocore`, `boto3` (Claude via AWS Bedrock) — **no `mlx`, no Apple-Silicon path.** Our M5/MLX box cannot run it; YC API credits do not supply the required NVIDIA GPUs.
- **Reviewer component CONFIRMED by reading `perform_llm_review.py` source**: it defines `reviewer_system_prompt_neg` AND `reviewer_system_prompt_pos` (biased personas), a `num_reflections` self-refine loop (`if num_reflections > 1:`), few-shot conditioning (`get_review_fewshot_examples`), and the exact rubric — Originality/Soundness/Presentation/Contribution (1-4), Overall (1-10), Confidence (1-5), binary Accept/Reject decision. Highest-value reuse pattern is real.

### Claims-check / over-optimism audit
- Stars: NOT overstated (exact match). License: the original survey correctly flagged it as non-OSS use-restricted, NOT as permissive/MIT — no over-optimism. Usability: original correctly said skip-for-benchmarking and cite-only — no over-optimism. **Nothing to penalize.**
- One framing note (same as pass #1): the task's worst-case hypothesis was "GPL/AGPL." Reality is a **RAIL-derivative use-restricted license, not copyleft.** Mechanism differs but the operative conclusion is identical and arguably stronger: the Sec-3.2 field-of-use restrictions + Sec-3.3 mandatory downstream propagation are **incompatible with releasing our harness under a permissive license (MIT/Apache)**, because we'd have to bind every downstream user of our repo to RAIL restrictions. So: cite/run-externally OK, **do NOT vendor any source into our codebase** — confirmed for RAIL-restriction reasons.

### "cite-only" pressure-test — HOLDS (independently)
Can we actually run/reuse it given MLX+API harness + this license?
- **Run as TEHR benchmark?** No. It is a paper-generation/discovery pipeline. No tool registry, no function-calling, no per-call tool-existence notion → zero overlap with TEHR; useless as RVR baseline.
- **Run at all on our infra?** No. CUDA/Linux/PyTorch-only; our harness is MLX (Apple Silicon) + cloud API. External repro would require renting Linux+NVIDIA GPUs for zero payoff to our claims. Don't budget time.
- **Vendor a component?** No — license blocks it for a permissive release (see above).
- **Reuse the reviewer pattern?** Yes, but as a clean RE-IMPLEMENTATION of the idea (rubric structure + reflection loop + pos/neg personas), not by copying the licensed `.py`. A rubric/scale is not itself copyrightable; the source file is.

### Verdict (this pass)
- **recommend: cite-only.** Cite as flagship autonomous-research-agent + LLM-as-reviewer prior art to motivate why reliable tool use / detecting tool-existence hallucination matters in agentic pipelines. Re-implement (do NOT vendor) the structured reviewer rubric + `num_reflections` reflection loop + positive/negative reviewer personas for our paper-revision skill & reviewer personas.
- **license_spdx: NOASSERTION** (no valid registered SPDX id; custom RAIL-derivative "AI Scientist Source Code License v1.0").
- **license_confirmed: true** — LICENSE read in full directly from the repo this pass.
- **confidence: high.** Every claim re-checked against live repo; no discrepancies with pass #1.
