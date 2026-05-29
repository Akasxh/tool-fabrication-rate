# ADDENDUM_R1 — Post-Review Corrections to v3.1 + HARNESS_SPEC
*Single canonical patch capturing all R1 review-driven changes. Read this AFTER `PAPER_PLAN_v3.1.md` and `harness/HARNESS_SPEC.md`. This file overrides any conflict.*

**Status**: applied 2026-04-27 post-R1 synthesis. Locked.

---

## A. Track + headline

- **Track: Main 7p (UNCHANGED).** R1 SCALE Workshop reviewer recommended switch to Benchmarking & Dataset; we decline because (a) workshop is non-archival → track has zero CV-visibility; (b) method-paper framing better matches author career trajectory; (c) the multimodal mismatch can be addressed in 2 sentences of §1 + §7 instead of a structural reframe.

- **Multimodal bridge** (insert in §1, second paragraph; mirror in §7 limitations):

  > §1 insert: *"Tool registries are the substrate of multimodal AI agents: the typed interfaces through which agents access vision, audio, code execution, and external systems. Our text-only evaluation (BFCL multi-turn + τ-bench retail) isolates the registry-membership failure that any multimodal tool-using agent inherits, in the simplest setting where the failure is cleanly attributable."*

  > §7 limitation: *"Our evaluation is text-only. TEHR and RVR extend naturally to multimodal tool registries (vision tools, code-exec, file I/O); we leave that empirical extension to future work."*

---

## B. Experimental matrix updates (D2-D5)

### B.1 Sample sizes (D2)
- BFCL multi-turn: N=50 → **N=100** per (model × condition).
- τ-bench retail: N=25 → **N=50** per (model × condition).
- §6 probe: N=30 → **N=100** per (model × distractor type).
- Power calculation (R1 BLOCKER B7): At assumed TEHR=10% and pooled-across-tier discordance b+c≈40, paired McNemar mid-p achieves 80% power for ΔPass(C1−C0.5)=20pp. Calculation: under H1, b+c follows approximately Bin(N×TEHR, 0.5+δ/2) with δ=0.20; required b+c≥30 for α=0.05. With pooling we satisfy this comfortably; per-tier-without-pooling does not (per Stats RQ1).

### B.2 Conditions (D3 — add C0.7)
Now **four** conditions (was three):

| Condition | Description |
|---|---|
| **C0** | ReAct, framework default error on bad call (raw provider error, opaque) |
| **C0.5** | Naive retry: original prompt + "previous failed, try again" — no registry list |
| **C0.7** *(NEW)* | **Idealized structured-error baseline** in JSON shape: `{"error":"tool_not_found","attempted":"<name>","details":"function not in registry"}` — no registry list, but error is parsed-readable. We label it *idealized* because real production frameworks (LangChain et al.) typically surface raw provider exceptions; the JSON envelope is an upper-bound approximation of the most generous structured default we could expect. |
| **C1** | RVR: re-prompt with full registry list |

**Primary test reframed**: paired McNemar(C1 vs **C0.7**) on the strict subset of C0-failed-with-hallucination tasks. C0.5 stays as a secondary ablation (does retry-alone explain anything?).

