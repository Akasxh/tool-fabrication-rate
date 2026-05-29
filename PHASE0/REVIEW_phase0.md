# Phase-0 Review

*Reviewer: senior code/paper reviewer. Source of truth: `PAPER_PLAN_v3.1.md`. Tone: tough; tighten before Phase 1 starts.*

## Per-file verdicts

- `PHASE0/prior_art.md`: **PASS** — clean, well-cited; verdict and reframing match v3.1 §2.3 / §2.4 exactly. Action items (1)-(4) all flow into v3.1.
- `PHASE0/related_work_notes.md`: **PASS-WITH-FIXES** — Czapla date discrepancy (line 12 says "2026-02-18 (URL slug 2026-01-20)"; v3.1 Δ2 + `prior_art.md` §6 lock the date as **2026-01-20**, single date, no slug-vs-published split). Notes file must be normalized before §2 author cites it as ground truth. Engländer framing correctly recorded.
- `paper/sections/02_related_work.tex`: **FAIL** — does **not** cite `\citep{li2023apibank}` or `\citep{cao2025reliability}` anywhere despite v3.1 Δ1, Δ6, §8 and Submission-Checklist line 189 making these mandatory. Also: comment on line 77 still says "Feb 2026" (must be Jan). Also: Czapla quote in body talks about "Claude, Gemini, and Grok" — fine — but the *anti-attack defense paragraph* called out in v3.1 Δ6 ("TEHR is API-Bank's API Hallucination renamed" → answered by per-call denominator + cross-tier + targeted intervention) is **absent** from §2's "Our differentiation" paragraph. Largest single gap in Phase-0 deliverables.
- `paper/sections/03_method.tex`: **PASS** — TEHR formula is well-defined; per-call denominator stated explicitly; system failures excluded as a footnoted carve-out. RVR pseudocode shape matches HARNESS_SPEC `intervention/rvr.py` description (single-turn membership check, registry list rendered, at-most-one retry enforced upstream by runner). Three distractor types (near-name / synonym / random) match v3.1 §4.3. Conditions C0/C0.5/C1 consistent with §4 and HARNESS_SPEC.
- `paper/sections/04_setup.tex`: **PASS** — 5 models, N=50 BFCL + N=25 τ-bench, 12 pre-registered decisions, McNemar mid-p / Holm-Bonferroni / TOST 1pp all match v3.1 §3, §4.3, §4.4. Local tier reported as a separate feasibility panel matches v3.1 §6.3 and item 12 of pre-reg list.
- `harness/HARNESS_SPEC.md`: **PASS-WITH-FIXES** — architecture solid; module contracts crisp; JSONL schema includes 16 required fields with `schema_version`; stats acceptance criteria hand-checked. **Anonymization leak**: "Akash" appears verbatim on lines 4 and 228. Fix before any harness file ships into the paper repo or supplementary zip. Also: open-question #1 (exact model IDs) and #5 (refusal deny-list) are Phase-1 blockers (see below).
- `paper/main.tex`: **PASS** — correctly `\input{}`s the three section files; preamble loads `listings` (needed by §3 pseudocode), `natbib` (needed by `\citep`), `amsmath`, `hyperref`. Compile-ability verified by inspection: every cite-key used in §2 has a matching bib entry in `refs.bib`; the listing in §3 uses no undefined commands; all `\label`s used by `\S\ref` cross-references resolve. `latexmk paper/main.tex` should produce a PDF (modulo the standard ICML class swap when SCALE-call-audit confirms the style files).
- `paper/refs.bib`: **PASS-WITH-FIXES** — `li2023apibank` and `cao2025reliability` are present (good) but unused, because §2 fails to cite them (see §2 verdict). Five `% TODO: verify arXiv ID` notes still in. Czapla bib entry has `month = January` ✓ (good — but §2 comment line 77 contradicts it).

---

## Cross-doc inconsistencies

