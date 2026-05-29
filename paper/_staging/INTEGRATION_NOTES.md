# Integration notes — paper/_staging/ → paper/

Date: 2026-05-29. Audience: whoever does the merge pass. Reconciled against
`paper/sections/*.tex`, `paper/refs.bib`, `PHASE0/RESULTS/headline_numbers.json`,
and `paper/_staging/stats_full.json` / `stats_table.md`.

All 13 cite keys used by staging artifacts are confirmed present in `refs.bib`
(spracklen2025packages, min2022rethinking, wei2022ushaped,
mckenzie2023inversescaling, li2023apibank, huang2024metatool, cao2025reliability,
toolbehonest2024, yin2026reasoningtrap, czapla2026, licl2026, englander2026,
bugstudy2026). No SUSPECT/NOT-FOUND keys.

---

## (1) Ranked merge plan

### Tier A — drop in as-is (no data dependency, no conflict)

1. **`priorart_table.tex`** → new float in `02_related_work.tex` (or §1).
   Self-contained `table*`, all 5 keys verified, idiom matches `05_results.tex`.
   READY. Only check: it deliberately maps "Xu et al. tool-type hallucination"
   onto `cao2025reliability` — confirm that's an acceptable attribution before
   the table caption claims a clean 5-work survey.

2. **`security_motivation.tex`** → 1 paragraph into §1 (after the TEHR-grain
   motivation). Uses `spracklen2025packages` (present). Honest, non-exploitation
   framing. READY. This is one of the cheap reframes the AC asked for (gives the
   per-call grain a "why it matters" hook). Drop in as-is.

3. **`coverage_matrix.tex`** → new float in §4 (`04_setup.tex`).
   READY and HIGH-VALUE: it pre-empts the "5 versions on everything" misread by
   showing the eleven-month breadth lives only on `multi_turn_base`. Its per-cell
   decomposition (Haiku 882, Opus 293, Sonnet-4.0 253, Sonnet-4.5 285,
   Sonnet-4.6 886 = 2,599) is the authoritative reconciliation of the headline
   "0/2,599" — use these exact denominators everywhere (see Conflict C-2).

4. **`stats_table.md` / `stats_full.json`** → source-of-truth for every CI in §5.
   Statsmodels-confirmed (analysis:stats-CI). READY as the numbers backbone, but
   see Conflict C-1: its POOLED Fisher figures differ from the paper's current
   RVR-validation table, by design — do not blindly overwrite the table.

### Tier B — drop in, but requires a one-line edit / decision

5. **`s33_s6_redraft.md` §3.3 trim** → replaces lines 42–47 of `03_method.tex`.
   READY pending the §3.4 follow-on edit it specifies (delete the final
   Friedman/Nemenyi sentence of the probe subsection). Removes the
   M-Retrieve/M-Constrain/M-Metacog over-framing the reviewer flagged. No data
   dependency. Merge once you accept demoting the distractor probe to descriptive.

6. **`citation_audit.md` fix** → optional cosmetic edit to `czapla2026` bib entry
   (keep `month = {February}`, optionally add `note = {accessed 2026-05-29}`).
   1-minute change, low priority.

### Tier C — BLOCKED on data (do not merge yet) — see section (4)

7. **`abstract_variants.md`** (Variant A vs B) — BLOCKED on C0.8 decoy result.
8. **`s33_s6_redraft.md` §6 redraft** — BLOCKED on the same `<<DECOY_RESULT>>`.
9. **`tau_bench_report.md` numbers** — plumbing READY; NO paper-ready τ-bench
   pass-rate numbers exist yet (smoke only, turn-cap-bound). See (4).
10. **`cross_family_report.md` runs** — parser fix READY (already merged in
    harness per the engineer); the cross-family TEHR *numbers* are BLOCKED on
    runs that cannot start until the M5 queue drains.

---

## (2) CONFLICTS / contradictions between artifacts

**C-1 (IMPORTANT — two different pooled Fisher headlines).**
The paper §5 and `abstract_variants.md` both report the RVR headline as
**14/973 (C0) vs 0/945 (C1), p = 7.1e-5**. But the freshly recomputed,
statsmodels-verified `stats_table.md` reports the pooled-over-4-nonzero-tiers
contingency as **19/1319 (C0) vs 0/945 (C1), p = 3.3e-5**, and an all-tiers pool
of 19/2405 vs 0/1484, p = 1.05e-4. These are NOT the same pool: the paper's
14/973 is the *RVR-validation re-run subset* (Table at `05_results.tex:202-205`,
8B = 4/269, 14B = 5/268), while stats_table aggregates the full probe C0 cells
from `headline_numbers.json` (8B = 9/615 across all probe runs). Both are
internally correct; they answer different questions.
→ RESOLUTION: pick ONE pool and label it explicitly. The cleanest story is to
keep 14/973 vs 0/945 as the *paired RVR-validation* result (matched C0/C1 cells)
and cite the 19/1319 figure separately as the full-probe descriptive rate. Do
NOT let the abstract say "14 fabrications" while a CI table elsewhere implies 19.
The C1 numerator (0/945) is consistent across both, so the "removes all
fabrications" claim is safe either way.

