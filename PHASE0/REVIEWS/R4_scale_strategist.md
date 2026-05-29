# SCALE Acceptance Strategist — Game Plan

## Predicted acceptance probability under current framing
**~32%.** A pure null-result calibration paper with N=15 probe tasks, no figure, no MetaTool replication, and no multimodal hook is borderline at best. Two cheap reviewer objections kill it: "where is the head-to-head replication of MetaTool's 25%?" and "this is text-only on a multimodal workshop." Both are 60-second rejects.

## Predicted acceptance probability under recommended framing
**~62%.** Reframed as a Benchmarking & Dataset Track submission — "we built a per-call hallucination measurement harness, ran 6 conditions on 2 frontier models + 1 weaker open-source model, and found TEHR is model-tier-dependent, not universal" — the paper becomes a clean B&D contribution with a real positive signal *somewhere* in the data.

## Single highest-leverage addition (1-3 hours)
**Run Qwen3-8B-Instruct on the same 4-arm distractor probe (N=15 tasks per arm, target removed, 4 distractor types).** The MLX harness is already built (`PHASE0/mlx_probe.py`, `mlx_feasibility.md`); cost is zero, wall-clock is ~90 minutes on Apple Silicon. Three outcomes, all good:

- **TEHR > 0 on Qwen3-8B** → headline becomes "TEHR is model-dependent: 0% on Sonnet/Haiku, X% on Qwen3-8B. The folklore failure mode survives in open-source small tiers — exactly the regime SCALE cares about (efficient agents on consumer hardware)." This is a *positive* result and converts a null-result paper into a tier-comparison paper.
- **TEHR = 0 on Qwen3-8B too** → strengthens the calibration claim across model families and gives a third data point for the "tool-existence hallucination is rarer than reported" headline. Still useful, marginally.
- **Qwen3-8B refuses or parse-fails at high rates** → reportable as a *system-failure characterization* finding, also workshop-fit.

This single experiment dominates every other addition by leverage. MetaTool replication on Sonnet 4.6 is second-best (~1 hr if you have a working MetaTool fork) but you don't have one staged; building from scratch eats the 3-hour budget.

**Ranking by acceptance-probability boost:**
1. Qwen3-8B distractor probe (+25pp) — uses existing harness, zero cost, three winning outcomes
2. MetaTool protocol replication on Sonnet 4.6 (+12pp) — strong but requires building a MetaTool adapter
3. Scaling-curve sketch (TEHR upper-CI vs N) (+5pp) — easy plot, mostly cosmetic

## Top-3 cosmetic improvements

1. **One headline figure on page 1 or 2.** A Wilson-CI-vs-N panel showing TEHR upper bound shrinking from ~25% (MetaTool 2023 baseline, cited from prior work) → ~5% (our N=1571 upper CI bound) → labeled tiers and conditions on the x-axis. Reviewers form 70% of their opinion from the abstract + first figure. Currently zero figures = readers leave without a memorable image.
2. **Inline "Reproducibility statement" subsection** in §4 (matches ICML 2026 reproducibility checklist verbatim). Free trust signal; reviewers tick the box and move on.
3. **Anonymized harness URL** in the abstract footnote (`anonymous.4open.science/r/...`). The abstract currently says "open-source experimental harness ($\sim 5{,}300$ LOC, $144$ unit tests)" but doesn't link to it. Reviewers who can click the harness in 5 seconds form a positive reproducibility prior before reading §3.

## Top-3 framing rewrites

1. **Switch the track to Benchmarking & Dataset.** Same 7-page limit. Your paper's load-bearing contribution is a *metric* (TEHR) + a *measurement instrument* (the 4-arm distractor probe) + a *harness* — that is canonically B&D. Main Track competes against full method papers with N≥100 and head-to-heads. R1_scale_workshop already flagged this; act on it.
2. **Recast the title.** Current title leads with the negative result, which primes a "so what?" reading. Try: *"Per-Call Auditing of Tool-Existence Hallucination: A Harness, Six Regime Tests, and a Tier-Dependent Result."* Foregrounds the infrastructure contribution (B&D-friendly) and hedges the headline so a Qwen-positive result slots in cleanly.
3. **Reposition RVR from "intervention we couldn't validate" to "released measurement instrument with a pre-registered evaluation protocol."** The current §3.2 + §5.4 reads as a half-finished method paper. Move RVR's full protocol to the appendix, keep only the 1-paragraph design summary in §3, and frame the body as: TEHR (metric) + distractor probe (instrument) + RVR (intervention released for replication on regimes that exhibit non-zero TEHR). This is the "tools/infrastructure" framing — workshops accept these without empirical validation when the tools are genuinely useful, and your harness *is* useful (regardless of whether RVR helps).

