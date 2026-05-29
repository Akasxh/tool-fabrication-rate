"""``tehr-run`` CLI entry point (HARNESS_SPEC §1 + ADDENDUM §D.2).

argparse-based; plans a (model × benchmark × condition) matrix and writes a
reproducibility manifest. ``--dry-run`` prints the plan without dispatching.

Modes:
    --pilot   4 API × 25 BFCL × C0+C1
    --main    4 API + 1 MLX × (50 BFCL + 25 τ-bench) × all 4 conditions
    --probe   §6 distractor probe (BFCL only)
"""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Iterable

from harness.cost_meter import CostMeter, BudgetAbort
from harness.repro_manifest import generate_manifest
from harness.trace_logger import TraceLogger

_PILOT_MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5", "gpt-4.1", "gpt-4.1-mini"]
_MAIN_MODELS = _PILOT_MODELS + ["mlx-community/Qwen3-8B-4bit"]
_MAIN_CONDITIONS = ["C0", "C0_5", "C0_7", "C1"]
_BUDGET_USD: dict[str, float] = {
    "anthropic": 400.0, "openai": 2000.0, "xai": 2000.0, "local": 10.0,
}


def _provider_for_model(model_id: str) -> str:
    if model_id.startswith("claude"):
        return "anthropic"
    if model_id.startswith("gpt"):
        return "openai"
    if model_id.startswith("grok"):
        return "xai"
    return "local"


def _matrix(args: argparse.Namespace) -> list[tuple[str, str, str]]:
    benchmarks = ["bfcl", "tau_bench"] if args.benchmark in (None, "all") else [args.benchmark]
    return [(m, b, c) for m in args.models for b in benchmarks for c in args.conditions]


def _make_cost_meters(models: Iterable[str]) -> dict[str, CostMeter]:
    meters: dict[str, CostMeter] = {}
    for m in models:
        prov = _provider_for_model(m)
        if prov in meters:
            continue
        meters[prov] = CostMeter(
            budget_usd=_BUDGET_USD.get(prov, 100.0),
            on_threshold=lambda spent, p=prov: print(
                f"[cost-meter] {p} reached 90% threshold: ${spent:.2f}", file=sys.stderr),
        )
    return meters


def _plan_summary(cells: list[tuple[str, str, str]], n: int) -> str:
    lines = [f"Dispatch matrix: {len(cells)} cells × n={n} tasks each"]
    for model, bench, cond in cells:
        lines.append(f"  - model={model:<32s} benchmark={bench:<10s} condition={cond}")
    return "\n".join(lines)


def _csv(s: str) -> list[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tehr-run",
                                description="TEHR experimental runner (SCALE @ ICML 2026).")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--main", action="store_true")
    mode.add_argument("--probe", action="store_true")
    p.add_argument("--models", type=_csv, default=None)
    p.add_argument("--benchmark", choices=["bfcl", "tau_bench", "all"], default=None)
    p.add_argument("--bfcl-split", default="multi_turn_base",
                   choices=["multi_turn_base", "multi_turn_long_context",
                            "multi_turn_miss_func", "multi_turn_miss_param"],
                   help="BFCL multi-turn split. miss_func deliberately removes a needed "
                        "function and is the right setting to elicit tool-existence hallucination.")
    p.add_argument("--conditions", type=_csv, default=None)
    p.add_argument("--n", type=int, default=None)
    p.add_argument("--output", type=Path, default=Path("results"))
    p.add_argument("--resume", default=None, help="Phase-2; no-op.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--run-id", default=None)
    return p


_MODE_DEFAULTS: dict[str, tuple[list[str], str, list[str], int]] = {
    "main":  (_MAIN_MODELS,  "all",  _MAIN_CONDITIONS, 50),
    "probe": (_MAIN_MODELS,  "bfcl", ["C0"],            100),
    "pilot": (_PILOT_MODELS, "bfcl", ["C0", "C1"],      25),
}