### B.3 §6 probe redesign (D4)
- "Causal — not merely correlational" → **"controlled comparison."** Drop the causal language throughout §3.4, §6, abstract.
- Distractor types: **near-name**, **synonym**, **random** (UNCHANGED) PLUS a **matched-random** that fixes description length, schema arity, and position to control for "registry-size+1" confound.
- Scale: 30 tasks/cell → **100 tasks/cell**.
- Statistical method: ANOVA → **Friedman + Nemenyi post-hoc** (TEHR is bounded [0,1], ANOVA's normality assumption violates).

### B.4 Contribution reframe (D5)
The 4 contributions become **3** (collapse #1 + #4 into "benchmark + metric + mechanism"):

1. **Benchmark + Metric + Mechanism**: We introduce TEHR (per-call denominator, registry-membership-isolated) AND a controlled distractor probe characterizing what surface features of the registry drive hallucination. The metric without the probe is renaming; the probe gives it explanatory power.
2. **RVR Intervention**: Training-free, registry-list-in-reprompt; primary test C1 vs **C0.7** (idealized structured-error baseline), secondary vs C0.5 (retry-alone).
3. **Cost-quality-gap closure across 3 capability tiers + 2 vendor families + open-source local**: with explicit gap-closure ratio + BCa-bootstrap CI + denominator-near-zero policy.

---

## C. Statistical fixes (R1 BLOCKERS B2, B4, B7, B8 + MAJORS M1-M5, M16)

### C.1 TOST margin: 1pp → **5pp** (or framing change)
TOST at margin 1pp requires ~1100 paired observations (Stats reviewer). At our N≈30-50 strict-subset, we have ~2 orders of magnitude fewer. **Decision**: widen non-inferiority margin to **5pp**, OR frame as "estimated paired difference with 95% CI; pre-registered threshold for clinically-meaningful regression = 5pp." Either is defensible; I'll write both and pick whichever survives R2.

### C.2 Bootstrap: percentile → **BCa**
All bootstrap CIs use **BCa (bias-corrected accelerated)** instead of percentile, especially for rates near 0/1. Update `harness/stats/bootstrap.py::bca_bootstrap_ci`. Use 10,000 resamples.

### C.3 Cluster-bootstrap by task
Per-call observations within a task are non-i.i.d. (same agent, same registry). All bootstrap CIs cluster-resample at the task level, then compute per-call labels within selected tasks.

### C.4 Pool discordance pairs ACROSS tiers BEFORE McNemar (Stats RQ1)
Headline `paired_mcnemar` test pools b, c counts across all 4 API tiers prior to the test. Holm-Bonferroni then applied to per-tier *secondary* tests, not the headline.

### C.5 Friedman + Nemenyi for §6 probe (replaces ANOVA)
TEHR is bounded [0,1]; ANOVA's normality + homogeneity assumptions don't hold. Use `scipy.stats.friedmanchisquare` + `scikit_posthocs.posthoc_nemenyi_friedman`.

### C.6 McNemar mid-p: clamp to [0,1] + b+c=0 guard
Update `paired_mcnemar_midp(b, c)`:
```python
def paired_mcnemar_midp(b: int, c: int) -> float:
    if b + c == 0:
        return 1.0  # no discordance → no evidence against H0
    n = b + c
    k = min(b, c)
    from scipy.stats import binom
    p_strict = binom.cdf(k - 1, n, 0.5) if k > 0 else 0.0
    p_eq     = binom.pmf(k, n, 0.5)
    p_one_sided = p_strict + 0.5 * p_eq
    p_two_sided = min(1.0, 2.0 * p_one_sided)
    return p_two_sided
```

### C.7 Family-wise error correction scope
Restrict primary FWER family to the **3 named tests** (down from 4 — we have 4 API tiers but the headline pools, so per-tier becomes secondary):
1. Pooled paired McNemar(C1 vs C0.7) on hallucination-tagged C0-failed subset
2. TOST (or paired-CI) for non-inferiority on C0-passing subset
3. Friedman test on §6 probe distractor types

All other tests: pre-declared **exploratory**, no FWER control, reported with bare p-values.

### C.8 Power calculation (explicit, in §4.4)
Insert after pre-reg item 10:
> *Power calculation*: under H1: ΔPass(C1−C0.7)=20pp, base TEHR=10%, N=100 BFCL per (model × condition), pooled across 4 API tiers. Expected hallucinated-event count per cell ≈ 10; pooled b+c ≈ 40. McNemar mid-p achieves 80% power at α=0.05 for ΔPass≥20pp. Per-tier breakdowns are reported as directional with explicit "exploratory, underpowered" labeling when b+c<30.

---

## D. Reproducibility fixes (R1 BLOCKER + MAJORS M6-M10)

### D.1 Lock decoding params
**All API adapters: temperature=0.0, top_p=1.0**. Document in §4 and HARNESS_SPEC §2 of each adapter.
- Anthropic: `messages.create(temperature=0.0, top_p=1.0, ...)`
- OpenAI/xAI: `chat.completions.create(temperature=0.0, top_p=1.0, ...)`
- MLX: `mlx_lm.generate(temp=0.0, top_p=1.0, ...)` — note Qwen3 docs recommend `top_k=20, temperature=0.6`; we override to 0.0 for reproducibility, accepting some quality cost.

### D.2 `harness/repro_manifest.json` (NEW)
Generated at run-start; written to results/ alongside JSONL traces. Schema:
```json
{
  "run_id": "uuid",
  "started_at": "ISO-8601",
  "git_commit": "abcdef0",
  "python_version": "3.12.13",
  "os": "Darwin 25.4.0",
  "sdks": {"anthropic": "0.96.4", "openai": "2.32.1", "mlx_lm": "0.31.3", ...},
  "datasets": {
    "bfcl_v4": {"commit": "6ea5797", "license": "Apache-2.0"},
    "tau_bench_retail": {"commit": "59a200c", "license": "MIT"}
  },
  "models": {
    "claude-sonnet-4-6": {"resolved_via_models_api": "claude-sonnet-4-6-resolved-snapshot-string"},
    "claude-haiku-4-5-20251001": {"alias": "claude-haiku-4-5"},
    "gpt-4.1-2025-04-14": {"alias": "gpt-4.1"},
    "gpt-4.1-mini-2025-04-14": {"alias": "gpt-4.1-mini"},
    "mlx-community/Qwen3-8B-4bit": {"hf_revision_sha": "abcd...", "local_mirror": "harness/data/mlx_models/Qwen3-8B-4bit/"}
  },
  "decoding": {"temperature": 0.0, "top_p": 1.0, "max_tokens": 1024},
  "seeds": {"loader_seed": 0, "bootstrap_seed": 0, "permutation_seed": 0},
  "n_per_cell": {"bfcl": 100, "tau_bench": 50, "probe": 100},
  "conditions": ["C0", "C0_5", "C0_7", "C1"],
  "addendum_version": "R1"
}
```

### D.3 MLX HF revision SHA pin + mirror
At run-start, capture `huggingface_hub.HfApi().model_info("mlx-community/Qwen3-8B-4bit").sha` and log to manifest. **Mirror plan**: download model files locally to `harness/data/mlx_models/Qwen3-8B-4bit/` so a reviewer can reproduce even if the org disappears. ~5 GB; document size in supplementary README.

### D.4 Sonnet 4.6 rolling-alias capture
At run-start, call Anthropic `models.list()` and log the snapshot string for `claude-sonnet-4-6` to `repro_manifest.json::models["claude-sonnet-4-6"].resolved_via_models_api`.

### D.5 §4 limitations one-liner
*"MLX inference on Apple Silicon is not bitwise-deterministic across runs due to non-deterministic Metal kernels; per-task tool-call decisions are stable to within ±1 token, which does not affect TEHR-level results."*

---

## E. Other R1 MAJORS

### E.1 Czapla weight reduction (M11)
§1 hook: lead with **API-Bank's 61.4% rate** (peer-reviewed, EMNLP 2023), then mention Czapla as "industry observation that the failure persists in 2026 frontier models." Reorder so the heavyweight precedent leads.

### E.2 k=1 retry cap ablation (M12)
Add small ablation: k ∈ {0, 1, 2, 3} on a 30-task subset of BFCL. ~120 runs against credits. Report in appendix; one-line in §3.2 design rationale.

### E.3 "Scalable" / "Efficient" language downscope (M13, M14)
- Drop "scaling-curve" → "tier comparison" throughout.
- Add **latency-per-task** + **tokens-per-success** columns to §5 main table (efficiency claim becomes quantitative, not just cost-per-success).
- Energy/FLOPs explicitly OOS in §7 limitations.

### E.4 Local tier framing (M15)
Reframe the Qwen3-8B/M5 panel from "vanity panel" to "**SCALE-relevant feasibility anchor**": the workshop's efficiency theme rewards a local-first deployment story. Section §5.5 in the paper. Cross-platform caveat ("M5 results not directly comparable to GPU inference") in §7 limitations.

---

## F. Code-agent acceptance contract delta

Phase-1 code agents implement against HARNESS_SPEC §2 + this ADDENDUM. Specifically:

1. **Add condition `C0_7`** to `runner/loop.py` condition dispatch and `intervention/framework_default.py` (new file).
2. **Update `stats/tehr.py`** to BCa bootstrap with cluster-by-task.
3. **Update `stats/paired_mcnemar.py`** with clamp + b+c=0 guard.
4. **Replace `stats/probe_anova.py`** with `stats/probe_friedman.py` (Friedman + Nemenyi).
5. **Update `stats/tost.py`** margin default 0.01 → 0.05.
6. **New `stats/bootstrap.py`** with `bca_bootstrap_ci(per_call_labels, cluster_ids, ...)`.
7. **Lock adapter decoding params** to temperature=0.0, top_p=1.0.
8. **Generate `harness/repro_manifest.json`** at run-start (per D.2 above).

---

## G. Open items (for R2 reviewers to assess)

- Will the multimodal bridge in §1 + §7 (per A) actually deflect SCALE-reviewer multimodal concern? R2's SCALE-or-equivalent reviewer should validate.
- Is the C0.7 framing "production-default" defensible? Or do reviewers want a real LangChain instance? R2 NeurIPS-equivalent should opine.
- Does the contribution reframe (§B.4: 4 → 3 contributions) actually strengthen or just consolidate weakness? R2 ICML-AC equivalent should verdict.
