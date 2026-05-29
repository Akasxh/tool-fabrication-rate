# Anonymization & Ethics Review — Round 2

**Reviewer**: Anonymization & Ethics (paranoid-but-precise persona)
**Date**: 2026-04-27
**Scope**: all `*.md`, `*.tex`, `*.py` files under `/Users/cero/Desktop/PROJECTS/icml/`, excluding `harness/data/` (vendored datasets) and `.git/`.

---

## Anonymization scan

Bash invoked: `grep -rni '<pattern>' --include='*.md' --include='*.tex' --include='*.py' --exclude-dir='data' --exclude-dir='.git'`. Counts below are **our-files** only; vendored hits in `harness/data/` are explicitly excluded by the `--exclude-dir=data` clause.

| Pattern | Hits in our files | Verdict |
|---|---|---|
| `akash` | **22** (PAPER_PLAN.md ×4, PAPER_PLAN_v2.md ×3, PAPER_PLAN_v3.md ×6, PAPER_PLAN_v3.1.md ×2, PHASE0/REVIEW_phase0.md ×6, PHASE0/REVIEWS/R1_synthesis.md ×3) | **FAIL** — not yet a paper-ship blocker (these are planning docs, not the paper), **but the strings will trip a supplementary-zip grep if any of these files are bundled.** Plan docs are unlikely to ship; double-check before zipping. |
| `iit` / `patna` | 0 (only as denied-list mentions inside the plan’s anonymization checklists, no real institution string) | PASS |
| `vllm` (in our files) | 0 hits in code/comments; **all 4 hits are inside denied-list bullets** (`PAPER_PLAN*.md`, `REVIEW_phase0.md`) talking *about* the deny-list. Vendored mentions in BFCL/τ-bench are out of scope. | PASS |
| `cern` / `gsoc` | 0 (only in deny-list bullets) | PASS |
| `gmail.com` / hand-typed personal email | 0 in our files. `paper/icml2026/example_paper.tex:101-102` has `first1.last1@xxx.edu` and `first2.last2@www.uk` — **template placeholders, harmless**. `harness/tests/test_logging_cost.py:181` uses `my_email@example.com` — **test fixture, not real.** | PASS |
| `github.com/` (hand-typed repo URLs) | 4 hits — `PHASE0/model_ids.md:48,111` (links to public OpenAI SDK release page); `PHASE0/dataset_status.md:16-17` (BFCL Gorilla repo + τ-bench Sierra repo). **All are vendor/dataset upstream URLs, not author handles.** | PASS — but `model_ids.md` should not ship in the supplementary zip. |
| `\author{}` / `\icmlauthor{}` non-Anonymous | `paper/main.tex:29` → `\author{Anonymous Submission \\ \small SCALE Workshop, ICML 2026}` ✓ PASS. `paper/icml2026/example_paper.tex:83-92` has `Firstname1 Lastname1` etc. — these are **upstream ICML template placeholders** in a vendored style folder; will not ship as the live paper. PASS as long as `main.tex` is the compile target (it is). |
| `pdfinfo` metadata | Cannot check pre-compile. **Phase-6 action item**: run `pdfinfo paper.pdf` and `pdftotext paper.pdf - \| head -50` before zip. Already on the v2/v3 checklist. |

**Subverdict**: PASS for the live paper artifact (`paper/main.tex` + `paper/sections/*.tex` + `paper/refs.bib`). FAIL for the planning corpus, but only if it ships.

---

## Ethics audit

- **Dataset licenses — CONFIRMED**.
  - `harness/data/bfcl_v4/repo/LICENSE` first line: `Apache License Version 2.0, January 2004` → matches `dataset_status.md:16` claim of Apache 2.0. ✓
  - `harness/data/tau_bench_retail/LICENSE` first lines: `MIT License / Copyright (c) 2024 Sierra` → matches `dataset_status.md:17` claim of MIT (© 2024 Sierra). ✓
- **Model attribution — CONFIRMED in §4 setup** (`paper/sections/04_setup.tex:6` names Anthropic, OpenAI, and Qwen3 with the MLX runtime, with vendor-tagged tier labels). xAI/Grok is parked as deferred and only appears in `HARNESS_SPEC.md:282-283` and plan docs; if Grok ships in §5, attribution to xAI must be added to §4.
- **LLM/agent disclosure section — PLACEHOLDER NEEDED**. `paper/main.tex` (lines 1-69) has no disclosure section, no `\section{Disclosure}` stub, and no comment marker. SCALE call audit (`PHASE0/scale_call_audit.md:153`) and `PAPER_PLAN_v3.1.md` Δ11 both flag this as mandatory. **Required action**: add a `\section*{Use of LLMs and Autonomous Agents}` placeholder before `\bibliography{refs}` in `main.tex` so Phase-5/§28 has somewhere to write into.
- **Dual-submission — OK**. Target is SCALE-only (`PHASE0/scale_call_audit.md:87`). No concurrent ICML-Main submission; no other venue; clean.
- **Compute / energy disclosure — OPTIONAL**. M5 + API calls is small; one sentence in §7 or the disclosure section is sufficient. Not a blocker.
- **Safety discussion — MISSING in paper, present only in plan/notes**. Czapla’s `read_secret()` framing (`PHASE0/related_work_notes.md:20-22`) is the canonical safety hook. The drafted §2 captures the security-risk quote (`02_related_work.tex` mentions hallucinated tools resolving against ambient functions implicitly via the Czapla quote on lines 21-23) but **§7 Discussion/Limitations is still a placeholder** (`main.tex:61-64`). The safety paragraph must land in §7 — not optional for a workshop on agentic systems.