def _apply_mode_defaults(args: argparse.Namespace) -> None:
    mode = "main" if args.main else "probe" if args.probe else "pilot"
    if mode == "pilot":
        args.pilot = True
    models, bench, conds, n = _MODE_DEFAULTS[mode]
    args.models = args.models or list(models)
    args.benchmark = args.benchmark or bench
    args.conditions = args.conditions or list(conds)
    args.n = args.n if args.n is not None else n


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _apply_mode_defaults(args)

    run_id = args.run_id or str(uuid.uuid4())
    run_dir = Path(args.output) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = run_dir / "repro_manifest.json"
    generate_manifest(
        run_id=run_id,
        n_per_cell={"bfcl": args.n, "tau_bench": args.n, "probe": args.n},
        conditions=list(args.conditions),
        out_path=manifest_path,
    )

    cells = _matrix(args)
    print(_plan_summary(cells, args.n))
    print(f"manifest: {manifest_path}")
    print(f"run_dir:  {run_dir}")

    if args.dry_run:
        print("(dry-run: no adapters constructed, no API calls dispatched)")
        return 0

    # Real dispatch path
    cost_meters = _make_cost_meters(args.models)
    adapters_cache: dict[str, object] = {}

    def _get_adapter(model_id: str):
        if model_id in adapters_cache:
            return adapters_cache[model_id]
        provider = _provider_for_model(model_id)
        if provider == "anthropic":
            from harness.adapters.anthropic_adapter import AnthropicAdapter
            inst = AnthropicAdapter(model_id)
        elif provider == "openai":
            from harness.adapters.openai_adapter import OpenAIAdapter
            inst = OpenAIAdapter(model_id)
        elif provider == "xai":
            from harness.adapters.openai_adapter import OpenAIAdapter
            inst = OpenAIAdapter(model_id, base_url="https://api.x.ai/v1")
        elif provider == "local":
            from harness.adapters.mlx_adapter import MLXAdapter
            inst = MLXAdapter(model_id)
        else:
            raise ValueError(f"Unknown provider for model {model_id!r}")
        adapters_cache[model_id] = inst
        return inst

    def _load_tasks(bench: str, n: int):
        if bench == "bfcl":
            from harness.bench_loaders.bfcl import load_bfcl
            return list(load_bfcl(n=n, seed=0, split=args.bfcl_split))
        if bench == "tau_bench":
            from harness.bench_loaders.tau_bench import load_tau_bench_retail
            return list(load_tau_bench_retail(n=n, seed=0))
        raise ValueError(f"Unknown benchmark {bench!r}")

    def _make_executor(task):
        from harness.runner.executors import make_bfcl_executor, make_tau_bench_executor
        if task.benchmark == "bfcl":
            return make_bfcl_executor(task)
        return make_tau_bench_executor(task)

    from harness.runner.loop import run_task

    summary: dict[str, dict] = {}
    aborted = False
    for model, bench, cond in cells:
        if aborted:
            break
        provider = _provider_for_model(model)
        slug = model.replace("/", "_")
        cell_key = f"{provider}_{slug}_{bench}_{cond}"
        trace_path = run_dir / f"{cell_key}.jsonl"
        cell_summary = {"runs": 0, "passes": 0, "tehr_num": 0, "tehr_denom": 0,
                        "system_failures": 0, "budget_aborted": False}
        print(f"\n[{cell_key}] dispatching n={args.n}…", file=sys.stderr)
        try:
            adapter = _get_adapter(model)
        except Exception as exc:
            print(f"  adapter init failed: {exc}", file=sys.stderr)
            summary[cell_key] = cell_summary
            continue
        cost_meter = cost_meters[provider]
        try:
            tasks = _load_tasks(bench, args.n)
        except Exception as exc:
            print(f"  task load failed: {exc}", file=sys.stderr)
            summary[cell_key] = cell_summary
            continue
        logger = TraceLogger(trace_path)
        try:
            for task in tasks:
                try:
                    executor = _make_executor(task)
                except Exception as exc:
                    print(f"  executor build failed for {task.id}: {exc}", file=sys.stderr)
                    cell_summary["system_failures"] += 1
                    continue
                try:
                    res = run_task(task=task, adapter=adapter, condition=cond,
                                   logger=logger, cost_meter=cost_meter,
                                   tool_executor=executor)
                except BudgetAbort:
                    print(f"  BUDGET ABORT for provider={provider} after {cell_summary['runs']} task(s)",
                          file=sys.stderr)
                    cell_summary["budget_aborted"] = True
                    aborted = True
                    break
                except Exception as exc:
                    print(f"  run_task crashed on {task.id}: {type(exc).__name__}: {exc}",
                          file=sys.stderr)
                    cell_summary["system_failures"] += 1
                    continue
                cell_summary["runs"] += 1
                cell_summary["tehr_num"] += res.get("tehr_num", 0)
                cell_summary["tehr_denom"] += res.get("tehr_denom", 0)
                if res.get("pass", False):
                    cell_summary["passes"] += 1
                if res.get("terminal") in {"timed_out", "system_failure"}:
                    cell_summary["system_failures"] += 1
        finally:
            logger.close()
        summary[cell_key] = cell_summary
        passes = cell_summary["passes"]; runs = cell_summary["runs"]
        tn, td = cell_summary["tehr_num"], cell_summary["tehr_denom"]
        tehr = (tn / td) if td > 0 else float("nan")
        spend = cost_meter.total()
        print(f"  done: {runs} runs, {passes} pass, TEHR={tn}/{td}={tehr:.3f}, "
              f"spend={spend:.4f}USD ({provider})", file=sys.stderr)

    print(f"\n=== run {run_id} complete ===", file=sys.stderr)
    for k, s in summary.items():
        print(f"  {k}: {s}", file=sys.stderr)
    for prov, m in cost_meters.items():
        print(f"  cost[{prov}] = ${m.total():.4f}", file=sys.stderr)
    return 0 if not aborted else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
