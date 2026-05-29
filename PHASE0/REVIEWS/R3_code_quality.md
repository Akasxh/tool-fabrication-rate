# Code-Quality Reviewer — Round 3

## Files reviewed

| File | LOC |
| --- | --- |
| `harness/types.py` | 143 |
| `harness/registry.py` | 160 |
| `harness/adapters/base.py` | 45 |
| `harness/adapters/anthropic_adapter.py` | 183 |
| `harness/adapters/openai_adapter.py` | 185 |
| `harness/adapters/mlx_adapter.py` | 240 |
| `harness/intervention/rvr.py` | 33 |
| `harness/intervention/naive_retry.py` | 23 |
| `harness/intervention/framework_default.py` | 31 |
| `harness/cost_meter.py` | 102 |
| `harness/trace_logger.py` | 131 |
| `harness/repro_manifest.py` | 124 |
| `harness/stats/__init__.py` | 22 |
| `harness/stats/bootstrap.py` | 110 |
| `harness/stats/tehr.py` | 64 |
| `harness/stats/paired_mcnemar.py` | 92 |
| `harness/stats/tost.py` | 101 |
| `harness/stats/probe_friedman.py` | 117 |
| `harness/stats/gap_closure.py` | 167 |
| `harness/bench_loaders/bfcl.py` | 280 |
| `harness/bench_loaders/tau_bench.py` | 150 |
| `harness/bench_loaders/_tau_user_simulator_haiku.py` | 131 |
| `harness/tests/test_*.py` (8 files) | 1591 |

All Phase-0 and in-flight Phase-1 files exist on disk. Nothing missing.

## API-contract compliance across adapters
**PASS.** All three adapters return `ProviderResponse` with the same fields:
`raw_text:str`, `tool_calls:list[ToolCall]`, `parse_ok:bool`, `finish_reason:str`,
`tokens_in:int`, `tokens_out:int`, `latency_ms:int`, `raw_provider_payload`.
`ToolCall` is the shared `harness.types.ToolCall(name:str, arguments:dict)` —
no adapter introduces a divergent shape. Finish-reason vocabulary is harmonised:
all three emit `"tool_use"` when a parsed call is present (Anthropic via the
`_FINISH_REASON_MAP`; OpenAI maps `"tool_calls"` → `"tool_use"`; MLX synthesises
from `_classify_finish`). `parse_ok=False ⇒ tool_calls=[]` invariant holds in
each adapter (Anthropic L155-157, OpenAI L142-149, MLX L133-134).

Minor inconsistency: Anthropic maps `"end_turn"` → `"stop"` and OpenAI passes
`"stop"` through verbatim, but MLX uses the literal `"stop"`. Consistent
downstream. No silent TEHR bias risk.

## Decoding-params lock (per ADDENDUM D.1)
- Anthropic: **PASS** (`anthropic_adapter.py:121-122` → `temperature=LOCKED_TEMPERATURE, top_p=LOCKED_TOP_P`).
- OpenAI / xAI: **PASS** (`openai_adapter.py:106-107`).
- MLX/Qwen3: **PASS** (`mlx_adapter.py:93` builds the sampler via
  `make_sampler(temp=LOCKED_TEMPERATURE, top_p=LOCKED_TOP_P)`).

Greps confirm zero literal-value drift; no adapter passes a hardcoded
`temperature=0.7` etc. anywhere. Tests assert this directly via mock-call
kwargs (`test_anthropic_adapter.py::test_locked_decoding_params_are_passed_to_sdk`,
`test_openai_adapter.py::test_locked_decoding_params_in_call_kwargs`, MLX path
indirectly via the sampler being passed to `generate`).

## BFCL schema normalization
**PASS** with one observation. `_normalize_bfcl_schema` (`registry.py:34-57`)
recurses through dicts and lists; only mutates the literal pair
`{"type": "dict"}`. It is idempotent (running it twice on a schema returns
the same result; verified by `test_normalize_is_idempotent`). It does NOT
rewrite the string `"dict"` if it appears in non-`type` values such as a
description (verified by `test_normalize_does_not_rewrite_dict_string_in_non_type_keys`).
`test_normalize_walks_lists_of_subschemas` exercises list-of-dict; nested-dict
covered by `test_normalize_rewrites_top_level_dict_to_object` and the loader
acceptance `test_registry_normalization_replaces_dict_with_object`. Finally
`validate_registry` raises if any leftover `"type": "dict"` survives at any
depth (`registry.py:97-101`), giving an extra runtime safeguard. The BFCL
loader applies normalization before yielding tasks and the `test_bfcl_loader`
suite asserts `'"type": "dict"'` does not appear in any registry JSON dump.

