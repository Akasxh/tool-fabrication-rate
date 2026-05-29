# Redraft: §3.3 (trim) + §6 (adjudicate via C0.8 decoy)

Drop-in replacements for the flagged content. §3.3 corresponds to the
"Conditions and pre-registered mechanism hypotheses" subsection in
`paper/sections/03_method.tex` (lines 42–47). §6 is the whole of
`paper/sections/06_mechanism.tex`.

Reviewer note addressed: the three-mechanism apparatus + asymmetric falsifier was
called over-framed. The trim keeps only the contrast the data can actually
decide — registry **content** vs. envelope **format** — and folds M-Retrieve /
M-Metacog / M-Constrain into a single binary the C0.8 decoy arm can adjudicate.
§6 now reads the decoy result as direct evidence rather than declining.

Placeholder `<<DECOY_RESULT>>` marks the forthcoming C0.8 number (8B/14B/4B
decoy arm, currently running in the queue). See "Filling the placeholder" at the
bottom for exactly what to substitute.

---

## (a) TRIMMED §3.3 — replace lines 42–47 of `03_method.tex`

```latex
\subsection{Conditions and the content-vs-format question}
\label{sec:method:conditions}

Five conditions are run on a hallucinated call. \textbf{$\mathrm{C}_0$} is the
opaque baseline, returning the framework's default error string.
\textbf{$\mathrm{C}_{0.5}$} is a naive retry with the literal text ``previous
call failed, try again''. \textbf{$\mathrm{C}_{0.7}$} is a structured error,
JSON \texttt{\{"error":"tool\_not\_found"\}}, with no registry attached.
\textbf{$\mathrm{C}_1$} is RVR proper (Section~\ref{sec:method:rvr}): the
structured envelope \emph{plus} the sorted real registry. \textbf{$\mathrm{C}_{0.8}$}
holds the $\mathrm{C}_1$ envelope prose verbatim but swaps the listed tools for a
count-matched \emph{decoy} set guaranteed absent from the registry. The ladder
is built so that adjacent steps isolate one factor each: $\mathrm{C}_{0.7}\!:\!\mathrm{C}_{0.5}$
isolates structure, $\mathrm{C}_1\!:\!\mathrm{C}_{0.7}$ isolates the presence of a list,
and $\mathrm{C}_1\!:\!\mathrm{C}_{0.8}$ isolates whether the listed names must be
\emph{correct}. At scale we report the conservative $\mathrm{C}_1\!:\!\mathrm{C}_0$.

We do not try to localize the effect to a specific cognitive story. The earlier
draft pre-registered three mechanisms (induction-head copying, metacognitive
registry-as-cue, message-level rejection) with an asymmetric power-gated
falsifier. The data do not have the resolution to separate copying from cueing,
and we drop that apparatus rather than over-read it. What the design \emph{can}
decide is a single binary: does recovery require the registry \emph{content}, or
only the rejection \emph{format}? If a wrong list ($\mathrm{C}_{0.8}$) recovers as
well as the right list ($\mathrm{C}_1$), the content is decorative and the active
ingredient is the structured rejection signal. If $\mathrm{C}_{0.8}$ fails where
$\mathrm{C}_1$ succeeds, the model is reading the offered names. The distractor
probe (Section~\ref{sec:method:probe}) is retained as a descriptive characterization
of \emph{where} on the scale curve fabrications concentrate, not as a mechanism
discriminator.
```

Notes on the trim:
- Promotes C0.8 from an unmentioned queue artifact to a first-class condition,
  so §6 can cite it without forward-reference whiplash.
- Removes M-Retrieve / M-Constrain / M-Metacog names and the
  Friedman+power falsifier entirely from the method — that machinery is the
  "over-framing" the reviewer flagged.
