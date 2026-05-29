# R1 — Statistics Review

**Reviewer**: R1 (Statistics, biostatistician hat)
**Materials**: `PAPER_PLAN_v3.1.md` §4.3–4.5, §6; `paper/sections/04_setup.tex` (12-item pre-reg); `harness/HARNESS_SPEC.md` §2 stats modules.

---

## Verdict
**Major Revision.** Right vocabulary (paired McNemar mid-p, Holm–Bonferroni, TOST, bootstrap CI); wrong arithmetic. Headline test is structurally underpowered, TOST margin is incompatible with available SE, and the headline ratio has no error bar. All fixable in <8h.

---

## Top-5 Defects (ranked by severity)

1. **Effective N for the headline test is far below what the pre-reg implies.** With BFCL N=50 and TEHR ∈ [5,15]%, the *strict subset* (C0-failed-with-hallucination) yields **2.5–7.5 events per (model × condition)**. Pooling 4 API models gives 10–30 events. McNemar mid-p on b+c = 5 has **maximum attainable two-sided p ≈ 0.0625** even when discordance is fully one-sided (b=5, c=0): the test cannot reach α=0.05 *under any data*. This is a **structurally underpowered headline**, not a power-deficit one.
2. **TOST margin of 1pp is incompatible with the available SE.** With paired N≈25 and p̂≈0.9, SE(diff) ≈ √(2p̂(1−p̂)/N) ≈ 0.085. A 1pp equivalence margin requires the 90% CI on the difference to fall within [−0.01, +0.01]; required N to declare non-inferiority at typical effect=0 is **N ≈ 1100 pairs**. As written, TOST will be inconclusive ~95% of runs — a **type-II machine**.
3. **Family-wise error is not actually controlled.** Holm–Bonferroni is applied "across per-tier tests" (4 tests). The paper's *actual* test family is 4 tiers × 2 benchmarks × {ΔPass, TOST, TEHR, probe} ≈ **30+ tests**. At nominal α=0.05, expected false rejections under global H0 ≈ 1.5. The pre-registration must declare the family explicitly or downgrade non-headline tests to "exploratory."
4. **Pooled-across-tiers headline is a hand-wave.** §4.4 item 9 says "headline is pooled." Pooling per-tier proportions requires either a common denominator (which you don't have — N varies per cell) or a random-effects estimator. **Neither DerSimonian–Laird nor REML is in the spec.** A naive weighted average produces a CI that ignores between-tier heterogeneity → **anticonservative** by 1.3–2× on typical τ².
5. **Gap-closure ratio has no variance estimator.** The headline ratio R = (P(small+C1) − P(small+C0)) / (P(frontier+C0) − P(small+C0)) is a ratio of two correlated differences. Delta-method variance:
   Var(R) ≈ Var(num)/μ_d² + (μ_n²/μ_d⁴)·Var(denom) − 2(μ_n/μ_d³)·Cov(num,denom).
   Plan reports a point estimate only. **Without a paired bootstrap CI on R itself, the headline is a number with no error bar.**

---

## Specific Concerns

### C1. McNemar mid-p formula (HARNESS_SPEC §2)
Spec: `0.5·P(X = min(b,c)) + P(X < min(b,c))`, doubled two-sided. Matches Fagerland, Lydersen & Laake (2013). **Algebraically correct.** But: clamp at 1.0 when b=c; special-case b+c=0 → 1.0. Unit test at b=5, c=0: p_mid = 2·(0 + 0.5·(0.5)⁵) = **0.03125**. *That* is the only configuration at N_disc=5 clearing α=0.05. Document this floor.

### C2. Percentile bootstrap (`tehr.py`)
At rates near 0/1 (probe random-distractor cells likely TEHR ≈ 0), percentile CI is **biased, non-monotone in n**. **Switch to BCa** (Efron 1987); `scipy.stats.bootstrap(method="BCa")` is in pinned SciPy ≥1.13. Mandatory for the gap-closure ratio.

### C3. Probe ANOVA assumes normality of a [0,1] outcome
ANOVA + Tukey on bounded proportions with small per-task denominators (often 1–3 calls) is mis-specified. Replace with **Friedman + Nemenyi** on per-task ranked TEHR across 3 distractor types (preserves within-task pairing). 5 lines of `scipy.stats.friedmanchisquare`. ANOVA → appendix sensitivity.

### C4. Power calculation is missing
§4.4 item 10: "ΔPass ≥ 20pp at 80%" — *under what π_C0.5 and ρ?* At π_C0.5=0.30, π_C1=0.50, ρ=0.5: McNemar needs N_pairs ≈ 38 (Connor 1987). At ρ=0.2: N≈55. Pre-reg **must** commit to π_C0.5, ρ before pilot or this is post-hoc-able. Suggest π_C0.5=0.10, ρ=0.3 → N_disc ≈ 45 → **headline only works if pilot TEHR ≥ ~12% on ≥3 of 4 API models**. Hard-code into G2.

### C5. TEHR denominator is per-call → cluster-correlated
§4.4 item 1: denominator = tool calls. Multiple calls per task → non-i.i.d. McNemar and bootstrap both assume independence; here they're cluster-correlated within task. `tehr_bootstrap_ci` resamples per-call, not per-task. **Bug.** Fix to cluster-bootstrap by task, or aggregate to per-task before testing.

---

## Required Changes (binding for headline defense)

| # | Change | Owner | Effort |
|---|---|---|---|
| RQ1 | Headline McNemar must pool C0-failed-hallucinated pairs across all 4 API models *before* the test, not after; report pooled b, c with cluster-bootstrap CI on the discordance ratio. | A4 | 2 h |
| RQ2 | TOST: widen margin to **5pp** OR reframe as "estimated diff with 95% CI; pre-registered non-inferiority threshold 5pp." | M | 30 min |
| RQ3 | Replace percentile bootstrap with **BCa** in `tehr.py` and in a new `gap_closure_bootstrap_ci`. | A4 | 1 h |
| RQ4 | Replace probe ANOVA with **Friedman + Nemenyi**; ANOVA → appendix. | A4 | 1 h |
| RQ5 | Pre-register the test family explicitly (count = K); apply Holm at α=0.05/K across the *entire* family, not per-tier. | M | 30 min |
| RQ6 | Add a **paired cluster-bootstrap CI on gap-closure ratio R** (resample tasks, recompute R 10K times, BCa). | A4 | 1.5 h |
| RQ7 | Power calc: commit to π_C0.5=0.10, ρ=0.3; recompute N_disc; tie G2 pass to pilot TEHR ≥ 12% on ≥3 models. | M | 30 min |

Total: **~7 h** of A4 + harness work, well inside Phase-1+2 envelope.

---

## Strongest Element
The **pre-registration mechanism itself** (§4.4 12 items locked at T+05:00 before pilot inspection) is the single best decision in the plan. It pre-empts the standard reviewer attack ("you HARKed your way to ΔPass=20pp"). Keep this; just *complete* it (RQ7).

## Weakest Element
The **gap-closure ratio as headline** without a CI. A ratio of two small differences with correlated noise is the single most fragile quantity in the paper, and the plan presents it as a point estimate. This is exactly the kind of statistic that produces **type-S errors** (sign flips under modest re-sampling) — Gelman & Carlin 2014.

---

## Justification
The plan honors the right *vocabulary* of frequentist inference but does not honor the *arithmetic*. McNemar at b+c=5 cannot reach α=0.05 except in the most extreme configuration; TOST at 1pp requires ~40× the available N; the headline ratio has no error bar; the test family is 6× larger than the correction admits. All four are first-week-of-biostats failure modes. Each has a one- or two-hour fix. Apply RQ1–RQ7 and the headline becomes defensible; ship as-is and the first competent reviewer reduces the paper to "directional pilot evidence."

— R1
