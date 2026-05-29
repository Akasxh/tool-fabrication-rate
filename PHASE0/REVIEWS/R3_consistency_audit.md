# Production-Grade Consistency Audit — Round 3

*Auditor: late-career copy-editor with math background. Read every `*.md` and `*.tex` in `paper/`, `paper/sections/`, `harness/HARNESS_SPEC.md`, `harness/README.md`, `PHASE0/`, plus `ADDENDUM_R1.md` and `PAPER_PLAN_v3.1.md`. Bash greps + close reading.*

## Section A: Number consistency

- **N=100 BFCL / N=50 τ-bench / N=100 probe**: live paper is consistent (`paper/sections/04_setup.tex:10,23,29` and `03_method.tex:58`). Stale numbers exist only outside the live paper:
  - `harness/HARNESS_SPEC.md:122` defaults loader signature `n=50`; line 125 defaults `n=25`. Acceptable per HARNESS_SPEC convention (runner overrides) but the loader docstring should carry an ADDENDUM note. **MINOR — tooling-doc drift, not a paper-blocker.**
  - `PAPER_PLAN_v3.1.md:67` table still says "BFCL N=50, τ-bench N=25" (pre-ADDENDUM). **MINOR — supersedèd by ADDENDUM, but readers must remember to apply that.**
- **3 vs 4 conditions**: live paper consistent at 4 (`03_method.tex:42`, `04_setup.tex:14`, `01_introduction.tex:14`). PHASE0 review docs reference the historical 3-condition design — acceptable as historical record.
- **5 core models + 1 deferred Grok**: paper says "five models" (`01_introduction.tex:12`, `02_related_work.tex:29`, `04_setup.tex:6`, `08_llm_disclosure.tex:6`); `PAPER_PLAN_v3.1.md:39` says "5 models" in the one-sentence main result; `:43` says "5–6 models". The paper text never mentions Grok. **Consistent within the paper; planning docs hedge.**
- **TOST margin 5pp**: `04_setup.tex:22` correctly says 5 pp. **HARNESS_SPEC.md still ships pre-ADDENDUM defaults**: `harness/HARNESS_SPEC.md:39` ("margin 1pp"), `:183` (`margin=0.01`), `:253` (acceptance test at `margin=0.01`). `PAPER_PLAN_v3.1.md:96` also says "1pp". **MINOR — implementation contract still pre-ADDENDUM; ADDENDUM C.1 mandates 5pp / 0.05.**

## Section B: Naming consistency

- `C0.5` / `C0_5` form is used appropriately by context: paper uses `$\mathrm{C}_{0.5}$`, JSONL/code uses `C0_5`. Alias map exists in `harness/HARNESS_SPEC.md:189-193` — but the map covers **only `C0` / `C0_5` / `C1`**, missing **`C0_7`**. **MINOR — map needs `"C0_7": "C0.7"` entry per ADDENDUM B.2/D.2.**
- RVR / TEHR: each is expanded once at first use (`01_introduction.tex:12,14`) and abbreviated thereafter. **PASS.**
- `ΔPass` / `ΔTEHR`: paper uses `\Delta\mathrm{Pass}` / `\Delta\mathrm{TEHR}` consistently. **PASS.**
- **C0.7 framing — INCONSISTENT.** ADDENDUM E (R2.1 BLOCKER) requires C0.7 be renamed away from "framework-default" to "idealized structured-error baseline" because real LangChain raises `OutputParserException` (strawman concern). Paper does this **partially**:
  - §1 `01_introduction.tex:14` correctly says **"idealized structured-error baseline … approximating the parsed-readable error path of mature production frameworks."** ✓
  - §4 `04_setup.tex:14` says **"framework-style structured error feedback"** — softened, acceptable ✓
  - §3 `03_method.tex:42` still says **"framework-default structured-error feedback … approximating LangChain's default tool-call-validation error path"** ✗ — this is precisely the strawman wording R2.1 flagged.
  - `paper/refs.bib:172` (note in `langchain_toolnotfound2025` entry) says "Production-engineer-proposed structured-error pattern (our C0.7)" — descriptive, acceptable.
  - `harness/README.md:35` says "Framework-style structured-error JSON" — acceptable.
  - `ADDENDUM_R1.md:50,186` still uses "production-default" — acceptable (ADDENDUM is a correction log).
  - **MAJOR — `03_method.tex:42` needs the same softening §1/§4 received.**

