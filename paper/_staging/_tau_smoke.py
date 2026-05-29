"""One-off τ-bench smoke: n=3 retail tasks on claude-haiku-4-5.
Hard abort if anthropic spend reaches $5 (CostMeter budget). Writes a JSONL
trace + prints a compact per-task summary. Not part of the harness package."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from harness.adapters.anthropic_adapter import AnthropicAdapter
from harness.bench_loaders.tau_bench import load_tau_bench_retail
from harness.cost_meter import BudgetAbort, CostMeter
from harness.runner.executors import make_tau_bench_executor
from harness.runner.loop import run_task
from harness.trace_logger import TraceLogger


def main() -> int:
    n = int(os.environ.get("TAU_SMOKE_N", "3"))
    out_dir = Path("paper/_staging")
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_path = out_dir / "tau_smoke_trace.jsonl"
    if trace_path.exists():  # fresh trace each run
        trace_path.unlink()

    adapter = AnthropicAdapter("claude-haiku-4-5")
    # Shared client for the Haiku user simulator so its cost lands on the SAME
    # ceiling-bound conversation budget is tracked separately by the env; we
    # additionally cap the agent-side meter hard at $5.
    cost_meter = CostMeter(
        budget_usd=5.0,
        on_threshold=lambda s: print(f"[cost] 90% threshold: ${s:.3f}", file=sys.stderr),
    )
    logger = TraceLogger(trace_path)
    tasks = list(load_tau_bench_retail(n=n, seed=0))
    print(f"loaded {len(tasks)} tau-bench retail tasks", file=sys.stderr)

    results = []
    user_sim_cost_total = 0.0
    try:
        for task in tasks:
            try:
                executor = make_tau_bench_executor(
                    task, anthropic_client=adapter._client  # reuse same SDK client
                )
            except Exception as exc:  # noqa: BLE001
                print(f"  executor build failed {task.id}: {exc}", file=sys.stderr)
                results.append({"task": task.id, "error": f"build:{exc}"})
                continue
            st = executor.state
            if not st.get("reset_ok"):
                print(f"  reset failed {task.id}: {st.get('reset_error')}", file=sys.stderr)
                results.append({"task": task.id, "error": f"reset:{st.get('reset_error')}"})
                continue
            try:
                res = run_task(
                    task=task, adapter=adapter, condition="C0",
                    logger=logger, cost_meter=cost_meter, tool_executor=executor,
                )
            except BudgetAbort:
                print("  BUDGET ABORT (>=$5) — stopping", file=sys.stderr)
                results.append({"task": task.id, "error": "budget_abort"})
                break
            env = executor.env
            sim_cost = 0.0
            try:
                sim_cost = float(env.user.get_total_cost())
            except Exception:  # noqa: BLE001
                pass
            user_sim_cost_total += sim_cost
            res2 = dict(res)
            res2.update({"task": task.id, "reward_final": st.get("reward"),
                         "user_sim_cost": round(sim_cost, 4)})
            results.append(res2)
            print(f"  {task.id}: pass={res['pass']} tehr={res['tehr_num']}/{res['tehr_denom']} "
                  f"turns={res['n_turns']} terminal={res['terminal']} reward={st.get('reward')} "
                  f"sim_cost=${sim_cost:.4f}", file=sys.stderr)
    finally:
        logger.close()

    agent_spend = cost_meter.total()
    print("\n=== TAU SMOKE SUMMARY ===")
    for r in results:
        print(" ", r)
    print(f"agent_spend=${agent_spend:.4f} | user_sim_spend=${user_sim_cost_total:.4f} "
          f"| total=${agent_spend + user_sim_cost_total:.4f}")
    print(f"trace: {trace_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
