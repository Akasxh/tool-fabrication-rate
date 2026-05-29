# Adversarial Pre-Review — MAIN-TRACK ICML bar

Target: ICML 2026 main track (NOT workshop). Four harshest personas. Brutal by design; this is to find kill-shots, not to reassure. Scores on the ICML 1–10 scale (1 reject, 6 weak accept, 8 accept).

---

## Reviewer 1 — Hostile Statistician

**Score: 3 (reject).** The paper is statistically literate — Clopper–Pearson at boundaries, Fisher exact instead of chi-square, Holm across the named family, exact-permutation Friedman, BCa cluster bootstrap. That is the *minimum* bar, and it is met. The problem is that the conclusions outrun the evidence, and the headline test is built on n=14 events.

LINE-LEVEL ISSUES:

- `05_results.tex:248` | The entire RVR effect is **14 pooled events across 4 strata**, with per-tier Fisher p = {0.24, 0.12, 0.058, 0.032}; **three of four tiers are individually non-significant** and you concede they are underpowered. Pooling 0/N cells into a single 2×2 inflates significance by treating a structural zero (RVR cannot execute a non-registry name by construction) as a sampled zero. The pooled p=7.1e-5 is therefore not a fair representation of evidence strength. | FIX: Report the test as descriptive; add a stratified Cochran–Mantel–Haenszel or exact conditional test and **test stratum heterogeneity (Breslow–Day / Cochran Q) before pooling** — currently no heterogeneity test is run before pooling four tiers with different TEHR (0.95–1.87%).

- `04_setup.tex:24-32` & `05_results.tex:245` | You state C0/C1 denominators differ per tier so "trials are not paired at the call level," then pool them as a single contingency table anyway. A 2×2 Fisher on unpaired pooled counts with **a near-deterministic treatment arm** (C1 zeros are guaranteed by the membership check, not observed) is the wrong frame. | FIX: State explicitly that C1=0 is partly structural and separate the "prevents the call from executing" (definitional) from "model stops proposing the name" (empirical) — currently conflated.

- `05_results.tex:230-232` | 8B denominators don't reconcile: probe pooled C0 = 4/269 (Table 3), RVR-validation C0 = 4/269, but the ablation ladder reports C0 = **4/268** and C1 = 0/258 while RVR-validation reports C1 = **0/258**… and miss_func reports 5/258=1.94% separately. The "1.49%" appears for both probe-8B (4/269=1.487%) and miss_func-base. A stats reviewer reconciling sections will flag the 268-vs-269 drift as sloppy and ask which N is canonical. | FIX: One canonical denominator table; reconcile 268/269.

- `05_results.tex:211-218` | TOST p_TOST = 0.91 / 0.63 with 1−β < 0.30 at N=60. You correctly decline to call it — but the abstract and intro still imply tier-conditional deployment is *justified*, when the Anthropic pass-rate cost is **undetermined**, not absent. A −11.7pp strict-pass drop with a CI that you cannot bound below the 5pp margin is a *signal of harm you cannot exclude*, not a neutral result. | FIX: Stop framing the Anthropic side as "RVR holds at zero"; lead with "we cannot rule out a pass-rate regression."

- `06_mechanism.tex:4` | Friedman χ²(3)=3.0, p=0.46, ≤5 events/cell — you correctly decline a mechanism. But then the abstract/intro narrate the "peak distractor type shifts (near→matched→synonym)" as a *finding*. With p=0.46 it is noise. | FIX: Demote the distractor-shift to "anecdotal pattern, not significant" everywhere, including the abstract.

- (a) Statistical correctness: **FIX-FIRST**
- (b) Most likely rubric ding: **headline RVR claim rests on 14 events with no pre-pooling heterogeneity test and a partly-definitional treatment zero.**
- (c) One-sentence fix: Report RVR as a descriptive 14→0 observation with CMH + heterogeneity test, and drop all significance language from the distractor-shift and the Anthropic non-inferiority claims.

**Single change that most raises score:** Multiply the event count. 14 total fabrications cannot carry a main-track headline; run the probe at N≥100/cell (your own pre-registered N, cut to 15) on the non-zero Qwen3 tiers so the per-tier Fisher tests stand alone.

---

## Reviewer 2 — Adversarial Reviewer (worst-case)

**Score: 2–3 (reject).** Three objections I can get other reviewers to co-sign:

