# Repo Survey: CycleReviewer / CycleResearcher

- **Repo:** https://github.com/zhu-minjun/Researcher
- **Canonical (URL not 404):** valid; repo title is "CycleResearcher: Improving Automated Research via Automated Review"
- **Stars:** 384 | **Forks:** 35 | **Lang:** Jupyter Notebook (+ Python pkg `ai_researcher`)
- **Created:** 2024-08-15 | **Last push:** 2026-03-05 (actively maintained)
- **License:** **NOASSERTION** (GitHub `key=other`). Actual = custom **CycleResearcher-License**, a derivative of the **Mistral AI Research License**. NON-COMMERCIAL, registration-required, applies to BOTH code and model weights.
- **Category:** research-automation
- **Paper:** ICLR 2025, arXiv:2411.00816 (Weng, Zhu, Bao, Zhang, Wang, Zhang, Yang). DeepReviewer follow-up: arXiv:2505.07920.

## What it is
A closed-loop "AI scientist" system. Two coupled models:
- **CycleResearcher** (policy / paper generator): 12B (Mistral-Nemo), 72B (Qwen2.5), 123B (Mistral-Large).
- **CycleReviewer** (reward model / automated peer reviewer): Llama3.1-8B, Llama3.1-70B, Pro-123B. Emits per-criterion scores, `avg_rating`, and `paper_decision`.
- **DeepReviewer** (7B/14B): multi-perspective review + self-verification (Fast/Standard/Best modes).
- Also ships `AIDetector` (AI-text detection) and an `OpenScholar` RAG QA module.

Datasets: Review-5K (peer reviews), Research-14K (papers), DeepReview-13K.
Headline claims: CycleReviewer −48.8% Proxy MSE vs human reviewers, 74% decision accuracy; CycleResearcher-12B avg score 5.36 (vs 5.69 accepted, 4.31 AI Scientist).

Python pkg modules: `ai_researcher/{cycle_researcher,cycle_reviewer,deep_reviewer,detector}.py`.
API: `CycleReviewer(model_size="8B").evaluate(paper_text)` → list of dicts with `avg_rating`, `paper_decision`.

## Relevance to OUR paper (TEHR / tool-existence hallucination on BFCL multi-turn + RVR)
Domain mismatch is large. This is automated *paper review/generation*; we study *tool-call hallucination in agentic function-calling*. There is NO tool-use, function-calling, agent, or hallucination benchmark in this repo. So:

- **RUN as extra benchmark?** No. It is not a tool-use / hallucination eval. Off-axis from TEHR and BFCL/tau-bench. Would not strengthen the main-track breadth claim.
- **Reuse a COMPONENT in harness?** No. License is non-commercial + registration-gated and explicitly bars redistributing code separately from models. Pulling `cycle_reviewer.py` into our harness is a license-risk no-go, and the models (8B–123B Llama/Mistral/Qwen) don't fit our M5 32GB MLX setup or test tool-call behavior.
- **Reuse as a BASELINE?** No. Not a tool-calling model; not comparable to Anthropic 4.x / Qwen3-4bit on TEHR.
- **Cite as PRIOR ART?** **Yes — light cite.** Strong, well-cited ICLR 2025 example of "LLM-as-automated-reviewer / reward-model-as-reviewer." Useful as a contrast point in related work IF we frame our paper-revision skill / reviewer-personas as related to automated-review literature. It is the canonical citation for "models can simulate peer review with low proxy error."
- **Borrow a PATTERN for the paper-revision skill / reviewer personas?** **Yes — this is the real value.** Two transferable ideas:
  1. **Structured review schema:** CycleReviewer emits per-criterion ratings + `avg_rating` + binary `paper_decision`. Our reviewer personas could adopt the same rubric shape (per-criterion score → aggregate → accept/reject), which maps cleanly onto ICML review fields.
  2. **DeepReviewer's multi-perspective + self-verification loop:** mirrors our desired multi-persona reviewer + merge pattern. Worth reading `deep_reviewer.py` for the prompt structure of "simulate N reviewers, then reconcile." This is pattern/prompt inspiration only — no code copy needed (and the license forbids it anyway).

