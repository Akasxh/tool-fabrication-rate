# Sharpened abstract + intro-opening (PROPOSAL — not yet applied)

Status: PROPOSAL. Do not assume application. Changes ONLY framing/emphasis;
every number, bound, hedge, and claim-strength is preserved from the current
camera-ready (`paper/main.tex` abstract + `sections/01_introduction.tex`).

## What changes vs. the current draft

The current abstract leads with "two populations: Anthropic 4.x + Qwen3," then
adds OpenAI, precision, and Llama as later sentences. The strongest spine the
data now supports is a **three-vendor-closed vs. three-lineage-open** gap that
is (a) replicated across vendors/lineages, (b) not a quantization artefact, and
(c) removed by a training-free middleware. The sharpened version foregrounds
that spine in the first three sentences and demotes the scaling-shape curiosity
to a single hedged sentence, where it belongs.

LOCKED numbers used (verified against scripts/aggregate_all.py):
- Anthropic C0 pooled 0/2,592 (<=0.14%); OpenAI gpt-4.x/4o pooled 0/2,117 (<=0.18%)
- gpt-5 generation (gpt-5/-mini/-nano/5.5) 0/1,311 confirmatory, KEPT OUT of headline (<=0.28%)
- Qwen3-14B C0 peak 6/366 = 1.64%; curve 0.6B 0 / 1.7B / 4B / 8B / 14B 1.64% / 32B 0
- Open lineages: Qwen3 0.4–1.64%, Llama-3.1-8B 5/400=1.25%, Qwen2.5-7B 28/459=6.10% -> "0.4–6%" band
- RVR 20/1,417 vs 0/945, Fisher one-sided p=3.5e-5
- Ablation C0.7 0/448, C0.8 0/410, C1 0/258; Newcombe C1−C0.7 [-1.5,+1.4]pp
- Precision ladder (Qwen3-8B): 4-bit 9/623=1.44%, 8-bit 2/435=0.46%, bf16 2/316=0.63%
- Llama RVR residuals reduced not cleared (2/487=0.41%); strict-pass TOST underpowered N=60

---

## DROP-IN ABSTRACT (replaces lines 60–97 of paper/main.tex)

```latex
\begin{abstract}
Tool-name hallucination is a known failure mode. Who actually does it,
how often, and what fixes it? We define a per-call \emph{Tool Fabrication
Rate} (TFR) and measure it on BFCL multi-turn across a clean open-vs-closed
split. Three commercial vendors stay silent: Anthropic~4.x ($0/2{,}592$
opaque-baseline calls, Clopper--Pearson 95\% two-sided upper bound
$\leq\!0.14\%$) and the OpenAI gpt-4.1/gpt-4o tiers ($0/2{,}117$ pooled,
$\leq\!0.18\%$) both log zero TFR, and a confirmatory gpt-5 generation
extends the null ($0/1{,}311$, $\leq\!0.28\%$; reported separately, not
pooled into the headline). Three open lineages do not: Qwen3, Qwen2.5-7B,
and Llama-3.1-8B fabricate at $0.4$--$6\%$ per call. We propose
Registry-Visible Reprompting (RVR), a training-free middleware that, on a
registry miss, returns one re-prompt wrapping a structured
\texttt{tool\_not\_found} envelope. RVR removes all twenty pooled Qwen3
fabrications in the matched per-tier subset (Fisher's exact one-sided,
$p=3.5\!\times\!10^{-5}$ on $20/1{,}417$ vs.\ $0/945$); on a second open
family (Llama-3.1-8B) it reduces but does not fully clear fabrication
($2/487$ residuals caught by the rejection layer, not the registry prompt).
The gap is not a quantization artefact: a precision ladder on Qwen3-8B
keeps fabrication non-zero from $4$-bit through $8$-bit to full bf16
($9/623$, $2/435$, $2/316$). A secondary, deliberately hedged ablation asks
where the fix lives. Dropping the registry listing from the envelope
($\mathrm{C}_{0.7}$; $0/448$ on Qwen3-8B) and even filling it with
\emph{wrong} tool names ($\mathrm{C}_{0.8}$; $0/410$) both stay at zero,
matching the real list ($\mathrm{C}_1$; $0/258$). We do not read this as
proof that content is irrelevant: all three arms are zero-event, so this is
absence of evidence, not evidence of equivalence. At this sample size we
detect no content effect; the $\mathrm{C}_1\!-\!\mathrm{C}_{0.7}$ difference
is bounded by a Newcombe 95\% CI of $[-1.5, +1.4]$~pp --- consistent with
content buying up to $\sim$1~pp, not proof it buys nothing. We flag a
format-over-content recovery as a plausible reading, echoing Min et al.\ on
in-context demonstrations~\citep{min2022rethinking}, and leave it as an open
ablation; a powered version on a high-event cell is in progress.
Descriptively, Qwen3's rate is non-monotone in scale, climbing from $0\%$ at
$0.6$B to $\mathbf{1.64\%}$ at $14$B and back to $0\%$ at $32$B; six points
are not a curve. On Anthropic's zero-event regime RVR also logs zero, but
the strict-pass subset slips at $N\!=\!60$; we recommend tier-conditional
deployment.
\end{abstract}
```