**C-2 (denominator drift the AC will flag — 268 vs 269, reused "1.49%").**
prereview.md R1/R4 flag `05_results.tex`: 8B C0 appears as **4/269** (Table 3,
:202) and **4/268** (ablation ladder, :230), and "1.49%" is printed for two
different cells (probe-8B 4/269=1.487% at :45, and miss_func-base at :230).
The `coverage_matrix.tex` and `stats_table.md` give the canonical per-version /
per-size denominators. → RESOLUTION: build ONE canonical denominator table from
coverage_matrix + stats_table, reconcile 268/269, and stop reusing "1.49%".
This is the same cleanup R1 and R4 both demand; it is free and removes a
credibility ding.

**C-3 (abstract N=2,599 vs stats_table N=2,456 / 3,237).**
abstract_variants.md and §1 say "0/2,599, CP upper ≤0.115%". stats_table.md
reports Anthropic *probe-only* = 0/2,456 (≤0.15%) and *probe+regime* = 0/3,237
(≤0.11%). The 2,599 figure (from coverage_matrix) is "all Anthropic C0 across
probe+regime+smoke". Three different pools, three different bounds, all floating
around. → RESOLUTION: state the pool inline every time a bound is printed. The
abstract's "2,599 / ≤0.115%" is defensible IF the body defines 2,599 as the
all-C0 pool (coverage_matrix does). Make §4 / coverage_matrix the single
definition and have abstract + §1 + §5 all point to it. This is NOT a numerical
error, it is an under-specified-denominator problem — exactly R1's pooling
complaint in a different guise.

**C-4 (NOT a real conflict — distractor-shift framing).**
abstract_variants Variant B narrates the distractor-type shift (near→matched→
synonym) as a finding; prereview R1 demands it be demoted to "anecdotal, not
significant" (Friedman p=0.46). s33_s6_redraft already does the demotion
correctly. → If Variant B is chosen, its distractor sentence must be softened to
match the s33_s6 redraft. Variant A already treats it as phenomenology.
No contradiction if A is chosen; a wording sync if B is chosen.

No citation any artifact RELIES ON is flagged SUSPECT — citation_audit cleared
all four high-risk 2026 refs, and all prior-art/mechanism keys exist in refs.bib.

---

## (3) Five highest-leverage MAIN-TRACK changes (distilled from prereview.md)

Ranked by vote-shift per unit effort, per the four-reviewer synthesis.

1. **Break the vendor/quantization confound with ONE run.** Add a full-precision
   (bf16) Qwen3 sweep, OR one non-Anthropic frontier API (GPT/Gemini) at the
   probe. Cited by R2 (confound), R3 (the single unrun counterfactual), R4
   (reject-reason #2). Tells you whether the Anthropic zero is a *frontier* or an
   *Anthropic* property and whether the non-monotone curve survives
   de-quantization. Cheapest high-leverage fix. (Partly addressable via
   cross_family runs — see (4) — but those are 4-bit too, so they break *vendor*
   not *quantization*; a bf16 run is still needed for the quant confound.)

2. **Multiply the event count on the non-zero Qwen3 tiers.** Restore the
   pre-registered N≥100/cell (cut to 15 for breadth) on 1.7B/4B/8B/14B so each
   per-tier Fisher stands without pooling, and so the C0.7/C0.8 "decorative
   registry" claim rests on >0 events rather than 0/253. Kills R1's pooling
   objection and R3's power gap. Zero marginal cost on M5 — no budget excuse.

3. **Prove RVR changes behavior, not just gates execution.** Measure (a)
   post-reprompt re-fabrication rate and (b) downstream task-success delta on the
   Qwen3 tiers (not just Anthropic N=60). Directly answers R2's circularity
   kill-shot ("a membership filter evaluated on membership violations"). Also
   extend the Anthropic non-inferiority N past 60 so the −11.7pp strict-pass drop
   is bounded (R1/R2/R4).

4. **Demote every underpowered narrative to descriptive — in the abstract too.**
   Distractor-type shift (p=0.46) and the "32B collapse" (CI overlaps 14B).
   Add a heterogeneity test (Breslow–Day / Cochran Q) BEFORE pooling the four
   RVR strata — currently no pre-pooling heterogeneity test is run. Cheap;
   removes R1's strongest rubric ding. (s33_s6_redraft already does the §6 half
   of this; the abstract half is gated on the A-vs-B choice in (4).)

