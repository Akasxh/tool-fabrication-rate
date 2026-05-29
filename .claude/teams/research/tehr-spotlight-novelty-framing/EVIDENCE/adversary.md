# adversary.md — corpus audit (Round 1, SEO-override)

Mandate: audit the web/X/GitHub/security-press corpus for citation laundering, inflated benchmark numbers, astroturf, and provenance failures BEFORE the synthesist builds the claim matrix. Tag each load-bearing source.

## Source-quality ledger

| Source | Tier | Verdict |
|---|---|---|
| Wei et al. U-shaped (2211.02011, EMNLP'23) | STRONG-PRIMARY | CLEAR. Title/authors/venue/mechanism/multi-family all verified incl. body fetch. Load-bearing OK. |
| McKenzie et al. Inverse Scaling (2306.09479, TMLR'23) | STRONG-PRIMARY | CLEAR. Four causes verified. Load-bearing OK. |
| Min et al. Rethinking Demonstrations (2202.12837, EMNLP'22) | STRONG-PRIMARY | CLEAR. "Random labels barely hurt; format/label-space/input-dist matter" is the well-known canonical result. Load-bearing OK for C0.7 analogy. |
| Olsson et al. Induction Heads (2209.11895, 2022) | STRONG-PRIMARY | CLEAR. |
| Ren et al. Semantic Induction Heads (2402.13055, ACL'24 Findings) | STRONG-PRIMARY | CLEAR. Venue + authors verified. Load-bearing for distractor-shift mechanism. |
| Spracklen et al. "We Have a Package for You" (USENIX Sec'25) | STRONG-PRIMARY | CLEAR. Numbers reconcile across two independent retrievals (≥5.2% commercial / 21.7% open; 205,474 unique; 16 models / 576K samples; 51/38/13 fabrication/conflation/typo split; 19.7% overall). Load-bearing OK. |
| BFCL "From Tool Use to Agentic" (Patil et al., ICML'25) | STRONG-PRIMARY | CLEAR. V4 scoring + "hallucination = relevance not membership" verified. |
| Cao et al. RelyToolBench/Relign (2412.04141, ICML'25) | STRONG-PRIMARY | CLEAR (matches Phase-0). |
| "Slopsquatting" coinage | MIXED→OK | Attribution VERIFIED: Seth Larson (PSF), April 2025; popularized by Andrew Nesbitt; Wikipedia entry. The TERM is citable as a named phenomenon; cite Larson/Wikipedia for the name, USENIX'25 for the numbers. Do NOT cite security-vendor blogs (aikido, socket, mend, syntax.ai) for numbers. |
| "Brief Is Better" (2604.02155, Apr'26) | MIXED | Single-author (Xuan Qi), April-2026 preprint, NOT peer-reviewed. Real and on-topic but UNVETTED. Treat as a THREAT to cite-and-distinguish, not as authority. Its 18%/28%/+45% numbers are REPORTED-NOT-VERIFIED (single preprint, no replication). Use the DIRECTION (CoT-budget ↔ function hallucination), not the specific numbers. |
| "Internal Reps as Indicators of Tool-Selection Hallucination" (2601.05214, Jan'26) | MIXED | Existence VERIFIED; method UNVERIFIED (PDF was slides). Constrains our mechanism-probe novelty — must cite as related work regardless. |
| "Secure or Suspect?" quantization-hallucination (2512.08213, Dec'25) | MIXED | Preprint, NCSU. The quant×size non-monotonic finding is REPORTED-NOT-VERIFIED numerically but the DIRECTION (4-bit quantization can itself produce non-monotonic hallucination-vs-size) is corroborated by general quant-degradation literature. Strong enough to be a CONFOUND we must address; not strong enough to assert exact numbers. |
| "Noisy Channels / Shannon" (2605.23901), "Hallucinations Live in Variance" (2601.07058), "Neural Diversity" (2510.20690) | WEAK/SPECULATIVE | Recent preprints, tangential. Cite at most as "non-monotonic hallucination is an active theme," never load-bearing. |
| GitHub issues (gemini-cli #25952, adk-python #4173), depscope dataset | ANECDOTAL-OK | Real production artifacts; use ONLY as existence/motivation evidence, never for rates. |
| Security-vendor blogs, prompt-engineering listicles, binaryverseai "AI scaling paradox" | REJECTED | SEO/marketing. Do not cite. |

## Red-team findings (corpus-level attacks)

### AT-1 (CRITICAL): The 4-bit quantization confound is a live threat to the entire U-shaped headline.
The Qwen3 curve was measured on **4-bit MLX** across the whole ladder. "Secure or Suspect?" (2512.08213) shows 4-bit quantization ITSELF induces non-monotonic hallucination-vs-size (e.g. their 7B IMPROVED while 0.5B catastrophically worsened). Therefore the observed TEHR hump could be a **quantization×scale interaction artifact**, not a property of the underlying models. A competent AC WILL raise this. The paper currently has NO control for it. This is the #1 thing the synthesis must confront. Mitigation requires at minimum an fp16 spot-check at 1-2 ladder points (the small members fit on M5 in fp16), or reporting that the hump replicates at a different quantization (8-bit).

### AT-2 (HIGH): Single-family N=1 is below Wei et al.'s evidentiary bar.
Wei et al. used PaLM + Chinchilla + GPT-3 (multi-family). A bare single-family curve is dismissable as "family/recipe-specific." Not corpus-fraud, but a legitimacy gap the synthesis must own.

### AT-3 (MEDIUM): "Brief Is Better" partially scoops the novelty surface.
A concurrent April-2026 preprint already reports non-monotonic function hallucination in Qwen-family agents (tied to CoT budget). Our differentiation (scale axis, thinking disabled) is real but MUST be stated explicitly or a reviewer who knows 2604.02155 will think we missed it.

### AT-4 (LOW): No astroturf detected.
Unlike the MemPalace case in MEMORY.md, none of the load-bearing sources here are hype-driven GitHub-star products with fabricated benchmarks. The security-blog ecosystem around slopsquatting is derivative-but-honest (all trace back to Larson + USENIX'25). Clean.

### AT-5 (MEDIUM): "Zero hallucinations across 2599 calls" (Claude 4.x) is a measurement-floor claim.
0/2599 is a strong claim. The adversary's concern is not fraud (it's the team's own reproduced data) but FRAGILITY: a single counterexample collapses it, and the 95% CI upper bound on 0/2599 is ~0.14% — non-trivial. The synthesis should report the Clopper-Pearson upper bound, not bare "0%", to be unimpeachable.

## Confidence
HIGH that the corpus is honest (no laundering/astroturf; all load-bearing sources are peer-reviewed primaries with reconciling numbers). HIGH on AT-1 (quantization confound) and AT-2 (N=1) as the dominant evidentiary threats. Handoff: these are reasoning/evidence threats, not corpus threats — route AT-1/AT-2/AT-3/AT-5 to skeptic and moderator.

## Verdict
Corpus is HONEST and citation-anchored — no laundering, no astroturf. The threats are EVIDENTIARY (quantization confound, N=1, concurrent-preprint overlap, floor-claim CI), not corpus-fraud. These go to the skeptic and moderator. The strongest citations (Wei, McKenzie, Min, Olsson, Ren, Spracklen/USENIX, BFCL, Cao) are all peer-reviewed primaries and safe to make load-bearing.
