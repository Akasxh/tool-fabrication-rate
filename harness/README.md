# tehr-harness

## What this is
Experimental harness for the **TFR** (Tool Fabrication Rate; formerly TEHR) study
submitted to **SCALE @ ICML 2026**. It runs a fixed matrix of (model × benchmark
× condition) cells against BFCL v4 multi-turn and τ-bench retail, emits per-turn
JSONL traces, and computes the headline statistics (paired McNemar mid-p,
TOST/paired-CI non-inferiority, BCa-cluster-bootstrap CIs, Friedman + Nemenyi
for the §6 distractor probe).

## Quickstart

```bash
# 1. Install (uv-managed; Python 3.12 required).
uv pip install -e ".[dev]"

# 2. Export provider credentials.
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export HF_TOKEN=...   # for MLX/Qwen3 weights mirror

# 3. Pilot run (small N for smoke testing).
tehr-run --pilot
```

Full main run: `tehr-run --full` (writes JSONL + `repro_manifest.json` to
`results/<run_id>/`).

## Conditions

| Label  | JSONL key | Description |
|--------|-----------|-------------|
| C0     | `C0`      | ReAct, raw framework error on bad call (opaque) |
| C0.5   | `C0_5`    | Naive retry: "previous failed, try again" — no registry |
| C0.7   | `C0_7`    | Framework-style structured-error JSON — no registry list |
| C1     | `C1`      | RVR: re-prompt with the full registry list |

Primary statistical test: paired McNemar(C1 vs C0.7) on the strict subset of
C0-failed-with-hallucination tasks, pooled across the four API tiers.

## Layout

```
harness/
  types.py         shared dataclasses (Task, ToolCall, ProviderResponse, Action)
  registry.py      registry helpers + _normalize_bfcl_schema
  adapters/        Anthropic / OpenAI+xAI / MLX
  bench_loaders/   BFCL + τ-bench
  intervention/    RVR, naive retry, framework-default
  runner/          ReAct loop, condition dispatch, CLI
  stats/           TFR, paired McNemar, TOST, bootstrap, Friedman
  tests/           pytest suite + fixtures
```

## License

Apache-2.0; see the repo-root [`LICENSE`](../LICENSE) file.
