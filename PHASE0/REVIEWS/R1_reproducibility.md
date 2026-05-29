# R1 — Reproducibility Review (SCALE @ ICML 2026)

**Reviewer persona**: Reproducibility auditor. Tone: meticulous, friendly-but-firm.
**Materials reviewed**: PAPER_PLAN_v3.1.md, paper/sections/04_setup.tex, harness/HARNESS_SPEC.md, PHASE0/model_ids.md, paper/refs.bib, PHASE0/dataset_status.md (cross-referenced).
**Date**: 2026-04-27.

---

## Verdict
**Weak Accept, conditional on fixing 5 of the 7 P0/P1 items below.** The plan shows real reproducibility hygiene (locked decisions at T+05:00, dataset commit pins, JSONL schema with version, stats seeds), which is rare at workshop tier. But several moving parts are pinned by *intention* rather than by *artifact*: SDK ranges instead of `==`, an MLX HF revision that is "to be captured at run-start" rather than already captured, a Sonnet 4.6 alias that is rolling, and no central `repro_manifest.json`. None are fatal; all are mechanical to fix before submit.

---

## Top 5 Issues
1. **No central reproducibility manifest.** Dataset commits, model dated aliases, MLX HF revision, SDK exact versions, Python version, OS, and seeds are scattered across `model_ids.md`, `dataset_status.md`, and `HARNESS_SPEC.md`. Reviewers expect one `repro_manifest.json` (or `reproduction.md`) shipped at the root of the supplementary zip.
2. **MLX HF revision SHA not yet pinned.** §8.5 says "HF revision pinned at run-start" — that is *future tense*. Until the SHA is captured and committed, the local-tier result is not reproducible. `mlx-community` is a community account; the repo can be force-pushed or deleted.
3. **Sonnet 4.6 has no dated alias.** `model_ids.md` calls this out, and the spec's mitigation ("query `/v1/models` at run-start; log to metadata") is correct but only works if that dump is *retained in the supplementary zip and cited in §4*. As written, §4.1 of the paper does not mention this dump at all.
4. **SDK pins use `>=,<` ranges.** `anthropic>=0.96.0,<1.0.0`, `openai>=2.32.0,<3.0.0`, `mlx-lm>=0.31.0` — minor-version drift can change tool-call serialization or token accounting. Pin to `==` exact versions in `pyproject.toml`, then optionally produce `uv.lock` / `requirements.lock` and ship that.
5. **MLX inference non-determinism on Apple Silicon is not acknowledged.** `mlx_lm.generate` on Metal kernels is not bitwise-deterministic across runs even with `mx.random.seed(...)` set, especially with quantized weights. The paper claims pass-rate point estimates without a sentence acknowledging this. Either set `mx.random.seed(0)` and report run-to-run variance from a 3× repeat, or add a one-line caveat to §4.1.

---

## Specific Concerns (audit-by-checklist)

### 1. Model versioning
| Model | Status | Action |
|---|---|---|
| Claude Sonnet 4.6 | Rolling alias only | **P0**: capture `/v1/models` at run-start, dump to `repro/sonnet_4_6_resolved.json`, cite in §4.1. |
| Claude Haiku 4.5 | Dated `claude-haiku-4-5-20251001` | OK. |
| GPT-4.1 | Dated `gpt-4.1-2025-04-14` | OK. |
| GPT-4.1-mini | Dated `gpt-4.1-mini-2025-04-14` | OK. |
| Grok-4 | Dated `grok-4-0709` (deferred) | OK if Grok activates. |
| Grok-4-fast | Rolling | Same `/v1/models` snapshot recommended. |
| Qwen3-8B-4bit | Repo pinned, **no SHA** | **P0**: capture `huggingface_hub.HfApi().model_info(repo_id, revision="main").sha` at load-time and pin via `revision=<sha>` in `from_pretrained`. |

