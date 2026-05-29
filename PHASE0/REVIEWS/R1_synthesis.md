# R1 Multi-Persona Review — Aggregate Synthesis
*Six reviewers, six angles, one consolidated fix-list. Source files in `PHASE0/REVIEWS/R1_*.md`.*

## Aggregate verdicts

| Reviewer | Verdict |
|---|---|
| ICML Area Chair | BORDERLINE — workshop-acceptable; not oral-pick |
| NeurIPS Method Reviewer | Weak Reject (5/10) — borderline; conditional on adding ≥3 missing ablations |
| Statistics Reviewer | Major Revision — multiple structural underpowering issues |
| Adversarial / Salty Reviewer | WEAK REJECT — TEHR-renamed attack, gap-closure ratio fragility, probe underpower |
| SCALE Workshop Reviewer | WEAK ACCEPT — conditional on TRACK SWITCH (Main → Benchmarking & Dataset) |
| Reproducibility Reviewer | Major Revision — 3 P0 gaps (MLX SHA, decoding params, no manifest) |

**Aggregate**: 0 ACCEPT, 1 conditional WEAK ACCEPT, 1 BORDERLINE, 4 effective REJECT / MAJOR REVISION. **The plan as written would not pass review at workshop bar even, without revisions.**

---

## BLOCKERS (must fix before Phase 1 commits to code)

| # | Issue | Source(s) | Fix |
|---|---|---|---|
| **B1** | **Multimodal mismatch.** Workshop title says "Multimodal AI Agents"; we're text-only (BFCL + τ-bench retail). | SCALE Workshop | **DECISION**: switch from Main Track → **Benchmarking & Dataset Track** (same 7-page limit, structurally lighter on multimodal expectation, fits TEHR + probe contributions natively). Needs Akash's explicit OK. |
| **B2** | **TOST 1pp margin requires ~1100 paired observations**; we have ~25. Test is a type-II machine. | Statistics, NeurIPS | Widen margin to **5pp** OR reframe as "estimated paired difference with 95% CI" + pre-registered 5pp threshold for "no clinically meaningful regression." |
| **B3** | **Contribution #1 ("per-call denominator")** is a metric-design choice, not a co-equal contribution; structurally weak. | ICML AC, Adversarial | Combine contribution #1 + #4 (mechanism probe) into a single **"benchmark + metric + mechanism"** contribution. Demote denominator-choice to a methodological note inside the metric. |
| **B4** | **Gap-closure ratio metric is unstable + circular**. Ratio of two correlated noisy differences; denominator can be near-zero/negative; assumes hallucinations *cause* the small-vs-frontier gap (never decomposed). | Statistics, NeurIPS, Adversarial | (a) Add **BCa-bootstrap CI on the ratio** via paired cluster-bootstrap by task (10K resamples). (b) Pre-register **denominator-near-zero policy**: if ΔPass(frontier−small) < 5pp, report "gap closure undefined; report ΔPass(small) only." (c) Add explicit decomposition section showing what fraction of the small-frontier gap is attributable to TEHR vs. other failure modes. |
| **B5** | **§6 probe is underpowered + missing matched controls**. 30 tasks × 3 distractors × per-tier = 30 obs/cell. "Causal not correlational" claim untenable. | NeurIPS, Adversarial | (a) **Drop "causal" framing** → "controlled comparison." (b) **Match the random distractor on length, schema arity, and position** so ΔTEHR isn't conflated with registry-size+1. (c) **Scale to N=100 tasks/cell** (~$30-50 added against credits). |
| **B6** | **C0.7 baseline missing.** Current C0/C0.5/C1 triad cannot answer "is RVR better than what production frameworks already deploy (LangChain default error feedback)?" | NeurIPS | **Add C0.7**: framework-style structured error feedback (`{"error": "tool not found", "details": "..."}`), no registry list. Now 4 conditions; +33% compute (well within credits). |
| **B7** | **Pre-registered power calculation lacks explicit math.** v3.1 §4.4 item 10 claims "ΔPass ≥ 20pp at 80% power" without showing the assumed prevalence + base rate. Pre-registration is incomplete. | Statistics | Compute power explicitly: at TEHR=10%, N=100 BFCL, hallucinated-event rate per cell ≈ 10. McNemar power at b+c=10 for ΔPass=20pp ≈ ?? Show the formula in §4.4. |
| **B8** | **Holm-Bonferroni only covers 4 per-tier tests; total test family is 30+** (4 tiers × 2 benchmarks × 3-4 conditions × multiple metrics). Family-wise error not actually controlled. | Statistics, NeurIPS | Either (a) restrict the *primary* family to just the 4 per-tier ΔPass tests (clearly named in §4.4) + treat all others as "exploratory, no FWER control"; or (b) widen Holm to all primary metrics. Pick (a) for cleaner story. |

