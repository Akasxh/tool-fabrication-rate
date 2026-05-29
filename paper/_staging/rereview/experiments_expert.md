# Re-Review — MARG Experiments Expert (main-track ICML bar)

**Paper:** "Who Hallucinates Tools, How Often, and What Fixes It" (TFR/RVR)
**Reviewer persona:** Empirical ML / experimental-design expert (MARG, arXiv:2401.04259)
**Bar applied:** ICML 2026 main track (not workshop).

I design the experiments the headline claims would require, then diff against what was run. My hypothetical design is the baseline.

---

## Headline claims under test

1. **Format-not-content recovery.** A structured `tool_not_found` envelope re-grounds the model regardless of registry content; the decoy (C0.8, wrong names) recovers as well as the real list (C1).
2. **Open-vs-closed split.** Anthropic 4.x (0/2,599) and OpenAI 4.x (0/2,070) fabricate ~0%; Qwen3 shows a non-monotone curve peaking at 1.87% at 14B.
3. **RVR fixes it.** 14/14 pooled Qwen3 fabrications removed, Fisher p=7.1e-5.
4. **The bump is a capability window, not a quantization artifact** (0.6B and 32B bracket it at the same 4-bit precision).

---

## Findings — `ISSUE | OBSERVED | YOUR-HYPOTHETICAL | GAP`

### F1 (BLOCKER). The headline "14 fabrications" undercounts the paper's own data by a third.
`ISSUE` Pooled-event arithmetic is inconsistent across tables.
`OBSERVED` Table 2 (`tab:qwen3-scale`, §5.3) sums to **19 events / 1,618 calls** (8B=9/615). Table 5 (`tab:rvr-validation`, §5.4) and the abstract claim **14/973** (8B=4/269). The paper footnotes that RVR cells are a "matched-run subset" with smaller denominators, but the abstract states RVR "removes all fourteen pooled Qwen3 fabrications" as the headline — silently dropping the other 5 events (the 8B 9→4 and 14B 5→5 reconciliation is never shown). Line main.tex:80–81; 05_results.tex:163–188.
`YOUR-HYPOTHETICAL` One canonical event ledger; RVR evaluated on the *same* C0 cells that produced the 19, or an explicit statement "RVR was only run on the 14 events in matched cells; the other 5 (8B full-probe) are untested by RVR."
`GAP` A reviewer who adds the table columns finds 19≠14 and cannot reconcile without the repo. At the main-track bar this reads as the central result not surviving its own arithmetic.

### F2 (BLOCKER). The format-not-content claim — the new spine of the paper — rests on **zero events to suppress.**
`ISSUE` C0.7 (0/448), C0.8 decoy (0/410), C1 (0/258) are all compared at **0 events each.** "A wrong list recovers as well as the right list" (06_mechanism.tex:31–33) is "0 = 0 = 0."
`OBSERVED` The 8B C0 base rate is 1.46% (9/615). C0.7/C0.8/C1 arms run on 258–448 calls. Expected events at 1.46% over ~450 calls ≈ 6–7; the arms could plausibly hit 0 even if the intervention did nothing, because the per-arm N is too small and the base rate too low. The decoy footnote (main.tex:87–90) splits 410 calls into four sub-arms of ~100, where expected events <2 each. CP upper bound on the decoy is ≤0.73% — fully overlapping the 1.46% baseline is NOT shown to be excluded; 0/410 only rules out rates above ~0.73%, but the baseline is 1.46%, so the arms ARE underpowered relative to baseline... yet the comparison is "indistinguishable from C1," which is a null-equals-null.
`YOUR-HYPOTHETICAL` Power the ablation against a base rate that *produces events*: run C0/C0.7/C0.8/C1 on the **14B synonym arm** (the 5/69=7.2% hot cell) or pool 8B+14B synonym to get N with ≥10 expected C0 events, so that C0.8≈C1≈0 while C0>0 is a real contrast, not 0-vs-0.
`GAP` The paper's marquee reframe ("format, not content") is currently a comparison of three zeros. That is the single weakest point and it is now load-bearing.

### F3 (MAJOR). Vendor/quantization confound — the gate from the prior round — is still open; the fix is in-flight, not in the paper.
`ISSUE` Anthropic/OpenAI run at native precision via API; Qwen3 runs 4-bit MLX. The "0.6B and 32B bracket the peak at the same 4-bit precision" argument controls *within* Qwen3 for the *shape* but does nothing for the *cross-vendor 0% vs 1.87% gap*, which is the open-vs-closed headline.
`OBSERVED` 07_limitations.tex:5 explicitly concedes "parameter count, 4-bit MLX quantization, training recipe, and provider guardrails co-vary." The bf16/8-bit control is NUMBERS_TODO (A1_appendix.tex:150–155).
`YOUR-HYPOTHETICAL` Qwen3-8B and 14B at bf16 + 8-bit on the same probe. If the curve survives, quantization is exonerated and the headline holds. This is exactly the in-flight cell.
`GAP` Until it lands, the central comparison (commercial-vs-open) is confounded by precision. The within-Qwen bracketing is a partial, not full, control.

