# Re-review Synthesis — "Who Hallucinates Tools, How Often, and What Fixes It" (TFR / RVR)

Date: 2026-05-29. Bar: ICML 2026 main track. Panel: 6 hostile personas. Baseline: pre-revision paper scored ~18% main-track accept (clear workshop accept), gated on (1) breaking the vendor/quant confound and (2) multiplying the ~19-event count.

---

## 1. Did the revision move the needle?

**No. It moved it backwards on the headline number, even though the craft improved.**

| Persona | Score /10 | Accept prob now | If-land | Verdict |
|---|---|---|---|---|
| hostile_statistician | 4 | 12% | 30% | WEAK_REJECT |
| adversarial_reviewer | 3 | 16% | 34% | REJECT |
| brutally_honest_AC | 3.5 | 14% | 41% | WEAK_REJECT |
| experiments_expert | 3.5 | 22% | 41% | WEAK_REJECT |
| main_track_area_chair | 3 | 7% | 16% | REJECT |
| quant_confound_skeptic | 4 | 12% | 30% | WEAK_REJECT |

- **Mean score now: 3.5/10. Median: 3.5/10.**
- **Mean accept prob now: ~13.8%. Median: ~13%.**
- **Baseline was ~18%.** The revision *lowered* the mean accept probability by roughly 4 points (18% → ~14%).

This is the honest, non-reassuring read: the prose, the prior-art table, the Clopper-Pearson bounds, and the honest underpowering admissions (Friedman p=0.46, TOST 1-β<0.30) are all real improvements and every persona credits them. But three things hurt:

1. **The new "format-not-content" spine is built on three zero-event arms** (C0.7 0/448, C0.8 0/410, C1 0/258). Five of six reviewers independently flag this as the textbook absence-of-evidence/evidence-of-absence error, now sitting in the *abstract* and as "the spine of this paper" (§1 L13). Leading with an equivalence-from-nulls claim is a *bigger* target than the old framing.
2. **The quant skeptic explicitly docked the paper *below* baseline** because the revision *hardened* the quant claim ("the curve is a capability effect, not a compression artifact," intro L65-68) while the controlling experiment (bf16/8-bit) is still TODO. It traded honest hedging for an overclaim the data does not back.
3. **Neither prior gate was closed.** The quant confound is still open (bf16 not in repo) and the event count was *not* multiplied — worse, the headline now reports the **14-event matched subset**, not the 19-event full pool, which reads as cherry-picking the cleanest denominator.

Net: the paper is a cleaner, better-written instance of the same workshop paper, now reaching for a main-track claim (format-not-content) it cannot power. Consensus is unanimous WEAK_REJECT/REJECT; no persona is at or above borderline today.

---

## 2. Projected score if the in-flight experiments land

In-flight: bf16/8-bit quant control, A2 reflection baseline (prelim 2/30), gpt-5 frontier rows, N≥100 event-multiplication on 14B/8B.

- **Mean if-land accept prob: ~32%. Median: ~32%.** Per-persona ceilings: stat 30%, adversarial 34%, AC 41%, experiments 41%, ACitc 16%, quant 30%.
- This roughly **doubles** the current ~14% and lands in **"borderline main-track / strong workshop"** territory — not a clear accept.
- The hard ceiling is set by the **area chair (16% even if everything lands)**: the in-flight list does not add a **second benchmark with a non-zero base TFR**, and it does not obviously put **events under the C0.7/C0.8 ablation**. Both the AC and the experiments expert state plainly that the queued experiments harden robustness but cannot flip the breadth gate or the format-not-content gate on their own.

So: in-flight success converts a unanimous reject into a *genuine borderline*, but four of six personas cap the if-land scenario at ≤41% precisely because the two structurally-load-bearing gaps (second site; events under the decoy) are not on the in-flight manifest.

---

## 3. Highest-leverage remaining fixes, ranked

### Tier A — structural, NOT addressed by any running experiment (these set the ceiling)

**A1. Put events under the format-not-content spine (powered C0/C0.7/C0.8/C1 on a hot cell).**
Five of six personas converge here. The decoy/no-list/real-list equivalence is currently 0=0=0; the C1−C0.7 Newcombe CI [-1.5,+1.4]pp is *consistent with content buying >1pp*. The experiments expert names the exact missing run: pool 8B+14B synonym (the 7.2% hot cell) or use the N≥100-boosted cell so C0 fires ≥10 events while C0.8≈C1≈0. **Critical: the listed N≥100 event-multiplication only fixes this IF the decoy arms are re-run on that boosted cell.** As specified, event-multiplication and the powered-decoy ablation are not the same experiment — make them one. *Until then, demote "content is decorative" / "recovers as well as" / "indistinguishable" to the bounded claim "no detectable content effect at this N, bounded by [-1.5,+1.4]pp" everywhere (abstract, §1, §6).* This is the single fix the AC, the brutally-honest-AC, and the statistician all say moves their vote.

