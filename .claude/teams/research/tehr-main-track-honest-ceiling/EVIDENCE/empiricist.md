# empiricist.md — decision-analytic: defensibility delta per framing & per running experiment (no new code; M5 busy)

Grounded in LIVE state (results/_queue/STATUS.tsv, queue.log, PROGRESS.md as of this session), not speculation.

## Ground-truth from the live run (load-bearing — changes the answer)
1. **The "format-not-content" headline was ALREADY A/B-TESTED on the review panel and LOST.** PROGRESS.md "Key lesson": the aggressive format-not-content reframe (equivalence from 3 zero-event arms) scored **~14% vs 18% baseline** on a 6-persona panel; it was walked back to bounded honest claims. → H2-as-headline is not merely honesty-risky (linguist.md); it is EMPIRICALLY KNOWN to score WORSE than the bounded version. This is the strongest possible evidence against H2 as the lead. The decoy "Variant A confirmed (0/410)" is a deployment wrinkle, not a powered mechanism result — the *powered* decoy on the hot 14B cell (events under the ablation) is still chained/unrun.
2. **Decoy state**: 8B C0.8 = 0/410 (n=25/cell, all 4 arms zero); C0.7 re-running now. The "events under the ablation" gate (powered 14B decoy) has NOT produced events. So "content decorative, proven" does NOT exist yet and may not (if the hot cell also under-fires).
3. **Frontier breadth already strong**: 5 OpenAI tiers done (0/2117), 5 Anthropic versions (0/2578). gpt-5 pending. The COMMERCIAL side of the gap is robustly multi-vendor TODAY. This is the asset.
4. **2nd-family + 2nd-benchmark**: running (Llama/Mistral/Qwen2.5; BFCL single-turn buildable today, tau-bench/Seal-Tools gated on data). Team's own note: "A2-gate (2nd non-zero benchmark) sets the ~borderline main-track ceiling."
5. **Team's own honest ceiling**: "even with all gates cleared, personas put it at borderline-accept, not safe. Main-track is a multi-day program."

## Defensibility scoring (qualitative, 0-5, "how well does an honest version survive a hostile main-track AC TODAY")

| Framing | Defensibility TODAY | After decoy lands w/ events | After 2nd benchmark non-zero | After 2nd family non-monotonic | Notes |
|---|---|---|---|---|---|
| H1 gap-led (phenomenon, not causal) | **3.5** | 3.5 (decoy doesn't touch it) | **4.0** | 4.0 | Most-backed; least contingent. Precision×family confound is the cap. |
| H2 format-not-content lead | **1.5** | 3.0 (only if events appear AND content still inert) | 1.5 | 1.5 | EMPIRICALLY scored 14% as a lead. High variance. Disowned in §6 today. |
| H3 metric-led | 2.5 | 2.5 | 3.0 | 3.0 | "Re-slicing prior taxonomies" attack. Honest but weak. |
| **H4 synthesis (gap headline + TFR instrument + RVR fix + bounded mechanism)** | **4.0** | 4.0 | **4.5** | **4.5** | Dominates: leads with the most-backed claim, gives metric/fix/mechanism honest subordinate roles, robust to decoy under-firing because the ablation is SUPPORTING not headline. |

## Single highest-leverage NEXT result (the user's Q4)
Rank by ceiling-lift per unit effort/risk, using the team's own gating notes:

1. **A 2nd benchmark with a NON-ZERO commercial-or-open base rate that reproduces the gap (tau-bench or BFCL-single-turn irrelevance/live).** HIGHEST lift. Reason: the tool-eval-specialist persona's DEFAULT reject is "single benchmark = workshop"; a 2nd benchmark is the named cure. It also tests external validity of BOTH the gap AND RVR. The team flags this as the ceiling-setter. Buildable: BFCL single-turn data is ON DISK today (HARNESS_ADAPTER_PLAN), tau-bench needs wiring. Even a SMALL 2nd-benchmark gap reproduction moves H4 from 4.0→4.5 and is the difference between "workshop+" and "main-track-plausible."
   - WHY it beats the decoy: the decoy only rescues H2 (a SUPPORTING claim in H4). The 2nd benchmark rescues the HEADLINE (the gap's generality) AND the tool-eval-specialist's structural objection. Strictly higher leverage.

2. **A 2nd open family (Llama OR Mistral) showing a non-zero, ideally non-monotone, rate.** SECOND. Converts "Qwen-specific artifact" → "open-weight lineage pattern" and is the Wei-bar partial-discharge (multi-family). Cheaper than tau-bench (parsing fix, no new env). Note: Spectral-Guardrails (2602.08082) already shows Llama-3.1-8B + Mistral-7B hallucinate tools at 20-22% on a General domain — so a non-zero 2nd-family rate is HIGHLY likely to reproduce; the risk is whether the NON-MONOTONIC SHAPE holds, which is a bonus not a requirement (the GAP only needs non-zero open vs zero commercial).

3. **fp16 quant control at 1-2 Qwen3 ladder points.** THIRD. Directly answers the quant-confound skeptic (persona 15) on the curve. But: it only defends the SUPPORTING curve, not the headline gap. Medium lift. The small members fit on M5.

4. **Powered decoy with events on 14B.** FOURTH for the HONEST framing. It only upgrades a supporting mechanism claim (and, per ground-truth #1, leading on it scored 14%). Worth running for §6 completeness, NOT a ceiling-setter for H4.

5. **Exploitability/collision probe** (does a fabricated name resolve against a plausible superset registry). Converts security from MOTIVATION to RESULT. High ceiling but high effort and scope-creep risk; the skeptic (prior session Attack 3) warns against leading security without it. NOT the single best next result; a stretch.

## Robustness check: is H4 robust to the decoy cell under-firing?
YES. H4 carries format-not-content as a BOUNDED supporting note ("no detectable content effect, CI [-1.5,+1.4]pp"). If the powered 14B decoy also under-fires, H4 is UNCHANGED — the bound just stays a bound. If it fires and content is still inert, H4 gains a crisp mechanism sentence. Either way the HEADLINE (the gap) is untouched. This asymmetry is exactly why H4 > H2: H4's headline does not depend on a high-variance pending result.

## Confidence
HIGH. The decisive input is empirical: the team already ran the format-not-content-lead A/B on a persona panel and it scored WORSE (14% vs 18%). Combined with the linguist's honesty gate (§6 disowns it), H2-as-headline is doubly eliminated. H4 (gap-led synthesis) is the robust dominant choice; the 2nd-benchmark gap reproduction is the single highest-leverage ceiling-lift.
