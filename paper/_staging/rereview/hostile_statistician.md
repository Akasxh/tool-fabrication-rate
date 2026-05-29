# Re-review — Hostile Statistician (main-track ICML bar)

**Paper:** "Who Hallucinates Tools, How Often, and What Fixes It: A Per-Call Study Across Anthropic 4.x and Qwen3"
**Reviewer persona:** statistical-theory PhD, rejects if any statistical sin survives.
**Bar applied:** ICML 2026 main track (not workshop).
**Verdict:** WEAK_REJECT as-it-stands; BORDERLINE if all in-flight experiments land clean.

---

## 0. Bottom line up front

The revision genuinely fixed the worst of the pre-revision sins: every zero now carries a
Clopper–Pearson bound (good — Wald at a boundary proportion was the single most ding-able
issue last round and it is gone), the Friedman test is honestly reported as underpowered
(p=0.46, n=4) and explicitly demoted to "phenomenology, not inference," and the vendor
story is now correctly hedged as a confound rather than a causal claim. The "format-not-content"
reframe (C0.8 decoy = C0.7 = C1) is a real, design-clean binary contrast and is the best
thing in the paper.

But the central inferential engine of the new framing rests on a **pile of zero-event cells**,
and a hostile statistician's job is to ask what a pile of zeros can and cannot establish. The
answer is: it can establish an *upper bound*, and the paper mostly respects that. Where it
does **not** respect it — the abstract's "recovers as well as," the §6 "indistinguishable,"
and the "registry content is decorative" claim — it is over-reading equivalence from
non-rejection. That is the headline statistical sin of this draft. Plus one hard
data-integrity problem (a fabricated cell still in §5) that on its own is FIX-FIRST.

---

## 1. FIX-FIRST findings (per persona format: LINE | ISSUE | FIX)

```
05_results.tex:38–42 | DATA INTEGRITY. The Qwen3-8B miss_func cell "5/258 = 1.94%" is
  printed as a result, but the canonical aggregator (scripts/aggregate_all.py) contains NO
  Qwen3-8B miss_func cell at all — the only Qwen3-8B regime cell is multi_turn_base, 0/108.
  The NUMBERS_TODO comment on line 38 admits the number "absent from aggregator." A printed
  numerical result with no backing run is a fabricated cell. A stats reviewer who spot-checks
  the repo finds this in five minutes and the paper is dead. | Either run the cell and
  reconcile, or delete the sentence and the claim that miss_func "logs 1.94%, slightly above
  base." Do not ship a number the aggregator cannot reproduce.

abstract:91 / 06_mechanism.tex:31–37 | EQUIVALENCE FROM NON-REJECTION. "registry content is
  decorative for recovery" / "A wrong list recovers as well as the right one" is an
  equivalence claim built from three ZERO-event arms (C0.7 0/448, C0.8 0/410, C1 0/258).
  Zero events do not establish equivalence; they establish that all three upper bounds are
  small (≤0.67–0.73%). The arms are mutually consistent with a TRUE difference anywhere in
  [−0.73%, +0.67%]. You cannot conclude "as well as" — you can only conclude "no arm exceeded
  ~0.7%." This is the absence-of-evidence/evidence-of-absence error, dressed in new clothes. |
  State it as a bounded claim: "no decoy/no-list arm produced a detectable fabrication;
  all three upper bounds ≤0.73%." Run a TOST or a two-one-sided CP-difference equivalence
  test against a pre-stated margin (e.g. 1pp) and report it, or drop "as well as"/"decorative."

06_mechanism.tex:31 | "indistinguishable from the real list." Same sin, named explicitly.
  Two 0/N cells are always "indistinguishable" — that is what zero-power looks like, not what
  equivalence looks like. | Replace with the bounded-difference CI you actually have
  (the C1−C0.7 Newcombe CI [−1.5,+1.4]pp is already in 05_results.tex:215 — USE that framing
  for C0.8 too, and state the equivalence margin you are claiming against).
```

