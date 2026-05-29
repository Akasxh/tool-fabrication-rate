# Adversarial Review — "Who Hallucinates Tools, How Often, and What Fixes It"
## Persona: worst-case senior referee, main-track ICML 2026 bar

I read this looking for any pretext to reject. The revision is genuinely
better written than the prior draft — the de-AI'd prose, the prior-art table,
and the Clopper-Pearson bounds on every zero are real improvements. But at the
**main-track ICML bar** (not workshop), the contribution is a measurement note
plus a one-line middleware, and the central numbers do not reconcile across the
paper's own tables. Below are the three objections most likely to carry an AC.

---

### Objection 1 — The headline "14/14 prevented" silently swaps to a smaller denominator than the paper's own central result (cherry-picked N).

**One sentence:** The fabrication count the paper claims RVR removes (14) is not
the fabrication count the paper's headline scaling table reports (19); the gap is
a quietly substituted, smaller 8B denominator.

**Quote / refs:** Table `tab:qwen3-scale` (`05_results.tex` lines 122–127) pools
the four non-zero tiers as 2 + 3 + **9** + 5 = **19** C0 events (8B = `9/615`).
But Table `tab:rvr-validation` (lines 180–185) reports the "prevented" pool as
2 + 3 + **4** + 5 = **14** (8B C0 = `4/269`), and the abstract (`main.tex` line
80) plus intro (`01_introduction.tex` line 76) both assert RVR "removes all
fourteen pooled Qwen3 fabrications." The caption (lines 168–171) admits the
matched-run C0 denominators are "smaller than the full distractor-probe pool,"
which is precisely the problem: the prevention claim is evaluated on the subset
where it looks cleanest. Five of the nineteen real C0 fabrications (the 8B
delta) never enter the RVR contingency table. Your own MEMORY baseline gate said
"multiply the ~19-event count" — the paper instead reports the 14-event subset.

**What makes it unrebuttable:** Run C1 on the *full* 615-call 8B probe (and the
full per-tier probe pools) so the prevented numerator equals the headline
fabrication count, or strike "all fourteen" and report 14/19 with the missing
five explained. As written, an AC sees a denominator chosen post hoc.

---

### Objection 2 — A self-admitted unreconciled, possibly fabricated number is stated as fact in the results.

**One sentence:** The paper asserts a Qwen3-8B miss_func rate of `5/258 = 1.94%`
that an inline author comment confesses is "absent from the aggregator" and needs
a rerun.

**Quote / refs:** `05_results.tex` line 38:
`% NUMBERS_TODO: Qwen3-8B miss_func cell (claimed 5/258=1.94%) absent from
aggregator; rerun and reconcile against the base full-probe 9/615=1.46%.`
Immediately followed (lines 39–42) by the load-bearing claim "On the same split
it logs `5/258 = 1.94%`, slightly above the `1.46%`... That is what BFCL's
design predicts." This number is doing rhetorical work (BFCL's miss_func "bites"
on Qwen but not Anthropic) yet by the authors' own admission is not regenerable
from the released aggregator. Setup §4 (`04_setup.tex` lines 37–44) and the
disclosure (`08_llm_disclosure.tex` line 18) both promise "no number without a
code path that regenerates it." This violates that promise in the body.

**What makes it unrebuttable:** It already is. The TODO is in the source. If a
reviewer downloads the anon repo and `aggregate_all.py` does not emit 5/258, the
paper is desk-checkable as containing an unverifiable headline-adjacent number.
This is the single most dangerous line in the manuscript.

---

### Objection 3 — The contribution is underpowered descriptive measurement; the "U-shaped scaling" headline is six points with overlapping CIs, and the "fix" is a one-line membership check.

**One sentence:** Strip the framing and the paper is: open models fabricate at
0.95–1.87%, closed models at 0%, a 6-point non-monotone curve whose endpoints'
CIs overlap its peak, and a `if name not in registry: reprompt` middleware.

**Quote / refs:** The "collapse" at 32B is explicitly "not-detected at this N"
with a CI overlapping the 14B peak (`05_results.tex` lines 104–107). Six points
"do not support a fitted scaling law" (line 151), the Friedman drift test is
null (`06_mechanism.tex` line 51, p=0.46), and per-tier RVR Fisher tests are all
individually non-significant (`05_results.tex` line 226: {0.24, 0.12, 0.058,
0.032}) — only the pooled contrast clears. The vendor gap is fully confounded
(`07_limitations.tex` line 5: "parameter count, 4-bit MLX quantization, training
recipe, and provider guardrails co-vary"). The RVR pseudocode (`03_method.tex`
lines 19–25) is six lines, and the format-not-content finding reduces to "a
structured rejection re-grounds output," already foreshadowed by Min et al. and
by the LangChain `ToolMessage` pattern the paper itself cites (line 80–84). For
a main-track slot, the novelty surface is thin: TFR is per-call MetaTool, RVR is
CRITIC specialized to registries (the paper concedes both, `02_related_work.tex`
lines 38–48, 73–76).

**What makes it unrebuttable:** The quantization confound and small-N are
self-disclosed; an AC need only quote the limitations section back. The in-flight
bf16/8-bit control is the *only* thing that converts this from "open-vs-closed,
fully confounded" to a real capability claim — and it is not in the paper.

---

## Secondary issues (would reinforce, not lead)