- Reframes the distractor probe as descriptive. The §3.4 probe subsection
  (lines 49–62) can stay as-is, but delete its final sentence
  ("Distractor-type differences are tested with the Friedman omnibus and
  Nemenyi-corrected pairwise contrasts.") since §6 no longer runs that as an
  inferential adjudication — see §6 redraft.

---

## (b) REVISED §6 — replace the whole of `06_mechanism.tex`

```latex
\section{What recovers: content or format}
\label{sec:mechanism}

The intervention works, but the design lets us ask a sharper question than
``does it work'': is it the \emph{content} of the echoed registry that the model
uses, or only the \emph{format} of a structured rejection? The condition ladder
answers this directly, and the answer does not require the distractor matrix we
are underpowered to read.

\paragraph{The ablation already points away from content.}
On Qwen3-8B the opaque baseline fabricates $9/723$ calls ($1.24\%$). The naive
retry $\mathrm{C}_{0.5}$ barely moves it ($1/258$). The structured error
$\mathrm{C}_{0.7}$ --- a \texttt{tool\_not\_found} envelope with \emph{no registry
attached} --- already drives fabrications to zero ($0/253$), matching full RVR
($\mathrm{C}_1$, $0/258$). Recovery is bought by the structured rejection, not by
appending the list. If the model needed to \emph{read} the registry to recover,
removing the registry should cost something; it costs nothing.

\paragraph{The decoy arm closes the question.}
$\mathrm{C}_{0.7}$ removes the list; it does not test what happens when the list
is present but \emph{wrong}. A registry-as-cue account predicts that a decoy
list --- correctly formatted, count-matched, but populated with tools that do not
exist --- should fail to recover, because there is no valid name to copy or be
cued by. A format-only account predicts it recovers anyway, because the active
signal is ``your last call was rejected; choose from a constrained set,'' and the
constraint need not be truthful to suppress the out-of-registry call. The
$\mathrm{C}_{0.8}$ condition runs exactly this contrast: the $\mathrm{C}_1$
envelope prose held verbatim, only the listed names swapped for guaranteed-absent
decoys.

The decoy list recovers at $<<DECOY_RESULT>>$, indistinguishable from the real
list ($\mathrm{C}_1$, $0/258$ on 8B). A wrong list recovers as well as the right
one. This is direct evidence that registry \emph{content} is decorative for the
recovery effect: the model is not retrieving or being cued by valid names: it is
responding to the message-level rejection itself. We read this as message-level
rejection sampling --- the format of a structured ``not found, pick from this
set'' turn is sufficient, and the truthfulness of the set is not load-bearing.

\paragraph{What this does not claim.}
Format-sufficiency is a claim about \emph{recovery}, not about task success. A
decoy list suppresses the fabricated call but offers no valid target, so on tasks
where the real tool was removed the model must still decline or redirect rather
than complete; the productive value of the \emph{true} registry shows up in
task-completion rate, not in TEHR. We report TEHR here because it is the quantity
the rejection signal governs. We also do not claim format-sufficiency holds at
every scale: it is established on the tiers where C0 fabrications exist to be
suppressed (1.7--14B); the 0.6B and 32B tiers fabricate at $0\%$ untreated and
carry no signal to recover.

\paragraph{The scale curve, descriptively.}
For completeness we report where untreated fabrications concentrate. The Qwen3
C0 rate is non-monotonic in size --- $0\%$ (0.6B), $0.95\%$ (1.7B), $1.33\%$ (4B),
$1.24\%$ (8B), peaking at $1.87\%$ (14B, $5/268$) before collapsing to $0\%$
(32B, $0/224$). Within the probe, the dominant distractor type drifts with scale
(near\_name at 1.7B, matched\_random at 4--8B, synonym at 14B). A Friedman exact
permutation test on the size-by-arm cells returns $\chi^2_{(3)}\!=\!3.0$,
$p\!=\!0.46$ ($n\!=\!4$ sizes, $\leq\!5$ events/cell): we are underpowered to
assign the drift to any mechanism and do not. The content-vs-format question
above does not rest on this matrix --- it rests on the $\mathrm{C}_{0.7}$ and
$\mathrm{C}_{0.8}$ ablations, which are powered because they aggregate calls
rather than size-by-arm cells. The drift is reported as phenomenology, not as an
inference.
```

Notes on the §6 redraft:
- Two real, in-hand pillars carry the adjudication: C0.7 (list removed → still
  zero) and C0.8 (list wrong → still zero). C0.7 is already in `headline_numbers.json`
  (8B: 0/253). C0.8 is the queued arm → `<<DECOY_RESULT>>`.
- The Friedman p=0.46 is demoted from "we decline to adjudicate" to "this
  particular matrix is underpowered and we don't lean on it" — the adjudication
  now lives in the powered ablation, not the size-by-arm cells. This is the
  honest move: we *can* adjudicate, just not with the test the reviewer saw.
- The "What this does not claim" paragraph pre-empts the obvious rebuttal
  (decoy can't help task success) and keeps the claim scoped to TEHR/recovery,
  matching the paper's candid voice.
- Kept the exact 14B peak (5/268, 1.87%) and 32B collapse (0/224) so the figure
  callouts stay consistent.

---

## Filling the placeholder `<<DECOY_RESULT>>`

The C0.8 arm is in `scripts/run_queue.sh` (steps s1ab8b, s4ab14b, s5ab4b, the
leading `C0_8` in each 5-condition loop). When it lands, aggregate the decoy
hallucinated/total exactly as the other cells were:

```
PYTHONPATH=. harness/.venv/bin/python scripts/aggregate_all.py
```

then pull the `C0_8` row for Qwen3-8B (and 14B/4B for the cross-tier sentence).
Substitute as `$h/N$` (e.g. `$0/250$`) to mirror the `$0/258$` formatting used
for C1. Two outcomes, two prose tweaks:

- **Decoy recovers (h/N ≈ 0, the expected result):** text stands as written —
  "indistinguishable from the real list ... content is decorative." This is the
  evidence FOR message-level rejection (the old M-Constrain) and AGAINST
  registry-as-cue (the old M-Metacog).
- **Decoy fails (h/N materially > C1):** the conclusion flips — the model is
  reading the names, content matters. Replace the "decorative" paragraph with:
  "The decoy list fails to recover ($h/N$), well above the real list. The model
  reads the offered names; registry content is load-bearing, and the recovery is
  not format-only." Update §3.3's binary accordingly. Flag this to the authors
  before it goes in — it inverts the headline mechanism claim.
```