## What to put in supplementary material

- `repro_manifest.json` (already specified in §4.5) — model-alias snapshot, SDK versions, all seeds, BFCL commit SHA
- All 1,571 tool-call JSONL traces, redacted (zip if OpenReview accepts; else anonymous repo)
- Full harness source ($\sim$5,300 LOC) + the 144 unit tests + a one-line reproduction recipe (`make reproduce`)
- Plotting scripts that regenerate every table and (the new) figure from the raw JSONL
- The 30 trace excerpts cited in §5.3 as a standalone PDF appendix (decomposition behavior is your most concrete positive finding — make it inspectable)
- BCa cluster-bootstrap implementation + numerical fixtures showing it matches `scipy.stats` on a known dataset
- A `LIMITATIONS.md` mirroring §7 verbatim — reviewers who don't read your paper *will* skim this
- An anonymized README pointing reviewers to the 3 most diagnostic JSONL files (one per regime test, one per probe arm)

## Reviewer assignment hedging

- **If we get an "accept-leaning" reviewer** (loves negative results, infrastructure, pre-registration): paper sells itself as *"a clean null-result calibration with a reusable per-call diagnostic and a pre-registered protocol that can be re-run on any future model."* Lean into the rigor — Holm-Bonferroni, BCa cluster-bootstrap, asymmetric falsifiability. This reviewer reads §3-§4 and gives you a 7.
- **If we get a "neutral" reviewer** (skims, looks for one memorable signal): emphasize *the single Qwen3-8B data point* (assuming you run the experiment tonight) — it's the only positive number in the paper and the only thing they'll remember. Put it in the abstract, the headline figure, and the conclusion. This reviewer gives you a 6 if they remember the Qwen number, a 4 if they don't.
- **If we get a "reject-leaning" reviewer** (skeptical, looks for fatal flaws): pre-empt by (a) acknowledging "TEHR=0 means RVR is unvalidated" *in the abstract*, not just §5.4 — owning the limit defuses the rejection vector; (b) explicitly addressing the multimodal mismatch in §1 with a one-paragraph bridge ("tool-use is the text↔external-system interface that gates all multimodal capability — vision tools, code-execution, file I/O all fail upstream of modality at registry boundaries"); (c) including the Qwen3-8B result so they can't say "you only tested two models from one vendor."

The dominant rejection vector is **"text-only on a multimodal workshop, no positive result, sample sizes too small."** Hedge against all three.

## Submission-day checklist (top 10)

1. Run the Qwen3-8B distractor probe tonight; lock the numbers into `RESULTS/headline_numbers.md`
2. Switch track from Main → Benchmarking & Dataset on OpenReview
3. Add the multimodal-bridge paragraph to §1 (3-4 sentences, frame tool-use as the modality interface)
4. Generate the headline TEHR-vs-N figure and place it on page 1 or 2
5. Update the abstract to lead with the harness/instrument framing, not the null result
6. Add the inline Reproducibility Statement subsection to §4
7. Verify `\usepackage{icml2026}` (no options) is set; compile against `icml2026.sty` not `article`
8. Run `exiftool -overwrite_original -all= submission.pdf` to scrub PDF metadata
9. Verify all citations resolve (the §2 file has 4 TODO arXiv IDs flagged in comments — those will get caught by a careful reviewer; resolve them)
10. Anonymize the harness repo on `anonymous.4open.science`; add the URL as an abstract footnote

## Honest 2-paragraph "what to do tonight" advice

Stop polishing the paper text. The paper as written is fine prose; another pass adds <2pp acceptance probability. The single dominant action is **run the Qwen3-8B probe**. Your `mlx_probe.py` is already written, the dataset is staged, the wall-clock is ~90 minutes on your Mac. Whatever number comes out, the paper improves: TEHR>0 gives you a positive headline (huge), TEHR=0 gives you a third tier of negative-result corroboration (modest), and a partial-failure result gives you a system-characterization story (small but real). The expected acceptance lift is +20 to +30pp — nothing else you can do in 3 hours competes.

After that, the next 2 hours should be: (a) switch the OpenReview track to B&D, (b) add the headline figure, (c) write the multimodal-bridge paragraph in §1, (d) update the abstract to surface the Qwen result. Skip MetaTool replication — building a MetaTool adapter from scratch is a 4-6 hour task and will go badly under deadline pressure. Skip the scaling-curve sketch unless time permits at the very end. Submit at 06:00 UTC on the 29th, not 11:59 — give yourself buffer for OpenReview platform issues, which are real on deadline day. Do *not* ship the supplementary zip until you've grep-scanned every JSONL trace for your name, your email, your home directory path, and your git config — anonymization fails are an automatic desk reject.