---

## Cross-doc consistency

- **Czapla date — PARTIAL FAIL**. Canonical = `2026-01-20` (per `PAPER_PLAN_v3.1.md:13`, `prior_art.md:38,56`, `refs.bib:11`, `02_related_work.tex:100` comment, `related_work_notes.md:11-12`).
  Divergences (all in stale planning docs, not the paper):
  - `PAPER_PLAN.md:12,31` → "Feb 2026"
  - `PAPER_PLAN_v2.md:31` → "Feb 2026"
  - `PAPER_PLAN_v3.1.md:178` (R24) still discusses the URL-slug-vs-date debate
  Live paper sources (`02_related_work.tex` body, `refs.bib`) are clean. **No paper-blocker; doc-hygiene cleanup recommended.**
- **Model lineup — PASS**. `PAPER_PLAN_v3.1.md:64` and `04_setup.tex:6` both lock 5 core (Sonnet 4.6, Haiku 4.5, GPT-4.1, GPT-4.1-mini, Qwen3-8B@MLX) + Grok deferred to G2. `HARNESS_SPEC.md:282-283` matches. Older v2/v3 saying "4 models" or "4 API + 1 local" is superseded.
- **N values — PARTIAL FAIL (post-ADDENDUM drift)**. ADDENDUM_R1 locks BFCL=100, τ-bench=50, probe=100/cell. `04_setup.tex:10,23,29` matches (N=100 BFCL, N=50 τ-bench). `03_method.tex:47` matches (100 BFCL probe). **But**:
  - `PAPER_PLAN_v3.1.md:65` still says "BFCL N=50, τ-bench N=25"
  - `HARNESS_SPEC.md:122,125` defaults are `n=50` BFCL, `n=25` τ-bench (loader signatures, will be overridden by runner — acceptable but should have ADDENDUM-aligned defaults or a comment).
  - `PHASE0/dataset_status.md:123,216,267` still cites n=50/n=25.
  - `02_related_work.tex` is silent (good).
  Live paper is consistent; tooling docs and the v3.1 plan need a sweep.
- **Conditions — PARTIAL FAIL**. Post-ADDENDUM = 4 (C0, C0.5, C0.7, C1). Live paper (`03_method.tex:42`, `04_setup.tex:14`) correctly says four. **But**:
  - `PAPER_PLAN.md:214` and `PAPER_PLAN_v2.md:199` still say 3 conditions.
  - `PHASE0/dataset_status.md:267` still says 3 conditions.
  - `PHASE0/REVIEWS/R1_neurips_method.md:23` references "5 models × 2 benchmarks × 3 conditions" — historical review, fine.
  Live paper is correct.

---

## Top-5 must-fix anonymization items

1. **Add LLM/agent-disclosure section placeholder to `paper/main.tex`** (right before `\bibliography{refs}`). Mandatory per SCALE CFP; missing today.
2. **Pre-zip grep guard.** Before any supplementary zip: `grep -rinE 'akash|iit|patna|cern|gsoc' <zip-staging-dir>` must return zero. The 22 "akash" hits in plan docs make this non-trivial — **explicitly exclude `PAPER_PLAN*.md`, `ADDENDUM_R1.md`, and `PHASE0/` from the zip** (or scrub them).
3. **Run `pdfinfo paper.pdf` + `pdftotext paper.pdf - \| head -50` after compile.** TeX/LaTeX often leaks `\author` macro contents into PDF metadata even when the title page is `\author{Anonymous}`; verify. Already on Phase-6 list — escalating to MUST-DO-AND-VERIFY.
4. **Scrub `harness/HARNESS_SPEC.md` "Akash" leaks** (lines 4 and 228 per R1 review). Already flagged in `PHASE0/REVIEW_phase0.md`. Open. If `HARNESS_SPEC.md` ships as supplementary, this is a desk-reject vector.
5. **Confirm `paper/icml2026/example_paper.tex` is NOT in the compile path.** It contains placeholder author names; harmless if untouched, but if anyone ever swaps `main.tex` for `example_paper.tex` to "fix" the ICML class issue, they import a leak vector.

---

## Submission-blockers (must-fix-before-submit)

- [ ] LLM-disclosure section present in compiled PDF.
- [ ] `pdfinfo` shows no Author/Creator/Producer fields tying to a real identity.
- [ ] HARNESS_SPEC.md "Akash" scrub confirmed (per R1).
- [ ] §7 Discussion includes the safety paragraph (`read_secret`-style risk).
- [ ] Supplementary zip excludes `PAPER_PLAN*.md`, `ADDENDUM_R1.md`, `PHASE0/`, or those files are scrubbed.
- [ ] If Grok is included in §5, xAI is named alongside Anthropic/OpenAI/Qwen3 in §4.

---

## Verdict

**FIX-LIST-MANAGEABLE.**

The live paper artifact (`paper/main.tex` + sections + bib) is structurally clean: `\author{Anonymous Submission}`, no real names/emails/handles in any `.tex` file, dataset licenses match claims, model attribution present. The fixable items are (a) the mandatory LLM-disclosure placeholder, (b) the safety paragraph in §7, and (c) zip-hygiene around planning docs that contain the author's first name. None are architectural; all are pre-submit checklist items. With the six blockers above ticked off and a final `pdfinfo` pass, this is submit-ready.
