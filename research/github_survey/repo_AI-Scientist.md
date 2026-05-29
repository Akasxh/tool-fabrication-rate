# AI-Scientist (SakanaAI)

- **Repo:** https://github.com/SakanaAI/AI-Scientist
- **Stars:** ~13,812 | **Forks:** ~1,963 | **Open issues:** 116
- **Language:** Python (repo tagged Jupyter Notebook by GitHub)
- **License:** **NOT OSS.** Custom "The AI Scientist Source Code License v1.0" (Dec 2025), derived from the Responsible AI Source Code License v1.1 (licenses.ai). `gh api` reports SPDX = `NOASSERTION`.
- **Paper:** arXiv:2408.06292 | **Category:** research-automation
- **Last pushed:** 2025-12-19 (actively maintained)

## What it does
First end-to-end "fully automated scientific discovery" pipeline: an LLM (1) generates research ideas + novelty-checks them against Semantic Scholar, (2) runs ML experiments via Aider on code templates (NanoGPT, 2D Diffusion, Grokking), (3) writes a LaTeX paper, and (4) runs an **automated LLM reviewer** that scores the paper on a NeurIPS rubric. Core modules: `ai_scientist/{generate_ideas,perform_experiments,perform_writeup,perform_review,llm}.py`. It executes LLM-written code (the README explicitly warns to containerize).

## License risk (important)
- Custom RAIL-style license, **not OSI-approved**. Behavioral-use restrictions (no surveillance, no synthetic media without watermark, etc.) plus a viral clause: §3.3 requires those restrictions be passed into any agreement governing derivative works.
- **§3.2(e) "The AI Scientist Clause":** any scientific manuscript/paper produced *using* the software must prominently disclaim that content was machine-generated/produced with The AI Scientist.
- Implication: do **not** vendor its code into our harness, and if any AI-Scientist component touches our ICML manuscript we incur a disclosure obligation. Safe path = cite + reimplement patterns ourselves, no code copied.

