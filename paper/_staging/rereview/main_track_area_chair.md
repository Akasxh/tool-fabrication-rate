# Review — Main-Track ICML Area Chair (significance / novelty / breadth gate)

Persona: senior AC, main technical track. Default REJECT; the paper earns each point.
Bar: does this change what the field believes, across the model zoo and benchmark suite,
in a way no reviewer can dismiss as "one measurement on one harness."

---

## Findings (DIMENSION | MAIN-TRACK BAR | CURRENT GAP | WHAT CLOSES IT)

**SIGNIFICANCE | A null that changes deployment behavior must be a robust null, and a fix
that beats baselines must move a number reviewers care about.** | The entire positive
result rests on 14 prevented events (`tab:rvr-validation`, 14/973 vs 0/945). That is the
*matched-subset* count, smaller than the ~19-event full-probe pool (`tab:qwen3-scale`:
1.7B 2 + 4B 3 + 8B 9 + 14B 5 = 19). The headline fix is "prevent 14 of 14" where 14 is an
event count, not a rate the field tracks, and the strongest per-tier Fisher is p=0.032
(`05_results.tex:226`), below the bar individually. TFR also ignores task success, so
"format-not-content recovery" suppresses the fabricated call but, by the paper's own
admission (`06_mechanism.tex:39-46`), leaves task completion untouched and unmeasured — the
quantity a deployer optimizes is absent. | A second benchmark showing the same RVR delta on
a *non-zero* base, OR a task-success metric demonstrating the envelope doesn't just silence
the call but lets the agent recover. As-is the positive contribution is an n=14 anecdote.

**ROBUSTNESS | The title's phenomenon (non-monotone Qwen3 curve) must survive its own
confounds before it goes in the title.** | The 14B peak is 5/268=1.87% with a CP bound the
authors concede overlaps the 32B "collapse" (`05_results.tex:104-106`: "read as not-detected
at this N"). Six points, one family, one quantization (4-bit MLX). The quantization control
is still NUMBERS_TODO (`A1_appendix.tex:150`). The data is *internally inconsistent*:
`05_results.tex:38` carries a live `NUMBERS_TODO` admitting the 5/258=1.94% miss_func cell is
"absent from the aggregator" and must be reconciled against 9/615; the RVR-validation 8B C0
cell (4/269) contradicts the scaling-table 8B cell (9/615) and is hand-waved in the caption.
A title-level scaling claim cannot ship on a curve whose own cells don't reconcile. | The
bf16/8-bit cells must land AND the miss_func cell must be reconciled. Even then six points is
descriptive, not a scaling phenomenon.

**NOVELTY | Per-call TFR and RVR must each clear named prior art.** | TFR is honestly
positioned (`02_related_work.tex:31-63`, `tab:priorart`) as MetaTool's per-query premise moved
to per-call multi-turn — a re-slicing of the denominator, useful but incremental. RVR is
explicitly "a registry-membership-specialized instance of [CRITIC]" (`02_related_work.tex:75`)
and LangChain already ships structured tool-not-found feedback (`02_related_work.tex:80-84`).
The genuinely new bit is the C0.7/C0.8 content-vs-format ablation — but that conclusion ("a
single structured rejection re-grounds the model") is established on *zero events* (0/448,
0/410, 0/258 all-zero arms). You cannot demonstrate that wrong content recovers "as well as"
right content when neither arm produced a single failure to recover from; this is absence of
signal, not evidence of equivalence. The Min-et-al. analogy (`abstract`, `01_introduction.tex:15`)
is rhetorical dressing on three all-zero columns. | Run the ablation on a tier/benchmark where
C0 produces enough events that C0.7-vs-C0.8 is a *powered* contrast.

**BREADTH | Two-population-one-benchmark is workshop scope.** | Anthropic 4.x + Qwen3 4-bit +
OpenAI (all 0%) is breadth in *vendors* but the only non-zero signal lives in one open family
at one quantization on BFCL alone. tau-bench is in `_staging` (`tau_bench_report.md`) but not
in the paper; the six-model cross-family release (`04_setup.tex:11-14`) is "supplementary,"
not evaluated in-body. The OpenAI rows add 0/2070 more zeros — they widen the null, they do
not add a second site where the phenomenon or the fix is observable. | One second benchmark
(tau-bench / ToolSandbox) carrying a non-zero TFR that RVR then reduces.

**PORTABILITY | The contribution must not be fused to this harness's existence check.** | RVR
is an O(1) set-membership test plus a re-prompt string (`03_method.tex:18-26`); the finding
lives in the harness's tool-existence check and the BFCL loaders. Portable in principle, but
unproven outside BFCL multi-turn, and the "envelope is what matters" claim is harness-specific
until shown on a second tool format. | A demonstration on a non-BFCL tool schema.

---

## Verdict

(a) **Significance: LOW** at the main-track bar. The null is wide (commercial 0/N tells us
0% is *easy*, not that it is non-trivial), and the positive result is 14 events with one
sub-0.05 per-tier test. The most interesting claim (format-not-content) is built on all-zero
columns and is logically an equivalence-from-no-data.

(b) **Verdict: REJECT. WORKSHOP-ONLY as it stands.** This is a clean, honest, well-instrumented
audit — a strong workshop paper (consistent with the prior ~18% main-track / clear-workshop
panel read). It does not change what the field believes across the zoo and suite.

(c) **Single highest-leverage add:** a *second benchmark with a non-zero base TFR* on which
RVR (and the C0.7/C0.8 ablation) is a *powered* contrast. That single add converts the entire
spine from "n=14 on one harness" to a portable phenomenon + fix, and is what flips workshop→main.
The in-flight quantization control and event-multiplication help robustness but do NOT add a
second site; they cannot flip the breadth gate alone.

(d) **Is the Qwen 14B peak safe to headline? NO.** Overlapping CI with the 32B endpoint
(`05_results.tex:104`), six points, one family, one quantization (control still TODO), and a
live unreconciled-cell `NUMBERS_TODO` in the curve's own data. Demote to a descriptive figure
until quantization control lands and the miss_func cell reconciles.

---

## Projection if in-flight experiments land as expected

In-flight: bf16/8-bit quant control, A2 reflection baseline (prelim 2/30 → reflection alone
doesn't help), gpt-5 frontier rows, N>=100 event-multiplication on 14B/8B.

- Quant control breaking the 4-bit confound → addresses the *robustness* finding; lets the
  curve be a capability effect not a compression artifact. Real, but it is a defensive fix.
- N>=100 event-multiplication → if it turns ~14 events into ~40-60 and the per-tier Fishers
  go individually significant, the RVR result stops being an anecdote. This is the single most
  valuable in-flight item.
- A2 reflection (2/30) → isolates "is RVR just reflection," a genuine reviewer objection;
  strengthens novelty modestly.
- gpt-5 rows → more zeros; widen the null, add nothing to the positive story.

Even all-landing, the breadth gate (one benchmark, one non-zero family) is untouched and the
format-not-content claim still rests on all-zero ablation columns unless the event-multiplied
runs are where C0.7/C0.8 are re-run. So in-flight success moves this from a low-end workshop
paper to a **strong workshop / borderline-main** paper, not a clear main-track accept. It
remains WEAK_REJECT at the main-track bar absent the second benchmark.

**Score now: 3/10. Accept prob now ~7%. Accept prob if in-flight lands as expected ~16%.**
