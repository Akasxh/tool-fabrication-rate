"""Registry-size ablation: addresses production-engineer reviewer's #1 ask.

Inflates the BFCL multi_turn_base registry with N - |R_real| synthetic
length-and-arity-matched random tools, then re-runs the probe at three
target sizes: 25 (baseline), 100, 250. Measures TEHR and RVR overhead
at each.

Output: results/registry_size_<TS>/<size>_C0/*.jsonl plus a summary table.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import string
import sys
import uuid
from dataclasses import replace
from pathlib import Path


def _stable_seed(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:4], "big")


def _random_tool_name(rng: random.Random, used: set, length: int = 8) -> str:
    while True:
        n = "tool_" + "".join(rng.choices(string.ascii_lowercase, k=length))
        if n not in used:
            return n


def _make_synthetic_tool(name: str, arity: int = 2) -> dict:
    return {
        "name": name,
        "description": "synthetic noise tool for registry-size ablation",
        "parameters": {
            "type": "object",
            "properties": {f"arg{i}": {"type": "string"} for i in range(arity)},
            "required": [],
        },
    }


def inflate_registry(task, target_size: int, rng: random.Random):
    """Add (target_size - len(registry)) synthetic noise tools to the
    registry. Existing tools (including any prior distractor) are preserved."""
    if not task.registry or len(task.registry) >= target_size:
        return task
    new_registry = dict(task.registry)
    used = set(new_registry.keys())
    while len(new_registry) < target_size:
        n = _random_tool_name(rng, used)
        new_registry[n] = _make_synthetic_tool(n, arity=rng.choice([0, 1, 2, 3]))
        used.add(n)
    return replace(task, registry=new_registry,
                   id=f"{task.id}__rsize{target_size}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="run_registry_size")
    p.add_argument("--model", default="mlx-community/Qwen3-8B-4bit")
    p.add_argument("--target-sizes", default="25,100,250",
                   help="Comma-separated target registry sizes")
    p.add_argument("--n", type=int, default=10,
                   help="Number of multi_turn_base tasks per cell")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--run-id", default=None)
    p.add_argument("--output", default="results")
    args = p.parse_args(argv)

    from harness.bench_loaders.bfcl import load_bfcl
    from harness.runner.executors import make_bfcl_executor
    from harness.runner.loop import run_task
    from harness.cost_meter import CostMeter
    from harness.trace_logger import TraceLogger

    if args.model.startswith("claude"):
        from harness.adapters.anthropic_adapter import AnthropicAdapter
        adapter = AnthropicAdapter(args.model)
    else:
        from harness.adapters.mlx_adapter import MLXAdapter
        adapter = MLXAdapter(args.model)

    run_id = args.run_id or f"registry_size_{uuid.uuid4().hex[:8]}"
    run_dir = Path(args.output) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    target_sizes = [int(x) for x in args.target_sizes.split(",") if x]
    base_tasks = list(load_bfcl(n=args.n, seed=args.seed,
                                 split="multi_turn_base"))
    print(f"Loaded {len(base_tasks)} base tasks", file=sys.stderr)

    summary = {}
    for target in target_sizes:
        cell_key = f"size_{target}"
        cell_summary = {"runs": 0, "tehr_num": 0, "tehr_denom": 0,
                         "passes": 0, "registry_size": target,
                         "tokens_in_per_turn": [], "tokens_out_per_turn": []}
        trace_path = run_dir / f"{cell_key}.jsonl"
        logger = TraceLogger(trace_path)
        meter = CostMeter(budget_usd=10.0)
        rng = random.Random(_stable_seed(f"{args.seed}_{target}"))
        try:
            for base_task in base_tasks:
                inflated = inflate_registry(base_task, target, rng)
                actual_size = len(inflated.registry)
                cell_summary["registry_size"] = actual_size
                try:
                    executor = make_bfcl_executor(inflated)
                except Exception as e:
                    print(f"  executor fail: {e}", file=sys.stderr)
                    continue
                try:
                    res = run_task(inflated, adapter, "C0", logger, meter, executor)
                except Exception as e:
                    print(f"  task crash on {inflated.id}: {type(e).__name__}", file=sys.stderr)
                    continue
                cell_summary["runs"] += 1
                cell_summary["tehr_num"] += res.get("tehr_num", 0)
                cell_summary["tehr_denom"] += res.get("tehr_denom", 0)
                if res.get("pass", False):
                    cell_summary["passes"] += 1
        finally:
            logger.close()
        td = cell_summary["tehr_denom"]
        tehr = cell_summary["tehr_num"] / td if td else 0
        print(f"[size={target} actual={cell_summary['registry_size']}] "
              f"runs={cell_summary['runs']} tehr={cell_summary['tehr_num']}/{td}={tehr:.3f} "
              f"pass={cell_summary['passes']}/{cell_summary['runs']}",
              file=sys.stderr)
        summary[cell_key] = cell_summary

    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== registry-size sweep {run_id} complete ===", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
