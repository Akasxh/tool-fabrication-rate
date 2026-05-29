"""Reproducibility manifest generator (ADDENDUM_R1 §D.2).

Captures git commit, Python / OS, SDK versions, dataset commits, model alias
table, decoding params, seeds, sample sizes, and conditions into a single
JSON file written alongside the run's JSONL traces.
"""
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Optional

# HARNESS_SPEC §8.1 + ADDENDUM §D.2 — pinned model alias table.
_MODELS: dict[str, dict[str, Any]] = {
    "claude-sonnet-4-6": {"resolved_via_models_api": None},
    "claude-haiku-4-5-20251001": {"alias": "claude-haiku-4-5"},
    "gpt-4.1-2025-04-14": {"alias": "gpt-4.1"},
    "gpt-4.1-mini-2025-04-14": {"alias": "gpt-4.1-mini"},
    "mlx-community/Qwen3-8B-4bit": {
        "hf_revision_sha": None,
        "local_mirror": "harness/data/mlx_models/Qwen3-8B-4bit/",
    },
}

_DATASETS: dict[str, dict[str, str]] = {
    "bfcl_v4": {"commit": "6ea5797", "license": "Apache-2.0"},
    "tau_bench_retail": {"commit": "59a200c", "license": "MIT"},
}

_SDK_PACKAGES: tuple[str, ...] = (
    "anthropic",
    "openai",
    "mlx_lm",
    "scipy",
    "numpy",
    "statsmodels",
    "scikit-posthocs",
    "pydantic",
)


def _git_commit() -> Optional[str]:
    """Return current HEAD commit SHA, or None if git is unavailable."""
    harness_dir: Path = Path(__file__).resolve().parent
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=harness_dir,
            check=True,
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def _sdk_versions() -> dict[str, Optional[str]]:
    versions: dict[str, Optional[str]] = {}
    for pkg in _SDK_PACKAGES:
        try:
            versions[pkg] = importlib_metadata.version(pkg)
        except importlib_metadata.PackageNotFoundError:
            versions[pkg] = None
    return versions


def _mlx_revision_sha() -> Optional[str]:
    """Best-effort fetch of the pinned MLX HF revision SHA (offline-tolerant)."""
    try:
        from huggingface_hub import HfApi  # local import keeps module light
        return HfApi().model_info("mlx-community/Qwen3-8B-4bit").sha
    except Exception:
        return None


def generate_manifest(
    run_id: str,
    n_per_cell: dict[str, int],
    conditions: list[str],
    out_path: Path | str,
) -> dict[str, Any]:
    """Build and persist the reproducibility manifest.

    Args:
        run_id: Caller-supplied unique ID for this run (typically a UUID).
        n_per_cell: Sample-size dict, e.g.
            ``{"bfcl": 100, "tau_bench": 50, "probe": 100}``.
        conditions: Ordered list of condition keys, e.g.
            ``["C0", "C0_5", "C0_7", "C1"]``.
        out_path: Destination JSON file. Parent dirs are created as needed.

    Returns:
        The manifest as a plain dict (also written to ``out_path`` as
        pretty-printed JSON with 2-space indent).
    """
    models: dict[str, dict[str, Any]] = {k: dict(v) for k, v in _MODELS.items()}
    models["mlx-community/Qwen3-8B-4bit"]["hf_revision_sha"] = _mlx_revision_sha()

    manifest: dict[str, Any] = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "python_version": platform.python_version(),
        "os": platform.platform(),
        "sdks": _sdk_versions(),
        "datasets": _DATASETS,
        "models": models,
        "decoding": {"temperature": 0.0, "top_p": 1.0, "max_tokens": 1024},
        "seeds": {"loader_seed": 0, "bootstrap_seed": 0, "permutation_seed": 0},
        "n_per_cell": dict(n_per_cell),
        "conditions": list(conditions),
        "addendum_version": "R1",
    }

    path: Path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False), encoding="utf-8")
    return manifest
