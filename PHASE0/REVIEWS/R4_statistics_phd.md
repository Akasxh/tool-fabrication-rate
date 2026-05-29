# Statistics PhD Reviewer — Final Statistical Audit

## Verdict
**OVERSTATED** (in the headline) and simultaneously **INCONSISTENT** (between the headline "TEHR=0/1571" framing and the per-cell evidence the data actually support). The numerical work that is reported is largely correct; what is missing is the upper-bound machinery that any zero-event paper *must* carry.

## Top-5 statistical defects (severity-tagged)

1. **[CRITICAL] No rule-of-three / Clopper–Pearson upper bound for any zero-event cell.**
   With $X = 0$ events in $N$ Bernoulli trials, the exact one-sided 95% Clopper–Pearson upper bound is
   $\;p_U = 1 - 0.05^{1/N}\;$, which is well-approximated by the rule of three $p_U \approx 3/N$ (Hanley & Lippman-Hand, *JAMA* 1983; Jovanovic & Levy, *Am. Stat.* 1997). For the headline pool $N=1{,}571$, $p_U \approx 3/1571 = 0.00191$ (0.19%). Per-cell:

   | cell | $N$ (calls) | rule-of-3 UB | Clopper–Pearson 95% UB |
   | --- | --- | --- | --- |
   | Sonnet × `multi_turn_long_context` | 81 | 3.70% | 3.65% |
   | Sonnet × `multi_turn_miss_func` | 171 | 1.75% | 1.74% |
   | Sonnet × `multi_turn_base` | 193 | 1.55% | 1.54% |
   | per-distractor pooled cell | 261–277 | 1.08–1.15% | 1.07–1.14% |
   | regime pool | 445 | 0.67% | 0.67% |
   | full headline pool | 1,571 | 0.19% | 0.19% |

   **None of these appear in the paper.** Tables 1–3 show "$0.0\%\;(N{=}\dots)$" with no UB. The claim "TEHR is at or near zero" is therefore literally a statement about the *point estimate* alone — a stronger but unstated claim that the rate is bounded above by ${\le}3.7\%$ in the worst cell and ${\le}0.19\%$ in the pool would actually be defensible. Rewrite the headline to carry the bound.

2. **[CRITICAL] The Friedman test on all-zero data is degenerate, not a result.**
   With $\mathrm{TEHR}_{ij}=0$ for all task $i$ and distractor type $j$, every per-task rank is tied at the average rank $(k+1)/2 = 2.5$ across the four columns. The Friedman statistic
   $\chi^2_F = \frac{12}{nk(k+1)}\sum_j R_j^2 - 3n(k{+}1)$
   is identically $0$ by construction; $p = 1$ by construction. Reporting "$\chi^2 \approx 0,\, p \approx 1.0$" as evidence "consistent with M-Constrain" is a cargo-cult inference: the test had nothing to test. Either drop the omnibus from the body and footnote it, or re-cast it explicitly as "test is undefined under all-tied data; therefore neither M-Constrain support nor M-Retrieve refutation can be drawn." §6.2 partially admits this in the "alternative interpretation" paragraph, but the headline still treats the result as falsifying M-Retrieve and M-Metacog. **It does not.** Both predictions become *unevaluable*, not *unsupported*.

