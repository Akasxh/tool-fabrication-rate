# Abstract + intro-opening variants (pending C0.8 decoy result)

The C0.8 decoy condition (RVR envelope listing DECOY/wrong tools, real
target still absent) decides the framing.

- If C0.8 stays at **zero** TEHR -> registry CONTENT is decorative; the
  structured rejection envelope alone re-grounds the model. Ship **Variant A
  (format-not-content recovery)**.
- If C0.8 **regresses** (fabrications return when the list is wrong) ->
  content MATTERS; the model needs a true grounding signal. Ship **Variant B
  (grounding-gap)**.

C0.7 (envelope, NO list) already hits zero on Qwen3-8B (0/253), so C0.8 is
the discriminating control: same envelope shape, but the list is now
actively wrong rather than absent. Decoy-zero confirms format; decoy-fail
confirms content.

Cite keys to use (all already in `paper/refs.bib`, verified):
- `min2022rethinking` -- Min et al., format-over-content in ICL (Variant A anchor)
- `wei2022ushaped` -- Wei et al., inverse scaling can become U-shaped (both variants, curve framing)
- `mckenzie2023inversescaling` -- McKenzie et al., inverse-scaling prize (already cited in intro for the bump)
- `czapla2026` -- production name-mismatch report (motivation, both variants)
- `li2023apibank`, `huang2024metatool`, `cao2025reliability` -- prior grain (both)

Both variants keep: Clopper-Pearson upper bounds, the zero-event Anthropic
regime, Fisher's exact on RVR, honest limitations (strict-pass slip at N=60,
tier-conditional deployment), and the "six points isn't a curve" candor.

---

## VARIANT A -- PRIMARY: format-not-content recovery

### A. Abstract

> Tool-name hallucination is a known failure mode. Who actually does it,
> how often, and what fixes it? We define a per-call Tool-Existence
> Hallucination Rate (TEHR) and run it on BFCL multi-turn against two
> populations: five Anthropic 4.x versions across an eleven-month release
> window, and the Qwen3-Instruct family at six sizes from $0.6$B to $32$B
> (4-bit MLX). The Anthropic side is quiet. Across $2{,}599$ opaque-baseline
> calls we logged zero TEHR events, Clopper--Pearson 95\% upper bound
> $\leq\!0.115\%$. Qwen3 isn't: its rate is non-monotone in scale, climbing
> from $0\%$ at $0.6$B to $\mathbf{1.87\%}$ at $14$B and back to $0\%$ at
> $32$B. We propose Registry-Visible Reprompting (RVR), a training-free
> middleware that, on a registry miss, returns one re-prompt wrapping a
> structured \texttt{tool\_not\_found} envelope. RVR removes all fourteen
> pooled Qwen3 fabrications (Fisher's exact one-sided,
> $p=7.1\!\times\!10^{-5}$ on $14/973$ vs.\ $0/945$). The surprise is where
> the fix lives. An ablation that keeps the envelope but drops the registry
> listing ($\mathrm{C}_{0.7}$; $0/253$ on Qwen3-8B) already hits zero, and a
> decoy that fills the envelope with \emph{wrong} tool names ($\mathrm{C}_{0.8}$)
> [does not re-introduce fabrications / re-introduces them]\footnote{fill
> from C0.8 result}. The recovery is format, not content: a single
> structured rejection re-grounds the model regardless of what the registry
> says, echoing the format-over-content effect Min et al.\ found for
> in-context demonstrations~\citep{min2022rethinking}. Read this way, the
> mid-scale bump stops being noise and becomes a predicted signature -- a
> U-shaped capability window~\citep{wei2022ushaped,mckenzie2023inversescaling}
> in the generative tool-name prior, controlled for quantization by the
> $0$-and-$32$B endpoints that bracket it at the same 4-bit precision. On
> Anthropic's zero-event regime RVR also logs zero, but the strict-pass
> subset slips at $N\!=\!60$; we recommend tier-conditional deployment. Our
> read: reactive agent error-recovery is less about telling the model the
> right answer than about re-grounding its output format, and one structured
> reply does it on the models where the failure shows up.

### A. Intro opening (replaces first two paragraphs of §1)

