"""Aggregate every JSONL trace under results/ and compute the final numbers
that fill the paper's [X], [Y], [N] placeholders.

Writes:
    PHASE0/RESULTS/headline_numbers.json  -- machine-readable
    PHASE0/RESULTS/headline_numbers.md    -- human-readable
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


RESULTS_ROOTS = [Path("results"), Path("paper/results")]
OUT_DIR = Path("PHASE0/RESULTS"); OUT_DIR.mkdir(parents=True, exist_ok=True)


def _classify_split_from_run(run_dir: Path) -> tuple[str, str]:
    """Return (run_kind, split). run_kind ∈ {'regime', 'probe', 'smoke'}."""
    name = run_dir.name
    if name.startswith("probe") or name.startswith("qwen3_"):
        return ("probe", "multi_turn_base")
    if name.startswith("supersmoke") or name.startswith("3cf") or name.startswith("8880"):
        return ("smoke", "multi_turn_base")
    if "missfunc" in name or "miss_func" in name:
        return ("regime", "multi_turn_miss_func")
    if "longctx" in name or "long_context" in name:
        return ("regime", "multi_turn_long_context")
    if "anthropic" in name or "pilot" in name:
        return ("regime", "multi_turn_base")
    return ("regime", "multi_turn_base")


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    # Cells: ((run_kind, split, model, condition[, distractor_type]) → list of records)
    cells: dict[tuple, list[dict]] = defaultdict(list)
    run_dirs: list[Path] = []
    for root in RESULTS_ROOTS:
        if not root.exists():
            continue
        run_dirs.extend(p for p in sorted(root.iterdir()) if p.is_dir())
    for run_dir in run_dirs:
        run_kind, split = _classify_split_from_run(run_dir)
        for jsonl in run_dir.rglob("*.jsonl"):
            stem = jsonl.stem
            # stem schemas:
            #   regime: anthropic_<model>_bfcl_<C0|C1>
            #   probe:  anthropic_<model>_<split>_<C0>_<distractor>
            parts = stem.split("_")
            if "_C0_" in stem or "_C1_" in stem or "_C0_5_" in stem or "_C0_7_" in stem:
                # Probe path: ..._<COND>_<distractor>
                # split is usually multi_turn_base
                # Heuristic: last token is distractor (might contain underscores like "matched_random" — handle that)
                # Walk back from stem to find model name and condition.
                # Easiest: split on "_<model>_"... but model has hyphens. Use string ops.
                pass
            # Aggregate by inspecting per-record fields (more robust)
            recs = _load_jsonl(jsonl)
            if not recs:
                continue
            sample = recs[0]
            model = sample["model"]; cond = sample["condition"]
            # Detect probe via task_id suffix
            is_probe = any("__rm" in r["task_id"] or "__near_name" in r["task_id"]
                           or "__synonym" in r["task_id"] or "__matched_random" in r["task_id"]
                           or "__unrelated" in r["task_id"] for r in recs)
            distractor = ""
            if is_probe:
                # Extract distractor type from task IDs
                for r in recs:
                    tid = r["task_id"]
                    for dt in ["near_name", "synonym", "matched_random", "unrelated"]:
                        if f"__{dt}" in tid:
                            distractor = dt
                            break
                    if distractor:
                        break
                key = ("probe", "multi_turn_base", model, cond, distractor)
            else:
                key = (run_kind, split, model, cond, "")
            cells[key].extend(recs)

    # Aggregate stats per cell
    summary = {"cells": [], "totals": {}, "regime": {}, "probe": {}}

    grand_records = []
    for key, records in sorted(cells.items()):
        kind, split, model, cond, distractor = key
        n_calls = sum(1 for r in records if r["tool_call_status"] in ("executed", "hallucinated") and r.get("parsed_tool_call") is not None)
        hallucinated = sum(1 for r in records if r["tool_call_status"] == "hallucinated")
        sys_fail = sum(1 for r in records if r["tool_call_status"] in ("timed_out", "parse_fail", "refused"))
        n_tasks = len({r["task_id"] for r in records})
        cost = sum(r.get("cost_usd", 0) for r in records)
        tokens_in = sum(r.get("tokens_in", 0) for r in records)
        tokens_out = sum(r.get("tokens_out", 0) for r in records)

        # Pass count via per-task last-turn no-error proxy
        by_task: dict[str, list[dict]] = defaultdict(list)
        for r in records:
            by_task[r["task_id"]].append(r)
        passes = 0
        for tid, turns in by_task.items():
            last = turns[-1]
            tr = last.get("tool_response")
            if isinstance(tr, dict) and "error" in tr:
                continue
            if any(t["tool_call_status"] == "timed_out" for t in turns):
                continue
            passes += 1

        cell = {
            "kind": kind, "split": split, "model": model, "condition": cond,
            "distractor": distractor or None,
            "n_tasks": n_tasks, "n_turns": len(records),
            "n_calls": n_calls, "hallucinated": hallucinated,
            "tehr": (hallucinated / n_calls) if n_calls else None,
            "sys_fail": sys_fail, "passes": passes,
            "cost_usd": round(cost, 4),
            "tokens_in": tokens_in, "tokens_out": tokens_out,
        }
        summary["cells"].append(cell)
        grand_records.extend(records)

    # Aggregate by (kind, split, model)
    by_split_model: dict[tuple[str, str, str], dict] = defaultdict(
        lambda: {"n_calls": 0, "hallucinated": 0, "n_tasks": 0, "cost_usd": 0.0})
    for c in summary["cells"]:
        key = (c["kind"], c["split"], c["model"])
        by_split_model[key]["n_calls"] += c["n_calls"]
        by_split_model[key]["hallucinated"] += c["hallucinated"]
        by_split_model[key]["n_tasks"] += c["n_tasks"]
        by_split_model[key]["cost_usd"] += c["cost_usd"]

    for (kind, split, model), agg in by_split_model.items():
        nc = agg["n_calls"]
        agg["tehr"] = (agg["hallucinated"] / nc) if nc else None
        target = summary["regime"] if kind == "regime" else summary["probe"]
        target.setdefault(split, {})[model] = agg

    # Grand totals
    summary["totals"] = {
        "n_cells": len(summary["cells"]),
        "n_records": len(grand_records),
        "n_calls": sum(c["n_calls"] for c in summary["cells"]),
        "hallucinated": sum(c["hallucinated"] for c in summary["cells"]),
        "n_tasks": sum(c["n_tasks"] for c in summary["cells"]),
        "cost_usd": round(sum(c["cost_usd"] for c in summary["cells"]), 4),
    }
    summary["totals"]["tehr"] = (summary["totals"]["hallucinated"] / summary["totals"]["n_calls"]
                                  if summary["totals"]["n_calls"] else None)

    (OUT_DIR / "headline_numbers.json").write_text(json.dumps(summary, indent=2))

    # Human-readable
    md = ["# Headline numbers (auto-generated)\n",
          f"Total cells: {summary['totals']['n_cells']}",
          f"Total tool calls (parsed): {summary['totals']['n_calls']}",
          f"Total hallucinations: {summary['totals']['hallucinated']}",
          f"Aggregate TEHR: {summary['totals']['tehr']!s}",
          f"Total cost: ${summary['totals']['cost_usd']:.3f}\n",
          "## Regime tests (BFCL splits)\n"]
    for split, models in sorted(summary["regime"].items()):
        for model, agg in sorted(models.items()):
            md.append(f"- **{split} / {model}**: TEHR = {agg['hallucinated']}/{agg['n_calls']} "
                      f"= {agg['tehr']!s}; tasks={agg['n_tasks']}; cost=${agg['cost_usd']:.3f}")
    md.append("\n## Probe (controlled-distractor, multi_turn_base, target removed)\n")
    for split, models in sorted(summary["probe"].items()):
        for model, agg in sorted(models.items()):
            md.append(f"- **probe / {model}**: TEHR = {agg['hallucinated']}/{agg['n_calls']} "
                      f"= {agg['tehr']!s}; tasks={agg['n_tasks']}; cost=${agg['cost_usd']:.3f}")

    md.append("\n## Per-cell\n")
    for c in summary["cells"]:
        md.append(f"- {c['kind']:6s} {c['split']:25s} {c['model']:24s} "
                  f"{c['condition']:5s} {c['distractor'] or '':16s} "
                  f"tehr={c['hallucinated']}/{c['n_calls']} pass={c['passes']}/{c['n_tasks']} "
                  f"cost=${c['cost_usd']:.3f}")

    (OUT_DIR / "headline_numbers.md").write_text("\n".join(md))
    print((OUT_DIR / "headline_numbers.md").read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