## Cost-meter unit convention drift
**PASS** across all adapters. The convention is locked at the parameter
name (`price_in_per_1k`, `cost_meter.py:55-72`) and the module docstring
warns explicitly about the 1000× failure mode. Per-adapter:
- Anthropic price table (`anthropic_adapter.py:44-47`): Sonnet 4.6 at
  $3/M = `0.003 / 0.015` per 1k; Haiku 4.5 at $1/M = `0.001 / 0.005` per 1k. Correct.
- OpenAI (`openai_adapter.py:30-40`): gpt-4.1 at $2/M = `0.002 / 0.008`;
  mini at $0.40/M = `0.0004 / 0.0016`; grok-4 at $3/M = `0.003 / 0.015`;
  grok-4-fast at $0.20/M = `0.0002 / 0.0005`. All correctly /1000.
- MLX (`mlx_adapter.py:65-66`): hardcoded `0.0 / 0.0` (local model). Correct.

No adapter ships per-1M numbers. `test_cost_meter_per_1k_unit_convention`
checks the locked arithmetic: $3/1k in × 1000 tokens + $15/1k out × 500 tokens
= $10.50 (matches paper economics).

## Statistical correctness
- **`paired_mcnemar_midp(b=10, c=2)`**: PASS. Implementation
  `p_two = 2 * (binom.cdf(min(b,c)-1, b+c, 0.5) + 0.5 * binom.pmf(min(b,c), b+c, 0.5))`
  matches the standard mid-p formula. Reference value computed independently:
  `2 * (binom.cdf(1,12,.5) + 0.5*binom.pmf(2,12,.5)) = 0.0224609375`.
  `test_mcnemar_matches_hand_reference` asserts the same identity to 1e-6.
  Edge cases handled (b+c=0 → 1.0; clamp to [0,1]).
- **`bca_bootstrap_ci`**: PASS. Uses Efron (1987): `z0 = norm.ppf(prop_below)`
  and acceleration `a_hat = sum((jbar - jack)^3) / (6 * sum((jbar - jack)^2)^1.5)`
  (`bootstrap.py:91-94`). Cluster resampling correctly resamples cluster
  *labels* with replacement and concatenates the per-cluster row buckets
  (`bootstrap.py:23-27`). Jackknife is leave-one-cluster-out when
  `cluster_ids` is set (`bootstrap.py:36`). Degeneracy fallbacks (constant
  bootstrap distribution, `prop_below ∈ {0,1}`, `a1 >= a2`) all collapse to
  percentile bounds. No off-by-one in `_jackknife_kept_indices`.
- **`tost_paired_proportions`**: PASS. On identical samples (`success_a == success_b`),
  `mean_diff=0`, `se=0`, the degenerate branch returns
  `p_lower = p_upper = 0.0` ⇒ `non_inferior=True` at any margin > 0
  (`test_tost_all_pass_non_inferior`, `test_tost_identical_mixed_non_inferior`).
- **`gap_closure_ratio` denominator policy**: clear and consistent.
  `denom <= near_zero_threshold + _TOL` returns `None` (inclusive boundary,
  with a 1e-9 tolerance to handle FP drift). The `test_gap_closure_denominator_at_threshold_returns_none`
  test asserts `(0.5, 0.7, 0.55)` (denom == 0.05) returns None. Documented
  in module docstring and propagates a `RuntimeWarning` in
  `gap_closure_with_ci`. Bootstrap branch uses the same threshold inside
  `_ratio`, so undefined resamples are dropped consistently.