> An agent calls \texttt{search\_flights}. The registry contains
> \texttt{find\_flights}. The call fails. Practitioners hit this mismatch in
> production with Claude, Gemini, and Grok~\citep{czapla2026}, and what
> stings is that the model knew the task, picked something plausible, and
> just got the name wrong. The reflex fix is to hand the model the registry
> -- show it the menu and it will order off it. We find the menu is mostly
> decoration. What clears the failure is the \emph{shape} of the rejection,
> not its contents: a structured \texttt{tool\_not\_found} envelope
> re-grounds the model whether or not it lists a single real tool. We call
> this format-not-content recovery, and it is the spine of this paper.
>
> The framing has a pedigree. Min et al.\ showed that in-context
> demonstrations help even when their labels are wrong -- the format carries
> the signal, the content rides along~\citep{min2022rethinking}. We report
> the reactive-recovery analogue: a registry-miss re-prompt fixes
> tool-name fabrication even when the listed registry is empty
> ($\mathrm{C}_{0.7}$) or actively wrong ($\mathrm{C}_{0.8}$). Existing
> benchmarks measure related quantities at the wrong grain.
> API-Bank~\citep{li2023apibank} reports per-task name-mismatch up to
> $61.4\%$ on a 2023-vintage model set; MetaTool~\citep{huang2024metatool}
> isolates fabrication via target removal and scores per-query Correct
> Selection Rate on single-turn prompts;
> RelyToolBench~\citep{cao2025reliability} folds non-existent-tool
> invocations into a composite reliability number. Read together, the
> failure looks architecture-agnostic and uniform. We don't think it is, and
> we don't think the fix is what it looks like either.

(then continue into the existing TEHR/two-populations paragraph, with one
edit to the non-monotonic paragraph: reframe the bump as a *predicted
signature* rather than a surprise -- see patch note below.)

#### A. Patch to the Qwen3 non-monotonic paragraph (§1)

Replace "The bump in the middle is what surprised us" framing with:

> The bump is not noise. A generative tool-name prior that strengthens with
> scale before a larger model's registry-grounding control catches up
> predicts exactly this shape -- a U-shaped capability
> window~\citep{wei2022ushaped,mckenzie2023inversescaling}. The $0\%$
> endpoints at $0.6$B and $32$B bracket the $1.87\%$ peak at the same 4-bit
> MLX precision, so quantization is held fixed across the arc; the curve is a
> capability effect, not a compression artifact. Six points still isn't a
> curve, and we say so -- but it is the shape the format-not-content account
> predicts.

---

## VARIANT B -- BACKUP: grounding-gap (use if C0.8 decoy regresses)

### B. Abstract

> Tool-name hallucination is a known failure mode. Who actually does it, how
> often, and why does it peak in the middle? We define a per-call
> Tool-Existence Hallucination Rate (TEHR) and run it on BFCL multi-turn
> against two populations: five Anthropic 4.x versions across an eleven-month
> release window, and the Qwen3-Instruct family at six sizes from $0.6$B to
> $32$B (4-bit MLX). The Anthropic side is quiet. Across $2{,}599$
> opaque-baseline calls we logged zero TEHR events, Clopper--Pearson 95\%
> upper bound $\leq\!0.115\%$. Qwen3 isn't: its rate is non-monotone in
> scale, climbing from $0\%$ at $0.6$B to $\mathbf{1.87\%}$ at $14$B and back
> to $0\%$ at $32$B, and the dominant distractor type shifts with it --
> near-name at $1.7$B, matched-random at $4$B/$8$B, synonym at $14$B. We read
> this as a grounding gap: the generative prior over plausible tool names
> matures faster with scale than the control that checks a proposed name
> against the registry it was actually given. Small models can't propose a
> convincing fake; mid-size models can propose but can't yet veto; large
> models recover the veto. The distractor-type shift is the same gap seen
> from the side -- as the prior sharpens, the hardest distractor moves from
> surface-similar to semantically-similar. We propose Registry-Visible
> Reprompting (RVR), a training-free middleware that, on a registry miss,
> returns one re-prompt wrapping a structured \texttt{tool\_not\_found}
> envelope listing what is available. RVR removes all fourteen pooled Qwen3
> fabrications (Fisher's exact one-sided, $p=7.1\!\times\!10^{-5}$ on
> $14/973$ vs.\ $0/945$); a decoy that lists the \emph{wrong} tools
> ($\mathrm{C}_{0.8}$) re-introduces fabrication, confirming that the
> registry content -- the grounding signal -- is doing the work, not the
> envelope alone. RVR is an external grounding control standing in for the
> internal one mid-scale models lack. The U-shaped
> curve~\citep{wei2022ushaped,mckenzie2023inversescaling} is the predicted
> signature of a prior that outpaces its own grounding. On Anthropic's
> zero-event regime RVR also logs zero, but the strict-pass subset slips at
> $N\!=\!60$; we recommend tier-conditional deployment.