1. **Czapla date is split-brain**:
   - `PHASE0/prior_art.md:38` → "2026-01-20 (January)"
   - `paper/refs.bib:9` → `month = January` (good)
   - `PHASE0/related_work_notes.md:12` → "Date: 2026-02-18 (URL slug 2026-01-20)" (wrong)
   - `paper/sections/02_related_work.tex:77` (comment) → "Feb 2026" (wrong)
   v3.1 Δ2 and §9 submission checklist demand a single date: **2026-01-20**.

2. **API-Bank / RelyToolBench citations missing in §2**:
   - v3.1 §2.4 / §8 / §9 all require these.
   - `refs.bib` has both keys (`li2023apibank`, `cao2025reliability`), but `02_related_work.tex` cites neither.
   - Direct contradiction with v3.1 Submission-Checklist line 189.

3. **Anti-attack defense paragraph missing in §2**:
   - v3.1 Δ6 ("§2.4 anti-desk-reject defense updated: 'TEHR is API-Bank's API Hallucination renamed' answered by per-call denominator + cross-tier evaluation + targeted intervention") is *promised* but `02_related_work.tex` "Our differentiation" paragraph does not name API-Bank or rebut the rename attack. Reviewer attack vector left wide open.

4. **HARNESS_SPEC mentions "Akash" twice** (lines 4 and 228). v3.1 §9 anonymization is implicit but standard for ICML double-blind. Must be redacted to "Main thread (M)" / "Open Questions for the maintainer".

5. **`fissiongrpo2026` vs `englander2026` arXiv-IDs unverified** — `bib` entries carry `% TODO: verify arXiv ID`. v3.1 R-list does not flag this but for camera-ready it must be tightened.

6. **HARNESS_SPEC condition keying drift** (minor): JSONL schema uses `"C0_5"` (line 176, 192) while paper uses `"C0.5"`. This is acceptable inside JSONL (dot-in-key is awkward), but the analysis layer must map `C0_5 ↔ C0.5` deterministically. Lock the convention in `stats/__init__.py` or it'll bite Phase 4.

---

## Anonymization scan

**FAIL** — leaks found:

- `harness/HARNESS_SPEC.md:4` → "M = Main thread (Akash) integrates."
- `harness/HARNESS_SPEC.md:228` → "## 6. Open Questions for Akash Before Phase 1 Starts"

No leaks for: IIT, Patna, vLLM, CERN, GSoC, gmail address, GitHub handle, real institutional name, real-name handles in code or comments. "Apple M5 (32 GB unified memory)" in `04_setup.tex:6` is a generic consumer-device spec and is **not** an anonymization risk for ICML double-blind.

**Required fix**: scrub both "Akash" occurrences in `HARNESS_SPEC.md`. If any harness code or trace logs will be uploaded as supplementary, a final `grep -i akash` over the whole zip is mandatory pre-submit.

---

## Top-5 must-fix items (priority order)

1. **Add API-Bank + RelyToolBench citations to `02_related_work.tex`**. v3.1 makes these mandatory; without them, contribution #1 (disaggregation framing) is unsupported in §2 and the paper will be desk-rejected on the API-Bank-rename attack. Drop the differentiation paragraph from `prior_art.md` line 50 verbatim into §2 — it already exists, fully written, just unused.

2. **Add the Δ6 anti-rename rebuttal to §2's "Our differentiation"**: explicit sentence naming API-Bank, calling out per-call denominator + cross-tier + paired intervention as the three load-bearing differentiators. v3.1 §2.4 spells this out; reviewer agent flagged it; §2 still doesn't have it.

3. **Scrub "Akash" from `HARNESS_SPEC.md`** (lines 4 and 228). One-line fix; non-negotiable for double-blind.

4. **Normalize Czapla date to 2026-01-20** across `02_related_work.tex` (line 77 comment), `related_work_notes.md` (line 12), and any other doc that ingests these. v3.1 §9 checklist line 190 demands single canonical date.