5. **Reconcile the numbers and defuse self-substitution.** Fix the 268/269 drift
   and doubly-used "1.49%" (= Conflict C-2); make one canonical results table.
   Separately, reframe `07_limitations.tex:5` so RVR is NOT described as
   replaceable by executor-side allow-listing — that line hands R2/R4 a free
   "why is this a contribution" reject. Argue the message-level signal changes
   the model's context (an allow-list does not), or move that comparison into a
   measured result (this is exactly what change #3 would provide).

**Gate:** Changes 1 and 2 are the accept/reject gate. Without more events + one
confound-breaking run, four reviewers reject (AC accept prob 18%, WEAK_REJECT;
clear ACCEPT at the SCALE workshop bar).

---

## (4) What is BLOCKED on decoy / N-expansion / queue results

**Blocked on C0.8 decoy arm** (running now in `scripts/run_queue.sh`; aggregate
via `PYTHONPATH=. harness/.venv/bin/python scripts/aggregate_all.py`, pull the
`C0_8` row for 8B/14B/4B):
- **Abstract + §1 opening choice (Variant A vs B).** abstract_variants.md is
  explicit: decoy stays at zero → Variant A (format-not-content recovery, the
  spotlight framing); decoy regresses → Variant B (grounding-gap). Two
  placeholders to fill: A-abstract footnote and B-RVR-patch.
- **§6 redraft `<<DECOY_RESULT>>`** (s33_s6_redraft.md). Substitute as `$h/N$`
  mirroring `$0/258$`. If decoy FAILS (h/N materially > C1) the headline
  mechanism claim INVERTS — s33_s6 flags this must go back to the authors before
  merge, and §3.3's content-vs-format binary flips with it.

**Blocked on N-expansion** (change #2 above; non-zero Qwen3 tiers at N≥100):
- Per-tier Fisher significance — currently only 14B (p=0.033) and 8B (p=0.042)
  individually reject and NONE survive Holm across the family of 6
  (stats_table.md §b: zero "Holm reject" cells). The per-tier story does not
  stand without more events.
- The C0.7/C0.8 "decorative registry" claim rests on 0/253 vs 0/258 on one model
  (R3's weakest-powered/most-novel point).

**Blocked on the M5 queue draining** (cross-family + bf16 + behavior runs — do
NOT launch; they contend for GPU memory per the run constraint):
- **cross_family_report.md**: parser fix is merged and verified, but the actual
  cross-family TEHR numbers need the queued `run_probe.py` commands (Llama-3.1-8B
  is the one family the fix definitively recovers from existing data; Mistral
  needs a fresh run; Phi/Gemma are structurally incapable — footnote them as "no
  tool template"). These are 4-bit, so they address change #1's *vendor* axis
  only, not quantization.
- The bf16 Qwen3 sweep (change #1) and the behavior/re-fabrication runs
  (change #3) are not yet queued anywhere — they are the gating experiments and
  someone must schedule them after the queue finishes.

**Blocked on a higher τ-bench turn cap** (tau_bench_report.md):
- τ-bench is wired end-to-end and verified (152 tests pass; 0/24 pooled TEHR on a
  3-task Haiku smoke), which answers the "BFCL-only" reviewer criticism at the
  *plumbing* level. But NO pass-rate numbers are paper-ready: all 3 smoke tasks
  hit the 8-turn cap (reward 0.0). Need `turns_max` raised to ~15–20 in
  `harness/bench_loaders/tau_bench.py` and a fuller cell (n≥15) before any
  τ-bench number goes in the paper. This is API-only (won't contend for M5), but
  watch Anthropic spend. Until then, cite τ-bench as "second benchmark wired,
  TEHR consistent with Anthropic null on smoke," not as a results pillar.

---

## Quick merge order (what to do first)

1. Now, no risk: merge Tier A (priorart, security_motivation, coverage_matrix);
   adopt stats_table as the CI backbone; do the C-2/C-3 denominator reconciliation
   pass (canonical table). Merge §3.3 trim (Tier B) + its §3.4 follow-on edit.
2. When C0.8 lands: choose Variant A/B, fill both placeholders, merge §6 redraft.
   If decoy FAILS, escalate to authors first (mechanism inverts).
3. After queue drains: run change #1 (bf16) + #2 (N≥100) + #3 (behavior) +
   cross-family probes; these are the main-track gate.
4. Separately: raise τ-bench turn cap, run one fuller cell, then decide whether
   τ-bench is a pillar or a footnote.