### F4 (MAJOR). "Is RVR just reflection?" has no in-paper baseline.
`ISSUE` The condition ladder has C0.5 ("try again", naive retry) but no *reflection* baseline (Reflexion-style self-critique) — yet §2 cites Reflexion/CRITIC as the nearest neighbors. C0.5 at 0.39% (1/258) is a single event; it does not isolate reflection from format.
`OBSERVED` A2 reflection arm is NUMBERS_TODO, preliminary 2/30. The paper as-it-stands cannot answer "does any structured retry work, or specifically the envelope?"
`YOUR-HYPOTHETICAL` A reflection arm at matched N with events. Preliminary 2/30 (≈6.7%) suggesting reflection does NOT help would be a strong differentiator — but it is not in the paper.
`GAP` The method's novelty over Reflexion/CRITIC is asserted (§2), not demonstrated.

### F5 (MAJOR). Event count is tiny; every per-tier test is underpowered and the authors say so.
`ISSUE` 19 (or 14) total positive events across the entire open-model arc. Per-tier Fisher p = {0.24, 0.12, 0.058, 0.032} — none individually significant (05_results.tex:226–229). The pooled p=7.1e-5 rests on 14 events in 4 strata.
`OBSERVED` Friedman p=0.46 (n=4 sizes) — the scale-curve "drift" is non-inferential by the authors' own admission (06_mechanism.tex:50–53). Probe N cut from 100 to 15/cell (A1:140).
`YOUR-HYPOTHETICAL` N≥100/cell event-multiplication on 8B/14B (the in-flight cell) to get per-tier significance, not just a pooled contrast carried by one or two events per tier.
`GAP` A 7pp non-monotone "curve" built on a peak of 5 events (14B synonym) is descriptively interesting but inferentially fragile; "six points isn't a curve" is conceded three times, which a main-track reviewer reads as the result not being ready.

### F6 (MAJOR). Unreconciled internal number flagged in the authors' own comment.
`ISSUE` 05_results.tex:38 carries a live `NUMBERS_TODO`: the Qwen3-8B miss_func cell "5/258=1.94%" is "absent from aggregator; rerun and reconcile against base full-probe 9/615=1.46%." The body states 5/258=1.94% as fact (line 39–40) while the comment says the number is not in the aggregator.
`OBSERVED` A claimed-but-unaggregated number is in the running text.
`YOUR-HYPOTHETICAL` Every number in the body regenerated by `aggregate_all.py` (the paper's own reproducibility promise, A1:163).
`GAP` This violates the disclosure claim "no p-value appears without a code path that regenerates it" (08:18–19). One number currently does not.

### F7 (MINOR). BFCL contamination unaddressed; Anthropic null may be a benchmark-memorization artifact.
`ISSUE` 07:5 concedes the zero-event regime "is indistinguishable from BFCL v4 contamination" with no paraphrase/membership control.
`YOUR-HYPOTHETICAL` A paraphrased-registry or held-out-tool-name control on ≥1 Anthropic model.
`GAP` The "Anthropic doesn't fabricate" half of the headline could be "Anthropic memorized BFCL." Cheap to partly rule out; not done.

### F8 (MINOR). Reproducibility-from-artifact: borderline pass.
144 unit tests, anonymous repo, master seed 42, SHA-256 distractor RNG, manifest pins (04_setup.tex:37–44). A $1000-compute reviewer CAN re-run the Qwen3 sweep on consumer hardware ($73 API + free local). Good. BUT F1/F6 mean the *released traces* must reconcile 19 vs 14 and supply the missing miss_func cell, or repro will surface the same contradiction.

---

## The single experiment most likely to flip a borderline vote (not run)

**A powered C0/C0.7/C0.8/C1 ablation on a hot cell that actually produces C0 events** (8B+14B synonym pooled, or N≥100 event-boosted). The entire "format-not-content" reframe currently compares three zeros (F2). One arm where C0 fires ≥10 events while C0.8≈C1≈0 would convert the spine from "null=null" to a real causal contrast. This single experiment, more than the quantization control, is what stands between "interesting workshop finding" and "main-track mechanism claim."

## Probability the existing experiments support the headline

**As-it-stands: 22/100.** The format-not-content headline is 0-vs-0-vs-0 (F2), the central event ledger is internally inconsistent (F1, 19≠14), one body number is un-aggregated (F6), and the cross-vendor gap is precision-confounded (F3). The descriptive curve and the engineering artifact are real and well-instrumented, but the *inferential* claims outrun 14–19 events.

**If in-flight lands as expected: 41/100.** bf16/8-bit control breaking the quant confound (F3) + A2 reflection showing 2/30 (F4) + N≥100 event-multiplication giving per-tier significance (F5) would together move this from "fragile workshop accept" toward "borderline main-track." It does NOT fix F2 unless the powered ablation runs on a cell with events, nor F1/F6 (pure bookkeeping). Even with everything landing, the format-not-content claim needs events under it; the in-flight list does not obviously include that specific powered-decoy arm.

---

## Verdict

**WEAK_REJECT at the main-track bar.** Strong diagnostic + clean artifact + honest limitations, but the marquee reframe rests on zero-event comparisons, the event ledger contradicts itself (19 vs 14), and the cross-vendor headline is precision-confounded. In-flight experiments materially help two of four blockers but do not, on their current spec, put events under the format-not-content spine. This is a clear workshop accept; main track needs the powered ablation.