5. **Resolve HARNESS_SPEC open questions #1 and #5** before Phase 1 spawn. (1) Pinned model strings: adapter agents cannot start without them. (5) Refusal deny-list: runner cannot classify the `refused` status without a frozen list. Both are 5-minute decisions that block 5 parallel agents otherwise.

---

## Phase-1 blockers

From HARNESS_SPEC §6 ("Open Questions for Akash Before Phase 1 Starts"):

- **Q1 (exact API model IDs) — BLOCKER**: A1 (Anthropic), A2 (OpenAI), A4 (Grok deferred) all need exact production strings or pinned dated aliases before they can write the SDK call. Two-line answer; must be locked at T+0.
- **Q5 (refusal deny-list lock) — BLOCKER**: runner's `tool_call_status` classification depends on this list; without it, A4's runner cannot finalize the classify step, and §3-of-spec ("single source of truth for `tool_call_status`") is unimplementable. Lock the proposed list `["I can't","I cannot","I'm not able","I won't"]` (case-insensitive prefix on text channel when no tool call) or amend it; either way, decide.
- Q2 (MLX HF ID) — soft-blocker: A3 cannot start adapter coding without it, but G0.5 probe at T+04:00 resolves it; if the probe runs *before* A3 spawns, no impact. Keep on critical path.
- Q3 (raw payload retention) — non-blocker: default ("drop before write, flag controllable") is fine; can be tweaked in Phase 4 without rework.
- Q4 (τ-bench env instantiation locus) — non-blocker for Phase-1 spawn but blocker before A4 wires the runner; recommendation in spec ("runner owns env lifecycle for the whole task") is correct, lock it.

---

## Submission-blockers

- **Anonymization leak in HARNESS_SPEC**: if any harness file or its derivatives ship in the supplementary zip without scrub, double-blind violated → desk reject. Mitigate by `grep -ri akash` over `paper/`, `harness/`, `results/` immediately before zip.
- **API-Bank/RelyToolBench citations missing**: triggers the canonical reviewer attack vector ("this is API-Bank renamed"). Per v3.1 R22, mitigated *only* by §2 explicitly citing both and including the differentiation paragraph. Currently unmitigated.
- **arXiv IDs marked `% TODO: verify`** in 5 bib entries: minor, but if any of those IDs is wrong at submission, citations break and reviewers will notice. Verify via `arxiv.org` search before T+35:30 PDF freeze.
- **Czapla date inconsistency** in §2 comment + notes file: low-severity but visible to anyone diffing v3.1 against `02_related_work.tex` source comments. Fix during the API-Bank-citation pass.
- **`paper/main.tex` style-file placeholder**: still uses `\documentclass[11pt]{article}` not `icml2026`. SCALE-call-audit must resolve this and `main.tex` must be swapped before T+33:45 (Phase 5 writing window) or page count math drifts.

---

## Top-3 most urgent fixes (returned for parent agent)

1. **§2 must cite `\citep{li2023apibank}` and `\citep{cao2025reliability}` and include the API-Bank-rename rebuttal paragraph.** This is the single largest gap and the highest desk-reject risk. The text already exists in `prior_art.md` lines 47, 51 — copy it in.
2. **Anonymization scrub of `harness/HARNESS_SPEC.md`** (lines 4, 228 — replace "Akash" with "the maintainer" / "Main thread (M)").
3. **Lock HARNESS_SPEC open-questions Q1 (model ID strings) and Q5 (refusal deny-list)** before Phase 1 spawns; both are blockers for 4-of-5 parallel adapter agents.

## Submission-blockers (returned for parent agent)

- The unredacted "Akash" string in HARNESS_SPEC and the missing API-Bank/RelyToolBench citations in §2 are the two items that, if uncaught, would block submission. Everything else (Czapla date discrepancy, arXiv-ID TODOs, ICML class swap, JSONL `C0_5` vs `C0.5` mapping) is fixable inside Phase 5 polish without architectural change.
