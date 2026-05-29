# POSITIONING v2 — The strongest DEFENSIBLE main-track framing for the TEHR/RVR paper

**Scope.** Given the paper's HONEST results (per-call TFR; commercial 0/2578 Anthropic + 0/2117 OpenAI; open-weight Qwen3 0.95–1.87% non-monotone; RVR clears 14/14; content-vs-format bounded to CI [−1.5,+1.4]pp and explicitly *not* claimed). A hostile panel capped the honest version at ~20% main-track (clear workshop accept) on TWO gaps: (a) the content/format ablation needs events under it, (b) breadth — a 2nd benchmark with non-zero base + a 2nd open family.

**Method.** Research-team investigation (planner → 5 lenses → synthesist → moderator → skeptic-vs-3-hostile-personas → evaluator PASS 4.74/5). Reused the prior `tehr-spotlight-novelty-framing` session's verified citation base; ran a fresh 2024–2026 arXiv sweep and a 14-day scoop scan; verified every new citation against arXiv. Full audit trail: `.claude/teams/research/tehr-main-track-honest-ceiling/`.

**Bottom line up front.** Adopt a **gap-led synthesis** framing (below). It is the defensible-today maximum and is worth single-digit score points (the team's own panel showed framing alone swings the score 14%↔18%). But framing is **necessary, not sufficient**: all three of your hostile personas independently converge on the SAME structural cure — **a second benchmark with a non-zero base that reproduces the gap.** That single result, not the powered decoy, is what moves the paper from workshop+ to borderline-main-track-plausible.

---

## (1) The single strongest HONEST framing

### THESIS (one sentence)
> **At the per-call grain, frontier commercial APIs have driven tool-existence fabrication to a measurement floor (≤0.14%) while locally-served open-weight models — exactly the ones deployed for cost and privacy — fabricate at a non-trivial rate (up to 1.87%); a per-call diagnostic exposes this reliability gap that aggregate task-success scores hide, and a training-free re-prompt closes it.**

This is **option (D), a synthesis**, but with a disciplined hierarchy — not a menu:

| Role | Element | Why it's here, not the headline |
|---|---|---|
| **HEADLINE (finding)** | The commercial-vs-open-weight tool-existence **reliability gap** | The most data-backed claim you have: multi-vendor on BOTH sides (5 OpenAI tiers + 5 Anthropic versions), a same-lineage check (Qwen2.5-7B 6.10%), and independent contemporaneous corroboration (HalluWorld, Spracklen/USENIX'25). Least contingent on any running experiment. |
| **INSTRUMENT** | Per-call **TFR** | The reason the gap is *visible* where BFCL/τ-bench/API-Bank fold it into composite scores. A method contribution, subordinate to the finding it enables. |
| **FIX** | **RVR** (training-free re-prompt) | The deployable payoff: 14/14 cleared, Fisher p=7.1e-5, tier-conditional. Scoped honestly (5 events untested; Anthropic strict-pass slips at N=60). |
| **MECHANISM (bounded)** | Non-monotone curve + format-not-content | Both carried at the paper's OWN hedge level. Supporting evidence, never the headline. |

### Why NOT the other three candidates (this is the load-bearing part)

- **"Format-not-content recovery (once powered)" — REJECTED as headline, on two independent grounds.**
  1. **Honesty gate**: your own §6 says it is "absence of evidence, not evidence of equivalence" and "we report no result for [the powered version] here." Leading on it requires a claim the manuscript explicitly disowns.
  2. **Empirical gate (decisive)**: you ALREADY ran this A/B. PROGRESS.md "Key lesson": the aggressive format-not-content lead scored **~14% vs 18%** on a 6-persona panel and was walked back. The decoy result you have (8B C0.8 = 0/410) is a *deployment wrinkle*, not a powered mechanism result — the powered 14B decoy with events under the ablation is still unrun and may under-fire. Do not re-make a mistake the project already paid for. Keep it as a bounded supporting note.

- **"Per-call diagnostic + the gap" (metric-led) — too weak as headline.** The bare metric drew "limited novelty" before (API-Bank's API-Hallucination; ToolBeHonest's non-existent-tool category; MetaTool's tool-removal). The metric is genuinely new as a *per-call, multi-turn, membership-clean* construct — but it persuades as the INSTRUMENT under the finding, not as the finding.

- **"Commercial-vs-open gap" alone (H1) — right headline, but leaves reviewer-impact on the table.** Promoting it to a synthesis (instrument + fix + bounded mechanism) is what converts "a two-family audit" into "a finding with a diagnostic and a fix."

### The one wording constraint that makes it defensible
Frame the gap as a **measured phenomenon**, never a causal weights-claim. SAFE: "API-served commercial frontiers vs locally-served 4-bit open-weight models." FORBIDDEN: "open-weight models fabricate *because* they are open" — §7 already concedes parameter count, 4-bit quantization, recipe, and provider guardrails co-vary. Pre-conceding this confound is what disarms the quant-confound skeptic; claiming past it is what gets you rejected.

### How defensibility moves with the running experiments
| Framing | Defensible TODAY | + 2nd benchmark non-zero | + 2nd open family | + powered decoy w/ events |
|---|---|---|---|---|
| Gap-led synthesis (recommended) | 4.0/5 | **4.5/5** | 4.5/5 | 4.0/5 (unchanged — decoy only upgrades a supporting note) |
| Format-not-content lead | 1.5/5 | 1.5 | 1.5 | 3.0 (only if events appear AND content still inert) |

The recommended framing is **robust to the decoy under-firing** — its headline does not depend on a high-variance pending result. That asymmetry is the core reason to pick it.

---

## (2) RELEVANT related work you're missing (all VERIFIED against arXiv)

Your refs.bib is already strong (Wei 2211.02011, McKenzie 2306.09479, Min 2202.12837, Spracklen 2406.10279, Cao 2412.04141, plus the 2026 concurrents Yin/Qi/Healy — all verified in the prior session and re-confirmed). The fresh sweep surfaces FIVE additions; two are load-bearing.

### ADD (load-bearing / motivation)
1. **HalluWorld** — Emmy Liu, Varun Gangal, Michael Yu, Zhuofu Tao, Karan Singh, Sachin Kumar, Steven Y. Feng. *"HalluWorld: A Controlled Benchmark for Hallucination via Reference World Models."* **arXiv:2605.19341, 19 May 2026.**
   - Verbatim: "perceptual hallucination on directly observed information is **near-solved for frontier models**, while multi-step state tracking and causal forward simulation remain difficult... models also struggle with when to **abstain**."
   - **Use**: independent, contemporaneous (10 days pre-this-session) corroboration that a class of hallucination is near-solved for frontier but not open-weight — direct support for your headline gap.
   - **CAVEAT (enforced)**: cite it ONLY at that bounded claim. It does NOT say frontier solved *all* hallucination (state-tracking is hard for everyone). A reviewer who read it will catch an over-read. Phrase: *"an independent controlled benchmark likewise finds a class of hallucination near-solved for frontier models but not open-weight [HalluWorld]."*

2. **AgentHallu** — Xuannan Liu, Xiao Yang, Zekun Li, Peipei Li, Ran He. *"AgentHallu: Benchmarking Automated Hallucination Attribution of LLM-based Agents."* **arXiv:2601.06818, 11 Jan 2026.**
   - 693 trajectories, 5-category taxonomy including Tool-Use; evaluates 13 models incl. GPT-5, Gemini-2.5-Pro; BFCL-V3 trajectories from GPT-4.1, Qwen3-32B, Llama-3.3-70B. Best model hits 41.1% step-localization, **dropping to 11.6% on tool-use hallucinations** — "the most challenging."
   - **Use**: MOTIVATION — tool-use hallucination is the least-tractable agent failure class to even localize. Complementary (attribution, no per-call existence rate, no fix); not a scoop.

### ADD (differentiation — detection-side neighbors)
3. **Spectral Guardrails / "Loud Liar"** — Valentin Noël. *"Spectral Guardrails for Agents in the Wild: Detecting Tool Use Hallucinations via Attention Topology."* **arXiv:2602.08082, 8 Feb 2026.**
   - Training-free DETECTION via attention-spectral features on Llama-3.1-8B + Mistral-7B (no Qwen, no commercial, no scaling). Single-author preprint — cite for EXISTENCE only, not its rates.
   - **Use**: group with Healy (2601.05214, already cited) to differentiate: *"activation/attention-level detectors of tool hallucination [Healy; Noël] require model internals; RVR prevents behaviorally without logit or activation access."* (One clause added to your existing §2 sentence.)

### OPTIONAL (use with care, or omit)
4. **LLMs as Noisy Channels** — Xu Ouyang et al. *"A Shannon Perspective on Model Capacity and Scaling Laws."* **arXiv:2605.23901, 22 May 2026.** Predicts U-shaped degradation from SNR collapse. **DOUBLE-EDGED**: it dignifies the non-monotone curve but also names *quantization* as a cause of non-monotonicity — i.e., citing it hands the quant-confound skeptic ammunition. If used at all, one mention in limitations with "...which is also why we run an fp16 control." Safe to omit.
5. **The Safety Gap Toolkit** — Dombrowski, Bowen, Gleave, Cundy. **arXiv:2507.11544, Jul 2025.** Open-weight safety gap widens with scale (Llama-3/Qwen-2.5). General safety, NOT tool use. At most a one-liner: "open-weight reliability/safety gaps are a recognized, scale-dependent research object." Omit if tight.

### SCOOP-RISK VERDICT
**No paper occupies your cell.** A targeted negative search for "per-call tool-existence rate × commercial-vs-open × multi-turn × training-free fix" returned only marketing blogs. The closest neighbors (AgentHallu = attribution; Spectral/Healy = internal-state detection; HalluWorld = controlled benchmark; Reasoning-Trap/Brief-Is-Better = reasoning-axis, already distinguished) are complementary. The white space HOLDS as of 29 May 2026.

---

## (3) How to spend the +1 camera-ready page (prioritized by reviewer-impact)

Body is 7pp of 8 allowed; the +1 page is for the main-track resubmission. Allocate by the skeptic's FATAL-vs-SURVIVABLE split — buy down the SURVIVABLE attacks with prose (cheap) and SIGNPOST the FATAL ones as in-progress.

**Priority order (highest impact per column-inch):**

1. **[~0.4 pg] A "Threats to Validity & What We Control" subsection** that pre-concedes, in the paper's own honest voice, the three confounds a hostile AC will raise — and turns each pre-concession into a credibility signal:
   - **Precision × serving stack**: "we compare API-served full-precision commercial models against locally-served 4-bit open-weight models; weights-availability, precision, and decoding stack co-vary, so we claim a measured reliability gap, not a causal effect of open weights." (Disarms persona-15's strongest survivable attack.)
   - **Contamination, turned into an asset**: state explicitly that the FABRICATED names the model reaches for are SYNTHETIC distractors absent from any corpus — so memorization of BFCL cuts *against* fabrication, strengthening the null rather than threatening it. (This is a point you currently under-sell.)
   - **Adjudication rule**: one sentence that membership is exact set-membership on parsed names (`name ∉ R`, execution-independent, system-failures excluded). (Disarms the "vendor-normalization manufactures events" attack.)

2. **[~0.3 pg] The 2nd-benchmark result the moment it lands** (see §4) — even a small gap reproduction on BFCL single-turn irrelevance or τ-bench. This is the single content addition that moves the ceiling; reserve the space for it now. If it has not landed by camera-ready, replace with an explicit "External validity (in progress): we are reproducing the gap on [benchmark]; preliminary [N] calls show [direction]" paragraph that signposts the main-track trajectory.

3. **[~0.2 pg] Promote the cross-vendor breadth into a first-class table.** You have 5 OpenAI tiers + 5 Anthropic versions all at 0 — this multi-vendor commercial breadth is currently scattered across prose and the coverage table. A single "Commercial-frontier audit (10 model-versions, 2 vendors, 0/4,695 pooled, CP UB ≤0.09%)" table makes the headline gap visually undeniable and answers "is the 0 a fluke of one vendor?"

4. **[~0.1 pg, if room] An fp16 spot-check row** at 1–2 Qwen3 ladder points (these fit on the M5), to upgrade the curve's limitation from "cannot disentangle" to "the hump persists / attenuates un-quantized." Only buys down the SUPPORTING curve, so it's last — but it directly neutralizes persona-15's headline-curve attack if you ever want to promote the curve.

**Do NOT spend the page on**: a bigger format-not-content section (scored 14%), a security/exploitation expansion without a collision probe (writes a check you can't cash), or more Qwen3-only ablations (deepens the single-family problem the breadth gap is about).

---

## (4) The honest ceiling, and the single result that most raises it

### Honest ceiling AS-IS
**Workshop-strong → borderline-main-track-weak-reject.** The ~20% panel verdict is a **scope verdict**, not a framing verdict. The gap-led synthesis raises the *ceiling* (the score a reviewer is willing to reach) by single-digit points and removes the "limited novelty / trivial intervention" framing problem — but it cannot, by itself, answer the structural objection that **all three of your hostile personas reach independently**: a two-family, single-benchmark, ~14–19-event result is a workshop result until the phenomenon survives a second benchmark. Persona 14 (AC): "interesting but narrow is a reject." Persona 13 (tool-eval): "single in-house metric with no external anchor is weak." Persona 15 (confound): the curve is a quant artifact until fp16-controlled (mitigated by demoting it). Your own PROGRESS.md agrees: "even with all gates cleared, personas put it at borderline-accept, not safe."

### The single result that most raises it
> **A second benchmark with a non-zero base rate that reproduces the commercial-vs-open gap.**

This is the unique result that all three personas name as the cure, and it does triple duty:
- discharges persona-13's cross-benchmark-triangulation + run-vs-cite bar,
- discharges persona-14's breadth gate,
- tests external validity of BOTH the headline gap AND RVR (and demonstrates TFR's portability, which INTEGRATION_PLAN confirms is execution-independent).

**Feasibility (from your own plans)**: BFCL single-turn irrelevance/live data is **on disk today** (HARNESS_ADAPTER_PLAN) — buildable with zero new download as an extension of `bfcl.py`. τ-bench is the higher-value but higher-effort option (needs env.reset/respond wiring + litellm). Either reproduces the gap if it exists; the bar is non-zero-open vs floor-commercial, not a perfect replication of the curve.

**Estimated lift**: from borderline-weak-reject toward borderline-weak-accept — i.e., it is the difference between "workshop, obviously" and "main-track, arguable." It does not guarantee acceptance (the event count stays modest), but it is the only single result that addresses the binding constraint.

### Ranked alternatives (why each is lower-leverage)
2. **A 2nd open family (Llama OR Mistral) with a non-zero rate.** Cheaper (parsing fix, no new env), discharges the Wei multi-family bar, and is *very likely to reproduce* a non-zero rate (Spectral-Guardrails shows Llama-3.1-8B + Mistral-7B hallucinate tools at 20–22% on a General domain). The non-monotone SHAPE holding is a bonus, not a requirement — the gap only needs non-zero-open vs floor-commercial. Strong second choice; pairs naturally with #1.
3. **fp16 quant control at 1–2 ladder points.** Protects the supporting curve only; does not touch the headline. Cheap, do it, but it is not a ceiling-setter.
4. **Powered decoy with events on 14B.** Worth running for §6 completeness, but it upgrades a SUPPORTING claim that already scored 14% as a lead. **Explicitly NOT the highest-leverage result** — do not let the project's prior fixation on the decoy override the triple-persona signal.
5. **Exploitability/collision probe** (does a fabricated name resolve against a plausible superset registry). Converts security from motivation to result — high ceiling, but high effort and scope-creep, and the skeptic warns against leading security without it. A stretch goal, not the lever.

---

## Confidence & residual risks
- **Confidence: MEDIUM-HIGH.** All five adversarial gates closed (synthesist claim matrix; moderator REFRAME on the H4-vs-H5 contradiction; skeptic via the three hostile personas; adversary corpus audit; evaluator PASS 4.74/5). Every new citation verified against arXiv. The decisive inputs (format-not-content scored 14%; triple-persona convergence on the 2nd benchmark; live experiment state) are grounded in your own artifacts, not speculation.
- **Why not HIGH**: the honest-ceiling estimate is qualitative (no calibrated reviewer-score prediction is possible), and the highest-leverage result (2nd benchmark) is named-but-not-yet-landed.
- **Carry these into the manuscript**: (1) never bare "0%" — always the CP upper bound; (2) HalluWorld cited only at its bounded claim; (3) Noisy-Channels omitted or used once-with-quant-caveat; (4) the gap is a measured phenomenon, not a causal weights-claim.

**Full audit trail**: `/Users/cero/Desktop/PROJECTS/icml/.claude/teams/research/tehr-main-track-honest-ceiling/` (QUESTION, HYPOTHESES, EVIDENCE/*, SYNTHESIS). Prior session reused: `/Users/cero/Desktop/PROJECTS/icml/.claude/teams/research/tehr-spotlight-novelty-framing/`.