## License risk (honest)
HIGH for any code/model reuse. Custom non-commercial license derived from Mistral AI Research License, requires user registration (name, institutional email, purpose), prohibits commercial use and separate code redistribution, and mandates AI-assistance disclosure on outputs. Even for a research paper, do not vendor code or weights. Citing the paper and re-implementing a review *pattern* from scratch carries no license exposure.

## Verdict
- **integration_class:** reuse-pattern (for the paper-revision skill/personas) + cite-only (related work). NOT runnable as a benchmark, NOT a harness component, NOT a baseline.
- **effort:** low (read 1–2 files for prompt/rubric inspiration; add one related-work citation). Any attempt to actually run/integrate would be high effort + license-blocked.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verified against GitHub API + raw `LICENSE.md` (not the survey summary). All survey claims hold up; nothing was overstated.

**License (confirmed, exact):** SPDX = `NOASSERTION` (GitHub `license.key=other`). The file is `LICENSE.md`, titled **"CycleResearcher License" Version 1.0, 2024/10/24**, explicitly "based on the Mistral AI Research License." Read in full:
- §1.1 scope covers "models, code, algorithms, documentation, and data" — code AND weights.
- §2 mandates user registration (full name, institutional email, research purpose) before any use/modification/distribution.
- §4.1 strictly prohibits commercial use (incl. monetizing outputs).
- §4.2 forbids redistributing the code separately from the models without permission; derivative works must keep this License.
- §5.2 requires an attribution notice in any software incorporating the Materials.
- §11 governing law = China; exclusive jurisdiction = Hangzhou courts.
This is NOT an OSI-approved license and NOT a recognized SPDX identifier. It is a bespoke non-commercial, registration-gated research license. It is more restrictive than GPL/AGPL: GPL/AGPL at least permit commercial use and vendoring-with-copyleft, whereas this license bars commercial use outright AND bars separating the code from the models. Therefore the GPL/AGPL caveat in the task brief applies a fortiori here — we may cite and (after registration) run externally, but we may NOT vendor any code or weights into our (permissive-intended) ICML harness.

**Stars / forks (confirmed):** 384 stars, 35 forks. Order-of-magnitude = hundreds, exactly as surveyed. Not inflated.

**Package structure (confirmed):** `ai_researcher/{cycle_researcher,cycle_reviewer,deep_reviewer,detector}.py` all present; repo also has `OpenScholar/`, `evaluate/`, `setup.py`. The API surface the survey described is real.

**Off-axis (confirmed):** code search for `tool_call` / `function_calling` / `BFCL` in the repo = 0 hits. Confirmed: no tool-use, function-calling, agentic, or hallucination benchmark. Irrelevant as a TEHR/BFCL benchmark or baseline.

**Pressure-test of "cite-only" runnability with OUR MLX+API harness:**
- Can we RUN it? Only in principle, and only after registration. Models are Llama3.1-8B/70B + Mistral/Qwen 12B–123B. On an M5 32GB MLX box, only the 7B/8B (DeepReviewer-7B, CycleReviewer-8B) class is even loadable at 4-bit; 70B–123B are out of reach locally. And running it produces *paper reviews*, not tool-call traces — it cannot measure TEHR, so running it yields nothing for our results section.
- Can we REUSE code/weights in-repo? No — license-blocked (non-commercial + no separate code redistribution + registration). Hard no-go for vendoring.
- Net: the survey's "cite-only (+ reuse-pattern by clean re-implementation)" is the correct and honest call. The only legitimate uses are (a) one related-work citation (ICLR 2025, arXiv:2411.00816) for LLM-as-automated-reviewer, and (b) reading `deep_reviewer.py` for prompt/rubric *inspiration* to re-implement our reviewer-personas from scratch — no code copied.

**Verdict:** `cite-only`. License confirmed (bespoke non-commercial, NOASSERTION). No over-optimistic claims found in the survey; if anything it was appropriately conservative. Confidence: HIGH.