## MAJORS (fix during Phase 1; flag if punted)

| # | Issue | Source(s) | Fix |
|---|---|---|---|
| M1 | McNemar at b+c < 10 unstable | Statistics | Pool discordance pairs across tiers BEFORE the test (per Statistics RQ1). |
| M2 | Bootstrap percentile CI biased near 0/1 | Statistics | Replace with **BCa** in `tehr_bootstrap_ci`. |
| M3 | Probe ANOVA assumes normality on bounded [0,1] TEHR | Statistics | Replace with **Friedman + Nemenyi post-hoc**. |
| M4 | Registry length × ordering ablation missing | NeurIPS | Add small ablation: tool-list size {3, 10, 25} × ordering {alphabetical, random, relevance-ranked}. ~150 runs against credits. |
| M5 | Cluster-bootstrap by task needed for non-i.i.d. per-call obs | Statistics | Update `stats/tehr.py` and `stats/paired_mcnemar.py` to cluster-by-task. |
| M6 | MLX HF revision SHA not pinned | Reproducibility | Pin via `huggingface_hub.HfApi().model_info(repo_id).sha` at run-start; log to `repro_manifest.json`. Add a mirror plan (locally vendored model file in case `mlx-community` org disappears). |
| M7 | API decoding params (temperature/top_p) undocumented | Reproducibility | Lock **temperature=0.0, top_p=1.0** for all API adapters. Document in §4 + HARNESS_SPEC. |
| M8 | No central `repro_manifest.json` | Reproducibility | New file `harness/repro_manifest.json` with: dataset SHAs, model dated aliases, SDK exact versions (`==`), Python version, OS, MLX revision, all seeds. Generated at run-start. |
| M9 | Sonnet 4.6 rolling-alias mitigation needs §4 wording | Reproducibility | Note in §4: "Anthropic Sonnet 4.6 is rolling; we capture the resolved snapshot via `/v1/models` at run-start and log to repro_manifest." |
| M10 | MLX/Metal non-determinism unacknowledged | Reproducibility | One-sentence acknowledgment in §4 limitations: "MLX inference on Apple Silicon is not bitwise-deterministic across runs; per-task results are stable to within ±1 token." |
| M11 | Czapla blog overweighted as motivation | Adversarial | Reduce Czapla's weight in §1 hook; lead with API-Bank's 61.4% rate. Czapla becomes a "we observe this in production too" footnote. |
| M12 | k=1 retry cap not ablated | Adversarial, NeurIPS implicit | Add small ablation (k ∈ {0, 1, 2, 3}) on a 30-task subset. ~$10-20 against credits. |
| M13 | "Scalable" claim needs scaling-curve evidence or downscoping | SCALE | Either run a 5-point scaling curve (cheap models in 4 sizes) or downscope language to "tier comparison." Recommend downscope. |
| M14 | "Efficient" claim needs FLOPs/latency/energy or downscoping | SCALE | Add latency-per-task and tokens-per-success columns to §5 main table. Energy/FLOPs out of scope for 36h. |
| M15 | Local tier is currently a "vanity panel" | Adversarial, SCALE | Either (a) fold into headline (with explicit cross-platform caveat) or (b) reframe as the SCALE-relevant feasibility anchor in §5.5. Pick (b) — feasibility is on-thesis for SCALE. |
| M16 | McNemar mid-p formula needs clamp-at-1 + b+c=0 guards | Statistics | Update `paired_mcnemar.py` accordingly. |