- **Denominator chaos across tables.** 8B C0 appears as `9/615` (scaling),
  `4/269` (RVR), `9/615` (ablation §5 line 211), and the coverage table
  (`A1_appendix.tex` line 127) lists 8B base as `615` but its regime row as
  `108` — four different 8B denominators. Even a sympathetic reviewer will lose
  the thread; an adversary calls it irreproducible.
- **Coverage table still says TEHR/`\textsc{tehr}`** (`A1_appendix.tex` lines
  104–105) after the global rename to TFR. Method label is `sec:method:tehr`
  (`03_method.tex` line 5). A double-blind reviewer reads stale labels as a sign
  the numbers were not re-derived after the rename.
- **C0.8 decoy is the new spine but lives in a footnote + §6.** The "wrong list
  recovers as well as right list" result (abstract footnote, `main.tex` 87–90;
  `06_mechanism.tex` 27–37) is the paper's most novel claim, yet it is 0/410 on
  a single model (8B) at a single condition. A zero-event result on one model is
  weak evidence for a "format-not-content" mechanism law; it is consistent with
  "8B simply stops fabricating after any reprompt." No positive control shows the
  decoy *could* have re-introduced fabrication.
- **"Commercial vs open" generalization rests on two vendors.** OpenAI + Anthropic
  both 0%; that is two closed labs, not "commercial models." Spracklen's 5.2%
  commercial package-hallucination rate (intro line 41) directly contradicts a
  clean 0% commercial story and is cited approvingly anyway.
- **Strict-pass regression is real and unresolved.** Sonnet 60→53/60 (−11.7pp)
  is a pass-rate cost (the persona's "pass-rate failure" pattern), waved off as
  "underpowered" (`05_results.tex` 190–198). An adversary reads −11.7pp as RVR
  actively harming the model where it was already perfect.
- **Circularity risk, mostly defused.** §3.3 (lines 47–58) and §6 honestly drop
  the registry-as-cue framing and adjudicate message-level rejection; the
  distractor probe is no longer the mechanism discriminator. This is the right
  call and largely neutralizes the "intervention fires only on events it defines"
  objection. Credit where due.

---

## Verdict math

**(a) Probability I convince an AC to reject (current paper): ~83%.** The
self-admitted unverifiable number (Obj. 2) and the 14-vs-19 denominator swap
(Obj. 1) are concrete, quotable, and desk-checkable — exactly the ammunition an
AC needs. The confound (Obj. 3) is conceded in the paper's own text.

**(b) The single killing objection:** Objection 2 — a NUMBERS_TODO in the source
admitting a stated results-section number cannot be regenerated from the released
aggregator. It is the cheapest possible reject ("authors' own comment says this
number is unverified") and it taints trust in every other zero.

---

## Projection if the in-flight experiments land as expected

The four in-flight items map directly onto the three killing objections:

1. **bf16/8-bit quantization control** — if Qwen3-8B/14B at bf16 reproduce the
   ~1–2% TFR curve, the *single biggest* confound (Obj. 3, and the prior gate)
   breaks: the U-shape becomes a capability effect, not a 4-bit artifact. This is
   the highest-leverage result in the pipeline. Moves Obj. 3 from "fatal" to
   "a real, if narrow, scaling finding."
2. **A2 reflection baseline (prelim 2/30)** — isolates "is RVR just reflection?"
   If reflection alone does *not* suppress fabrication while the structured
   envelope does, the format-not-content claim gains its missing positive
   control and the C0.8 result (secondary issue) stops looking like "any reprompt
   works." Directly strengthens the spine.
3. **N≥100 event-multiplication on 14B/8B** — converts the ~19-event base (and
   the 14-event prevented subset) into double-digit-per-tier counts, which fixes
   Obj. 1's denominator problem *and* makes per-tier Fisher tests individually
   significant instead of {0.24, 0.12, 0.058, 0.032}. This is what the prior gate
   asked for.
4. **gpt-5 family rows** — incremental; widens the closed-model null but does not
   address a confound.

**Critical caveat the in-flight work does NOT fix:** Objection 2 (the
unverified 5/258 and the TEHR/denominator inconsistencies) is a *hygiene* failure,
not an experiment. No new data fixes a number that the source says is
unaggregated. The authors must reconcile every table to a single regenerated
aggregator pass and delete/replace the TODO'd number before submission. If they
land all four experiments but ship with the inconsistencies intact, the paper
still draws Obj. 1/2 and likely still rejects.

**Projected accept probability if (1)+(2)+(3) land AND the hygiene is fixed:**
the paper becomes a defensible empirical contribution — a quantization-controlled
non-monotone open-model fabrication curve, a closed-model null with tight bounds,
and a controlled format-not-content recovery result with a reflection baseline.
That is a clear, strong workshop accept and a *borderline* main-track paper. The
remaining ceiling is intrinsic: it is still a measurement-plus-trivial-middleware
paper with a 6-point curve and a two-vendor "commercial" claim, which caps
main-track enthusiasm regardless of how clean the execution is.

- Score as-it-stands: **3/10** (main-track scale).
- Accept prob current: **~16%**.
- Accept prob if in-flight lands as expected + hygiene fixed: **~34%**.
- Verdict: **REJECT** (current). Would move to BORDERLINE/WEAK_REJECT with the
  confound broken and tables reconciled.
