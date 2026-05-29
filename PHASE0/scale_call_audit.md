# SCALE @ ICML 2026 Call Audit

**Auditor:** scale-call-audit agent
**Date run:** 2026-04-27
**Audited document:** `/Users/cero/Desktop/PROJECTS/icml/PAPER_PLAN_v3.1.md` §3
**Verdict (TL;DR):** v3.1 §3 is largely accurate. No discrepancies found in the load-bearing claims (title, tracks, page limit, deadline, format, OpenReview). The CFP is **silent** on arXiv, supplementary material, and rebuttal — so v3.1 should not assume any of those without contacting organizers. ICML 2026 author kit downloaded successfully.

---

## Sources

- https://scale-icml-2026.github.io/ — official SCALE workshop site; primary CFP source. Contains tracks, page limits, deadlines, anonymization, dual-submission, LLM-disclosure rule.
- https://openreview.net/group?id=ICML.cc/2026/Workshop/SCALE — OpenReview venue group (URL referenced by SCALE site as the submission portal); page itself is gated/sparse to anonymous fetch.
- https://blog.icml.cc/2026/04/06/announcing-the-icml-2026-workshops-and-affinity-workshops/ — ICML blog confirming SCALE is on the accepted-workshops list with full title.
- https://icml.cc/Conferences/2026/Dates — ICML 2026 master calendar; confirms universal workshop notification 14–15 May 2026 and workshop days July 10–11 in Seoul (Coex).
- https://icml.cc/Conferences/2026/CallForPapers — main-conference CFP, used to fill in arXiv policy and ICML-wide anonymization rules referenced by the workshop's "ICML 2026 LaTeX style file" requirement.
- https://icml.cc/Conferences/2026/AuthorInstructions — ICML 2026 author instructions; double-blind, 50 MB PDF cap, links to icml2026.zip.
- https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip — official ICML 2026 LaTeX style bundle (downloaded; contents below).

---

## Verbatim deadline