## MINORS

- m1. Add 1-paragraph "TEHR is X renamed" pre-emptive defense to §1 + §7.
- m2. Citation key cleanup in `refs.bib` (verify all 5 TODO arXiv IDs).
- m3. Czapla date already corrected (2026-01-20); confirmed in v3.1 Δ2.

## Convergent themes across reviewers

| Theme | Reviewer count flagging |
|---|---|
| Probe underpowered + missing matched controls | 3 (NeurIPS, Adversarial, Statistics implicit) |
| TOST 1pp margin impossible at our N | 2 (Statistics, NeurIPS) |
| Gap-closure ratio fragility | 3 (Statistics, NeurIPS, Adversarial) |
| Contribution #1 weak | 2 (ICML AC, Adversarial) |
| Missing C0.7 production-default baseline | 1 strong (NeurIPS) |
| Family-wise error coverage | 2 (Statistics, NeurIPS) |
| Reproducibility manifest gaps | 1 strong (Reproducibility) |
| Workshop-fit / multimodal mismatch | 1 BLOCKER strength (SCALE) |

## Big decisions for Akash (need explicit OK before I apply)

1. **TRACK SWITCH: Main → Benchmarking & Dataset.** Cleanest single fix to the multimodal mismatch + better thematic fit for TEHR + probe contributions. **My recommendation: YES, switch.** Page limit unchanged (7p). Reframes the paper from "method paper with benchmark" to "benchmark + method." Loses some methodological prestige; gains acceptance probability + thematic fit.

2. **N BUMP: 50 → 100 BFCL, 25 → 50 τ-bench.** Doubles main-run compute (~$60 → ~$120 against credits, comfortable). Necessary for B2 + M1 to actually work. **My recommendation: YES, bump.**

3. **C0.7 BASELINE ADDITION.** 4 conditions instead of 3, +33% compute. Necessary for B6 (NeurIPS attack). **My recommendation: YES, add.**

4. **§6 PROBE REDESIGN: drop "causal", add matched controls, scale to N=100.** Rebuilds the mechanism claim on defensible footing. **My recommendation: YES, redesign.**

5. **CONTRIBUTION #1 REFRAME: combine with §6 into "benchmark + metric + mechanism" single contribution.** Strengthens the headline by collapsing two weak claims into one strong claim. **My recommendation: YES, combine.**

## Fix plan (after decisions)

### Apply NOW (no direction change, all reviewers agree, no user-input needed)
- M2: BCa bootstrap in `tehr_bootstrap_ci`
- M3: Friedman + Nemenyi for probe ANOVA
- M5: Cluster-bootstrap by task in stats modules
- M6: MLX HF revision SHA pinning + mirror plan
- M7: Lock temperature=0.0, top_p=1.0
- M8: `repro_manifest.json` spec + scaffold
- M9: Sonnet 4.6 rolling-alias §4 wording
- M10: MLX/Metal non-determinism §4 acknowledgment
- M11: Czapla weight reduction in §1
- M16: McNemar mid-p clamp + zero-guard
- B7: Explicit power calculation in §4.4
- B8: Restrict primary family in §4.4

### Pending Akash's OK (5 big decisions above)
- B1: Track switch
- B2: N bump
- B3 / contribution combine
- B5: Probe redesign
- B6: C0.7 baseline

### Defer to Phase 5 polish
- m1: Pre-emptive defense paragraphs
- m2: arXiv ID verification

## Time budget

If all 5 big decisions land "YES" tonight, harness work to apply BLOCKER+MAJOR fixes ≈ 7h, fits inside Phase 1+2 envelope (T+13:00 → T+18:30). N bump increases main-run wall-clock by ~1h (still fits T+18:30 → T+21:30). C0.7 condition fits in same dispatched batch. Probe redesign at N=100 fits the +50 min probe slot.