## 2. NEEDS-NOTES findings

```
05_results.tex:220–230 | Fisher pooled vs. per-tier. The pooled 14/973 vs 0/945 Fisher
  one-sided p=7.1e-5 is the load-bearing significance claim. Pooling four 2×2 tables without
  a heterogeneity check (Breslow–Day / Cochran's Q) is exactly the pooling sin on the persona
  checklist. The per-tier p's {0.24,0.12,0.058,0.032} are all individually non-significant;
  the pooled p is driven by collapsing strata. With all four C1 cells at 0 events the direction
  is consistent, but you owe the reader a Cochran–Mantel–Haenszel stratified test (or
  exact-stratified) rather than a naive pooled 2×2, plus a one-line statement that the four
  strata are homogeneous. | Report CMH stratified by tier (it will still be significant) and
  state Breslow–Day p. Naive pooling of heterogeneous-denominator strata is the citable error.

05_results.tex:221–224 | "not paired at the call level; we treat the four tiers as independent
  strata." Good that you flagged it. But Fisher's exact assumes fixed margins / independence;
  the C0 and C1 runs are on the SAME tasks (matched runs, different N). Treating them as two
  independent samples throws away the pairing that exists at the task level. This is
  conservative for a reduction-to-zero (fine), but a sharp reviewer will note you chose the
  test that ignores your own design. | Acknowledge in one sentence that an exact paired
  (McNemar / conditional) analysis is unavailable because denominators differ, hence the
  unpaired Fisher as a conservative fallback. You half-say this; make it explicit.

05_results.tex:191–198 | TOST non-inferiority at N=60, power <0.30. Correctly reported as
  "can call neither." Honest. But then the abstract (line 99) and intro (84) both say "we
  recommend tier-conditional deployment" partly ON the strength of an undetermined cost. A
  recommendation cannot be derived from an underpowered null. | Keep the recommendation but
  anchor it on the C0 audit (deploy where TFR>0 is audited), not on the strict-pass TOST,
  which is uninformative. Minor framing, not a stats error per se.

abstract:74 / 01_intro:52 / appendix:142 | OpenAI pooled denominator drift. Paper says
  "0/2,070 pooled" across five OpenAI tiers; the aggregator gives gpt-4o = 0/466 (not 0/419
  as in 05_results.tex:141) and a five-model sum of 0/2,117, not 0/2,070. The bound moves
  trivially (≤0.14% either way) but the printed denominators do not reconcile with the repo.
  A reviewer who sums your own table catches it. | Re-pull from the aggregator and print the
  numbers it produces. Reconcile gpt-4o 419 vs 466.

stats_table.md vs paper | The staging stats_table.md (auto-gen header) reports Anthropic
  probe+regime = 0/3,237 and probe-only = 0/2,456, while the paper uses 0/2,599. The live
  aggregator DOES reproduce 0/2,599, so the paper is right and stats_table.md is stale — but
  a referee handed both the PDF and the repo sees two different "canonical" pooled N's. |
  Regenerate stats_table.md from the current aggregator before release so the supplement
  is internally consistent. Stale intermediate artifacts in the repo are a soft credibility hit.

04_setup.tex:34 | "Holm–Bonferroni across the three primary tests." Good that a family is
  named. But the family is {Fisher, Friedman, TOST} — three tests of three DIFFERENT
  hypotheses. Holm across non-exchangeable hypotheses of different families is defensible but
  unusual; the more natural family is the four per-tier Fisher tests (or the per-arm
  contrasts), which is where multiplicity actually bites. | State why the family is these
  three and not the per-tier panel. As-is it reads like multiplicity theater on the one test
  (Fisher) that would survive anyway.

01_intro:42 / appendix | "U-shaped capability window" invoked from SIX points, one of which
  (0.6B, 0/75) and the top end (32B, 0/224) are zero-event with CP uppers 3.92% and 1.33% —
  both of which OVERLAP the 1.87% peak. You say this ("read as not-detected, not emergent,"
  05_results:104–107). Good. But the abstract (95) calls the bump "a predicted signature,"
  which is a much stronger inferential claim than six points with overlapping CIs can carry.
  A Cochran–Armitage trend test on the size ladder is not significant and you don't run it. |
  Either run the trend/non-monotonicity test and report it (it will be null), or downgrade
  "predicted signature" to "consistent with" in the abstract to match §5's own hedge.
```