- **Friedman + Nemenyi**: PASS. Includes a guard against rank-degenerate
  data (`np.all(np.ptp(arr, axis=1) == 0)` → p=1.0 to dodge scipy's div-zero)
  and a Bonferroni-Wilcoxon fallback when `scikit_posthocs` is missing.

## Trace logger
**PASS.** The pydantic model (`trace_logger.py:23-48`) mirrors HARNESS_SPEC §3
with a regex-pinned `schema_version="1.0"`. Missing required fields raise
`TraceSchemaError` with the offending field names exposed (verified by
`test_trace_logger_missing_field_raises`, `test_trace_logger_bad_schema_version_raises`).
`raw_provider_payload` is dropped on write unless `persist_raw=True` (verified
by `test_trace_logger_drops_raw_payload_by_default` and counterpart). Redaction
walks dicts and lists recursively (`_redact`) and is exercised on both
`agent_message` and `tool_response` by `test_trace_logger_redaction`. Append
mode preserves prior records (`test_trace_logger_appends`).

## Refusal classification ownership
**PASS.** All three adapters pass content through unmodified. Anthropic
docstring states this explicitly (L13-14). OpenAI uses the SDK `refusal`
channel only as a finish-reason hint (`openai_adapter.py:155-161`); the text
itself is forwarded as `raw_text`. MLX's `_classify_finish` only emits
`tool_use | length | stop` and never `refusal`. No deny-list strings
("I can't", "I cannot", etc.) appear anywhere in `harness/adapters/`.

## Cost meter threshold callback
**PASS.** Single-fire guarded by `self._threshold_fired` flag inside the lock
(`cost_meter.py:73-83`). Tests cover three scenarios:
`test_cost_meter_threshold_fires_exactly_once` (fires once after 9 successive
adds reaching exactly 90% of $10), `test_cost_meter_threshold_does_not_refire`
(crossing 90% on first add, then 2 more adds — still 1 fire),
`test_cost_meter_budget_abort` (raises `BudgetAbort` at >= budget). Callback
fires *outside* the lock (good — user code can re-enter or be slow).

## Anonymization
`grep -rni "akash" /Users/cero/Desktop/PROJECTS/icml/harness/` returns
**zero hits**. However `/Users/cero/...` literal paths appear in two
production files: `bench_loaders/bfcl.py:39` (`DEFAULT_DATA_DIR`) and
`bench_loaders/tau_bench.py:29`. These are `cero`, not `akash`, so they pass
the literal-name check, but they're a username string and a deanonymisation
risk for the artifact submission. **Recommend** parameterising via an
environment variable (`ICML_DATA_DIR`) before public release. Test files
use the same path under `PYTHONPATH=` and in module docstrings.

## Type-hint consistency
**PASS in harness code.** Greps for `Dict[`/`List[`/`Tuple[`/`Set[`
return zero hits in `harness/` outside the `data/` vendored
third-party trees (BFCL + τ-bench upstream sources). All harness
modules use Python 3.12 builtins (`list[X]`, `dict[X, Y]`, `X | None`)
or `typing.Optional` for `Optional` only. Acceptable.

Minor stylistic note: `repro_manifest.py`, `cost_meter.py`, `types.py`,
`trace_logger.py`, `_tau_user_simulator_haiku.py`, and
`openai_adapter.py` import `Optional` from `typing` rather than using
`X | None`. Both forms are valid PEP 604 — keep one for consistency in
a future polish pass; not blocking.

## Test coverage
| Module | Test file | Public-API coverage |
| --- | --- | --- |
| `types.py` | `test_types_registry.py` | Imports + `ActionKind` values. |
| `registry.py` | `test_types_registry.py` | normalize (top, nested, list, idempotent, non-`type`-key safety), validate (positive, dict-leftover, missing properties, deep nested), all 3 renderers. |
| `adapters/base.py` | `test_intervention.py::test_base_locked_decoding_constants` | Constants asserted. |
| `adapters/anthropic_adapter.py` | `test_anthropic_adapter.py` | 4 fixtures + decoding lock + max_tokens override + AdapterError on ConnectionError + price-table aliasing. |
| `adapters/openai_adapter.py` | `test_openai_adapter.py` | 4 fixtures (clean / hallucinated / refusal / parse_fail) + decoding lock + APIConnectionError + AuthenticationError + xAI base_url env routing + unknown model_id. |
| `adapters/mlx_adapter.py` | `test_mlx_adapter.py` | 4 fixtures + `enable_thinking=False` + date-hint injection (3 cases) + envelope stripping + finish_reason heuristic + lazy-load. |
| `intervention/*` | `test_intervention.py` | All 3 conditions: clean→EXECUTE, hallucinated→RE_PROMPT, empty→EXECUTE(None), feedback-string assertions. |
| `cost_meter.py` | `test_logging_cost.py` | Per-1k arithmetic, threshold once, no-refire, BudgetAbort, history. |
| `trace_logger.py` | `test_logging_cost.py` | Roundtrip, persist_raw on/off, missing-field raise, bad schema_version, redaction, append. |
| `repro_manifest.py` | `test_logging_cost.py::test_generate_manifest_writes_and_returns` | All top-level keys + ADDENDUM-R1 marker + on-disk match. |
| `stats/bootstrap.py` | `test_stats.py` | Constant data, single-cluster degeneracy, empty NaN, balanced sample brackets. |
| `stats/tehr.py` | `test_stats.py` | Basic, NaN guard, mismatched lengths, CI brackets. |
| `stats/paired_mcnemar.py` | `test_stats.py` | Hand reference, [0,1] parametric, symmetry, Holm pattern + order preservation + empty, pooled. |
| `stats/tost.py` | `test_stats.py` | Identical→non_inferior (2 forms), length mismatch, effective_n. |
| `stats/probe_friedman.py` | `test_stats.py` | No-difference, clear-difference, mismatch, too-few-groups. |
| `stats/gap_closure.py` | `test_stats.py` | Threshold boundary, normal case, finite CI, undefined-denom warning. |
| `stats/__init__.py` | `test_stats.py::test_condition_alias_roundtrip` | Roundtrip + C0_7 alias. |
| `bench_loaders/bfcl.py` | `test_bfcl_loader.py` | 11 synthetic + 2 real-data tests. |
| `bench_loaders/tau_bench.py` | `test_tau_bench_loader.py` | 6 loader + 4 simulator tests. |

Test runs (verified locally): 72 M-owned + 56 Phase-1 = **128 tests pass, 1 skipped**.
No paid API calls in any test — all SDK paths mocked or use `litellm` skipif.

## Top-5 must-fix code issues

1. **MINOR — `harness/bench_loaders/bfcl.py:39` and `tau_bench.py:29`**: hard-coded
   absolute paths embed the developer username `cero`. *Fix*: read from
   `os.environ.get("ICML_BFCL_DIR")` (resp. `ICML_TAU_DIR`) with the current
   string as the dev fallback, then update tests + manifest accordingly.
   Required before camera-ready code release; not a research-correctness blocker.
2. **MINOR — `gap_closure.py:148-149`**: `max(1e-12, 1.0 - a_hat * (z0 + zL))`
   silently floors a negative denominator, which can flip the BCa adjustment
   sign for extreme `a_hat`. *Fix*: detect `1.0 - a_hat * (z0 + zq) <= 0` and
   fall back to percentile (the same fallback `bootstrap.py` uses at L98-100).
   Synthetic test passes today but the failure mode is silent on real data.
3. **MINOR — `mlx_adapter.py:208-209`**: `tokens_in = len(self._tokenizer.encode(prompt))`
   re-tokenises a prompt that was already tokenised by `apply_chat_template`,
   doubling cold-CPU cost on every call. *Fix*: thread `return_tensors=False`
   through `apply_chat_template(... tokenize=True ...)` once and reuse the
   token list. Not a correctness bug; performance-only.
4. **MINOR — `openai_adapter.py:155-163`**: `finish_reason` mapping silently
   passes `"length"` and `"stop"` through but downstream (Anthropic) emits
   `"stop"` for `"end_turn"`. Trivial drift across adapters. *Fix*: add
   `"function_call" → "tool_use"` (legacy) and document in the docstring
   that Anthropic and OpenAI both emit `"stop"` and `"length"`.
5. **MINOR — `repro_manifest.py:46-60`**: `_git_commit` uses
   `Path(__file__).resolve().parent` which works only for in-tree runs;
   if the harness is installed via `uv pip install`, this returns the
   site-packages path and fails silently. *Fix*: prefer
   `subprocess.run([..., "rev-parse", "HEAD"], cwd=Path.cwd(), ...)` or accept
   an explicit `repo_dir` arg.

No BLOCKER or MAJOR issues found.

## Code-quality verdict
**LANDS-WITH-FIXES.**

The harness implementation is research-grade: API contract harmonised across
all three adapters, decoding lock enforced via shared base constants and
verified by mock-call assertions in every adapter test, BFCL schema
normalization is recursive + idempotent + guarded at validation time, cost
meter convention is documented at the parameter name and arithmetic is
correct, BCa bootstrap follows Efron (1987) including jackknife
acceleration with proper cluster handling, mid-p McNemar matches the
hand-derived reference to 1e-6, all 128 unit tests pass, no paid API calls
in any test, and `grep akash` is clean. Plan adherence is high: HARNESS_SPEC §2
shapes are honoured, ADDENDUM_R1 §B.2 (C0.7) and §D.1 (decoding lock) are
implemented, §C.2/C.3/C.4/C.6 statistical guards are present.

The five must-fix items are all MINOR — username paths in defaults
(deanonymisation hygiene, fixable in 30 minutes), an extreme-edge BCa
denominator floor, a tokenisation perf wart, finish-reason cosmetic
inconsistency, and a manifest cwd assumption. None of them bias the
TEHR/CI numbers the paper depends on. Recommend landing the harness as
the experimental scaffold for the SCALE @ ICML 2026 submission and
opening one follow-up PR for the must-fix list before camera-ready.

## Top-3 must-fix (for inline reply)
1. Parameterise the `/Users/cero/...` BFCL and τ-bench `DEFAULT_DATA_DIR` constants
   via env vars (deanonymisation hygiene; `bfcl.py:39`, `tau_bench.py:29`).
2. Replace `max(1e-12, 1 - a_hat*(z0+z))` with an explicit fallback to
   percentile when the BCa denominator is non-positive (`gap_closure.py:148-149`).
3. Stop double-tokenising the rendered prompt in `MLXAdapter.dispatch`
   (`mlx_adapter.py:208-209`) — fold `tokenize=True` through `apply_chat_template`.
