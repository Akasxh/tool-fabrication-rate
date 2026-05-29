# skeptic.md — three hostile personas vs the H4 (gap-led synthesis) framing

Each attack tagged FATAL-WITHOUT-DATA (no framing rescues it; needs an experiment) or SURVIVABLE-TODAY (honest scoping/wording defuses it). Personas 13/14/15 attacked faithfully per their files.

## Persona 14 — Main-track Area Chair (significance/novelty/breadth)
| Attack | Tag | Rebuttal that survives |
|---|---|---|
| **Significance: is the 0% just easy?** "Anthropic 0 is only significant if the null is non-trivial — robust to harder registries?" | SURVIVABLE-TODAY (partial) | The null is on a TARGET-REMOVED distractor probe (the registry is adversarially missing the needed tool) + multi-vendor (5 OpenAI + 5 Anthropic) + corroborated by HalluWorld's independent "near-solved for frontier" on a class. Report CP UB ≤0.14%, never bare 0%. RESIDUAL: a harder near-name-dense registry stress arm would make it bulletproof — a cheap optional add. |
| **Novelty: per-call TFR = re-slicing ToolBeHonest/MetaTool?** | SURVIVABLE-TODAY | TFR extends MetaTool per-query→per-call on MULTI-TURN agentic traces (MetaTool is single-turn per-query); ToolBeHonest catalogs qualitatively, no rate. Prior session's librarian confirmed the {per-call × membership × multi-turn × fix} cell is unoccupied; this session's scoop scan confirms it HOLDS at 29 May 2026. The construct is genuinely new — make the paper prove it against the named prior art (it does, in §2 + Table priorart). |
| **Breadth: two families + one benchmark = workshop.** | **FATAL-WITHOUT-DATA** | NO framing answers this. This is the binding constraint (moderator C1 / H5). Cure = 2nd benchmark non-zero base reproducing the gap (+ 2nd open family). This is THE main-track gate. |
| **Over-claim audit: does the abstract promise a phenomenon the experiments deliver as a harness measurement?** | SURVIVABLE-TODAY (and H4 helps) | H4 deliberately frames the gap as a MEASURED phenomenon, not a causal law, and carries the curve + format-not-content at their hedged level. This is the honest posture the AC rewards. H2-as-headline would FAIL this audit (promises content-decorative, delivers a zero-vs-zero bound). |

**Persona 14 verdict (simulated)**: significance MEDIUM (gap real + corroborated, but external-validity unproven on a 2nd benchmark); MAIN-TRACK: **NO as-is, borderline-plausible with a 2nd benchmark**; single highest-leverage add = **one more benchmark with non-zero base**; 14B peak safe to headline = **NO** (keep descriptive).