**A2. Add a second benchmark with a non-zero base TFR (tau-bench / ToolSandbox / Seal-Tools).**
This is the *only* fix the main-track AC says flips workshop→main, and it is the one gap no in-flight item touches. tau-bench material exists in `_staging/tau_bench_report.md` but is not in-body. Without a second non-zero site, the entire positive story is "n=14 on one harness," which caps main-track enthusiasm regardless of execution quality. Highest *ceiling-raising* fix; also the most expensive.

### Tier B — hygiene, NOT fixable by experiments, cheapest reject levers (do these regardless)

**B1. Reconcile every table to one regenerated aggregator pass.** All six personas cite at least one of these; the adversarial reviewer calls it the cheapest reject lever an AC has:
- **Delete or regenerate the live `NUMBERS_TODO` miss_func cell** (`05_results.tex:38-42`, "5/258=1.94% absent from aggregator"). Cited by all 6. Violates the §8 disclosure pledge ("no number without a code path that regenerates it"). Desk-checkable in five minutes.
- **Resolve the 14-vs-19 event ledger.** Either run C1 on the full per-tier probe pools so prevented = headline fabrication count, or restate honestly as "14/19, the other 5 (8B full-probe) untested by RVR."
- **Fix the four conflicting 8B denominators** (9/615 scaling, 4/269 RVR, 9/615 ablation, 108 coverage-regime in `A1_appendix.tex:127`).
- **Fix the 2,578-vs-2,599 reconciliation** (regime 661 + probe 1,917 = 2,578 by the path §5.2 hands the reader; coverage table sums to 2,599 via different per-model counts, e.g. Sonnet 4.6 = 561 vs 677).
- **Reconcile the OpenAI pooled denominator** (gpt-4o 419 vs 466; five-model sum 2,070 vs 2,117).
- **Kill the stale `\textsc{tehr}`** in the coverage caption (`A1_appendix.tex:105`) and the `sec:method:tehr` label after the TFR rename — reads to a blind reviewer as "numbers not re-derived after rename."

### Tier C — running experiments DO address these (necessary, not sufficient)

**C1. bf16/8-bit Qwen3-14B at matched N.** Addresses the quant confound (Gate 1) and the skeptic's single most dangerous objection. *Decisive both ways:* if 1.87% survives, the curve is earned; if it collapses, the paper must reframe entirely around the confound-clean RVR result. Also requires disclosing the per-checkpoint quantization recipe (group size, bits-per-weight, identical `mlx_lm convert` flags) — the skeptic notes the manifest pins none of this, so even a surviving curve needs recipe disclosure to be airtight.

**C2. A2 reflection baseline at N≥100.** Isolates "is RVR just reflection?" — the missing positive control the experiments expert and statistician most want, because it introduces a *non-zero comparator arm* into a field of zeros. Prelim 2/30 (~6.7%) suggesting reflection alone does NOT help is exactly the differentiator over Reflexion/CRITIC the §2 novelty defense currently asserts but doesn't demonstrate. Land at N≥100/arm.

**C3. N≥100 event-multiplication on 8B/14B.** Converts ~14-19 events into per-tier-significant counts (current per-tier Fisher {0.24, 0.12, 0.058, 0.032} all individually non-significant). Note this *also* requires a Cochran-Mantel-Haenszel stratified test + Breslow-Day homogeneity (the statistician flags naive pooling of heterogeneous-denominator strata as a citable error). **Only flips the spine if the decoy arms ride on the boosted cell — see A1.**

**(gpt-5 rows: cosmetic. More zeros widen the commercial null; address no confound and no gate. Lowest priority.)**

---

## 4. Honest verdict on main-track viability

This is a clean, honest, well-instrumented **workshop paper** wearing a main-track frame it cannot support. As it stands it is a unanimous reject (mean 3.5/10, ~14% accept) and the revision, despite genuinely better craft, *lowered* the expected accept probability by leading with a "format-not-content" equivalence claim built on three zero-event arms and by hardening the quant claim ahead of its data. The realistic **ceiling, even if all four in-flight experiments land clean, is ~30-41% — a true borderline, not an accept** — and that ceiling is held down by two gaps no running experiment touches: there is still only one benchmark with a non-zero signal (the AC's breadth gate), and the marquee ablation still has zero events under it unless the decoy arms are deliberately re-run on the event-multiplied cell. The fastest path off the floor is the cheap hygiene pass (Tier B: kill the unverified cell, reconcile every denominator, demote "decorative" to a bounded claim) plus the bf16 control; the only thing that genuinely flips workshop→main is the powered decoy ablation **and** a second non-zero benchmark, and the team should decide now whether the deadline (2026-04-28 AoE — note: already past per current date 2026-05-29, so this is presumably a resubmission/rebuttal cycle) allows both. If it does not, the strategically correct move the quant skeptic and others gesture at is to **reframe the paper around the confound-clean RVR result and demote the scaling curve to descriptive** — a defensible strong-workshop paper told honestly beats a main-track paper whose spine is three zeros.
