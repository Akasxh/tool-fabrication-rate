# SCALE @ ICML 2026 — Final Pre-Submission Audit (2026-04-28)

**Auditor:** scale-call-audit-v2 agent
**Date run:** 2026-04-27 / 2026-04-28
**Inputs:** `scale_call_audit.md` (v1), `paper/icml2026/icml2026.sty`, `paper/icml2026/example_paper.tex`, web (SCALE site, ICML 2026 author instructions, OpenReview venue, HuggingFace mlx-community).

---

## Time remaining

- **Deadline (verbatim):** "28 April 2026" with "All deadlines are Anywhere on Earth (AoE) time." (Extended; previously 24 April.)
- **Deadline UTC:** 2026-04-29 **11:59 UTC** (28 April 23:59 AoE = UTC-12).
- **Hours from now (anchor 2026-04-28 ~18:00 UTC, ~11:00 PT):** **~18.0 h**.
- **Effective deadline with 1-hour OpenReview-load buffer:** **2026-04-29 10:59 UTC** (~17.0 h from anchor). Plan to upload final PDF by **2026-04-29 10:00 UTC** to also leave a metadata-scrub + re-render contingency.
- **Notification:** 15 May 2026.
- **Camera-ready / workshop days:** No camera-ready deadline published (workshop is non-archival); workshop is at ICML 2026 in Seoul (Coex), 10–11 July 2026.

---

## Track decision

**RECOMMEND: Main 7p (Track 1).**

**Justification.** The paper has three primary contributions: (a) a per-call audit *metric* (TEHR — Tool-Existence Hallucination Rate), (b) a tier-dependence *finding* across Anthropic Frontier+Small + an open-source 8B on BFCL-Multi-Turn, and (c) an *intervention* (RVR — Retrieval-Verified Routing). Two of three contributions are scientific claims about model behavior, not new datasets. BFCL-Multi-Turn is reused, not introduced. The Benchmarking & Dataset Track is for papers whose central artifact is the benchmark/dataset itself; ours uses an existing benchmark to measure a phenomenon. Late-breaking 3p would force dropping either the tier-dependence analysis or RVR — both load-bearing. Main 7p (refs + appendix free) accommodates all three contributions cleanly.

**Fallback:** If late edits force scope cuts, Late-breaking (3p) is acceptable as a "tier-dependence finding only" pitch — but only as a contingency.

---

## Submission mechanics (verbatim from the call)

- **Page limit:** Main Track and Benchmarking & Dataset Track = **7 pages, excluding references and appendix**. Late-breaking = 3 pages, excl. refs and appendix.
- **Format:** "All submissions must be in PDF format using the **ICML 2026 LaTeX style file**." (Use `\usepackage{icml2026}` with no option for the blind-submission build — confirmed in `icml2026.sty` lines 130, 136, 176–177; without `[accepted]` or `[preprint]`, `\icmlshowauthors` stays false and the title block renders "Anonymous Authors / Anonymous Institution".)
- **Anonymization:** "The reviewing process will be **double blind**. Anonymize your submission." Workshop CFP gives no further specifics; ICML 2026 main-CFP rules apply by reference (no author-revealing GitHub links, no acknowledgments/grant numbers in submitted version, scrub PDF metadata).
- **arXiv concurrent posting:** **Allowed.** Workshop CFP is silent at the workshop level but says "Papers under review elsewhere are allowed" + "non-archival ... Submissions can be submitted to other venues." ICML main policy permits arXiv preprints with the constraints (a) do not advertise as a SCALE submission during review, (b) the submitted version must not refer to the non-anonymized version. Use `\usepackage[preprint]{icml2026}` for any concurrent arXiv post — *not* the anonymous build.
- **Submission file format:** Single PDF via OpenReview venue `ICML.cc/2026/Workshop/SCALE`. SCALE site does not specify a size cap; ICML 2026 main author instructions (which the workshop inherits via the LaTeX-style requirement): **PDF ≤ 50 MB at submission, ≤ 20 MB at camera-ready**.
- **Supplementary:** SCALE CFP is **silent**. ICML main allows two kinds (supplementary manuscript + code/data) at submission deadline. Whether SCALE's OpenReview form exposes a separate supplementary upload is not visible to anonymous fetch — verify on the form when logged in. **Safe default: pack everything load-bearing into the appendix of the main PDF + an anonymous repo URL** (anonymous.4open.science).
- **Disclosure section heading:** Workshop CFP says only: *"All submissions must include a section describing the nature and extent of LLM/agent usage in their research and ideation. This section does not count toward the page limit."* **No specific heading text is mandated.** Our current §8 heading "LLM and Agent Usage Disclosure" is compliant. Recommend renaming to **"LLM/Agent Usage Disclosure"** to mirror the CFP's exact phrasing — cosmetic but trivially safer.
- **Single/double-blind:** **Double-blind.** Rebuttal phase: not mentioned → assume **none** (2.5-week review window 28 Apr → 15 May supports this assumption). Treat the submitted PDF as final-substance.

---

## Discrepancies vs current paper

(Top 3, ranked by risk to acceptance.)

1. **Disclosure section heading wording.** Current §8 is "LLM and Agent Usage Disclosure". The CFP phrases it "LLM/agent usage". Rename §8 to **"LLM/Agent Usage Disclosure"** so a quick reviewer ctrl-F hits the expected string. Low-cost, fully eliminates the risk a desk-reviewer flags it as missing.

