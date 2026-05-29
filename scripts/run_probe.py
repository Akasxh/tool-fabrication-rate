"""§6 controlled distractor probe.

Takes BFCL multi_turn_base tasks, injects ONE synthetic distractor tool of a
chosen type (near_name / synonym / matched_random / unrelated) into the
registry, re-runs through the existing harness, measures TEHR.

The hypothesis: TEHR ≈ 0% on the unmodified registries (we measured this);
TEHR rises sharply when the agent is offered a tool that is lexically or
semantically similar to a tool the task needs.

Usage:
    PYTHONPATH=. python scripts/run_probe.py \\
        --models claude-haiku-4-5 \\
        --distractor-types near_name,synonym,matched_random \\
        --n 25 \\
        --condition C0 \\
        --run-id probe_$(date +%s)
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import sys
import uuid
from dataclasses import replace
from pathlib import Path


def _stable_seed(s: str) -> int:
    """Process-stable hash of a string. Python's built-in hash() is salted by
    PYTHONHASHSEED per process; this function returns a deterministic int."""
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:4], "big")

# Distractor generators -------------------------------------------------------

def _near_name(real: str) -> str:
    """Generate a name at Levenshtein 1-2 from `real`."""
    rng = random.Random(_stable_seed(real))
    transformations = [
        lambda s: s + "s" if not s.endswith("s") else s[:-1],
        lambda s: s[:-1] + "_v2" if "_" not in s else s.replace("_", "", 1),
        lambda s: s.upper()[:1] + s[1:],
        lambda s: s + "_async",
        lambda s: "_" + s,
    ]
    bad = rng.choice(transformations)(real)
    if bad == real or not bad:
        bad = real + "x"
    return bad


def _synonym(real: str) -> str:
    swaps = {"get_": "fetch_", "fetch_": "retrieve_", "set_": "update_",
             "create_": "make_", "delete_": "remove_", "list_": "enumerate_",
             "send_": "dispatch_"}
    for prefix, sub in swaps.items():
        if real.startswith(prefix):
            return sub + real[len(prefix):]
    return f"alt_{real}"


def _matched_random(real_names: list[str], rng: random.Random) -> str:
    avg_len = max(4, sum(len(n) for n in real_names) // max(1, len(real_names)))
    chars = "abcdefghijklmnopqrstuvwxyz_"
    return "".join(rng.choices(chars, k=avg_len)) + "_tool"


def _unrelated(rng: random.Random) -> str:
    return rng.choice(["xyzzy_query", "plover_handle", "frob_widget", "zorch_state"])


def make_distractor_schema(name: str, description_len: int, arity: int) -> dict:
    """Build a JSON-Schema-2020-12-compliant tool schema with given description
    length and parameter arity (so matched_random matches the average shape of
    real registry entries). Description is repetitive filler text.
    """
    # Description filler (kept close to real BFCL description length).
    desc_words = ["operation", "subroutine", "utility", "auxiliary"]
    desc = " ".join(desc_words * (max(1, description_len // 32) + 1))[:description_len]
    properties = {f"arg{i}": {"type": "string"} for i in range(arity)}
    return {
        "name": name,
        "description": desc,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": [],
        },
    }


def _inner_schema(schema: dict) -> dict:
    """Return the canonical-inner view of a tool schema. BFCL emits
    canonical-inner ({name, description, parameters}); τ-bench emits the OpenAI
    wrapper ({type:"function", function:{...}}). desc/arity must be read from
    the inner fields in both cases so matched_random distractors match shape."""
    if schema.get("type") == "function" and isinstance(schema.get("function"), dict):
        return schema["function"]
    return schema


def inject(task, distractor_type: str, rng: random.Random,
           remove_target: bool = False):
    """Return a new Task with one distractor tool added to the registry.

    If remove_target=True, the picked target real tool is REMOVED from the
    registry and the distractor is added in its place — this reproduces the
    Czapla-style scenario where the agent expects a tool to exist but the
    registry only offers a near-similar one.

    Benchmark-agnostic: handles both BFCL canonical-inner registries and
    τ-bench OpenAI-wrapper registries. The injected distractor is always
    canonical-inner; the runner's tau path flattens the whole registry to
    canonical-inner before classification, so mixing shapes is safe.
    """
    if not task.registry:
        return task

    real_names = list(task.registry.keys())
    target = rng.choice(real_names)
    inner = _inner_schema(task.registry[target])
    desc_len = len(inner.get("description", "") or "")
    arity = len(inner.get("parameters", {}).get("properties", {}) or {})

    if distractor_type == "near_name":
        bad = _near_name(target)
    elif distractor_type == "synonym":
        bad = _synonym(target)
    elif distractor_type == "matched_random":
        bad = _matched_random(real_names, rng)
    else:
        bad = _unrelated(rng)

    suffix = 0
    while bad in task.registry:
        suffix += 1
        bad = f"{bad}{suffix}"

    new_registry = dict(task.registry)
    if remove_target:
        new_registry.pop(target, None)
    new_registry[bad] = make_distractor_schema(bad, desc_len, arity)
    return replace(
        task,
        id=f"{task.id}__{distractor_type}{'__rm' if remove_target else ''}",
        registry=new_registry,
        expected_outcome={**(task.expected_outcome or {}),
                          "_probe_distractor_type": distractor_type,
                          "_probe_distractor_name": bad,
                          "_probe_target_real_tool": target,
                          "_probe_remove_target": remove_target},
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run_probe")
    p.add_argument("--models", required=True,
                   help="Comma-separated model IDs (must be Anthropic for now).")
    p.add_argument("--distractor-types", default="near_name,synonym,matched_random,unrelated")
    p.add_argument("--n", type=int, default=25)
    p.add_argument("--condition", default="C0", choices=["C0", "C0_5", "A2", "C0_7", "C0_8", "C1"])
    p.add_argument("--run-id", default=None)
    p.add_argument("--output", default="results")
    p.add_argument("--benchmark", default="bfcl", choices=["bfcl", "tau_bench"],
                   help="Which benchmark's Tasks to probe. tau_bench loads the "
                        "Sierra retail tasks (a genuinely different, non-zero-base "
                        "benchmark) and uses the τ-bench env-step executor + "
                        "Haiku user simulator.")
    p.add_argument("--bfcl-split", default="multi_turn_base")
    p.add_argument("--tau-split", default="test",
                   help="τ-bench split: test (115), dev (20), train (500).")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--remove-target", action="store_true",
                   help="Also remove the real target tool the distractor mimics. "
                        "Reproduces Czapla-style scenario where the model expects a "
                        "tool that exists in the runtime but not in the provided registry.")
    args = p.parse_args(argv)

    from harness.runner.executors import make_bfcl_executor, make_tau_bench_executor
    from harness.runner.loop import run_task
    from harness.cost_meter import CostMeter
    from harness.trace_logger import TraceLogger
    from harness.repro_manifest import generate_manifest

    def _make_adapter(model_id: str):
        if model_id.startswith("claude"):
            from harness.adapters.anthropic_adapter import AnthropicAdapter
            return AnthropicAdapter(model_id)
        if model_id.startswith("gpt") or model_id.startswith("grok"):
            from harness.adapters.openai_adapter import OpenAIAdapter
            base_url = "https://api.x.ai/v1" if model_id.startswith("grok") else None
            return OpenAIAdapter(model_id, base_url=base_url)
        # MLX or any HuggingFace-style repo id
        from harness.adapters.mlx_adapter import MLXAdapter
        return MLXAdapter(model_id)

    run_id = args.run_id or f"probe_{uuid.uuid4().hex[:8]}"
    run_dir = Path(args.output) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    distractor_types = [t.strip() for t in args.distractor_types.split(",") if t.strip()]
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    generate_manifest(
        run_id=run_id,
        n_per_cell={"probe": args.n},
        conditions=[args.condition],
        out_path=run_dir / "repro_manifest.json",
    )

    if args.benchmark == "tau_bench":
        from harness.bench_loaders.tau_bench import load_tau_bench_retail
        base_tasks = list(load_tau_bench_retail(n=args.n, seed=args.seed,
                                                split=args.tau_split))
        split_label = f"tau_{args.tau_split}"
        make_executor = make_tau_bench_executor
    else:
        from harness.bench_loaders.bfcl import load_bfcl
        base_tasks = list(load_bfcl(n=args.n, seed=args.seed, split=args.bfcl_split))
        split_label = args.bfcl_split
        make_executor = make_bfcl_executor
    print(f"Loaded {len(base_tasks)} base tasks from {split_label} "
          f"(benchmark={args.benchmark}).", file=sys.stderr)
    print(f"Distractor types: {distractor_types}", file=sys.stderr)
    print(f"Models: {models}", file=sys.stderr)
    print(f"Condition: {args.condition}", file=sys.stderr)

    summary: dict[str, dict] = {}
    for model in models:
        adapter = _make_adapter(model)
        meter = CostMeter(budget_usd=400.0)
        model_slug = model.replace("/", "_")
        for dtype in distractor_types:
            cell_key = f"{model_slug}_{split_label}_{args.condition}_{dtype}"
            trace_path = run_dir / f"{cell_key}.jsonl"
            cell_summary = {"runs": 0, "tehr_num": 0, "tehr_denom": 0, "passes": 0}
            print(f"\n[{cell_key}] dispatching n={args.n} (distractor={dtype})…",
                  file=sys.stderr)
            logger = TraceLogger(trace_path)
            try:
                rng = random.Random((args.seed + _stable_seed(dtype)) & 0xFFFF)
                for base_task in base_tasks:
                    probe_task = inject(base_task, dtype, rng,
                                         remove_target=args.remove_target)
                    try:
                        executor = make_executor(probe_task)
                    except Exception as exc:
                        print(f"  executor failed: {exc}", file=sys.stderr)
                        continue
                    try:
                        res = run_task(probe_task, adapter, args.condition,
                                       logger, meter, executor)
                    except Exception as exc:
                        print(f"  run_task crashed on {probe_task.id}: "
                              f"{type(exc).__name__}: {exc}", file=sys.stderr)
                        continue
                    cell_summary["runs"] += 1
                    cell_summary["tehr_num"] += res.get("tehr_num", 0)
                    cell_summary["tehr_denom"] += res.get("tehr_denom", 0)
                    if res.get("pass", False):
                        cell_summary["passes"] += 1
            finally:
                logger.close()
            summary[cell_key] = cell_summary
            tn, td = cell_summary["tehr_num"], cell_summary["tehr_denom"]
            tehr = (tn / td) if td else float("nan")
            print(f"  done: runs={cell_summary['runs']} tehr={tn}/{td}={tehr:.3f} "
                  f"pass={cell_summary['passes']} spend=${meter.total():.4f}",
                  file=sys.stderr)

    print(f"\n=== probe {run_id} complete ===", file=sys.stderr)
    for k, s in summary.items():
        td = s["tehr_denom"]
        tehr = s["tehr_num"]/td if td else float("nan")
        print(f"  {k}: tehr={s['tehr_num']}/{td}={tehr:.3f} pass={s['passes']}/{s['runs']}",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