1. **Circular evaluation / definitional intervention (>70% co-sign).** `03_method.tex:31-37`: RVR is an `if proposed.name not in registry` check. It fires on *exactly* the events TEHR defines, and on a hit the call cannot execute. The "prevents 14/14" headline (`05_results.tex:186`) is therefore partly a tautology: a membership filter trivially blocks membership violations. The empirical question — does the *model stop proposing* fabricated names after the re-prompt — is buried, and the only clean test of it (C0.7 vs C1) sits at N=253 on one model. *Unrebuttable if:* you show RVR can't be replaced by a silent executor-side allow-list (which you already recommend in limitations — undercutting your own contribution).

2. **Confounded headline axis (>60% co-sign).** `07_limitations.tex:5` admits it: "parameter count, 4-bit MLX quantization, training recipe, and provider guardrails co-vary." The "Anthropic vs Qwen3" gap — your stated headline — confounds vendor, quantization, scale, and post-training simultaneously. The non-monotone curve is one family, one quantization, six points, p=0.46 on the shape. *Unrebuttable if:* a single full-precision Qwen3 run, or any non-Anthropic frontier API (GPT/Gemini) at full precision, breaks the vendor/quantization confound. You dropped OpenAI for budget.

3. **Pass-rate failure (>55% co-sign).** `05_results.tex:211`: RVR drops Sonnet strict-pass 60→53 (−11.7pp). The intervention helps a metric (TEHR) it defines while plausibly hurting task success — the textbook "helps the metric, hurts the downstream signal" reject. You cannot exclude it at N=60.

- (a) Probability I convince an AC to reject: **75**
- (b) Killing objection: **the intervention is a membership filter evaluated on membership violations — circular — and where it isn't (Anthropic), it appears to hurt pass-rate.**

**Single change that most raises score:** Add an experiment proving RVR changes *model behavior* (subsequent proposals), not just *gates execution* — e.g., measure post-reprompt re-fabrication rate and downstream task-success delta on the Qwen3 tiers, not just on Anthropic at N=60.

---

## Reviewer 3 — MARG Experiments Expert

**Score: 4 (borderline reject).** Solid diagnostic engineering; the experiment matrix is too thin to support the claims.

ISSUE | OBSERVED | HYPOTHETICAL | GAP

- Headline scale curve | 6 Qwen3 points, N=75–269/size, 14 total events, p=0.46 on shape | One family at ≥3 seeds × ≥100/cell, plus one second family (Llama or Mistral) run to full sweep to test whether non-monotonicity replicates | The curve is the headline yet rests on single-run greedy decode; **no seed variance on the open models** despite the claim that the *shape* is the result. A non-monotone curve from 14 events at one seed is indistinguishable from sampling noise.

- Vendor gap | Anthropic 0/2599 vs Qwen3 4-bit | Same probe on a full-precision frontier *open* model AND a non-Anthropic frontier API, so "vendor" is isolated from "quantization" and "scale" | The single most important counterfactual is unrun: is the zero an Anthropic property or a frontier-capability property? Without GPT/Gemini, the headline comparison is Anthropic-vs-small-quantized-open, which nobody believes is a fair fight.