### 2. Random seeds
- Dataset loader seed: locked (`seed=0`, HARNESS_SPEC §2 / acceptance §5 item 6). **OK.**
- API temperature/top_p: **NOT mentioned anywhere**. **P0**: lock `temperature=0.0` (or document the chosen value) in adapter config and disclose in §4.1. Anthropic and OpenAI both honor `temperature=0` for tool-use; document.
- Bootstrap CI seed: `tehr_bootstrap_ci(seed=0)`. **OK.**
- McNemar permutation: N/A (mid-p is exact). **OK.**
- MLX generation seed: `mlx_lm.generate` accepts no native seed parameter; use `mx.random.seed(0)` in the adapter. **P1**: HARNESS_SPEC does not mention this — add it.

### 3. Dataset commit pins
- BFCL @ `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`, τ-bench @ `59a200c6d575d595120f1cb70fea53cef0632f6b`. **Pinned in `dataset_status.md` §1, but not in any single manifest reachable from §4 or the supplementary zip.** **P1**: add to `repro_manifest.json` and reference from §4.2.

### 4. SDK versions
See Issue #4 above. **P1**.

### 5. Data licenses
BFCL Apache-2.0 + τ-bench MIT, both confirmed by file inspection. **The paper §7 (acknowledgements) is not yet drafted.** **P1**: add a one-paragraph data-attribution block per `dataset_status.md` §1 verbatim.

### 6. Anonymized supplementary zip
§9 of v3.1 lists "supplementary zip" but **does not enumerate its contents**. **P1**: add an explicit manifest:
- `code/` — `harness/` minus `data/` minus `.git/` minus `.env` (~5 MB)
- `traces/` — sampled JSONL (10% of runs) with redaction applied (~50–150 MB depending on `persist_raw=False`)
- `figures/` — final-paper PNGs/PDFs (~5 MB)
- `repro_manifest.json` — see Issue #1
- `README.md` — reproduction recipe + estimated wall-clock + estimated cost
- **Estimated total: 60–200 MB**, well under OpenReview's typical 100 MB cap if traces are sampled (else split traces to a separate "extended traces" supplementary).
**Anonymization scrub**: `trace_logger` deny-list (HARNESS_SPEC §5 item 8) covers user email + API keys; **add author name, GitHub URLs, and `cero` username to the deny-list before zipping**. Run `grep -F` on the zip recursively as a final gate.

### 7. Reviewer reproduction effort
Given supplementary zip + paper, a third party needs:
- Apple-Silicon Mac with 32 GB unified memory (M-series) for the local tier — **otherwise drop to API-only re-run**.
- API keys + ~$200–400 of credits (matches our redeemed budget, but reviewer pays this).
- 6–8 h compute + 4–6 h setup/integration if the manifest is well-formed; **~12–16 human-hours total** for full main run, **~3 h** if reviewer just re-runs the 25 BFCL pilot tasks at 1 model.

### 8. Floats and determinism
- Bootstrap: deterministic given `seed=0`. **OK.**
- McNemar mid-p: exact; no seed needed. **OK.**
- MLX/Metal: **non-deterministic without explicit `mx.random.seed`**. See Issue #5. **P1**.
- Anthropic/OpenAI at `temperature=0`: deterministic-ish; in practice still drifts due to provider-side batching and float reductions. **P2**: add a one-line "API responses at temperature=0 are not bitwise reproducible across provider-side updates" caveat to §4.1.

### 9. ICML 2026 reproducibility-checklist mapping
See Pass/Fail section below.

### 10. Live, accessible artifacts
- `mlx-community/Qwen3-8B-4bit` is a community-org HF repo. If deleted/renamed, the local-tier result is unreproducible. **P1**: mirror to author's own HF account (or to the supplementary zip if size permits — quantized 8B 4-bit is ~4.5 GB, too big for OpenReview, so mirror is the answer) and cite both URLs.

---

