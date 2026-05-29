# AgentLaboratory (SamuelSchmidgall)

- **Repo:** https://github.com/SamuelSchmidgall/AgentLaboratory
- **Stars:** 5,649 | **Language:** Python
- **License:** **MIT** (SPDX `MIT`, OSI-approved, permissive — confirmed via `gh api .license.spdx_id`)
- **Paper:** "Agent Laboratory: Using LLM Agents as Research Assistants" (arXiv:2501.04227, AMD + Johns Hopkins) | **Category:** research-automation
- **Last pushed:** 2025-08-20 (not archived; moderately stale, ~9 months idle as of survey)

## What it does
End-to-end autonomous research-assistant pipeline. Three sequential phases driven by role-specialized LLM agents:
1. **Literature Review** — agents pull and analyze arXiv papers.
2. **Experimentation** — collaborative plan formulation, data prep, and automated code execution via an `mlesolver` (iterative ML-engineering code-writer/runner). Example task domain: the MATH dataset.
3. **Report Writing** — `papersolver` generates a LaTeX paper, optionally compiled with pdflatex.

Backends: OpenAI (o1 / o1-preview / o1-mini / gpt-4o / o3-mini) and DeepSeek (deepseek-v3) selected via `--llm-backend`. Executes LLM-written Python (containerization advised). Has an **AgentRxiv** extension where agents share/build on prior generated research.

Monolithic top-level Python (no package): `agents.py`, `ai_lab_repo.py` (entrypoint), `mlesolver.py`, `papersolver.py`, `inference.py`, `tools.py`, `utils.py`, plus `experiment_configs/`. No abstraction layers, no plugin system.

