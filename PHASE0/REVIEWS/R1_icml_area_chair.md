# ICML Area Chair Review — Round 1

## Persona
Senior ML researcher (~15y), regular ICML AC. Rewards crisp contributions; rejects buried ledes.

## Verdict
BORDERLINE (workshop-acceptable; would not hand-pick for oral)

## Top-5 issues (severity-tagged)
1. **[BLOCKER] — Contribution #1 is structurally weak.** v3.1 §2.3 item 1 reduces to *"we use a denominator API-Bank didn't,"* and 02_related_work.tex lines 39–48 reinforce that framing. "Disaggregation" is real but is *one* metric-design choice — not a contribution co-equal with the intervention or scaling claim. **Fix**: fold #1 into a measurement subsection of #2; promote the §6 causal probe (currently buried at 03_method.tex line 47) to its own contribution slot — it's the most novel thing here.
2. **[MAJOR] — Four contributions are not four.** §2.3 items 2/3/4 are *result, method, headline number* of the same study. A skimming reviewer sees one method + one finding. **Fix**: re-tile as (i) instrument, (ii) intervention, (iii) causal probe, (iv) cost-quality recommendation — each independently citable.
3. **[MAJOR] — N=50 BFCL + N=25 τ-bench is borderline for ICML-Main.** 04_setup.tex line 10 plus pre-reg item 10 concedes it. The *strict subset* (C0-failed-with-hallucination, paired) is the real denominator and can fall <30 in the small tier if TEHR is low. McNemar power at ΔPass=20pp with n≈30 is marginal. **Fix**: pre-commit N≥75 BFCL on the two frontier models; report strict-subset n in every table; if any cell <30, demote to descriptive in §5.
4. **[MAJOR] — Differentiation from L-ICL / Fission-GRPO / Engländer is asserted, not earned.** 02_related_work.tex lines 64–82 names them but never compares numbers or runs them on the same slice. "Orthogonal to Fission-GRPO" (line 75) is hand-waved — yet the local tier already runs Qwen3-8B, the exact base for the public Fission-GRPO checkpoint. **Fix**: stack RVR on a Fission-GRPO Qwen3-8B in appendix, or explicitly scope out with a paragraph.
5. **[MINOR] — "Training-free" collides with the constrained-decoding analog framing** (03_method.tex (iv), lines 36–37). If RVR is "constrained decoding without logit access," reviewers will ask for an apples-to-apples constrained-decoding baseline on the Qwen3-8B local tier where logits *are* accessible. **Fix**: run it, or drop the framing.

## Specific concerns
The narrative arc is present in the plan but the prose leads with measurement (TEHR) instead of phenomenon. A reviewer spends ~30s on §1; they need "frontier models call tools that don't exist; this is measurable, recoverable, tier-dependent" *before* they meet TEHR. The "Empirical analysis of agent failures" paragraph (02_related_work.tex 17–29) is closer to the right opening than anything in §2.3.

Limitations are honest in the plan (R22, pre-reg item 10, §6.3 cuts) but absent from the drafted sections. The paper does not yet acknowledge small N, strict-subset collapse risk, local-tier-unpooled, or the ~80% API-Bank overlap (`prior_art.md` §1). These belong in §1 and §7, not just v3.1. Separately, Czapla (lines 21–24) is the only non-academic anchor and is doing too much; promote `bugstudy2026` (lines 25–28) to load-bearing and demote Czapla to a footnote.

## What I'd want changed before camera-ready
- §1 lede: phenomenon first, metric second, intervention third, scaling claim fourth — in that order, in three sentences.
- Re-tile the four contributions so each is independently defensible and the §6 probe is promoted.
- Add a pre-registered minimum strict-subset n; report it per-cell.
- Either run RVR-on-Fission-GRPO-Qwen3-8B in appendix, or explicitly scope out with a one-paragraph justification.
- Move limitations (N=50, strict-subset collapse risk, API-Bank overlap, local tier unpooled) into §1 and §7, not only the plan.
- Drop the "constrained-decoding analog" framing or back it with a Qwen3-8B logit-level baseline.

## Strongest contribution (even reviewers find one)
The C1-vs-C0.5 paired contrast on the *strict hallucination-tagged subset* — this is a genuinely clean causal isolation of the registry-list content from the act of retrying, and prior work does not have it.

## Most damaging weakness
The four claimed contributions are not four; an ICML reviewer will read one method and one result, conclude novelty is thin, and the §6 causal probe — the actual best part — is currently buried as a "preview" in §3.

## Verdict justification
The design is unusually careful for a 36h submission (pre-registration, paired McNemar, TOST, gap-closure ratio). But the paper trips on three things: a contribution list that double-counts, an N the authors themselves flag as borderline, and differentiation from concurrent work that is asserted rather than demonstrated. With the §6 probe promoted, strict-subset n's reported transparently, and one head-to-head against Fission-GRPO or L-ICL, this becomes a clear accept. As-is, it is the right venue but not the session's standout.