### B. Intro opening (replaces first two paragraphs of §1)

> An agent calls \texttt{search\_flights}. The registry contains
> \texttt{find\_flights}. The call fails. Practitioners hit this mismatch in
> production with Claude, Gemini, and Grok~\citep{czapla2026}, and what
> stings is that the model knew the task, picked something plausible, and
> just got the name wrong. Two things have to go right for the model not to:
> it must generate a candidate name, and it must check that candidate against
> the registry it was handed. We find these two abilities mature at different
> rates with scale, and the gap between them is where tool-name hallucination
> lives.
>
> Call it the grounding gap. A model's generative prior over plausible tool
> names sharpens with scale before its registry-grounding control -- the
> check that vetoes a name absent from the menu -- catches up. Small models
> can't propose a convincing fake; mid-size models propose but can't veto;
> large models recover the veto. That story predicts a U-shaped TEHR curve in
> scale~\citep{wei2022ushaped,mckenzie2023inversescaling} and a shift in the
> hardest distractor type as the prior sharpens, both of which we observe on
> Qwen3. Existing benchmarks measure related quantities at the wrong grain.
> API-Bank~\citep{li2023apibank} reports per-task name-mismatch up to
> $61.4\%$ on a 2023-vintage model set; MetaTool~\citep{huang2024metatool}
> isolates fabrication via target removal and scores per-query Correct
> Selection Rate on single-turn prompts;
> RelyToolBench~\citep{cao2025reliability} folds non-existent-tool
> invocations into a composite reliability number. Read together, the failure
> looks architecture-agnostic and uniform. We don't think it is -- and we
> think its scale dependence is the tell.

(then continue into the existing TEHR/two-populations paragraph. The RVR
paragraph needs one edit: frame RVR as an *external grounding control* and
add the C0.8 decoy-regression result as positive evidence that content
matters -- see patch note below.)

#### B. Patch to the RVR paragraph (§1)

> Registry-Visible Reprompting (RVR) is what we built to close the gap from
> the outside. The middleware is training-free: intercept the proposed call,
> check the name against the live registry, and on a miss re-prompt with a
> structured \texttt{tool\_not\_found} envelope listing what is available --
> the grounding control the mid-scale model is missing, supplied externally.
> Across the four Qwen3 tiers with non-zero TEHR ($1.7$B, $4$B, $8$B, $14$B),
> RVR clears all fourteen pooled fabrications: Fisher's exact one-sided on
> $14/973$ vs.\ $0/945$ gives $p=7.1\!\times\!10^{-5}$. Two ablations locate
> the signal. Dropping the registry list but keeping the envelope
> ($\mathrm{C}_{0.7}$) [matched / did not match] $\mathrm{C}_1$; filling the
> envelope with \emph{wrong} names ($\mathrm{C}_{0.8}$) re-introduced
> fabrication. The content is load-bearing: RVR works because it tells the
> model what is actually there, not merely that something is wrong.

---

## Notes for integration

- Variant A's strongest move is reframing the non-monotonic curve from a
  reported curiosity into a *prediction* the format-not-content account
  makes -- this raises the paper from descriptive to mechanistic without
  overclaiming (still hedged with "six points isn't a curve").
- Variant B keeps the descriptive honesty of the current draft and adds a
  causal handle (prior-vs-control maturation) that the distractor-type shift
  already supports independent of C0.8.
- Either way, the quantization-control sentence ("$0$ and $32$B endpoints
  bracket the peak at the same 4-bit precision") is worth keeping in the
  body even if it does not fit the abstract -- it pre-empts the obvious
  reviewer objection that the bump is a compression artifact.
- C0.8 result placeholder appears in exactly two spots (A abstract footnote,
  B RVR patch). Fill both from PHASE0/RESULTS once the run lands.