## License risk
None of note. MIT is permissive and OSI-approved — we may vendor, fork, or copy code with attribution and no behavioral-use or manuscript-disclosure clauses (contrast with AI-Scientist's RAIL-style license + "AI Scientist clause"). This makes it the *safer* of the two autonomous-research repos to borrow code from if desired.

## Concrete judgment for our SCALE/TEHR paper
- **Run as extra benchmark?** **No.** Not a tool-calling or tool-existence benchmark; produces no per-call TEHR-style metric and nothing comparable to BFCL/tau-bench multi-turn. It is an open-ended research-generation pipeline. Out of scope for our harness's `bench_loaders/*.py`.
- **Reuse a component in harness?** **No (low value).** Its `inference.py`/backend layer only wraps OpenAI + DeepSeek, lacks Anthropic 4.x and any MLX/local-model path, and is written as a flat script rather than a reusable library. Our harness already runs MLX + API models; nothing here improves on that. `mlesolver`/`papersolver` are coupled to the full agent loop and not cleanly extractable.
- **Use as a baseline?** **No.** Different task (autonomous research generation vs. tool-existence hallucination measurement). Not a comparable system on any axis we measure.
- **Cite as prior art?** **Yes — recommended (secondary).** Canonical reference for the LLM-agents-as-research-assistants line, alongside AI-Scientist. Useful to position our paper-revision skill and the broader autonomous-research framing, and to note that these pipelines write papers but do **not** audit tool-call reliability — a gap our TEHR work addresses.
- **Borrow a PATTERN for the paper-revision skill / reviewer personas?** **Yes — modest value.** Two patterns worth studying (MIT lets us copy directly if we choose):
  - **`papersolver.py`** — iterative paper-writing/refinement loop (draft → critique → revise per LaTeX section). A reference for a section-wise revision controller in our paper-revision skill.
  - **`agents.py` role specialization** — distinct agent roles (PhD student, postdoc, professor, reviewer) with role-conditioned system prompts. A lighter-weight template for reviewer personas than AI-Scientist's, but AI-Scientist's `perform_review.py` (structured NeurIPS rubric + neg/pos reviewer priors + meta-reviewer) remains the richer source for the *reviewer* side specifically.

## Recommendation
Cite-only for the manuscript (prior art on autonomous research assistants; contrast that these systems do not measure tool-call/tool-existence reliability). Optionally reuse-pattern: study `papersolver.py`'s iterative section-revision loop and `agents.py` role prompts for the paper-revision skill; MIT permits direct copy with attribution, but the code is thin enough that reimplementing is cleaner. Do not run it as a benchmark, vendor it into the harness, or use it as a baseline.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

**Method:** `gh api` for metadata + decoded LICENSE file; direct inspection of `inference.py`, `agents.py`, `papersolver.py`, `requirements.txt`; README cross-check via WebFetch.

### Confirmed
- **License = MIT (SPDX `MIT`), CONFIRMED from the actual LICENSE file** (full MIT text, "Copyright (c) 2025 Samuel Schmidgall"), not just GitHub's heuristic `spdx_id`. Genuinely permissive/OSI-approved. We MAY vendor, fork, or copy with attribution. No GPL/AGPL/RAIL/behavioral-use clause — no copyleft contamination of our (permissive) harness. The survey's license claim is fully accurate.
- **Stars = 5,649** (exact, via API), order-of-magnitude ~5.6k. Accurate.
- **Not archived; last push 2025-08-20.** Accurate.
- **Not a tool-calling / tool-existence benchmark.** Confirmed — it is an autonomous research-generation pipeline. Produces no per-call TEHR-style metric, nothing comparable to BFCL/tau-bench. Survey accurate. **Run-as-benchmark and use-as-baseline verdicts (both "No") stand.**

### Survey claims CORRECTED (over-/under-statements found)
1. **Backend claim OVER-STATED (minor inaccuracy).** Survey says `inference.py` "only wraps OpenAI + DeepSeek, lacks Anthropic 4.x and any MLX/local-model path." Reality: the code has explicit branches for **Anthropic (`claude-3-5-sonnet`, pinned `claude-3-5-sonnet-latest`) and Google Gemini (1.5-pro, 2.0-pro)** in addition to OpenAI (gpt-4o/o1/o3-mini) and DeepSeek. So "only OpenAI + DeepSeek" is wrong for the *code* (it matches only the *README's advertised* backends). HOWEVER the load-bearing sub-claims hold: **no Anthropic 4.x** (capped at 3.5, hardcoded model strings), and **zero MLX/local/vLLM/ollama/HF-local path** (grep confirms: only `base_url` is DeepSeek's cloud endpoint). For our MLX + Anthropic-4.x harness, the backend layer is still **not reusable** — wrong model generation, no local inference, flat hardcoded `query_model` with per-model if/elif branches. Reuse-component verdict ("No / low value") stands.
2. **Reviewer-persona value UNDER-STATED.** Survey says AI-Scientist's `perform_review.py` "remains the richer source for the reviewer side." But `agents.py` contains a `ReviewersAgent` with a **3-persona reviewer ensemble** (harsh-but-fair / impact-focused / novelty-focused) feeding a `get_score()` numeric scorer, plus a full role hierarchy (`ProfessorAgent`, `PostdocAgent`, `MLEngineerAgent`, `SWEngineerAgent`, `PhDStudentAgent`, each with `role_description()` + phase-conditioned prompts) and an ICLR-submission framing. This is **directly relevant** to the user's reviewer-persona / paper-revision-skill goal and is a stronger pattern source than the survey credited. MIT permits direct copy with attribution.
3. **`papersolver.py` pattern CONFIRMED and stronger than described.** `PaperSolver.solve()` runs a step loop with `PaperReplace` (full rewrite) and `PaperEdit` (line-range edit, N M) commands that are **error-gated** (LaTeX must compile or the edit is rejected). A genuinely good reference for a section-wise, compile-validated revision controller in our paper-revision skill.

### "Cite-only" claim — pressure-tested
**Holds as the primary manuscript recommendation, but it is more precisely "cite-only + optional pattern-borrow."** Could we actually run/reuse it under our MLX+API harness + (permissive) license?
- **License:** No blocker. MIT lets us run externally AND vendor/copy. (Contrast the brief's GPL/AGPL warning — N/A here; nothing to flag.)
- **Run it end-to-end?** Possible but low value: it would need API keys, a pinned Python 3.12 env, a heavy `requirements.txt` (tensorflow, diffusers, datasets, accelerate, etc.), and it targets old model generations. It cannot exercise our MLX local models or Anthropic 4.x without code edits. No reason to run it for our TEHR work.
- **Vendor a component?** Legally yes (MIT); practically the code is flat/monolithic, `mlesolver`/`papersolver` are coupled to the full agent loop and `inference.py`. Reimplementing the *patterns* is cleaner than vendoring. The reviewer-persona/role-prompt and compile-gated-edit ideas are worth lifting conceptually.

### Adjusted recommendation
**`include-parts`** (lean: cite-only for the manuscript + borrow the reviewer-persona ensemble and compile-gated section-edit patterns for the paper-revision skill / reviewer personas). Do NOT run as benchmark, do NOT use as baseline, do NOT vendor the backend/inference layer. License is a clean MIT — no copyleft risk to our codebase.

**Confidence: high.** License verified from file; stars/metadata from API; code claims verified by direct inspection. The two survey inaccuracies are minor and do not change the run/benchmark/baseline verdicts.

---

## SECOND INDEPENDENT RE-VERIFICATION (2026-05-29, fresh pass)

**Method:** Re-ran `gh api repos/.../{,/license}` and decoded the LICENSE file from scratch; re-fetched and grepped `inference.py`, `agents.py`, `papersolver.py` directly from the GitHub contents API. Did not rely on the prior verification block.

### Independently CONFIRMED
- **License = MIT (SPDX `MIT`).** Decoded LICENSE file = canonical MIT text, "Copyright (c) 2025 Samuel Schmidgall". `license.spdx_id` from API also = `MIT`. **No GPL/AGPL/RAIL/behavioral-use clause.** We may run-externally AND vendor/fork/copy with attribution; no copyleft contamination of our permissive harness. The brief's GPL/AGPL warning is N/A — nothing to flag. License claim is fully accurate; `license_confirmed = true`.
- **Stars = 5,649** (exact, API). Order-of-magnitude ~5.6k. Accurate.
- **Not archived; last push 2025-08-20.** Accurate (~9mo idle).
- **Backend layer:** `query_model` has hardcoded if/elif branches for gpt-4o / gpt-4o-mini / o1 / o1-mini / o1-preview / o3-mini, `claude-3-5-sonnet` (pinned `claude-3-5-sonnet-latest`), gemini-1.5-pro / gemini-2.0-pro, deepseek-chat. **Confirmed: no Anthropic 4.x** (grep for claude-4/3-7/opus/sonnet-4 = 0 hits; capped at 3.5). **Confirmed: zero local-inference path** (grep for mlx/ollama/vllm/llama_cpp/transformers/torch/localhost in inference.py = 0; only `base_url` present is DeepSeek's cloud endpoint). For our MLX + Anthropic-4.x harness the backend is NOT reusable. Survey's original "only OpenAI + DeepSeek" wording is wrong for the *code* (Anthropic-3.5 + Gemini branches exist), but the load-bearing conclusions are correct.
- **Reviewer personas:** `ReviewersAgent` (agents.py:184) runs a **3-reviewer ensemble** — reviewer_1 "harsh but fair", reviewer_2 "impactful in the field", reviewer_3 "novel ideas" — each calling `get_score()`. `get_score()` embeds a full **NeurIPS-style 1-10 rubric** (Award quality / Strong Accept / Strong Reject, soundness/presentation/contribution). Full role hierarchy confirmed: `ProfessorAgent`, `PostdocAgent`, `MLEngineerAgent`, `SWEngineerAgent`, `PhDStudentAgent`, each with `role_description()` + phase-conditioned prompts. **Directly relevant** to the reviewer-persona / paper-revision-skill goal.
  - *Minor correction to prior block:* the rubric is **NeurIPS-framed (1-10 award scale)**, not "ICLR-submission framing" as the first verification stated. Does not change value.
- **`papersolver.py` compile-gated edit loop CONFIRMED.** `PaperReplace` (full rewrite) and `PaperEdit N M` (line-range edit) both route through `compile_latex(...)`; on a LaTeX error the edit is **rejected and reverted** (`if "error" in latex_ret.lower(): return (False, ...)`; "Paper was reverted back to original state before edits"). Genuine compile-validated, section-wise revision controller — a good reference for our paper-revision skill.

### "Cite-only" — re-pressure-tested
Confirmed it should be **cite-only for the manuscript + optional pattern-borrow**, NOT run-as-benchmark / baseline / backend-vendor:
- It is an autonomous research-*generation* pipeline; emits no per-call tool-existence signal, nothing comparable to BFCL/tau-bench multi-turn. Cannot produce a TEHR-style metric. Run-as-benchmark and use-as-baseline = **No** (stand).
- License permits vendoring, but the code is flat/monolithic and `mlesolver`/`papersolver` are coupled to the full agent loop + `inference.py`; reimplementing the *patterns* (3-persona reviewer ensemble, NeurIPS-rubric scorer, compile-gated section edit) is cleaner than vendoring. Backend layer is not worth lifting (wrong model generation, no local path).

### Verdict
**`include-parts`** — cite-only in the manuscript (prior art on autonomous research assistants; contrast that these systems write papers but do NOT audit tool-call / tool-existence reliability, which is our gap) + optionally borrow the reviewer-persona ensemble, NeurIPS-rubric scorer, and compile-gated section-edit patterns for the paper-revision skill / reviewer personas. Do NOT run as a benchmark, do NOT use as a baseline, do NOT vendor the backend/inference layer. License = clean MIT; no copyleft risk.

**Confidence: high.** Two independent passes agree; the only discrepancies found are cosmetic (survey's "OpenAI+DeepSeek only" understated the backend list; prior block's "ICLR framing" should be "NeurIPS rubric"). None affect the run/benchmark/baseline/license verdicts.
