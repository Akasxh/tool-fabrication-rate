"""B4 downstream-utility analysis: per-(model, condition) task-success proxy,
abstention, re-prompt overhead, turns, and latency — computed from JSONL traces.

Answers the reviewer objection that TEHR ignores latency / abstention / pass-rate
by quantifying what RVR (C1) and the structured envelope (C0.7) cost vs the
opaque baseline (C0) on the same tasks.

Pass proxy (BFCL): a task passes if no executor error appears in any
tool_response and no turn timed out (mirrors loop.py's pass criterion; the
official trajectory-equivalence scorer is a deferred Phase-2 step).

Usage:
    PYTHONPATH=. python scripts/analyze_utility.py [--model SUBSTR] [--probe-only]
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path

ROOTS = ["results", "paper/results"]


def load_records() -> list[dict]:
    recs = []
    for root in ROOTS:
        for f in glob.glob(f"{root}/**/*.jsonl", recursive=True):
            for line in open(f):
                line = line.strip()
                if line:
                    try:
                        recs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return recs


def is_probe(task_id: str) -> bool:
    return any(s in task_id for s in
               ("__rm", "__near_name", "__synonym", "__matched_random", "__unrelated"))


def metrics(records: list[dict]) -> dict:
    by_task: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_task[r["task_id"]].append(r)
    n = len(by_task)
    halluc = sum(1 for r in records if r["tool_call_status"] == "hallucinated")
    denom = sum(1 for r in records
                if r["tool_call_status"] in ("hallucinated", "parse_fail")
                or (r["tool_call_status"] == "executed" and r.get("parsed_tool_call")))
    refused = sum(1 for r in records if r["tool_call_status"] == "refused")
    reprompts = sum(1 for r in records if r.get("intervention_event"))
    passes = sum(
        1 for _, rs in by_task.items()
        if not any(isinstance(r.get("tool_response"), dict) and "error" in r["tool_response"]
                   for r in rs)
        and not any(r["tool_call_status"] == "timed_out" for r in rs)
    )
    lat = sum(int(r.get("latency_ms", 0)) for r in records)
    return dict(
        n_tasks=n, n_calls=denom, halluc=halluc,
        tehr=(halluc / denom) if denom else float("nan"),
        pass_proxy=(passes / n) if n else float("nan"),
        abstain=(refused / n) if n else float("nan"),
        reprompts=reprompts,
        turns_per_task=(len(records) / n) if n else float("nan"),
        latency_ms_per_task=(lat / n) if n else float("nan"),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="", help="substring filter on model id")
    ap.add_argument("--probe-only", action="store_true")
    args = ap.parse_args()

    recs = load_records()
    if args.model:
        recs = [r for r in recs if args.model in r["model"]]
    if args.probe_only:
        recs = [r for r in recs if is_probe(r["task_id"])]

    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in recs:
        cells[(r["model"], r["condition"])].append(r)

    print(f"{'model':38s} {'cond':5s} {'tasks':>5s} {'TEHR':>7s} {'pass':>6s} "
          f"{'abst':>5s} {'rprmt':>5s} {'turns':>6s} {'lat/task(ms)':>12s}")
    for (model, cond) in sorted(cells):
        m = metrics(cells[(model, cond)])
        short = model.split("/")[-1]
        print(f"{short:38s} {cond:5s} {m['n_tasks']:5d} "
              f"{m['tehr']*100:6.2f}% {m['pass_proxy']*100:5.1f}% "
              f"{m['abstain']*100:4.1f}% {m['reprompts']:5d} "
              f"{m['turns_per_task']:6.2f} {m['latency_ms_per_task']:12.0f}")

    # Condition deltas vs C0, per model
    print("\n=== Δ vs C0 (per model) ===")
    by_model: dict[str, dict[str, dict]] = defaultdict(dict)
    for (model, cond), rs in cells.items():
        by_model[model][cond] = metrics(rs)
    for model in sorted(by_model):
        if "C0" not in by_model[model]:
            continue
        base = by_model[model]["C0"]
        short = model.split("/")[-1]
        for cond in ("C0_5", "C0_7", "C0_8", "C1"):
            if cond not in by_model[model]:
                continue
            c = by_model[model][cond]
            print(f"{short:30s} {cond:5s}  Δpass={100*(c['pass_proxy']-base['pass_proxy']):+5.1f}pp "
                  f"Δabstain={100*(c['abstain']-base['abstain']):+4.1f}pp "
                  f"Δturns={c['turns_per_task']-base['turns_per_task']:+5.2f} "
                  f"ΔTEHR={100*(c['tehr']-base['tehr']):+5.2f}pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