## Concrete judgment for our SCALE/TEHR paper
- **Run as extra benchmark?** No. It is not a tool-calling / tool-existence benchmark and produces no per-call TEHR metric. Orthogonal to BFCL/tau-bench. Out of scope.
- **Reuse a component in harness?** No. License (non-OSI + viral + manuscript-disclaimer) makes vendoring code into `harness/` a liability. Our bench_loaders pattern (BFCL, tau-bench) has no overlap with its experiment-runner.
- **Use as a baseline?** No. Different task (open-ended discovery vs. tool-existence hallucination). Not a comparable system.
- **Cite as prior art?** **Yes — recommended.** Canonical reference for LLM-as-automated-reviewer and autonomous-research framing. Cite to (a) position our paper-revision skill / reviewer personas against a known automated-review system, and (b) acknowledge the limits of LLM reviewers (Sakana's own analysis shows the auto-reviewer is lenient/biased) — useful for our reviewer-persona calibration discussion.
- **Borrow a PATTERN for the paper-revision skill / reviewer personas?** **Yes — highest-value use.** `ai_scientist/perform_review.py` is a clean, study-only reference (do not copy text/code) for:
  - A structured NeurIPS review form: Summary, Strengths, Weaknesses, Originality, Quality, Clarity, Significance, Questions, Limitations, Ethics, **Soundness (1-4)**, **Presentation (1-4)**, **Contribution (1-4)**, **Overall (1-10)**, **Confidence (1-5)**, **Decision (Accept/Reject)**.
  - **Persona priors:** `reviewer_system_prompt_neg` vs `reviewer_system_prompt_pos` (harsh-vs-lenient reviewer biases) — directly maps to building distinct reviewer personas.
  - **Meta-reviewer / Area-Chair** prompt (`get_meta_review`) that aggregates multiple reviews — a model for a "merge" reviewer in our parallel-reviewer pattern.
  - **Ensembling + self-reflection:** runs N reviewers and averages numeric scores; optional reflection rounds to refine — a rubric-scoring + self-consistency pattern for the revision skill.
  - **Few-shot review examples** (`get_review_fewshot_examples`) to anchor score calibration.

## Recommendation
Cite-only for the manuscript (prior art on automated research + LLM reviewing) AND reuse-pattern for the skill: reimplement our own reviewer personas + meta-reviewer + rubric ensemble informed by `perform_review.py`, written from scratch so no licensed code or manuscript-disclaimer obligation attaches. Do not run it, vendor it, or use it as a baseline.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

**Method:** `gh api` on live repo + decoded the actual `LICENSE` blob + read `requirements.txt`, repo tree, and `ai_scientist/perform_review.py` source. Did not trust the summary.

### License — CONFIRMED, with one framing correction
- **SPDX = `NOASSERTION`** (`license.key = "other"`, name "Other"). Confirmed via API. There is no OSI SPDX identifier; do not record a standard SPDX tag.
- LICENSE file is verbatim **"The AI Scientist Source Code License, Version 1.0, December 2025"**, "based on the Responsible AI Source Code License v1.1 (http://licenses.ai/)". Confirmed.
- §3.2(e) **"The AI Scientist" Clause** (manuscript machine-generated disclosure) — confirmed verbatim.
- §3.3 viral pass-through of restrictions into derivative-work agreements — confirmed verbatim.
- §4 termination on restricted use — confirmed.
- **CORRECTION to the user's GPL/AGPL framing:** This is NOT a copyleft license. §2 grants a permissive copyright license (royalty-free reproduce / prepare derivative works / distribute) with **no share-alike on the code**. The "viral" element is *behavioral-use* (RAIL-style restrictions in §3.2 + the §3.3 pass-through), NOT source-disclosure copyleft. So the GPL/AGPL mental model is the wrong axis: the blocker for us is (a) non-OSI status, (b) §3.2(e) manuscript-disclaimer obligation that would attach to our ICML paper if AI-Scientist code touches it, and (c) §3.3 requiring we propagate the use-restrictions. Net effect for a permissive ICML codebase = still **do not vendor** (incompatible obligations + manuscript disclaimer), even though it's technically not copyleft.

### Stars / maintenance — CONFIRMED
- 13,812 stars, 1,963 forks, 116 open issues, pushed 2025-12-19, not archived. Order of magnitude (~14k) is correct. Actively maintained.
- Language reported by GitHub = **Jupyter Notebook** (survey's parenthetical was right; "Python" is the substantive language).

### "Cite-only" pressure-test — HOLDS, with a sharper runnability note
- `requirements.txt` LLM backends = `anthropic`, `openai`, `google-generativeai` + `aider-chat`. **API side is compatible** with our API harness.
- **MLX is NOT supported.** Local experiment templates run on `torch`/`transformers` (NanoGPT etc.). The "run with our MLX+API harness" idea is only half-true: our MLX models cannot drive its experiment runner without a custom backend. So even setting aside the license, it does not slot into our MLX path.
- It is an **open-ended discovery pipeline (idea→experiment→writeup→LLM-review)**, produces **no per-call tool-existence/TEHR metric**, and is not a tool-calling benchmark. Orthogonal to BFCL/tau-bench. NOT a baseline, NOT an extra benchmark. Confirmed.
- **Pattern-reuse claims VERIFIED in source** (`perform_review.py`): `reviewer_system_prompt_neg`/`_pos` personas, NeurIPS rubric (Soundness/Presentation/Contribution 1-4, Overall 1-10, Confidence 1-5), `num_reviews_ensemble` averaging, `num_reflections` reflection rounds, `get_review_fewshot_examples`, `get_meta_review`. These are real and the "reimplement from scratch, do not copy" guidance is the right call (copying code/text would drag in the §3.2(e)+§3.3 obligations).

### Verdict
**cite-only** (prior art on automated research + LLM-as-reviewer), plus study-only pattern reference for our reviewer personas / meta-reviewer / rubric-ensemble — reimplemented from scratch, no licensed code copied. Do not vendor, do not run as a benchmark, not a baseline. Survey was accurate; only over-optimistic element was the implicit "MLX+API runnable" assumption (API yes, MLX no) and the GPL/AGPL framing is the wrong license axis (it's RAIL behavioral-use, not copyleft).

---

## ADVERSARIAL RE-VERIFICATION #2 (2026-05-29, independent, Opus)

**Method:** Re-ran everything from the live repo, did NOT trust the survey OR the prior verification block. `gh api` for metadata; decoded the raw `LICENSE` blob (read full text, all 8 sections); pulled `requirements.txt`; grepped the whole repo for `mlx`; read symbol-level evidence from `ai_scientist/perform_review.py`.

### License — CONFIRMED (exact text read, not summarized)
- `license.key = "other"`, `license.name = "Other"`, **SPDX = `NOASSERTION`**. There is NO valid OSI SPDX identifier. Do not record a standard SPDX tag — `NOASSERTION` is the only honest value.
- LICENSE file verbatim: **"The AI Scientist Source Code License, Version 1.0, December 2025"**, explicitly "based on the Responsible AI Source Code License v1.1 (http://licenses.ai/)". Confirmed by decoding the blob.
- **§2 grants a permissive copyright license** (royalty-free reproduce / prepare derivative works / distribute). Read verbatim — there is NO source-disclosure / share-alike clause. **This is NOT GPL/AGPL and NOT copyleft.**
- **§3.2(e) "The AI Scientist" Clause CONFIRMED verbatim:** any scientific manuscript/research paper/technical report generated or disseminated using the Contribution must prominently disclaim (abstract, or a Disclosure/Methods section) that content was machine-generated or produced using The AI Scientist.
- **§3.2(a)-(d)** RAIL behavioral-use restrictions (surveillance, synthetic-media-without-watermark, healthcare, criminal-prediction) — confirmed.
- **§3.3 CONFIRMED verbatim:** the §3.2 restrictions MUST be propagated as an enforceable provision into any legal agreement governing use/distribution of the Work or derivatives. This is the "viral" element — viral on *use-restrictions*, not on source.
- **§4** termination on restricted use — confirmed.

**On the user's GPL/AGPL framing:** The user's question framed the worry as "GPL/AGPL = cite/run-externally but not vendor." That copyleft axis is the WRONG model here, and answering it literally would be misleading. The actual license is permissive-grant + RAIL-behavioral-restrictions. **But the user's bottom-line instinct is still correct, just for different reasons:** we must NOT vendor AI-Scientist code into our (permissive) ICML codebase, because (1) it is non-OSI / `NOASSERTION` and incompatible with declaring a clean permissive license on our repo; (2) §3.3 would force us to inject Sakana's use-restrictions into our project's license terms; and (3) §3.2(e) would attach a "machine-generated" disclaimer obligation to our ICML manuscript the moment AI-Scientist code participates in producing it. So: same "do not vendor" verdict, corrected legal reasoning.

### Stars / maintenance — CONFIRMED
- 13,812 stars (order of magnitude ~14k — correct), 1,963 forks, 116 open issues, pushed 2025-12-19, not archived. Actively maintained.
- GitHub primary language = **Jupyter Notebook** (substantive language is Python). Survey's parenthetical was accurate.

### "Cite-only" pressure-test — HOLDS. Two over-optimistic claims penalized.
- **API path:** `requirements.txt` ships `anthropic`, `openai`, `google-generativeai`, `aider-chat`. Compatible with our API harness. TRUE.
- **MLX path: FALSE / over-optimistic.** Whole-repo code search for `mlx` returns exactly ONE hit, and it is in `review_iclr_bench/iclr_parsed/PlFtf_pnkZu.txt` — a parsed ICLR paper used as review-benchmark *data*, NOT a backend. Local experiment templates run on `torch`/`transformers`/`datasets` (NanoGPT-style). **There is zero MLX support.** Our MLX models cannot drive its experiment runner without writing a custom backend. Any implication that AI-Scientist is "runnable on our MLX+API harness" is only half-true (API yes, MLX no). PENALIZED.
- **Not a benchmark / not a baseline:** It is an open-ended discovery pipeline (idea -> experiment -> writeup -> LLM-review). It emits NO per-call tool-existence signal, NO TEHR, and is not a tool-calling benchmark. Orthogonal to BFCL / tau-bench. Cannot be a baseline for TEHR/RVR and cannot serve as an extra tool-existence benchmark. CONFIRMED.
- **Pattern-reuse claims VERIFIED at symbol level in `perform_review.py`:** `reviewer_system_prompt_neg` (line 18) / `reviewer_system_prompt_pos` (line 22) harsh-vs-lenient personas; NeurIPS rubric Soundness 1-4 / Overall 1-10 / Confidence 1-5 (lines 54-58, 182-186); `num_reviews_ensemble` averaging (lines 132, 151, 161); `num_reflections` reflection rounds (lines 130, 222-224); `get_review_fewshot_examples` (line 323); `get_meta_review` area-chair aggregation (lines 170, 361). All real. "Reimplement from scratch, copy nothing" is the correct guidance — copying any code/text would drag in §3.3 + §3.2(e).

### Net verdict (independent)
**recommend = cite-only.** Cite as prior art on automated scientific discovery and LLM-as-reviewer; use `perform_review.py` as a STUDY-ONLY reference for our reviewer personas / meta-reviewer / rubric-ensemble, reimplemented from scratch with no licensed code copied. Do NOT vendor (non-OSI + §3.3 use-restriction propagation + §3.2(e) manuscript-disclaimer that would taint our ICML paper). Do NOT run as a benchmark, NOT a baseline, NOT on our MLX path (no MLX support). 
- license_confirmed = true; license_spdx = NOASSERTION.
- Survey was substantively accurate. Penalized claims: (1) implicit "MLX+API runnable" — API only, no MLX backend exists; (2) the GPL/AGPL framing in the task is the wrong license axis — it's RAIL permissive-grant + behavioral-use restrictions, not copyleft, though the "do not vendor" conclusion still stands.
- Confidence: HIGH (license text read verbatim, metadata + source confirmed live).
