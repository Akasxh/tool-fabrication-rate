"""Read a run dir's JSONL traces, compute per-cell TEHR + pass-rate + cost,
and print a tabular summary plus a Gate 2 verdict line (TEHR ≥5% on ≥N tiers).

Usage:
    python scripts/analyze_run.py results/<run_id>
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _cell_key(rec: dict) -> str:
    return f"{rec['model']}|{rec['benchmark']}|{rec['condition']}"


def _summarize_cell(records: list[dict]) -> dict:
    n_turns = len(records)
    if n_turns == 0:
        return {"n_turns": 0, "n_tasks": 0, "tehr_num": 0, "tehr_denom": 0,
                "tehr": float("nan"), "passes": 0, "tokens_in": 0,
                "tokens_out": 0, "cost_usd": 0.0,
                "system_failures": 0}
    by_task: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_task[r["task_id"]].append(r)
    n_tasks = len(by_task)

    # TEHR per call (denom = parsed_tool_call != null AND status not refused/parse_fail)
    tehr_num = sum(1 for r in records if r["tool_call_status"] == "hallucinated")
    tehr_denom = sum(1 for r in records
                     if r["tool_call_status"] in ("executed", "hallucinated")
                     and r.get("parsed_tool_call") is not None)
    sys_fail = sum(1 for r in records if r["tool_call_status"] in ("timed_out", "parse_fail", "refused"))

    # Per-task pass: a task is judged passed if its FINAL turn's executor didn't
    # error AND no timeout was logged. Coarse but matches the runner's proxy.
    passes = 0
    for task_id, turns in by_task.items():
        last = turns[-1]
        if last.get("tool_response") and isinstance(last["tool_response"], dict) \
                and "error" in last["tool_response"]:
            continue
        if any(t["tool_call_status"] == "timed_out" for t in turns):
            continue
        passes += 1

    tokens_in = sum(r["tokens_in"] for r in records)
    tokens_out = sum(r["tokens_out"] for r in records)
    cost = sum(r["cost_usd"] for r in records)

    tehr = (tehr_num / tehr_denom) if tehr_denom else float("nan")
    return dict(n_turns=n_turns, n_tasks=n_tasks, tehr_num=tehr_num,
                tehr_denom=tehr_denom, tehr=tehr, passes=passes,
                tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost,
                system_failures=sys_fail)


def main(run_dir: Path) -> int:
    if not run_dir.is_dir():
        print(f"error: {run_dir} is not a directory", file=sys.stderr)
        return 2
    cells: dict[str, dict] = {}
    grand_records: list[dict] = []
    for jsonl in sorted(run_dir.glob("*.jsonl")):
        records = _load_jsonl(jsonl)
        if not records:
            continue
        grand_records.extend(records)
        cells[jsonl.stem] = _summarize_cell(records)

    if not cells:
        print(f"no traces in {run_dir}")
        return 1

    print(f"\nrun_dir: {run_dir}")
    print(f"  total records: {len(grand_records)}")
    print(f"  total cells:   {len(cells)}")

    print(f"\n{'cell':50s}  {'tasks':>5}  {'turns':>5}  {'pass':>4}  "
          f"{'TEHR':>10s}  {'cost':>8}  {'sysfail':>7}")
    print("-" * 110)
    for cell_name in sorted(cells):
        s = cells[cell_name]
        tehr_str = (f"{s['tehr_num']}/{s['tehr_denom']}={s['tehr']:.3f}"
                    if s["tehr_denom"] else f"{s['tehr_num']}/{s['tehr_denom']}=nan")
        print(f"{cell_name[:50]:50s}  {s['n_tasks']:>5d}  {s['n_turns']:>5d}  "
              f"{s['passes']:>4d}  {tehr_str:>10s}  ${s['cost_usd']:>6.3f}  "
              f"{s['system_failures']:>7d}")

    # Gate 2 logic: aggregate TEHR per (model, benchmark) across conditions
    by_model: dict[str, dict] = defaultdict(lambda: {"num": 0, "denom": 0})
    for cell_name, s in cells.items():
        # cell_stem = "{provider}_{model}_{bench}_{condition}"
        parts = cell_name.split("_")
        # Recompose model from possibly-hyphenated chunks; keep up to "_<bench>_<cond>"
        # cells are named "<provider>_<model_with_hyphens>_<bench>_<cond>"
        if len(parts) < 4:
            continue
        model = "_".join(parts[1:-2])
        by_model[model]["num"] += s["tehr_num"]
        by_model[model]["denom"] += s["tehr_denom"]

    print("\nPer-model aggregate TEHR (across conditions):")
    n_above_5pct = 0
    for model, agg in sorted(by_model.items()):
        denom = agg["denom"]
        rate = (agg["num"] / denom) if denom else float("nan")
        flag = " ✓ ≥5%" if denom and rate >= 0.05 else ""
        print(f"  {model:40s}  TEHR={agg['num']:3d}/{agg['denom']:3d}={rate:.3f}{flag}")
        if denom and rate >= 0.05:
            n_above_5pct += 1

    print(f"\nGate 2 (TEHR ≥5% on ≥1 model): {'PASS' if n_above_5pct >= 1 else 'FAIL'}  "
          f"(reached on {n_above_5pct} model(s))")
    if n_above_5pct == 0:
        print("  → consider switching to multi_turn_miss_func split which deliberately")
        print("    removes functions to elicit hallucination.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "results")))