3. **[CRITICAL] Post-hoc power < 0.20 is computed wrong (and shouldn't be computed at all).**
   Hoenig & Heisey (*Am. Stat.* 2001) show that *observed-power* calculations are monotone in the observed $p$-value and contain no information beyond it. The paper's "post-hoc power $<0.20$" is therefore both methodologically inadmissible and almost certainly underestimating the *prospective* power that the pre-registration nominally targets. For McNemar at $\alpha=0.05$ with $b{+}c$ discordant pairs and proportion-of-discordant-positive $\pi$, the standard normal approximation gives power
   $\;1-\beta = \Phi\!\left(\sqrt{(b{+}c)}\,|2\pi-1| - z_{1-\alpha/2}\right)\;$.
   For $b{+}c = 15$ paired tasks per cell and a 20-pp $\Delta\mathrm{Pass}$ (the paper's pre-registered MDE, not 5-pp), $|2\pi-1|=0.20$ gives power $\approx \Phi(0.775 - 1.96) \approx 0.12$ — so the cell-wise *prospective* number is consistent with the paper's "<0.20" but for a different effect size than claimed. For the registered 5-pp pairwise probe, the prospective power on $N=15$ paired tasks is on the order of $0.06$, i.e. essentially the type-I rate — meaning the probe was *never* powered to detect M-Retrieve / M-Metacog under the pre-registered MDE. **The paper should state prospective power ex ante, not post-hoc, and should explicitly state the MDE rather than the misleading "<0.20" summary.**

4. **[HIGH] Cluster-effective $N$, not call count, is the headline denominator.**
   The paper's framing "$1{,}571$ parsed tool calls" is a genuine call-count but is *not* the inferential $N$. With clustering by task, the design-effect-adjusted effective sample size is $N_{\mathrm{eff}} = N_{\mathrm{calls}}/\mathrm{DEFF}$ where $\mathrm{DEFF} = 1 + (\bar{m}-1)\rho$ and $\bar{m}$ is mean calls/task. With $\bar{m} \approx 1571/(\text{tasks}) \approx 1571/(\sim\!200) \approx 7.9$ and a plausible within-task ICC of $\rho \in [0.3, 0.6]$ for tool-name decisions (highly correlated within a single trace), $\mathrm{DEFF} \in [3.1, 5.1]$ and $N_{\mathrm{eff}} \in [310, 510]$, i.e. roughly the **cluster (task) count**, not the call count. The Clopper–Pearson UB on $N_{\mathrm{eff}} \approx 310$ is $\approx 0.96\%$, not the $0.19\%$ the call-count framing implies. The headline must use $N_{\mathrm{tasks}}$ or carry an explicit DEFF correction.

5. **[HIGH] System-failure exclusion is missing-not-at-random (MNAR), not justified.**
   §3.1 and pre-reg item 11 exclude timeout/refusal/parse-fail "from numerator and denominator." If refusal is *causally* triggered by registry mismatch — exactly the failure mode TEHR is meant to capture — the exclusion deflates TEHR by removing the events where the agent *almost* hallucinated but caught itself. This is a textbook MNAR mechanism (Little & Rubin 2002, ch. 1). The defensible move is a **stratified report**: TEHR among completions, refusal-rate, and a worst-case "TEHR + refusals attributable to mismatch" upper envelope. Currently we have only the most-favorable-to-the-claim version.

## Required fixes before acceptance

- **Add Clopper–Pearson upper bounds to every "0.0%" cell in Tables 1–3** and in the §7 summary; in particular, attach the rule-of-three bound to the $1{,}571$-call headline ($\le 0.19\%$ at 95%) and to the worst-cell bound ($\le 3.7\%$ on Sonnet × `multi_turn_long_context`, $N=81$).
- **Replace the per-call $N$ with a cluster-effective $N$** in any displayed CI; equivalently, report task counts alongside call counts in every table caption.
- **Drop Friedman from the §5/§6 body** or relabel it explicitly as "undefined under all-ties; reported for completeness." Move the verdict mapping (§6.2) to "all three mechanism hypotheses are unevaluable in this regime," because a test that cannot fire cannot adjudicate any of them.
- **Replace post-hoc power with prospective power** at the pre-registered MDE (5-pp), with the formula and the per-cell pair count made explicit. State that the probe was *under-powered by design at this $N$* for the M-Retrieve / M-Metacog 5-pp prediction.
- **Remove TOST from the body.** §3.4 pre-registers TOST at 5-pp on the strict $\mathrm{C}_0$-failed-with-TEHR subset. That subset is empty. The procedure has nothing to compute on. Mention it once in the limitations and excise it from §4.3.
- **Justify or stratify the system-failure exclusion.** A one-paragraph addition reporting refusal rate and a worst-case "MNAR-adjusted TEHR upper envelope" suffices.
- **Drop "discordance pooled across tiers before the test"** unless conditional independence of discordance counts across tiers is justified. With $b+c = 0$ in the pooled cell anyway, the entire test is moot — but the methodology section should not advertise a procedure that is statistically only valid under an unjustified assumption.

## What the headline SHOULD say (one sentence)

> Across $\sim\!200$ BFCL multi-turn tasks (1,571 parsed tool calls clustered within tasks) on Anthropic Sonnet 4.6 and Haiku 4.5, we observed zero tool-existence hallucinations under the opaque baseline; the exact one-sided 95% upper bound on per-call TEHR is $0.19\%$ in the pool and at most $3.7\%$ in the smallest cell ($N{=}81$) — sufficient to bound the rate, **not** to claim mechanistic null-effects on the $N{=}15$-per-cell distractor probe, which was prospectively under-powered for the pre-registered 5-pp pairwise contrast.

## What's secretly fine (be fair)

- **Per-call denominator with task-level clustering** (§3.1) is the right design choice; many TEHR-style papers conflate trace verbosity with rate.
- **Pre-registration of the asymmetric-falsifiability protocol** (§3.4) is genuinely well-designed: distinguishing "non-rejection" from "support" via a power threshold is the correct epistemics, even though the *execution* of it via post-hoc power is wrong.
- **Reporting a dual gap-closure ratio** (restricted causal-attribution vs. unrestricted descriptive, pre-reg item 14) is unusually disciplined and should be kept.
- **The distinction between $\mathrm{C}_{0.5}$, $\mathrm{C}_{0.7}$, $\mathrm{C}_1$** isolates retry-with-content from retry-without-content from idealized-structured-error, which is exactly the contrast a reviewer would demand. This is good experimental design even if the data are silent on it.
- **The §5.4 "implication for RVR" paragraph** is honest about the empty subset; the harness-release framing is the appropriate move when the regime didn't fire.
- **BCa cluster-bootstrap with 10,000 resamples** at the task level (pre-reg item 9) is the right CI method for non-i.i.d. per-call observations; the criticism is that the CI is missing for zero-event cells, *not* that the method is wrong.

---

*Reviewer signature: Statistics PhD, biostatistics group. Recommendation: major revision conditional on the rule-of-three / cluster-effective-$N$ fixes; the underlying empirical observation (TEHR is small under these regimes) survives, but the framing currently overstates the precision of that observation by roughly an order of magnitude.*
