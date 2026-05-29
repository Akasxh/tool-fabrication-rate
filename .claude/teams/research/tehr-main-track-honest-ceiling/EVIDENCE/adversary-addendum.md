# adversary-addendum.md — corpus audit of NEW citations only

The prior session's corpus audit (`tehr-spotlight-novelty-framing/EVIDENCE/adversary.md`) stands for all REUSED cites (Wei, McKenzie, Min, Olsson, Ren, Spracklen, BFCL, Cao — all STRONG-PRIMARY, CLEAR). This addendum audits ONLY the citations newly surfaced this session.

## Source-quality ledger (new cites)

| Source | arXiv | Tier | Verdict |
|---|---|---|---|
| HalluWorld | 2605.19341 | STRONG-PRIMARY (with scope caveat) | Abstract fetched + quoted. CMU/UW-flavored author list (Emmy Liu, Sachin Kumar, Steven Feng). Real, recent (19 May 2026), controlled-benchmark methodology. **CAVEAT enforced**: load-bearing ONLY for the bounded claim "a class of hallucination is near-solved for FRONTIER models but not open-weight"; NOT for "frontier solved hallucination." The abstract explicitly says BOTH frontier and open struggle on state-tracking. Tag the claim, not the paper, as bounded. OK to cite as corroborating support. |
| AgentHallu | 2601.06818 | STRONG-PRIMARY | Abstract fetched + quoted. 5 authors (Liu/Yang/Li/Li/He). Real benchmark, Jan 2026. The 11.6% (tool-use step-localization) and 41.1% (overall) are from the paper's own eval of 13 models. Use as MOTIVATION ("tool-use hallucination is the hardest agent failure to localize"), not as a competing rate. CLEAR. |
| Spectral Guardrails / Loud Liar | 2602.08082 | MIXED→OK (single-author preprint) | Abstract fetched + quoted. SINGLE author (Valentin Noël), Feb 2026, not peer-reviewed. The 98.2%/94.7%/AUC-0.900 detection numbers are REPORTED-NOT-VERIFIED (single preprint, no replication). BUT we are NOT using its numbers — only its EXISTENCE as a detection-side neighbor to differentiate RVR (prevention) from detection. For that use, single-author-preprint tier is sufficient. Do NOT cite its rates as authority. |
| LLMs as Noisy Channels | 2605.23901 | MIXED (use direction only) | Abstract fetched + quoted. 8 authors, 22 May 2026, not peer-reviewed. R²=0.847 and the Shannon-SNR framework are REPORTED-NOT-VERIFIED. **DOUBLE-EDGED FLAG**: it predicts U-shaped degradation from quantization — citing it to support the curve simultaneously hands the quant-confound skeptic ammunition. RECOMMEND: cite at most once, in limitations/mechanism, for the DIRECTION ("non-monotonic capability-vs-scale is a theorized phenomenon"), never as the load-bearing explanation. Optional; safe to omit. |
| Safety Gap Toolkit | 2507.11544 | STRONG-PRIMARY (off-target scope) | Abstract fetched + quoted. Gleave/FAR-AI-flavored authors, Jul 2025. Real, solid. BUT scope = general safety (biochem/cyber/refusal), NOT tool use. Use ONLY as a one-line "open-weight reliability/safety gaps are a recognized, scale-dependent research object." NOT load-bearing. If space is tight, omit. |

## Red-team findings (corpus-level, new)

### AT-N1 (MEDIUM): HalluWorld overclaim trap.
The seductive misread is "HalluWorld proves frontier models don't hallucinate, just like our 0%." FALSE. HalluWorld says PERCEPTUAL hallucination on directly-observed info is near-solved for frontier; state-tracking is hard for ALL. If the paper cites HalluWorld as blanket frontier-solved support, a reviewer who read HalluWorld will catch the overclaim and it BACKFIRES. Mitigation: cite the exact bounded claim. ENFORCED in historian-addendum A2.

### AT-N2 (MEDIUM): Noisy-Channels is a confound gift.
Citing 2605.23901 to dignify the non-monotonic curve also imports its claim that quantization causes non-monotonicity — i.e., it strengthens persona-15's quant-confound attack. Net-neutral-to-negative. RECOMMEND omit or use once with explicit "and this is also why we run an fp16 control" framing.

### AT-N3 (LOW): No new astroturf/laundering.
All marketing hits (PricePerToken, CallSphere, Codersera, latent.space, VentureBeat) were correctly REJECTED by web-miner as landscape-only. No fabricated-benchmark hype product in this corpus (unlike the MemPalace case in MEMORY.md). Clean.

### AT-N4 (LOW): Spectral Guardrails / AgentHallu do not scoop.
Confirmed: both are complementary (detection / attribution), neither does per-call existence-rate + commercial-vs-open + fix. The scoop-risk verdict (historian-addendum D) is corpus-clean.

## Verdict
New corpus is HONEST. Two enforced caveats: (1) HalluWorld cited only at its bounded claim (AT-N1); (2) Noisy-Channels omitted or used once with the quant-control caveat (AT-N2). HalluWorld + AgentHallu are the two safe NEW load-bearing/motivation adds. Spectral Guardrails is a safe differentiation cite (existence only). Route AT-N1/AT-N2 to the synthesist so the SYNTHESIS does not overclaim either.

## Confidence
HIGH. All five new sources had abstracts fetched and quoted; tiers assigned per the 4-tier scale (STRONG-PRIMARY / MIXED / REPORTED-NOT-VERIFIED / REJECTED) from MEMORY.md.
