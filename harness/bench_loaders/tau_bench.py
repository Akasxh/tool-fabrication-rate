"""τ-bench retail loader (HARNESS_SPEC §2, §8.4, §8.9). Loader does NOT
instantiate the env; runner owns env lifecycle. ``expected_outcome`` carries
env-config + reward oracle + ``user_simulator_model="claude-haiku-4-5"``.

τ-bench's ``__init__`` chain transitively imports ``litellm`` which we don't
depend on; we stub the heavy package ``__init__`` files in ``sys.modules``
and import only the submodules we need."""
from __future__ import annotations

import importlib
import random
import sys
import types as _types
from collections.abc import Iterator
import os
from pathlib import Path

from harness.types import Task

# Resolved at import time; override via ICML_TAU_DIR env var or pass data_dir= kwarg.
# Falls back to harness/data/tau_bench_retail relative to this file.
_HARNESS_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = os.environ.get(
    "ICML_TAU_DIR",
    str(_HARNESS_ROOT / "data" / "tau_bench_retail"),
)
USER_SIMULATOR_MODEL = "claude-haiku-4-5"
ENV_CLASS_FQN = "tau_bench.envs.retail.MockRetailDomainEnv"
_SPLIT_TO_MODULE: dict[str, tuple[str, str]] = {
    "test": ("tau_bench.envs.retail.tasks_test", "TASKS_TEST"),
    "dev": ("tau_bench.envs.retail.tasks_dev", "TASKS_DEV"),
    "train": ("tau_bench.envs.retail.tasks_train", "TASKS_TRAIN"),
}


def _install_namespace_stubs(data_dir: Path) -> None:
    """Stub the three heavy package ``__init__`` files (which import litellm).
    ``...retail.tools.__init__`` is harmless and IS the source of ``ALL_TOOLS``,
    so it stays unstubbed."""
    if str(data_dir) not in sys.path:
        sys.path.insert(0, str(data_dir))
    for qualname, subpath in (
        ("tau_bench", "tau_bench"),
        ("tau_bench.envs", "tau_bench/envs"),
        ("tau_bench.envs.retail", "tau_bench/envs/retail"),
    ):
        if qualname not in sys.modules:
            mod = _types.ModuleType(qualname)
            mod.__path__ = [str(data_dir / subpath)]  # type: ignore[attr-defined]
            sys.modules[qualname] = mod


def _load_split(data_dir: Path, split: str) -> list:
    if split not in _SPLIT_TO_MODULE:
        raise ValueError(f"Unknown τ-bench split: {split!r}")
    _install_namespace_stubs(data_dir)
    module_name, attr = _SPLIT_TO_MODULE[split]
    return list(getattr(importlib.import_module(module_name), attr))


def _load_registry(data_dir: Path) -> dict[str, dict]:
    """Canonical OpenAI-shape registry from ``ALL_TOOLS.get_info()`` — τ-bench
    tools already use ``"type":"object"`` so no BFCL-style normalization."""
    _install_namespace_stubs(data_dir)
    tools_pkg = importlib.import_module("tau_bench.envs.retail.tools")
    return {
        (info := tc.get_info())["function"]["name"]: info
        for tc in tools_pkg.ALL_TOOLS
    }


def load_tau_bench_retail(
    n: int = 25,
    seed: int = 0,
    split: str = "test",
    data_dir: str | Path | None = None,
) -> Iterator[Task]:
    """Yield up to ``n`` τ-bench retail tasks deterministically. Splits:
    ``"test"`` (115, default), ``"dev"`` (20), ``"train"`` (500)."""
    root = Path(data_dir) if data_dir is not None else Path(DEFAULT_DATA_DIR)
    if not root.exists():
        raise FileNotFoundError(f"τ-bench data dir not found: {root}")
    all_tasks = _load_split(root, split)
    registry = _load_registry(root)
    rng = random.Random(seed)
    take = min(n, len(all_tasks))
    indices = sorted(rng.sample(range(len(all_tasks)), take))
    for ord_i, task_index in enumerate(indices):
        t = all_tasks[task_index]
        expected_outcome: dict = {
            "task_split": split,
            "task_index": task_index,
            "user_id": t.user_id,
            "instruction": t.instruction,
            "actions": [a.model_dump() for a in t.actions],
            "outputs": list(t.outputs),
            "env_class": ENV_CLASS_FQN,
            "env_init_kwargs": {
                "user_strategy": "llm",
                "user_model": USER_SIMULATOR_MODEL,
                "user_provider": "anthropic",
                "task_split": split,
                "task_index": task_index,
            },
            "user_simulator_model": USER_SIMULATOR_MODEL,
        }
        yield Task(
            id=f"tau_retail_{ord_i:03d}",
            benchmark="tau_bench",
            registry=registry,
            initial_prompt=t.instruction,
            turns_max=8,
            expected_outcome=expected_outcome,
        )