## Persona 15 — Quantization & Confound Skeptic
| Attack | Tag | Rebuttal that survives |
|---|---|---|
| **The non-monotonic curve is a 4-bit MLX artifact, not capability.** | **FATAL-WITHOUT-DATA for any curve-as-headline; SURVIVABLE if curve is demoted.** | H4 demotes the curve to SUPPORTING and §5 already says "cannot disentangle scale from 4-bit quantization; bf16 control forthcoming." Cure for upgrading the curve = fp16 spot-check at 1-2 ladder points (small members fit M5). But under H4 the curve is NOT the headline, so this attack does not threaten the paper's contribution — only its weakest supporting claim. |
| **The gap is precision×serving-stack, not weights-availability.** Anthropic/OpenAI = API full-precision schema-enforced; Qwen3 = 4-bit local MLX. | **SURVIVABLE-TODAY** (must be owned in words) | This is exactly why H4 frames the gap as "API-served commercial frontiers vs locally-served 4-bit open-weight" and makes NO pure-weights causal claim (claim #3 is forbidden). §7 already lists the co-variation. The honest framing PRE-CONCEDES this; the AC cannot use a confound the paper already disclosed as load-bearing against it. RESIDUAL honesty paragraph required (see +1 page). |
| **Tool-not-in-registry adjudication: exact-match vs normalized? Could vendor normalization manufacture/erase events for one family?** | SURVIVABLE-TODAY | §3 defines membership as `name ∉ R` set-membership; loop.py:177 flags purely on `call.name not in active_registry` (execution-independent — INTEGRATION_PLAN confirms). Disclose the matching rule explicitly in the +1 page (it is exact-set-membership on parsed names, system-failures excluded). A normalization arm (does case/underscore folding change counts?) is a cheap robustness add. |
| **Contamination: is Anthropic 0 just memorized BFCL tool names?** | SURVIVABLE-TODAY (partial) | §7 already concedes "indistinguishable from BFCL v4 contamination; ran no paraphrase/MI control." A paraphrased-registry arm is the cure. Honest disclosure suffices for now; the gap-as-phenomenon does not require ruling out contamination (the distractor names are SYNTHETIC, not in any corpus — a point the paper should make louder: the FABRICATED names the model reaches for are not BFCL-canonical, so memorization cuts AGAINST fabrication here). |

**Persona 15 verdict (simulated)**: most dangerous uncontrolled confound = **QUANT (for the curve) / PRECISION-STACK (for the gap)**; single missing-but-doable control = **bf16 14B arm** (protects the curve) and a **paraphrased/normalized-registry arm** (protects the gap-and-null); recommended disclosure paragraph = the precision×serving co-variation (already drafted in §7, promote to the +1 page).

## Persona 13 — Tool-eval / benchmark specialist
| Attack | Tag | Rebuttal |
|---|---|---|
| **Single in-house metric, no external anchor.** "Is TEHR corroborated by a differently-defined number from another benchmark (ToolBeHonest, where GPT-4o/Gemini DO fabricate)?" | **FATAL-WITHOUT-DATA (partial)** | This is the cross-benchmark-triangulation bar. Cure = run ONE license-clear benchmark (BFCL single-turn irrelevance is on-disk TODAY; tau-bench wired) and show the gap reproduces. Currently the only external anchor is Qwen2.5-7B 6.10% (same-lineage, not cross-benchmark). |
| **Run vs cite: are tau-bench/Seal-Tools/ToolSandbox actually RUN or only cited?** | **FATAL-WITHOUT-DATA** | Currently cited, not run (HARNESS_ADAPTER_PLAN: tau-bench gated on env wiring; Seal-Tools/RestBench gated on data vendoring; BFCL single-turn runnable now). The specialist's single named cure = "a second benchmark that reproduces the 0-vs-nonzero split." |
| **Metric portability: does per-call TFR transfer cleanly or change meaning across harnesses?** | SURVIVABLE-TODAY | INTEGRATION_PLAN: TEHR is execution-independent (`call.name ∉ registry`), so it ports to any loader yielding an OpenAI-shape registry. Demonstrate by running the 2nd benchmark — which doubles as the triangulation cure. |
| **Null robustness: does Anthropic-0 survive a HARDER registry?** | SURVIVABLE-TODAY (optional add) | Same as Persona-14 significance attack. Near-name-dense stress registry arm is the cheap cure. |

**Persona 13 verdict (simulated)**: breadth = **WORKSHOP-ONLY as-is**; single best conversion = **a 2nd benchmark reproducing the 0-vs-nonzero split (tau-bench or BFCL single-turn irrelevance)**; 14B peak safe to headline = **NEEDS-REPLICATION**.

## Cross-persona synthesis (the decisive pattern)
**All three independent hostile personas converge on the SAME single cure: a 2nd benchmark with a non-zero base that reproduces the gap.** Persona 14 calls it the breadth gate; persona 13 calls it cross-benchmark triangulation + run-vs-cite; persona 15's confound concerns are mostly SURVIVABLE-TODAY by honest disclosure (the curve demotion + precision-stack pre-concession). This is strong triple-confirmation of empiricist rank-1 and moderator C1.

- **FATAL-without-data attacks** (cannot be reframed away): (1) breadth = 2nd benchmark [14,13]; (2) cross-benchmark triangulation / run-vs-cite [13]; (3) curve-as-headline quant artifact [15] — but H4 NEUTRALIZES (3) by demoting the curve.
- **SURVIVABLE-today attacks** (honest wording defuses): novelty, over-claim, precision-stack (pre-concede), contamination (disclose + note synthetic distractors), adjudication rule (disclose), null-on-easy-registry (optional stress arm).

## Surviving recommendation after the hostile panel
H4 framing is correct AND survives the SURVIVABLE attacks cleanly. The FATAL attacks all reduce to ONE experiment: the 2nd-benchmark gap reproduction. The curve must be demoted (persona 15) — H4 already does this. Security stays motivation (prior Attack 3). Net: H4 is the defensible-today framing; the honest ceiling is gated by the 2nd benchmark, which all three personas independently name.

## Confidence
HIGH. The triple-persona convergence on "2nd benchmark" is the strongest signal in the session: it is not one reviewer's idiosyncrasy but the structural main-track bar for a single-benchmark measurement paper. The FATAL/SURVIVABLE split tells the user exactly which gaps are wording (free) and which are data (the multi-day program).
