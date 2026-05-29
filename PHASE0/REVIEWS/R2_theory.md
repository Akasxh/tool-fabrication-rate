# R2 — Theory Review (Mechanism / First-Principles)

**Reviewer voice**: ML theorist, Bayesian / information-theoretic / learning-theoretic priors. Read PAPER_PLAN_v3.1, ADDENDUM_R1, §3 method, §4 setup, prior_art.md.

---

## Verdict
**Weak Accept conditional on mechanism formalization.** The empirical scaffolding is strong; the theoretical scaffolding is decorative. Three specific gaps must be closed for the paper to read as a mechanism contribution rather than a renamed-metric + retry-trick paper. None require new experiments — they require explicit assumptions and a 0.5-page mechanism paragraph in §3.

## Top-5 Concerns

1. **§3.2(i) handwaves the active mechanism.** "Exploits the autoregressive prior so the next sampled name is conditioned on the correct vocabulary" is a slogan, not a mechanism. There are at least three competing hypotheses (retrieval prior, message-level constrained-decoding analog, metacognitive self-correction prior) and they make *different falsifiable predictions* about §6 probe outcomes. The paper does not commit.
2. **The cost-quality-gap framing presupposes the gap is hallucination-bounded.** Pass-rate gaps between Haiku and Sonnet plausibly arise from argument-validity errors, plan-step errors, refusal drift, or context-length brittleness. The "gap-closure ratio" attributes 100% of any closure to TEHR mechanisms; this is a structural confound, not a statistical one.
3. **Per-call denominator's i.i.d.-Bernoulli generative assumption is unstated and almost certainly false.** Tool calls within a trace are conditionally dependent on prior calls (e.g., a hallucinated `get_user` corrupts subsequent `update_user` plans). The "cleaner asymptotics" claim in §3.1 needs either an explicit conditional-Bernoulli model or a downscope to "less length-confounded" rather than "cleaner."
4. **§3.2(iv) claims RVR is a constrained-decoding analog without engaging the obvious objection.** Token-level grammar-constrained decoding (Outlines, llama.cpp BNF, JSON-mode) strictly dominates message-level rejection sampling in expected-token-cost terms; why would anyone use RVR if logit access were available? The paper should own the trade-off: RVR is a *no-logit-access approximation* with strictly worse sample efficiency, justified only by closed-API constraints.
5. **The non-inferiority claim has no theoretical bound on the degradation channel.** TOST at 5pp is a statistical decision rule, not a mechanism. There exist plausible mechanisms by which RVR *should* degrade C0-passing tasks (registry-list as in-context distractor; over-conservative re-prompting on near-pass calls). The paper should at minimum enumerate them in §3 and predict their direction.

## Specific Concerns

### S1. Formalize the RVR mechanism (§3.2(i)).

Three candidate mechanisms — pick one or argue the §6 probe disambiguates them:

- **(M-Retrieve)** *In-context retrieval prior.* Conditional on $\mathcal{R}$ being in the recent context window, the next-token distribution $p(c_{\text{name}} \mid \text{ctx}, \mathcal{R}\subset\text{ctx})$ concentrates on names in $\mathcal{R}$ via copy / induction-head behavior. Predicts: RVR's gain *increases* with registry length up to a saturation point set by attention bandwidth.
- **(M-Constrain)** *Message-level rejection-sampling analog.* RVR is equivalent to a 1-bit acceptance gate on the message-level proposal distribution: $q_{\text{RVR}}(c) \propto p_\theta(c \mid \text{ctx}) \cdot \mathbb{1}[c.\text{name}\in\mathcal{R}]$. The "1-bit" is the membership oracle. Predicts: RVR's effect is *bounded by* the original support overlap $\Pr_{p_\theta}[c.\text{name}\in\mathcal{R}]$.
- **(M-Metacog)** *Self-correction prior.* The model updates its task representation upon being told the registry was specified. Predicts: RVR works even when $\mathcal{R}$ is *paraphrased* or *truncated* in the re-prompt; (M-Retrieve) and (M-Constrain) predict it fails.

The §6 probe arms partially disambiguate: a near-name distractor failure under C0 + recovery under C1 favors (M-Constrain) (the constraint resolves the near-collision); recovery driven primarily by description-text copying favors (M-Metacog). The paper should *pre-register a mechanism interpretation* of §6 outcomes, not just report distractor effect sizes.

### S2. Cost-quality-gap closure: decompose or downscope.

The headline ratio $[\text{Pass}(\text{small}+C_1) - \text{Pass}(\text{small}+C_0)] / [\text{Pass}(\text{frontier}+C_0) - \text{Pass}(\text{small}+C_0)]$ silently equates the numerator-mechanism (TEHR-recovery) with the denominator-mechanism (whatever drives Sonnet > Haiku). Either:

- (a) **Decompose** the denominator into hallucination-attributable vs argument-attributable vs plan-attributable failure modes, and report a within-category gap-closure ratio. The strict $C_0$-failed-with-hallucination subset already gives this for free — it's the right population for the headline.
- (b) **Downscope** the claim to "RVR closes $X$pp of the small-tier hallucination-bounded failure rate" and treat the small/frontier comparison as secondary.

Option (b) is cheaper and probably stronger.

### S3. Per-call denominator: state the generative model.

§3.1 says per-call gives "cleaner asymptotics under varying trace lengths." The implicit model is i.i.d. Bernoulli per call — wrong, because (i) within-trace dependence (corrupted state propagates), (ii) registry-content dependence (first-call hallucinations are likely on rarer-tool tasks, biasing the denominator distribution). A defensible weakening: "per-call gives a length-invariant rate under exchangeability of within-trace calls; we do not claim per-call independence and report cluster-bootstrap CIs accordingly." This already aligns with ADDENDUM C.3 (cluster bootstrap by task) — make the alignment explicit in §3.

### S4. Constrained-decoding: own the inferior position.

§3.2(iv) should read: *"RVR is the message-level analog of token-level grammar-constrained decoding (Outlines~\citep{outlines}, GBNF, JSON-mode) when logit access is unavailable. Token-level approaches are strictly more sample-efficient — they zero out invalid prefixes during sampling rather than after — but require provider cooperation. RVR's contribution is the no-logit-access approximation with quantified overhead (<2% tokens, ≤1 retry)."* This frames RVR as honestly second-best in an environment where first-best is unavailable. Reviewers respect that.

### S5. Non-inferiority degradation channels.

Add to §3.2: *"RVR could degrade $C_0$-passing tasks via two mechanisms: (a) the registry list acts as an in-context distractor, and (b) the re-prompt fires on a near-pass that the agent would have self-corrected. We expect (a) to scale with $|\mathcal{R}|$ and (b) to be small under at-most-one retry."* TOST then tests for the *combined* magnitude. Without naming the channels, the test is unanchored.

### S6. §6 probe predictions, not just effect sizes.

The probe arms should map onto Bayesian priors:

- **Near-name** isolates BPE / induction-head proximity → effect predicted by token-level edit distance + shared subword count.
- **Synonym** isolates description-embedding overlap → effect predicted by cosine similarity of description encoder embeddings.
- **Random** is a passive control.
- **Matched-random** isolates the registry-size+1 information-theoretic confound: an extra entry adds $\log_2(|\mathcal{R}|+1) - \log_2|\mathcal{R}|$ bits of uncertainty to a uniform retrieval prior, which is asymptotically zero. Predict: matched-random ΔTEHR ≈ 0.

If matched-random ΔTEHR is non-zero, the model is not using a uniform retrieval prior — that's an interesting finding and should be stated as a pre-registered comparison.

## Required Changes

1. Add a 0.5-page §3.5 "Mechanism" paragraph naming (M-Retrieve / M-Constrain / M-Metacog) and pre-registering which §6 outcomes favor which.
2. Restrict the headline gap-closure ratio to the hallucination-bounded subpopulation (S2(b)); demote cross-mechanism gap-closure to secondary.
3. State the generative model behind the per-call denominator (S3); align explicitly with cluster-bootstrap.
4. Rewrite §3.2(iv) to position RVR as the no-logit-access analog of grammar-constrained decoding (S4).
5. Enumerate degradation channels in the non-inferiority discussion (S5).
6. Pre-register matched-random ΔTEHR ≈ 0 as the null prediction (S6).

## Strongest Aspect
ADDENDUM B.3's matched-random distractor arm is the single most theoretically defensible move in the paper — it isolates a confound (registry-size+1) that would otherwise contaminate every probe interpretation. Keep it; foreground it.

## Weakest Aspect
The mechanism story for *why RVR works*. As written, §3.2 reads as a sequence of design choices justified by analogy. A reviewer hostile to "agent prompt engineering as research" can dismiss the paper on this paragraph alone. A 0.5-page formalization defuses that attack at zero experimental cost.

## Justification
The empirical design is solid post-ADDENDUM (BCa cluster bootstrap, McNemar pooling, Friedman, matched-random control). The theoretical layer is thinner than the empirical layer — atypical for ML workshop papers, where the inverse is usually true. Closing this asymmetry is cheap (writing only) and disproportionately strengthens the paper against mechanism-skeptical reviewers.

---

**Top-3 mechanism gaps + formalization moves** (for caller):

1. **No committed mechanism for RVR.** Move: pre-register M-Retrieve / M-Constrain / M-Metacog and tie each to a §6 probe outcome.
2. **Gap-closure attributes all small→frontier improvement to TEHR.** Move: restrict headline to hallucination-bounded subset; treat unrestricted gap-closure as secondary.
3. **Per-call denominator's generative model is unstated; "constrained-decoding analog" is unowned.** Move: state exchangeability (not i.i.d.) for per-call; explicitly position RVR as the no-logit-access approximation of token-level grammar-constrained decoding.

Word count: ~970.