## Required Changes (ordered by severity)
1. **P0** Capture and commit MLX HF revision SHA before any main-run JSONL is written. Pin via `revision=<sha>`.
2. **P0** Lock `temperature` (and `top_p` if used) for all 5 adapters; disclose in §4.1.
3. **P0** Run-start `/v1/models` dump for Sonnet 4.6 (and Grok-4-fast if activated); save to `repro/`.
4. **P1** Repin SDKs to `==` exact versions; ship a `uv.lock` or `requirements.lock`.
5. **P1** Add `repro_manifest.json` collating: dataset commits, model dated aliases + revision SHAs, SDK exact versions, Python version, OS version, M5 unified-memory size, MLX runtime version, all seeds.
6. **P1** Set `mx.random.seed(0)` in the MLX adapter; add a one-line non-determinism caveat to §4.1.
7. **P1** Mirror MLX repo to author HF account; cite both URLs.
8. **P1** Define supplementary-zip contents explicitly; add anonymization gate (author name + GitHub URLs + `cero`) to deny-list.
9. **P2** Cite BFCL/τ-bench licenses in §7.

---

## Strongest Aspects
- Stats seeds (`tehr_bootstrap_ci(seed=0)`), exact mid-p McNemar, locked TOST margin, and Holm-Bonferroni are all spelled out — far above workshop median.
- Pre-registration locked at T+05:00 with 12 explicit decisions in §4.4.
- Dataset commit SHAs already captured.
- BFCL `"type":"dict"`→`"object"` normalization is documented and unit-tested (acceptance §5 item 9) — exactly the kind of silent bug that breaks reproductions.
- JSONL schema version field (`"1.0"`) is forward-thinking.

## Weakest Aspects
- No single reproducibility manifest — reviewers will have to triangulate across 3 docs.
- Inference-time determinism (temperature, MLX seed) is undocumented in the paper, only implied in the harness.
- MLX HF revision SHA is "to be captured" rather than captured.
- Supplementary zip contents not enumerated.

---

## Justification
Submission is reproducible *in principle* — datasets, statistics, and condition definitions are all locked. The remaining gaps are clerical (capture-and-commit operations) rather than design-level, and can be closed in <2 h before deadline. I would not block submission for these, but I would mark every P0/P1 in the rebuttal as "addressed in camera-ready" and ship the manifest in the supplementary zip.

---

## ICML 2026 Reproducibility-Checklist Pass/Fail

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | Code (supplementary or anonymous link) | **PASS (planned)** | OpenReview attachment per v3.1 §9; contents need explicit enumeration. |
| 2 | Data — splits, preprocessing, commit | **PASS** | BFCL@6ea5797, τ-bench@59a200c; loader is deterministic; `_normalize_bfcl_schema` is unit-tested. |
| 3 | Pretrained models — IDs, versions, sources | **PARTIAL** | 4/6 models have dated aliases; Sonnet 4.6 + Grok-4-fast rolling; MLX revision SHA missing. |
| 4 | Hyperparameters — tools list, prompt templates, decoding params | **PARTIAL** | Tool list and prompt templates locked; **temperature/top_p not specified anywhere**. |
| 5 | Compute environment — hardware, OS, Python, drivers | **FAIL** | M5/32 GB stated; OS version, Python version, MLX-lm version, Metal driver version all missing. |
| 6 | Random-seed disclosure | **PARTIAL** | Loader and bootstrap seeds locked; MLX generation seed and API temperature missing. |
| 7 | Statistical-significance disclosure | **PASS** | McNemar mid-p, Holm-Bonferroni, TOST 1pp, bootstrap 95% CI all specified. |
| 8 | Cite all baselines | **PARTIAL** | API-Bank + RelyToolBench cited in v3.1 §2; full §2/§5 text not yet reviewed. |
| 9 | License + attribution for data/models | **PARTIAL** | Identified in `dataset_status.md`; not yet in paper §7. |
| 10 | Live-artifact accessibility | **PARTIAL** | API endpoints assumed live; MLX repo on community account with no mirror plan. |

**Pass: 3 / Partial: 6 / Fail: 1.** Bring item 5 to PARTIAL and items 3, 4, 6 to PASS via the manifest, and the checklist crosses the bar.

---

*Word count: ~960.*
