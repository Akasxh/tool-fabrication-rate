# Poster Outline — Who Hallucinates Tools, How Often, and What Fixes It

**Venue:** SCALE @ ICML 2026 (Accept-Poster). **Poster session:** June 21.
**Board:** 31" H x 24" W, **portrait**. **Reviews:** 8 / 6 / 3.

Design intent: one finding, two regimes. Vertical portrait flow — title at
top, then a left-to-right reading order within each horizontal band, top to
bottom. All numbers below are locked and verified against
`scripts/aggregate_all.py`; do not alter. Honest voice — "bound vs estimate
is the finding," six points are not a curve, ablation is hedged.

Suggested grid: a single full-width title band, then **three horizontal bands**
of two columns each (the body), then a full-width takeaways footer. Roughly
3:1 figure-to-text per panel. Keep total panel count to 8 so 24" of width is
not overcrowded.

---

## BAND 0 — Title strip (full width, top ~5" of the 31" height)

- **Title:** Who Hallucinates Tools, How Often, and What Fixes It: A Per-Call
  Study Across Anthropic 4.x and Qwen3
- **Authors:** S Akash, Shine Gupta — Indian Institute of Technology Patna,
  India. Corresponding: drakathakash@gmail.com
- **One-line hook (sub-title band):** "Commercial frontiers log ~0 tool
  fabrication; open-weight families fabricate at ~0.4–6%. A training-free
  middleware (RVR) removes every fabrication we logged."
- Optional small QR to the anonymized harness repo (153 unit tests; total API
  spend $82; Qwen3 sweep at zero marginal cost on M5).
- No figure. Largest type on the board.

---

## BAND 1 — Left column: THE QUESTION  |  Right column: THE METRIC

### Panel 1 (left) — The question
- **Headline:** An agent calls `search_flights`. The registry has
  `find_flights`. The call fails.
- Existing benchmarks measure at the wrong grain (per-task / per-query, folded
  into composite scores) — the failure *looks* architecture-agnostic. At the
  per-call grain it is not.
- Three questions: **who** fabricates tool names, **how often**, **what fixes
  it**.
- **Figure/table:** small version of `figures/fig4_distractor_probe.png` (the
  distractor probe: target removed, one synthetic look-alike injected in its
  slot — near_name / synonym / matched_random / unrelated). Caption: "Closest
  benchmark proxy for the production name-collision."
- Risk framing (one line, no exploitation claim): a fabricated name is an
  attack surface — the tool-registry analog of package "slopsquatting."