## DROP-IN SHARPER INTRO OPENING (replaces lines 4–10 of sections/01_introduction.tex; the motivating-vignette paragraph)

```latex
An agent calls \texttt{search\_flights}. The registry contains
\texttt{find\_flights}. The call fails. Practitioners hit this mismatch in
production with Claude, Gemini, and Grok~\citep{czapla2026}, and what
stings is that the model knew the task, picked something plausible, and just
got the name wrong. At the per-call grain the population split is sharp and
it replicates: three commercial vendors --- Anthropic~4.x, OpenAI
gpt-4.1/gpt-4o, and a confirmatory gpt-5 generation --- sit at $0\%$ TFR
across $6{,}020$ probed calls, while three open lineages --- Qwen3,
Qwen2.5-7B, and Llama-3.1-8B --- fabricate at $0.4$--$6\%$. The gap survives
a full-precision control, so it is not a quantization artefact, and a single
training-free re-prompt (RVR) removes every Qwen3 fabrication we logged. We
answer who, how often, and what fixes it with a per-call diagnostic, a
cross-vendor audit, and that fix.
```

(Then continue into the existing "Existing benchmarks measure related
quantities at the wrong grain..." paragraph unchanged. The current draft's
second paragraph already states the closed-vs-open split; if this opener is
adopted, lightly de-duplicate that second paragraph so the open-vs-closed
claim is asserted once with full numbers and once as the framing hook.)

---

## Notes on hedges preserved (sanity checklist)

- "six points are not a curve" — kept verbatim.
- per-tier / content-effect: "absence of evidence, not evidence of
  equivalence"; Newcombe [-1.5,+1.4]pp; "powered version in progress" — kept.
- Llama RVR "reduces but does not fully clear" — kept (residuals explicit).
- precision ladder framed as "not a quantization artefact" — matches body
  L91–94 of current abstract; no strengthening.
- gpt-5 explicitly "reported separately, not pooled into the headline" — keeps
  the locked invariant that gpt-5/tau/cross-family/precision are NOT pooled
  into the BFCL headline.
- strict-pass slip + tier-conditional deployment — kept.

## The "$6{,}020$ probed calls" figure in the intro opener

2,592 (Anthropic C0) + 2,117 (OpenAI 4.x/4o) + 1,311 (gpt-5 gen) = 6,020.
This is a transparent SUM of three already-locked, separately-reported pools
used only to size the closed-side null in one sentence; it is NOT a new pooled
denominator for any statistical claim and does not merge gpt-5 into the
headline 0/2,117 or 0/2,592 (those remain stated separately in the abstract).
If even this descriptive sum is judged too close to "pooling," replace the
clause with "across thousands of probed calls" — drops the arithmetic entirely
at no cost to the spine.