2. **Anonymization sweep on GitHub URL + acknowledgments + PDF metadata.** Earlier audit flagged this as a checklist; verify that the final PDF: (a) replaces every `github.com/<user>/...` with the corresponding `anonymous.4open.science/r/...` mirror, (b) omits the Acknowledgments section in the submission build (keep it as a `\iftoggle{accepted}` block for camera-ready), (c) `exiftool -overwrite_original -all= submission.pdf` immediately before upload. Style file already scrubs author names from the title block under `\usepackage{icml2026}` with no option, but PDF *metadata* is independent and is the most common silent leak.

3. **arXiv timing (if planning concurrent post).** If posting to arXiv around the same time, the arXiv build must use `\usepackage[preprint]{icml2026}` (real authors visible per `icml2026.sty` line 137 + 177), and the title page must NOT say "Submitted to SCALE @ ICML 2026". The submitted-to-SCALE build must NOT cite or link the arXiv version. Easiest path: post to arXiv only *after* notification (15 May) to avoid both pitfalls.

(Lower-priority items: dual-submission language in §10 of the plan should drop the unconditional "supplementary zip" reference per v1 audit; the SCALE OpenReview form's supplementary field is unverified.)

---

## Qwen3 MLX family (HuggingFace availability)

All confirmed by direct HF page-fetch on 2026-04-27/28. All are MLX-converted by `mlx-lm v0.24.0` and ship the Qwen3 chat template (`tokenizer.apply_chat_template`), which is unified across Qwen3 dense models — drop-in compatible with the existing `mlx-community/Qwen3-8B-4bit` adapter, no code changes needed.

| Repo ID | Size on disk | MLX-quantized | Same Qwen3 chat template (tools-capable) | Verified |
|---|---|---|---|---|
| `mlx-community/Qwen3-0.6B-4bit` | 335 MB | yes (4-bit) | yes | ✓ this audit |
| `mlx-community/Qwen3-1.7B-4bit` | 968 MB | yes (4-bit) | yes | ✓ this audit |
| `mlx-community/Qwen3-4B-4bit` | 2.26 GB | yes (4-bit) | yes | ✓ this audit |
| `mlx-community/Qwen3-8B-4bit` | 4.61 GB | yes (4-bit) | yes | ✓ this audit (also: already in use) |
| `mlx-community/Qwen3-14B-4bit` | 8.31 GB | yes (4-bit) | yes | ✓ this audit |
| `mlx-community/Qwen3-32B-4bit` | 18.4 GB | yes (4-bit) | yes | ✓ this audit |

**Implication for scaling:** A 0.6B → 32B size-sweep is plug-and-play with the existing MLX adapter. Tier-dependence claim could be sharpened post-notification by adding the 1.7B and 14B points (both fit comfortably on Apple Silicon ≥ 16 GB unified memory; 32B needs ~32 GB+). Pre-submission, this is informational; for the rebuttal-equivalent revision window or camera-ready, it is a cheap follow-up. Note: Qwen3 MoE variants and Qwen3-Coder require a different inference path — out of scope for this paper's "open-source 8B" claim.

---

## Pre-submit checklist (top 10)

1. **Build with `\usepackage{icml2026}`** (no option) — confirms blind title block. Spot-check by opening the PDF and verifying first page reads "Anonymous Authors" / "Anonymous Institution".
2. **§8 rename:** "LLM and Agent Usage Disclosure" → **"LLM/Agent Usage Disclosure"**.
3. **Anonymize all repo URLs** to `anonymous.4open.science/r/...`. Grep the .tex for `github.com`, also check footnotes and the bib file.
4. **Strip Acknowledgments** in submission build. If the .tex has an `\section*{Acknowledgments}`, wrap it in a toggle that is off for the submission build.
5. **Strip grant numbers / institutional disclosures** from any footnote.
6. **PDF metadata scrub:** `exiftool -overwrite_original -all= submission.pdf` immediately before upload. Re-verify with `exiftool submission.pdf` (Author, Producer, Title fields all empty or generic).
7. **Page-count check:** body ≤ 7 pages excluding references and appendix; LLM-disclosure section does *not* count toward 7p.
8. **PDF size check:** ≤ 50 MB. If over, downsample figures.
9. **OpenReview dry-run upload by 2026-04-29 06:00 UTC** (≥ 5 h before deadline). Confirm: (a) supplementary upload field availability, (b) abstract field length, (c) track selection (Main Track).
10. **Final upload no later than 2026-04-29 10:00 UTC** (≈ 2 h buffer before 11:59 UTC AoE deadline). Do not advertise the submission publicly until 15 May notification.

---

## Sources

- SCALE workshop CFP (primary): https://scale-icml-2026.github.io/
- ICML 2026 main author instructions (inherited): https://icml.cc/Conferences/2026/AuthorInstructions
- ICML 2026 main CFP (inherited arXiv policy): https://icml.cc/Conferences/2026/CallForPapers
- OpenReview venue (gated): https://openreview.net/group?id=ICML.cc/2026/Workshop/SCALE
- Local: `paper/icml2026/icml2026.sty` (lines 130, 136, 176–177), `paper/icml2026/example_paper.tex`
- HuggingFace mlx-community Qwen3 0.6B / 1.7B / 4B / 8B / 14B / 32B 4-bit pages (each verified by direct fetch).
