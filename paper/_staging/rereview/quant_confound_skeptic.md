# Re-review — Persona 15: Quantization & Confound Skeptic
**Paper:** "Who Hallucinates Tools, How Often, and What Fixes It" (TFR, formerly TEHR)
**Bar:** ICML 2026 main track. **Date:** 2026-05-29.

My prior: a "model X fabricates more than model Y" headline is a confound until
each of {quantization, contamination/leakage, simulator-vendor bias} is ruled
out one-at-a-time. I reject any family/scaling claim that survives only because
a confound was left uncontrolled. Verdict up front: the paper is honest about
its confounds in prose but still *leads* with a curve it has not yet earned, and
the one control that would earn it (bf16/8-bit at the peak) does not exist in the
repo. Findings below in `LINE | CONFOUND-TYPE | HEADLINE-AT-RISK | FIX` form.

---

## Findings

**abstract L97-98 ("controlled for quantization by the 0-and-32B endpoints that
bracket it at the same 4-bit precision") | QUANT | Y | run bf16/8-bit @14B.**
This is the load-bearing confound-defense in the whole paper and it is a logical
sleight-of-hand. "Same nominal 4-bit format at the endpoints" does NOT hold
quantization *damage* fixed. `mlx-community` builds each Qwen3 size independently;
group size and per-tensor outlier handling are not pinned (I checked: the repo
manifest pins only `mlx_lm 0.31.3` and a local mirror for 8B; no `config.json`
quantization block is committed for any size — `harness/data/mlx_models/*/config.json`
absent). 4-bit damage to tool-name-token fidelity is a *non-linear function of
both scale and recipe*; a peak at 14B is exactly what a recipe-by-size interaction
would produce. The endpoint argument controls the *label* "4-bit," not the *thing*
(per-checkpoint reconstruction error). Until a bf16 14B arm reproduces the 1.87%,
the headline curve is observationally indistinguishable from an MLX-quantization
artifact at 14B.

**intro L65-68 ("the curve is a capability effect, not a compression artifact") |
QUANT | Y | same fix.** This sentence states the conclusion the missing control
is supposed to license. As written it is an assertion, not a result. The repo has
NO `*8bit*`, `*bf16*`, `*fp16*` run directory (verified: `ls results/*8bit*` →
no matches). The appendix `NUMBERS_TODO` (A1 L153) honestly lists
"Qwen3-8B-8bit, Qwen3-8B-bf16, Qwen3-14B-8bit" as still running. So the body
makes a claim the authors themselves have flagged as un-run. This is the kind of
sentence a hostile reviewer screenshots. Soften to "we cannot yet exclude a
quantization-damage account; a bf16 control is pending" OR hold the curve until
the control lands.

**setup L4-14 / L160 ("six sizes ... 4-bit MLX") | QUANT | Y | disclose recipe
per checkpoint.** Persona-core check: is the quantization scheme pinned and
identical across sizes? No. The paper names only "mlx-community 4-bit MLX builds."
Different sizes in that org are quantized at different times with whatever the
then-current `mlx_lm` default group size was. The paper must either (a) state
group size + bits-per-weight + that all six used one `mlx_lm convert` invocation
with identical flags, or (b) concede the recipe may vary by size. Right now a
reader cannot tell, and "non-monotone curve" + "uncontrolled recipe drift" is the
textbook confound.

**results L132-136 (Qwen2.5-7B "same-family check," 6.10%) | QUANT/LEAKAGE | N |
keep, but it does not rescue the curve.** This is offered as evidence the effect
"isn't a Qwen3-specific artifact." It is also 4-bit MLX, so it inherits the same
confound; it shows the *lineage* fabricates, not that *4-bit is innocent*. Fine as
color, but do not let it stand in for the precision control. It is the wrong axis.

**limitations L5 ("indistinguishable from BFCL v4 contamination ... ran no
paraphrase or membership-inference control") | CONTAMINATION/LEAKAGE | Y for the
Anthropic-null claim | add a paraphrased-registry arm.** Credit for naming it.
But the open-vs-closed headline (Anthropic/OpenAI 0% vs Qwen 0.95-1.87%) is
*built on* the very null this sentence says could be memorized BFCL tool names.
BFCL v4 predates every commercial model tested; newer/larger commercial models are
more likely to have ingested BFCL registries and worked traces. The 0/2,599 and
0/2,070 zeros could be memorization, not grounding. A held-out / novel-registry
arm (rename every tool to a synthetic string, re-run a 200-call Anthropic+OpenAI
slice) is cheap and would convert "indistinguishable from contamination" into a
real control. As-is, the cross-vendor split is leakage-fragile.

**setup L16-19 + method L7-11 (BFCL string-matched membership adjudication) |
SIMULATOR-VENDOR | partial | state normalization explicitly.** TFR = `name ∉ R`.
Is the membership test exact-match, case/whitespace-normalized, or semantic? Not
stated. If API models emit names in BFCL's exact serialization while local MLX
models drift in casing/underscores, formatting drift gets misread as fabrication
on the open side and the open-vs-closed gap is partly a serialization artifact.
The §6 decoy result *mitigates* this for the RVR story (recovery is format-driven)
but does not address whether the *baseline* C0 events on Qwen are real fabrications
vs normalization misses. One sentence pinning the matcher fixes it.

**results L38 + 05_results NUMBERS_TODO comment | DATA-INTEGRITY | Y | reconcile.**
A live `NUMBERS_TODO` admits the Qwen3-8B miss_func cell (5/258=1.94%) is "absent
from aggregator; rerun and reconcile." This number is cited in-body (L40). A
headline-adjacent number that the authors flag as not reproduced by their own
aggregator is a desk-reject risk if a reviewer runs `aggregate_all.py`. Must be
resolved before submission, independent of the confound question.

**method L28 / results L161-188 (RVR C0 vs C1 share weights) | CROSS-CONFOUND | N
| no action.** Correctly handled. RVR's 14→0 is within-checkpoint, same precision,
same decode stack, so the *intervention* result is confound-clean even if the
*scaling curve* is not. This is the paper's safest claim and should arguably be
the headline instead of the curve. The A2 reflection baseline (in repo,
`qwen3_8B_A2_lean`, preliminary 2/30) is the right control to isolate "is RVR just
reflection" — landing it materially de-risks the RVR story, which is orthogonal to
the quant confound but is the part of the paper I'd actually accept.

---

## Required outputs

**(a) Most dangerous uncontrolled confound: QUANT.** The non-monotone Qwen3 curve
is the stated headline (Fig 1 caption, intro L35) and its only defense is the
endpoint argument, which controls the format label not the quantization damage.
No bf16/8-bit data exists in the repo. Everything rides on a control that is
in-flight.

**(b) Single missing-but-doable control that most protects the headline:** a
**bf16 (or 8-bit) Qwen3-14B arm at the same N as the 4-bit 14B cell.** If 1.87%
survives at bf16, the curve is a capability effect and the headline is earned. If
it collapses to ~0, the curve was a 4-bit artifact and the paper should be reframed
entirely around RVR (which is confound-clean). This single arm is decisive and is
already queued. Secondary: a paraphrased/novel-registry Anthropic+OpenAI slice to
de-fang the contamination reading of the cross-vendor zeros.

**(c) Recommended honest-disclosure paragraph (drop into §7):**
> "Our scaling curve is reported at a single precision (4-bit MLX) using
> per-size community quantizations whose group-size and calibration we did not
> control or verify to be identical across checkpoints. The 0%/32B and 0%/0.6B
> endpoints share the nominal 4-bit *format* but not necessarily the same
> quantization *damage*, which is a non-linear function of both scale and recipe.
> We therefore cannot presently exclude that the 14B peak is a quantization
> artifact rather than a capability window; a full-precision 14B control is the
> decisive test and is pending. Likewise, the commercial-side zeros are consistent
> with, and we cannot rule out, memorization of BFCL v4 registries, as we ran no
> paraphrased- or novel-registry control on the API models."

---

## Scoring

**As-it-stands (current repo):** The paper *claims* the quant confound is
controlled (abstract L97, intro L65-68) while the controlling experiment does not
exist and is flagged TODO by the authors. A skeptic reads "controlled for
quantization" as overclaiming. The RVR + format-not-content result is genuinely
clean and interesting, but the paper foregrounds the un-earned curve. Plus a live
data-integrity TODO (miss_func cell) on a cited number. **Score 4/10. WEAK_REJECT
at the main-track bar.** Below the prior 18% baseline framing because the revision
*hardened* the quant claim ("is a capability effect, not a compression artifact")
without adding the data to back it — it traded honest hedging for overclaim.
Main-track accept prob ~12%.

**If in-flight lands as expected:** bf16/8-bit @14B reproduces ~1.87% (curve is
real), A2 shows reflection-alone doesn't fix (RVR isolated), gpt-5 rows extend the
commercial null, event count multiplies past ~19. That removes my single most
dangerous confound and converts the headline from asserted to demonstrated. The
contamination/leakage confound on the Anthropic-null would still be uncontrolled
(no paraphrase arm is in-flight), so I would not go above borderline-accept, but
it crosses from reject into contention. **Projected score 6/10, BORDERLINE.**
Main-track accept prob ~30%, contingent on bf16 actually reproducing the peak —
if bf16 *kills* the peak, the curve story dies and the score does not improve, it
inverts (the paper would need a full reframe around RVR).