- RVR ablation | C0.5/C0.7/C1 at N≈253 on **Qwen3-8B only** | The C0.7-already-zero claim (the paper's most interesting mechanistic result) replicated on ≥2 tiers with ≥100 events each | The "registry list is decorative" claim — genuinely novel and the spotlight framing — is supported by **zero events on one model**. 0/253 vs 0/258 cannot distinguish "list is decorative" from "both arms under-powered to see the residual." This is the claim most worth strengthening and it is the weakest-powered.

- Contamination | "indistinguishable from BFCL v4 contamination," no control run | A paraphrase or held-out-registry control on the Anthropic null | Admitted gap; the Anthropic null could be memorization.

- Reproducibility from artifact | 144 tests, anonymous repo, manifest | A $1000-compute reviewer reproduces the headline | Plausible for the Qwen3 sweep (M5, zero marginal); the Anthropic side needs $73 of API and dated snapshots that may be deprecated by review time — partial.

- The single experiment most likely to flip a borderline vote that was NOT run: **one full-precision (bf16) Qwen3 sweep** — it simultaneously (a) breaks the quantization confound in the vendor gap and (b) tests whether the non-monotonic shape is real or a 4-bit artifact. This is the cheapest high-leverage run and it is missing.
- Probability existing experiments support the headline: **35**

---

## Reviewer 4 — Brutally Honest Area Chair (final verdict)

The paper is unusually candid — it pre-registers, logs deviations, and refuses to over-claim mechanism (Friedman p=0.46 → declines to assign). That honesty is its best asset and, ironically, its problem: read end-to-end, the authors have written a careful **negative/descriptive result** (Anthropic doesn't do this; small quantized Qwen3 sometimes does; one re-prompt gates it) and dressed it as a main-track contribution with a method (RVR) that the same paper admits is replaceable by executor-side allow-listing (`07_limitations.tex:5`).

The one thing that shifts my vote accept→reject: **the total evidential mass.** The RVR headline is 14 events; the scale curve is 14 events at one seed with a non-significant shape; the spotlight "registry is decorative" claim is 0-vs-0 on a single model. For a *workshop* (SCALE), this is a clean, honest, well-instrumented contribution — accept. For **main-track ICML**, three independent failure modes each individually justify rejection: (1) the intervention is partly definitional and admittedly substitutable, (2) the headline vendor gap confounds four variables and the authors say so, (3) every inferential claim beyond the Anthropic upper bound is underpowered by the authors' own tests.

Numbers do reconcile mostly, but the 268/269 8B denominator drift (`05_results.tex:202` vs `:231`) and the abstract's "1.49%" reused for two different cells need a cleanup pass.

Nothing here is dishonest — it is simply below the main-track evidence bar. The fix is not more polish; it is more events and one confound-breaking run.

- (a) Acceptance probability (main track): **18**
- (b) Verdict: **WEAK_REJECT** (clear ACCEPT at workshop bar)
- (c) Single most-important fix: **Raise event count (N≥100/cell on non-zero tiers) and add one full-precision or non-Anthropic-frontier run to break the vendor/quantization confound; without these the headline is descriptive, not a main-track finding.**

---

## Synthesis — 5 highest-leverage changes for MAIN-TRACK acceptance

Ordered by vote-shift per unit effort.

1. **Break the vendor/quantization confound with ONE run.** Add a full-precision (bf16) Qwen3 sweep on the M5/cluster, or one non-Anthropic frontier API (GPT or Gemini) at the probe. This is the single most-cited objection across all four reviewers (R2 confound, R3 counterfactual, R4 reject-reason #2). It tells you whether the Anthropic zero is a *frontier* property or an *Anthropic* property, and whether the non-monotone curve survives de-quantization. Cheapest high-leverage fix.

2. **Multiply the event count on the non-zero Qwen3 tiers.** Restore the pre-registered N≥100/cell (you cut 100→15 for breadth) on 1.7B/4B/8B/14B so each per-tier Fisher test stands without pooling, and so the C0.7-vs-C1 "decorative registry" claim rests on >0 events, not 0/253. Kills R1's pooling objection and R3's power gap. The Qwen3 sweep is zero-marginal-cost — there is no budget excuse.

3. **Prove RVR changes behavior, not just execution.** Measure (a) post-reprompt re-fabrication rate and (b) downstream task-success delta on the Qwen3 tiers (not just Anthropic N=60). This directly answers R2's circularity kill-shot — show the model *stops proposing* fabricated names rather than the filter merely *blocking* them — and converts a partly-tautological "14/14 prevented" into an empirical claim. Also extend the Anthropic non-inferiority N past 60 so the −11.7pp strict-pass drop is bounded, neutralizing the pass-rate-harm objection (R1, R2, R4).

4. **Demote every underpowered narrative to descriptive, in the abstract too.** The distractor-type shift (p=0.46) and the "32B collapse" (CI overlaps 14B, you say so in body) are narrated as findings in the abstract/intro. Align the abstract's confidence with the body's hedges; add a heterogeneity test (Breslow–Day/Cochran Q) before pooling the four RVR strata. Cheap, removes R1's strongest rubric ding and a chunk of R4's over-claim concern.

5. **Reconcile the numbers and defuse self-substitution.** Fix the 268/269 8B denominator drift and the doubly-used "1.49%"; make one canonical results table. Separately, reframe limitations so RVR is *not* described as replaceable by executor-side allow-listing — that line (`07_limitations.tex:5`) hands R2/R4 a free "why is this a contribution" reject. Either argue why the message-level signal beats a silent allow-list (it changes the model's context, an allow-list does not) or move that comparison into a measured result.

**Bottom line:** at the current evidence mass this is a strong *workshop* paper and a *weak-reject* main-track paper. Changes 1 and 2 are the gate; without more events and one confound-breaking run, the headline is descriptive and four reviewers reject. With them, the candor and instrumentation become an asset and this moves to borderline-accept.
