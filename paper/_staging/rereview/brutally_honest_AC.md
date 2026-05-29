# Final meta-review — Brutally honest AC (main-track ICML bar)

**Paper:** "Who Hallucinates Tools, How Often, and What Fixes It" (TFR / RVR)

The revision is a real improvement: the prior-art table (App. Tab. tab:priorart),
Clopper–Pearson bounds on every zero, the OpenAI 0/2070 fold-in, and the honest
underpowering admissions (Friedman p=0.46, TOST 1−β<0.30) are exactly what the last
panel asked for. The de-AI'd prose reads cleanly. But at the *main-track* bar one
structural problem and two reconciliation defects remain, and one of them is
vote-flipping.

## The single vote-flipping issue: the new spine is an argument from three nulls
The paper now leads with "format-not-content recovery" as "the spine of this paper"
(§1 L13) and rests it on §6: C0.7 (0/448), the C0.8 decoy (0/410), and C1 (0/258) on
Qwen3-8B all hit zero, therefore "registry content is decorative" (§6 L31-32, abstract
footnote). This does not survive scrutiny. The matched 8B C0 base rate is ~1.5%
(4/269, Tab. tab:rvr-validation). Three *zero-event* arms at N≈250–450 are mutually
indistinguishable — and indistinguishable from C0.5's 1/258 — because there are no
events left to separate them. The paper's own Newcombe CI on C1−C0.7 is [−1.5,+1.4]pp
(§5.4 L215): an interval fully consistent with content buying >1pp. You correctly
refuse to over-read Friedman and TOST for identical power reasons, then exempt the
headline from the same humility. "Content is decorative" is absence-of-evidence sold
as evidence-of-absence. As stated, the central claim is not supported at the bar it
is pitched. Either (a) demote it to "no detectable content effect at this N, bounded
by [−1.5,+1.4]pp" throughout (abstract, §1, §6), or (b) multiply events so the three
arms can actually be distinguished. This is the one fix that moves my vote.

## Two reconciliation defects a senior reviewer will catch
1. **The 2,599 pool does not reconcile by the path the paper hands the reader.** §5.2
   L58-60 instructs: "Combine the regime cells with the probe cells." Probe table
   (1,917) + regime (661) = **2,578**, not 2,599 (21-call gap). The coverage table
   (App. tab:coverage) *does* sum to 2,599, but via different per-model counts
   (Sonnet 4.6 = 677 there vs 561 in tab:anth-temporal). Two stated paths, two answers.
2. **A flagged-unverified number is live in the body.** §5.1 L40 asserts Qwen3-8B
   miss_func = "5/258 = 1.94%," while the inline comment (L38) admits the cell is
   "absent from aggregator; rerun and reconcile." This directly contradicts the
   disclosure pledge that "no number appears without a code path that regenerates it"
   (§8). Remove or regenerate before submission.

Minor: stale `\textsc{tehr}` survives the rename in the coverage caption (App. L105).

## Verdict
As-is, this is a strong workshop paper over-reaching for a main-track claim it cannot
power. The descriptive Qwen3 non-monotone curve + open-vs-closed split + RVR are a
genuine, well-instrumented contribution; the "format-not-content" spine is the part
that breaks. The total non-Anthropic signal is still **19 events** (RVR demo rests on
14), so every inferential claim is one re-seed away from moving.

**If the in-flight experiments land as expected:** the bf16/8-bit quant control breaks
the most damaging confound (4-bit-artifact) and is the highest-value of the four; the
A2 reflection baseline (prelim 2/30) isolates "is RVR just reflection?" and directly
shores up §6; N≥100 event-multiplication on 14B/8B is what actually lets you say
"content is decorative" instead of "no detectable effect"; gpt-5 rows extend the
closed-model null. Together these convert the spine from unsupported to defensible and
roughly double the event base. That is the difference between a clear reject-to-borderline
and a credible weak-accept.

**(a) Acceptance probability: 14 (current) / 41 (if in-flight lands).**
**(b) Verdict: WEAK_REJECT.**
**(c) Single most-important final fix:** demote "content is decorative" to a
power-bounded claim ([−1.5,+1.4]pp) everywhere it appears, OR land the N≥100
event-multiplication so the three recovery arms can be statistically separated — and
fix the 2,578-vs-2,599 reconciliation and the live unverified 5/258 cell.