## 3. What the in-flight experiments do and do not buy (statistically)

- **Quantization control (8-bit/bf16):** This is the right experiment and addresses the
  largest *confound* (4-bit artifact), but it is a confound fix, not a *power* fix. It will
  let you say the curve is not a compression artifact. It does NOT increase the event count
  on which every significance and equivalence claim rests. Necessary, not sufficient.

- **A2 reflection baseline (currently 3/168 in aggregator: near 2/100, syn 1/68; paper memo
  says "2/30"):** Genuinely valuable — it is the one experiment that isolates "is RVR just
  reflection?" If reflection alone leaves TFR>0 while C0.7 drives it to 0, the format-not-content
  story gets a real comparator instead of three mutually-zero arms. This is the highest-value
  in-flight item from a stats standpoint because it introduces a NON-zero contrast arm.
  Caveat: at N≈30–168 it is itself underpowered; land it at N≥100/arm.

- **gpt-5 frontier rows (0/19, 0/53 so far):** Adds breadth, adds nothing inferential —
  more zero cells widen the commercial-null bound marginally. Cosmetic.

- **N≥100 event-multiplication on 14B/8B:** THIS is the single most important in-flight item.
  Every equivalence claim (C0.7≈C1≈C0.8), the per-tier Fisher power, and the CMH stratified
  test are all bottlenecked on ~14 total events. Multiplying events is what converts
  "all bounds ≤0.7%" into an actual powered equivalence test with a stated margin, and what
  rescues the per-tier Fisher from {0.24,0.12,0.058,0.032}. If this lands, the §6 thesis
  goes from "bounded" to "demonstrated."

**Projection:** if (a) the fabricated miss_func cell is removed/reconciled, (b) the
event-multiplication lands so a proper TOST equivalence (margin ≤1pp) backs "content is
decorative," (c) the A2 arm shows reflection-alone ≠ 0, and (d) quant control kills the
artifact reading — then the statistical objections collapse to NEEDS-NOTES and the paper is a
defensible BORDERLINE main-track submission. None of (a)–(d) is in the PDF today.

## 4. Persona-required summary

- **(a) Statistical correctness:** FIX-FIRST. One fabricated cell (05_results:38) and one
  equivalence-from-zero overclaim ("registry content is decorative," abstract:91 /
  §6:31) are disqualifying as written. The CP bounds, the honest Friedman demotion, and
  the unpaired-Fisher disclosure are correct and creditable.

- **(b) Single most ding-able issue on a stats rubric:** Claiming equivalence ("recovers as
  well as," "indistinguishable," "decorative") from three mutually zero-event arms with no
  equivalence test and no pre-stated margin — absence of evidence read as evidence of absence,
  the textbook error, sitting in the abstract.

- **(c) One-sentence fix:** Replace every "as well as / indistinguishable / decorative" with
  the bounded-difference framing you already use for C1−C0.7 ([−1.5,+1.4]pp), run a TOST at a
  pre-stated margin once the event-multiplication lands, and delete the unbacked
  Qwen3-8B miss_func 5/258 cell.

---

### Scoring (main-track ICML bar)
- As-it-stands: 4/10. Clean diagnostic and a genuinely clever format-vs-content contrast,
  but a fabricated cell and equivalence overclaims keep it under the bar.
- If all in-flight land as expected: ~5.5/10, BORDERLINE — promotable to weak-accept territory
  only if the powered equivalence test and A2 non-zero comparator both come in clean.