### Panel 2 (right) — The metric (TFR)
- **Definition box (the load-bearing equation):**
  TFR = (# parsed tool calls whose name ∉ registry R) / (# parsed tool calls).
  Per **call**, not per task. System failures (timeout/refusal/parse-fail)
  excluded from numerator and denominator.
- Why per-call: per-task aggregation conflates rate with trace length (one bad
  agent emitting 20 bad calls swings the headline an order of magnitude).
- Stats one-liner: Clopper–Pearson 95% two-sided upper bounds on zero-event
  cells; BCa task-clustered bootstrap on non-zero cells; Fisher's exact
  one-sided for the RVR headline; Holm–Bonferroni across primary tests.
- **Table:** the prior-art positioning table (from `A1_appendix.tex`,
  `tab:priorart`) trimmed to 3 columns — Work / Granularity / Existence-clean?
  Bottom row bold: **Ours (TFR): per-call · multi-turn agentic traces ·
  existence-clean · 0%–1.64%.** Caption: "Not apples-to-apples; positions what
  each metric counts, not which model is best."

---

## BAND 2 — Left column: COMMERCIAL-vs-OPEN HEADLINE  |  Right column: SCALING CURVE

### Panel 3 (left) — The headline finding: a bound-vs-estimate split
- **Big-number callouts (the central contrast):**
  - Anthropic 4.x pooled C0: **0 / 2,592** events → upper bound **≤ 0.14%**
    (5 versions, 11 months — a stability check, not a trend).
  - OpenAI (gpt-4.1 + gpt-4o tiers) pooled: **0 / 2,117** → **≤ 0.18%**.
  - Open-weight Qwen3: **non-zero**, peaking at **1.64%** (6/366, 14B).
- **Table:** Anthropic per-version probe (`tab:anth-temporal`): Opus 4.7 0/293,
  Sonnet 4.6 0/561, Sonnet 4.5 0/285, Sonnet 4 0/253, Haiku 4.5 0/539 → pooled
  probe 0/1,931. Note the `miss_func` split (designed to elicit fabrication)
  did not bite — agents chain in-registry calls instead of inventing a
  one-shot (trace: pwd→ls→cd→mkdir→mv vs a fabricated `mv_recursive()`).
- **The line to print verbatim:** "The bound-vs-estimate asymmetry is the
  finding." Anthropic ≤0.14% sits an order of magnitude below the Qwen3
  0.95–1.64% band.

### Panel 4 (right) — The Qwen3 scaling curve (descriptive)
- **Figure:** `figures/fig1_scaling_curve.pdf` (Qwen3 family TFR vs size, C0
  target-removed probe, Clopper–Pearson error bars, dashed Anthropic upper
  bound). This is the marquee plot.
- **Inset table** (`tab:qwen3-scale`, pooled column only):
  0.6B 0/75 · 1.7B 2/210 · 4B 3/226 · 8B 9/615 · **14B 6/366 = 1.64%** · 32B
  0/224.
- Caption discipline: rate is **non-monotone** in scale (0% → 1.64% peak at 14B
  → 0% at 32B). The 32B bound is wide enough to overlap the 14B estimate, so
  "collapse" = "not detected at this N," not emergent capability.
  **Six points are not a curve** — reported descriptively, not a fitted law.
- Trace intuition (one line): 1.7B rarely emits well-formed calls (little
  surface to fabricate on); 14B formats fluently but doesn't check the
  registry; 32B does both.

---

## BAND 3 — Left column: RVR + VALIDATION  |  Right column: CONTROLS

### Panel 5 (left) — RVR: the fix and its validation
- **Mechanism box:** Registry-Visible Reprompting — training-free, single-turn
  middleware between agent and executor. On a registry miss, return one
  re-prompt wrapping a structured `tool_not_found` envelope listing available
  tools. O(1) membership check; zero provider round-trips on hits, one on
  misses; rendered registry ~100–200 tokens (<5% of context).
- **Figure (small):** `figures/fig3_rvr_architecture.png`.
- **Headline result table** (`tab:rvr-validation`): per-tier C0 → C1
  - 1.7B 2/210 → 0/200 · 4B 3/226 → 0/228 · 8B 9/615 → 0/258 · 14B 6/366 →
    0/259
  - **Pooled: 20/1,417 → 0/945, all 20/20 prevented.**
- **Significance callout:** Fisher's exact one-sided on pooled 20/1,417 vs
  0/945: **p = 3.5 × 10⁻⁵** (survives Holm–Bonferroni, p_Holm = 2.1 × 10⁻⁴).
- **Ablation strip** (`fig2_ablation_ladder.pdf`, Qwen3-8B): opaque C0 1.46%
  (9/615) → naive retry 0.39% (1/258) → structured envelope C0.7 **0/448** →
  full RVR C1 **0/258**. Hedged caption: the structured *envelope* drives the
  prevention; adding the real registry list buys no further detectable
  reduction (Newcombe 95% CI on C1−C0.7: **[−1.5, +1.4] pp**). Decoy list
  C0.8 (wrong names) also **0/410**. **All three arms zero-event → absence of
  evidence, not evidence of equivalence**; content could buy up to ~1pp. A
  powered test on a high-event cell is in progress.
- Anthropic note: RVR holds 0-event on the frontier, but strict-pass slips at
  N=60 (Sonnet 60→53/60, Haiku 60→56/60), underpowered TOST → recommend
  **tier-conditional deployment** (deploy only where audited TFR > 0).

### Panel 6 (right) — Cross-family & precision controls
- Kills two objections: "it's a 4-bit MLX artifact" and "it's one family."
- **Precision ladder (Qwen3-8B), same C0 probe** (`tab:controls`):
  - 4-bit **9/623 = 1.44%** · 8-bit **2/435 = 0.46%** · bf16 **2/316 = 0.63%**.
  - All three CIs overlap → no claimed precision effect; load-bearing fact is
    the **floor: fabrication persists at full precision → not a quantization
    artifact.**
- **Second open family:**
  - Llama-3.1-8B (4-bit) C0 **5/400 = 1.25%** — squarely inside the
    open-weight band.
  - Qwen2.5-7B C0 **28/459 = 6.10%** — higher than any Qwen3 size; the lineage
    carries the failure.
  - Llama-3.1-8B C1 (RVR) **2/487 = 0.41%** (~3x reduction); both residuals
    caught by RVR's `tool_not_found` rejection layer before reaching the
    environment.
- Honest caption: weaker per-call null than the matched Qwen3 sweep (single
  N≈500 cross-family probe). Gap now appears in **two distinct open lineages**;
  we do not claim general cross-family transfer.
- **Do NOT pool** these tau/cross-family/precision numbers into the BFCL
  headline — keep them visually walled off as "controls."

---

## BAND 4 — Takeaways footer (full width, bottom ~4")

1. **A per-call diagnostic (TFR)** exposes existence failures that production
   guardrails silently absorb.
2. **An open-vs-closed split:** commercial frontiers ≤0.14–0.18% (bound),
   open-weight Qwen3 / Llama / Qwen2.5 at ~0.4–6.10% (estimate). The
   bound-vs-estimate asymmetry is the finding.
3. **A training-free fix (RVR):** clears every logged Qwen3 fabrication
   (20→0, p = 3.5 × 10⁻⁵); generalizes to Llama (residuals caught by the
   rejection layer).
4. **A hedged, actionable ablation:** at this N the structured envelope alone
   suffices — ship rejection without echoing internal tool names and lose
   nothing detectable (content effect bounded to ±1.5 pp; powered test in
   progress).
5. **Deploy tier-conditionally:** RVR/C0.7 only on tiers with audited TFR > 0,
   paired with executor-side allow-listing.
- **Artifacts (footer strip):** per-call TFR diagnostic · 11-model audit over
  11 months · RVR with per-tier validation · open harness (153 unit tests).
  Total API spend $82; Qwen3 sweep at zero marginal cost on Apple M5. QR to
  anonymized repo.

---

### Asset checklist (existing files, reuse as-is)
- `figures/fig1_scaling_curve.pdf` → Panel 4 (marquee).
- `figures/fig2_ablation_ladder.pdf` → Panel 5 (ablation strip).
- `figures/fig3_rvr_architecture.png` → Panel 5 (mechanism).
- `figures/fig4_distractor_probe.png` → Panel 1 (the probe).
- Tables retypeset from `tab:priorart`, `tab:anth-temporal`, `tab:qwen3-scale`,
  `tab:rvr-validation`, `tab:controls`. No new numbers; locked values only.

### Invariants honored
- Every figure asset already exists in `paper/figures/`.
- No new overclaims; non-monotone shape, ablation, and cross-family null all
  carry their paper hedges.
- tau / cross-family / precision controls are walled off from the BFCL headline
  (Panel 6 is explicitly "controls").