---

## ADVERSARIAL VERIFICATION #2 (2026-05-29, independent primary-source re-check by verifier agent)

Re-checked from scratch against the live GitHub API and the *decoded raw* `LICENSE.md` (not the survey summary, and not trusting the prior verification block). All claims hold; the survey is conservative, not over-optimistic.

**License (EXACT, re-confirmed from full decoded LICENSE.md):**
- SPDX = `NOASSERTION`; GitHub `license.key=other`, `license.name=Other`; file = `LICENSE.md`.
- Title: "CycleResearcher License", Version 1.0, 2024/10/24, "based on the Mistral AI Research License."
- §1.1: scope = "models, code, algorithms, documentation, and data" (code AND weights).
- §1.2 + §2: registration-gated (Full Name, Affiliation, Institutional Email, Research Purpose, Intended Use) before any use/modify/distribute.
- §4.1: commercial use strictly prohibited, including monetizing outputs.
- §4.2: "You may not redistribute the code separately from the Models without permission"; derivative works must keep this License.
- §5.2: software incorporating the Materials must carry a CycleResearcher attribution notice.
- §9.1: licensor reserves right to add restrictions / require re-acceptance.
- §11: governed by laws of China; exclusive jurisdiction = People's Courts in Hangzhou.
- NOT OSI-approved, NOT a recognized SPDX identifier. Bespoke non-commercial, registration-gated research license. STRICTLY MORE RESTRICTIVE than GPL/AGPL: copyleft licenses permit commercial use and vendoring-with-copyleft; this bars commercial use outright and bars separating code from models. The task's GPL/AGPL "cite/run-external but do not vendor" caveat therefore applies *a fortiori* — NO vendoring of any code or weights into our (permissive-intended) ICML harness.

**Stars / forks (re-confirmed live):** 384 stars, 35 forks. Order-of-magnitude = hundreds. Not inflated. created 2024-08-15, pushed 2026-03-05, primary language Jupyter Notebook.

**Off-axis (re-confirmed via code search):** GitHub code search in-repo for `BFCL` = 0, `function_calling` = 0, `tool_call` = 0. Top-level contents: `ai_researcher/`, `OpenScholar/`, `evaluate/`, `Tutorial/`, `generated_paper/`, `setup.py`. No tool-use, function-calling, agentic, or hallucination benchmark anywhere. Useless as a TEHR/BFCL/tau-bench benchmark or as a tool-calling baseline.

**Pressure-test of "cite-only" runnability with OUR MLX+API harness:**
- RUN it? Only in principle, only after registration. Models: Llama3.1-8B/70B + Mistral/Qwen 12B–123B. On M5 32GB MLX only the ~7B/8B class loads at 4-bit; 70B–123B unreachable locally. Critically, running it emits *paper reviews*, not tool-call traces — it cannot produce a TEHR number, so even a successful run contributes nothing to our results section.
- REUSE code/weights in-repo? Hard no — license-blocked (non-commercial + no separate code redistribution + registration + China jurisdiction). Vendoring is the worst-case license exposure of any repo surveyed so far.
- Legitimate uses only: (a) ONE related-work citation (ICLR 2025, arXiv:2411.00816) as the canonical "LLM-as-automated-reviewer / reward-model-as-reviewer" prior art; (b) reading `deep_reviewer.py` / `cycle_reviewer.py` for prompt/rubric *inspiration* to clean-re-implement our reviewer-personas + paper-revision skill from scratch — no code copied (license forbids it anyway, but clean re-implementation of an idea carries no exposure).

**Penalty check (over-optimism):** None found. If anything the survey under-states the license severity slightly by grouping it with GPL/AGPL-style risk; this license is harsher (no commercial use, no code/model separation, registration, foreign jurisdiction). The `cite-only` recommendation is correct and honest.

**Verdict:** `cite-only` (with clean-re-implement-pattern as the only real value). license_confirmed = true; license_spdx = NOASSERTION (CycleResearcher License v1.0, Mistral-AI-Research-License-derived, non-commercial). Confidence: HIGH.