- **Submission window opens:** 6 April 2026 (AoE) — *"6th April 2026 Paper Submission Starts"*
- **Submission deadline:** 28 April 2026 (AoE), extended from 24 April — *"Deadline extended to 28 April 2026. (Previously 24 April 2026.)"*
- **AoE → UTC:** AoE is UTC-12, so 28 April 2026 23:59 AoE ≈ **29 April 2026 11:59 UTC ≈ 12:00 UTC**.
- **Author notification:** 15 May 2026 (consistent with ICML's universal workshop notification date of 14–15 May 2026).
- **Submission window grace period:** None advertised. AoE itself is the de-facto grace.
- **Camera-ready deadline:** Not specified on the SCALE site or on icml.cc/Conferences/2026/Dates as of 2026-04-27. Workshop is **non-archival**, so a hard camera-ready may not exist; expect a "post-acceptance polish" window between 15 May and 10 July 2026.

---

## Page limit

- **Main pages:** **7 pages** for Main Track and Benchmarking & Dataset Track; **3 pages** for Late-breaking Track. (Verbatim: *"Maximum limit of 7 pages, excluding references and appendix"* / *"Late-breaking track ... Maximum limit of 3 pages, excluding references and appendix"*.)
- **References:** Excluded from page count (no cap stated).
- **Appendix:** Excluded from page count (no cap stated).
- **Mandatory extra section (does not count toward page limit):** "All submissions must include a section describing the nature and extent of LLM/agent usage in their research and ideation. This section does not count toward the page limit."

---

## Tracks (verified)

1. **Main Track** — 7 pages. (v3.1 §3 target track.)
2. **Benchmarking and Dataset Track** — 7 pages.
3. **Late-breaking Track** — 3 pages.

v3.1's "Main / Benchmarking / Late-breaking" naming is correct.

---

## Anonymization rules

- **Workshop CFP (verbatim):** *"The reviewing process will be double blind. Anonymize your submission."* No further specifics.
- **PDF metadata:** Workshop CFP is **silent**. Standard ICML practice (inherited via the "ICML 2026 LaTeX style file" requirement) is to scrub author names from PDF metadata. Recommend running `exiftool -overwrite_original -all= submission.pdf` before upload.
- **Title page:** Use `\usepackage{icml2026}` (no option) — produces blind title block with "Anonymous Authors" / "Anonymous Institution"; suppresses real `\icmlauthor`/`\icmlaffiliation` macros. Confirmed in `icml2026.sty` lines 130–179: the `accepted` and `preprint` options set `\icmlshowauthorstrue`; without them, real authors are hidden.
- **GitHub URLs:** Workshop CFP silent. ICML 2026 main CFP (which the workshop references) says authors must "avoid ... links to public code repositories" that reveal identity; anonymize repos via anonymous.4open.science or similar.
- **Acknowledgments:** Workshop CFP silent. ICML 2026 main CFP: omit acknowledgments / grant numbers in the submission version.
- **ICML LaTeX template's anonymization toggle:**
  - Submission (anonymous): `\usepackage{icml2026}`
  - Preprint (non-anonymous, e.g. arXiv): `\usepackage[preprint]{icml2026}`
  - Camera-ready (after acceptance): `\usepackage[accepted]{icml2026}`
  - Verified directly from `icml2026.sty` (DeclareOption blocks on lines 130 and 136; `\icmlshowauthorstrue` gating on lines 176–177).

---

## arXiv policy

- **VERDICT:** **Silent at the SCALE workshop level → fall back to ICML 2026 main-conference policy, which permits arXiv preprints.**
- **Source quote (ICML 2026 main CFP, https://icml.cc/Conferences/2026/CallForPapers):** *"Authors are allowed to post versions of their work on preprint servers such as arXiv. They are also allowed to give talks on the work(s) submitted to ICML during the review."* Constraint: *"under no circumstances should the work be advertised as an ICML submission at any time during the review period"* and *"if a non-anonymized version exists online before decisions are made, the submitted version must not refer to the non-anonymized version."*
- **Workshop-specific note:** SCALE is non-archival and explicitly says *"Papers under review elsewhere are allowed"* and *"Submissions can be submitted to other venues"* — this strongly implies arXiv concurrent posting is fine, but the workshop CFP does not explicitly say so. Use the `[preprint]` style option for any concurrent arXiv post; do not refer to it as a "SCALE submission" until accepted.

---

## Supplementary material

- **Format:** Workshop CFP is **silent**. ICML 2026 main practice via OpenReview is single PDF, with optional supplementary uploaded as a separate file. Workshop probably inherits OpenReview's defaults (single PDF main + optional separate supplementary file).
- **Size limit:** Workshop CFP is **silent**. ICML 2026 main: PDF ≤ 50 MB at submission, ≤ 20 MB at camera-ready (per https://icml.cc/Conferences/2026/AuthorInstructions). Workshop will most likely inherit 50 MB.
- **Zip allowed:** Unverified — depends on OpenReview venue config, which is not exposed publicly. Plan B: pack code/data into appendix PDF or anonymous repo link.
- **Action:** When the OpenReview submission form opens (or check it from a logged-in account), confirm the supplementary upload field's accepted MIME types and size cap. Until then, plan for "single PDF + anonymous repo URL" as the safe default.

---

## Dual-submission rules

- **Workshop CFP (verbatim):** *"Papers under review elsewhere are allowed."* / *"The workshop is non-archival. Submissions can be submitted to other venues."*
- **Implication for ICML Main + SCALE:** Concurrent submission to ICML 2026 main conference would have been fine on the SCALE side, but the **ICML main CFP forbids it**: *"identical, or substantially similar [versions] ... submitted in parallel to other conferences or journals"* are prohibited. Since v3.1 is targeting only SCALE (not ICML main), this is not a blocker for our plan, but the conjunction matters for any future paper.
- **Implication for arXiv + SCALE:** Allowed.
- **Implication for re-submitting after SCALE rejection:** Allowed — workshop is non-archival.

---

## Reviewer model

- **Double-blind:** Confirmed (workshop CFP verbatim).
- **Rebuttal phase:** Workshop CFP is **silent**. Many ICML workshops skip rebuttal entirely given the short 2.5-week review cycle (28 April → 15 May). **Plan as if there is no rebuttal**; treat the submitted PDF as final-substance.

---

## Camera-ready deadline (informational)

- Not published on the SCALE site or icml.cc/Conferences/2026/Dates as of 2026-04-27.
- Workshop is non-archival → no formal proceedings → "camera-ready" is likely a polish window before workshop days (10–11 July 2026, Seoul Coex).
- Action: monitor the SCALE site after the 15 May 2026 notification.

---

## Discrepancies vs PAPER_PLAN_v3.1.md §3

| v3.1 §3 claim | Audit finding | Verdict |
|---|---|---|
| Workshop full title: "Scalable Learning and Optimization for Efficient Multimodal AI Agents" | Site title: "SCALE: Scalable Learning and Optimization for Efficient Multimodal AI Agents" | **MATCH** (v3.1 omits the "SCALE:" prefix; cosmetic) |
| Tracks: Main / Benchmarking / Late-breaking | Site tracks: Main / Benchmarking and Dataset / Late-breaking | **MATCH** (v3.1 abbreviates "Benchmarking and Dataset" to "Benchmarking"; cosmetic) |
| Page limit: 7 pages excl. references and appendix | 7 pages for Main Track, excl. references and appendix | **MATCH** |
| Deadline: 2026-04-28 AoE (~2026-04-29 12:00 UTC) | 28 April 2026 AoE (extended from 24 April); ≈ 29 April 11:59 UTC | **MATCH** |
| Format: ICML 2026 LaTeX, double-blind | "All submissions must be in PDF format using the ICML 2026 LaTeX style file." + "double blind" | **MATCH** |
| Submission: OpenReview | OpenReview venue ID `ICML.cc/2026/Workshop/SCALE` | **MATCH** |
| §10: arXiv concurrent posting → "Pending SCALE-call-audit agent" (Q4) | Workshop silent; ICML main policy permits arXiv preprints with caveats | **RESOLVED — allowed** |
| §9 submission checklist mentions "supplementary zip" | Workshop CFP silent; ICML main practice is single-PDF + optional separate file. Zip-as-supplementary is **unverified**. | **GAP — verify on OpenReview form before T+35:00** |

**No fact-corrections needed in v3.1 §3 itself.** The only concrete fixes are (a) §10 should drop the "supplementary zip" assumption until OpenReview is checked, and (b) §11 Q4 ("arXiv concurrent posting?") can be marked **YES, allowed** with the source quoted above.

---

## ICML LaTeX author kit

- **Download status:** **SUCCESS.** Fetched `https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip` (228 368 bytes, 9 files).
- **Files placed in `/Users/cero/Desktop/PROJECTS/icml/paper/icml2026/`:**
  - `algorithm.sty` (2 223 B)
  - `algorithmic.sty` (7 414 B)
  - `example_paper.bib` (2 051 B)
  - `example_paper.pdf` (193 509 B)
  - `example_paper.tex` (29 714 B)
  - `fancyhdr.sty` (31 715 B)
  - `icml_numpapers.pdf` (2 823 B)
  - `icml2026.bst` (27 147 B) — bibliography style
  - `icml2026.sty` (27 344 B) — main style file
  - `icml2026.zip` (228 368 B) — original archive retained
- **Class vs style:** ICML 2026 uses a **`.sty` (style)** package on top of `\documentclass{article}`, not a `.cls`. Confirmed in `example_paper.tex` line 3 (`\documentclass{article}`) + line 23 (`\usepackage{icml2026}`).
- **Compile-test:** Skipped (no LaTeX install verified in this audit). Sanity checks performed instead:
  - `icml2026.sty` declares both `[accepted]` and `[preprint]` options as expected (lines 130, 136).
  - `example_paper.tex` shows the canonical three-mode toggle (lines 23, 26, 29) — submission / preprint / accepted.
  - `example_paper.pdf` is the rendered reference output (193 KB) — useful for visual diff against our own builds.
- **Compile command (for later):** `pdflatex example_paper && bibtex example_paper && pdflatex example_paper && pdflatex example_paper` from inside `/Users/cero/Desktop/PROJECTS/icml/paper/icml2026/`.

---

## Action items

1. **v3.1 §10 ("Submission checklist"):** Drop the unconditional reference to "supplementary zip"; replace with "supplementary material per OpenReview form (verify field accepts zip; otherwise pack into appendix PDF or anonymous repo URL)."
2. **v3.1 §11 Q4:** Mark resolved — *"arXiv preprint allowed under ICML main policy; SCALE non-archival policy compatible. Use `\usepackage[preprint]{icml2026}` for any arXiv post; do not advertise as a SCALE submission until accepted."*
3. **Submission checklist additions:**
   - Include the mandatory **LLM/agent usage disclosure section** (does not count toward 7-page limit).
   - Anonymize PDF metadata pre-upload (`exiftool -overwrite_original -all= paper.pdf`).
   - Anonymize all GitHub/code links (anonymous.4open.science or similar).
   - Strip acknowledgments / grant numbers from the submitted version.
   - Use `\usepackage{icml2026}` (no option) for the submitted PDF.
4. **Plan as if there is NO rebuttal phase** for SCALE (CFP silent; 2.5-week review window is too short). Submitted PDF is treated as final-substance.
5. **Pre-T+35:00 check:** Once the maintainer logs into OpenReview, confirm the submission form's supplementary upload limits (MIME types, size). Until then, default plan = single PDF main + appendix-in-PDF + anonymous repo URL.
6. **Camera-ready:** No fixed deadline yet; monitor SCALE site after 15 May 2026 notification. Workshop is non-archival, so this is informational, not blocking.
7. **Author kit (no action needed):** All files in place at `/Users/cero/Desktop/PROJECTS/icml/paper/icml2026/`. Compile test deferred to first real PDF build in Phase 5.