## Section C: Date / version consistency

- **Czapla blog 2026-01-20**: `refs.bib:9-12` correct; `02_related_work.tex` body uses date-free citation. **PASS in live paper.** Stale "Feb 2026" appears only in `PAPER_PLAN.md` and `PAPER_PLAN_v2.md` (acknowledged by `R2_anonymization_ethics.md:43-48` as historical, planning-docs only). Doc-hygiene only.
- **Engländer "environmental curiosity deficit"**: `refs.bib:33-39` title and framing correct ("Agents Explore but Agents Ignore: LLMs Lack Environmental Curiosity"). `02_related_work.tex:89-94` describes the work as agents "fail to exploit" environmental signals — matches. `PAPER_PLAN_v3.1.md:14,153,198` correctly notes the relabel. No stale "first-hypothesis anchoring" framing in any live paper file. **PASS.**

## Section D: Citations

- Every `\citep`/`\citet` in `paper/sections/*.tex` resolves to a `refs.bib` entry — matched all 16 citations against 19 bib entries.
- **Two entries in `refs.bib` are NEVER cited in any `.tex`**:
  - `stableTOOLbench2024` (refs.bib:175) — uncited.
  - `anthropicagentskills2025` (refs.bib:183) — uncited.
  - **MAJOR — these are dead bib entries (R3 spec called them "newly-added citations actually used in the text" — they aren't). Either cite them or remove from `refs.bib`.**
- `huang2024metatool`, `gou2024critic`, `langchain_toolnotfound2025` are all cited (`02_related_work.tex:37,64,72`). **PASS for these three.**
- TODO-flagged arXiv IDs (`bugstudy2026`, `licl2026`, `fissiongrpo2026`, `englander2026` — IDs `2602.21806`, `2602.00276`, `2601.15625`, `2604.17609`) all carry inline `% TODO: verify arXiv ID` annotations in `refs.bib` and a duplicate annotation block in `02_related_work.tex:113-117`. **PASS — explicitly flagged.**

## Section E: Cross-references

- All `\ref{sec:Y}` resolve: `sec:results`, `sec:method`, `sec:related`, `sec:setup`, `sec:method:rvr`, `sec:method:probe`, `sec:mechanism`, `sec:discussion` all have matching `\label`s in `main.tex` or sections. **PASS.**
- Labels defined but never `\ref`'d: `sec:intro`, `sec:llm-disclosure`, `sec:method:tehr`, `sec:method:conditions`, `sec:method:mechanism-hypotheses`, `sec:setup-models`, `sec:setup-benchmarks`, `sec:setup-conditions`, `sec:setup-prereg`, `sec:setup-repro`, all five `sec:limitations:*` labels. These are all section/subsection anchors usable from a future Phase-5 results write-up; spec allows "stable anchor" exemption. **PASS.**
- `\S\ref{sec:mechanism}` appears as `§\ref{...}` (raw §) in `03_method.tex:47` rather than `\S\ref{...}` as elsewhere. Renders correctly in pdflatex with utf8 input but inconsistent with the rest of the paper. **MINOR.**

## Section F: Math notation

- `$\mathcal{R}$` for registry: consistent throughout `03_method.tex` and `07_limitations.tex:19`. **PASS.**
- `\mathrm{TEHR}(m, b, x)` formal definition (`03_method.tex:9`); plain `TEHR` thereafter in prose; both are used in math-mode (e.g. `04_setup.tex:29`). **PASS.**
- Subscript condition labels in math mode: `$\mathrm{C}_0$ / $\mathrm{C}_{0.5}$ / $\mathrm{C}_{0.7}$ / $\mathrm{C}_1$` — used consistently in `01_introduction.tex`, `04_setup.tex`. `02_related_work.tex` uses bare `$C_1$ / $C_{0.5}$ / $C_{0.7}$` (no `\mathrm`). `03_method.tex:42` mixes: starts with bare `\textbf{C0}` then switches to `\textbf{$\mathrm{C}_{0.5}$}`. **MINOR — pick one (with or without `\mathrm`) and apply globally.**

## Section G: Anonymization

- `grep -rni "akash\|Akash" paper/ harness/HARNESS_SPEC.md harness/README.md` → **0 hits.** **PASS.**
- `paper/main.tex:29` — `\author{Anonymous Submission}`. **PASS.**
- `paper/main.tex:26-28` — `\title{Tool-Existence Hallucination ... Closes [Y]\% of the Cost-Quality Gap}` — placeholder Y%, deanonymizing only if it reveals authorship — it doesn't. **PASS.**
- Note: PHASE0/REVIEWS still contains "Akash" references (R1_synthesis, R2_anonymization, REVIEW_phase0). These are scoped to PHASE0 and explicitly to be excluded from the supplementary zip per `R2_anonymization_ethics.md:67`. **PASS for paper/harness; documented zip-hygiene risk.**

## Section H: Compile-readiness

- All `\input{sections/0X}` files exist on disk: 01, 02, 03, 04, 07, 08. ✓
- `\section{Results}` / `\section{Mechanism}` placeholders in `main.tex:47-56`. ✓
- `\documentclass[11pt]{article}` (still placeholder). Comment at `main.tex:2` notes the swap to `\usepackage{icml2026}` is pending. `paper/icml2026/icml2026.sty` and `.bst` exist on disk. **MINOR — class swap not yet made; will need a `\usepackage{icml2026}` and remove `[margin=1in]{geometry}` (icml2026.sty owns geometry).**
- `\usepackage{listings}` is used (`lstlisting` in `03_method.tex:18-29`); `\lstset{...}` is configured in `main.tex:15-24`. ✓
- `\usepackage{xcolor}` loaded but no obvious `\color{}`/`\textcolor{}` use. Likely loaded for hyperref. **MINOR — unused-package-warning candidate.**
- `\usepackage{hyperref}` last (correct order). ✓

---

## Top-10 must-fix inconsistencies (priority)

1. **MAJOR** — `paper/sections/03_method.tex:42` — calls C0.7 "framework-default structured-error feedback ... approximating LangChain's default tool-call-validation error path." This is the *strawman wording* R2.1 (BLOCKER) explicitly required to be removed; §1 and §4 already use the corrected "idealized structured-error baseline" / "framework-style" phrasing. **Fix**: replace the §3 phrasing to match §1 — "idealized structured-error baseline approximating the parsed-readable error path of production frameworks (LangChain's `ToolMessage` proposal in [langchain_toolnotfound2025] is the closest concrete instance)."
2. **MAJOR** — `paper/refs.bib:175` (`stableTOOLbench2024`) and `:183` (`anthropicagentskills2025`) are defined but never cited in any `.tex` file. **Fix**: either add a `\citep{stableTOOLbench2024}` to §2 (Related Work, "tool-using agents and benchmarks" paragraph is the natural home) and a `\citep{anthropicagentskills2025}` to §1 multimodal-bridge paragraph or §7 deployment discussion, or delete both entries.
3. **MAJOR** — `paper/sections/02_related_work.tex:93` — "evaluated as a paired causal contrast rather than observationally." ADDENDUM B.3 mandates dropping causal language throughout. **Fix**: change "paired causal contrast" → "controlled paired comparison." (Mirrors §1:18 phrasing.)
4. **MAJOR** — `paper/sections/01_introduction.tex:20` — Contributions §(iii) still says "scaling-curve evidence." ADDENDUM E.3 mandates "scaling-curve" → "tier comparison." `07_limitations.tex:33` correctly says "we do not claim a scaling law (the three tiers are a comparison, not a swept axis)" — direct contradiction. **Fix**: replace "scaling-curve evidence" with "cross-tier evidence" or "tier-comparison evidence."
5. **MAJOR** — `harness/HARNESS_SPEC.md:39,183,253` — TOST margin still defaulted to `1pp` / `margin=0.01`; ADDENDUM C.1 mandates `5pp` / `0.05`. The implementation contract is now inconsistent with the paper (`04_setup.tex:22` correctly says 5pp). **Fix**: update HARNESS_SPEC default to `margin=0.05` and acceptance test in §5 item 7.
6. **MAJOR** — `harness/HARNESS_SPEC.md:189-193` — `CONDITION_LABEL_FOR_PAPER` map is missing the `C0_7 ↔ C0.7` entry. With four conditions live, the alias map will silently drop C0.7 from any paper-side rendering. **Fix**: add `"C0_7": "C0.7"` (and ideally regenerate the inverse map shown on `:191`).
7. **MAJOR** — `harness/HARNESS_SPEC.md:40,185-186` — `stats/probe_anova.py` and `oneway_anova_tukey()` still in the spec. ADDENDUM C.5 / F.4 mandates replacement with `stats/probe_friedman.py` (Friedman + Nemenyi). Paper §4 pre-reg item 13 already says Friedman/Nemenyi (`04_setup.tex:32`). **Fix**: rename the file in the spec, change the function signature.
8. **MINOR** — `paper/sections/03_method.tex:42` — opens with "\textbf{C0}" (no math mode) then immediately switches to "\textbf{$\mathrm{C}_{0.5}$}" / "\textbf{$\mathrm{C}_{0.7}$}" / "\textbf{$\mathrm{C}_1$}". Pick one form. **Fix**: change "\textbf{C0}" → "\textbf{$\mathrm{C}_0$}" for consistency with §1 / §4.
9. **MINOR** — `paper/sections/03_method.tex:47` — uses `§\ref{sec:mechanism}` (raw § character) where the rest of the paper uses `\S\ref{...}` (`01_introduction.tex:22`, `03_method.tex:53`, `04_setup.tex:14`, `08_llm_disclosure.tex:8`). **Fix**: change `§\ref{sec:mechanism}` to `\S\ref{sec:mechanism}` for uniformity.
10. **MINOR** — `PAPER_PLAN_v3.1.md` is still pre-ADDENDUM at multiple points: §3 hard-constraints table line 67 (N=50/N=25), §4.2 conditions table (3 conditions, primary test C1 vs C0.5), §4.3 metrics ("TOST margin 1pp"), §2.3 contribution #3 ("primary test C1 vs C0.5"). The file's preamble does say ADDENDUM overrides, but a careful reader will diff and find drift. **Fix**: either add ADDENDUM-deltaed footnotes to each affected line, or freeze v3.1 and write the canonical four-condition / N=100 / 5pp design into a new top-level CANONICAL_DESIGN.md.

---

## Verdict

**MINOR-FIX-NEEDED** — leaning toward the upper end of MINOR.

The live paper artifact (`paper/main.tex` + `paper/sections/*.tex` + `paper/refs.bib`) is structurally clean: anonymization is solid, citations resolve, all section labels resolve or function as stable anchors, math notation is internally consistent, the four-condition design and N=100/50/100 numbers are correct everywhere they appear in the paper proper. **No BLOCKERS.** The audit surfaces five MAJOR issues — three live in the paper text (items 1, 3, 4: the §3 strawman wording, the §2 "paired causal" residue, the §1 "scaling-curve" residue), one is a dead-bib hygiene issue (item 2), and three are in the implementation contract (items 5, 6, 7) where ADDENDUM-mandated changes were never propagated into HARNESS_SPEC. The minor items (8, 9, 10) are pure copy-edit + planning-doc-drift. None require structural rewrites; all close in well under one Phase-5 polish slot.

Items 1 and 4 are the only paper-text issues a reviewer would notice on first read — the §3 wording invites the exact strawman attack R2.1 anticipated, and the §1 contribution-list "scaling-curve" phrasing flatly contradicts the §7 limitation it pairs with. Fix those two and the audit clears.
