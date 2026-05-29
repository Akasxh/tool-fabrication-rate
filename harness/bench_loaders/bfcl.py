"""BFCL v4 multi-turn dataset loader (Phase-1 D).

Yields :class:`harness.types.Task` instances for one of the four BFCL v4
multi-turn splits, applying :func:`harness.registry._normalize_bfcl_schema`
once at load time so all three downstream adapters (Anthropic, OpenAI,
MLX/Qwen3) can treat ``Task.registry`` as canonical OpenAI shape.

See HARNESS_SPEC.md §2 ``bench_loaders/bfcl.py``, §8.8 (BFCL JSON-Schema
normalization), §8.10 (BFCL multi-turn staged user messages) and
``PHASE0/dataset_status.md`` §3 + §5.1 for the source-of-truth schema audit.

Tool-key naming convention (cross-class collisions):
    Registry keys are the **unqualified** tool name (e.g. ``"cat"``), matching
    what BFCL ground-truth Python-source-call expressions use and what the
    model emits at run time. The audit confirms zero per-task name collisions
    in any of the four multi-turn splits across all 800 tasks: the only
    cross-class shadowing is between ``memory_kv`` and ``memory_vector`` (9
    overlapping names) and no task ever pulls in both classes. If that
    invariant is ever violated by a future BFCL release, the loader emits a
    ``UserWarning`` so the silent shadowing surfaces in test output.
"""
from __future__ import annotations

import json
import warnings
from collections.abc import Iterator
from pathlib import Path
from random import Random
from typing import Any

from harness.registry import _normalize_bfcl_schema
from harness.types import Task

# Default points at the BFCL v4 sparse-checkout root. The data files live one
# level deeper at ``bfcl_eval/data/`` (NOT ``data/multi_turn/`` — the leader
# in HARNESS_SPEC §2 referenced that subdir but the audit in PHASE0/
# dataset_status.md §2 confirms the actual layout used here).
import os
from pathlib import Path

# Resolved at import time; override via ICML_BFCL_DIR env var or pass data_dir= kwarg.
# Falls back to harness/data/bfcl_v4/... relative to this file so relocating the
# repo doesn't require code changes.
_HARNESS_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = os.environ.get(
    "ICML_BFCL_DIR",
    str(_HARNESS_ROOT / "data" / "bfcl_v4" / "repo" / "berkeley-function-call-leaderboard"),
)

# Class-name → tool-doc-filename mapping. The BFCL task records use CamelCase
# class names (``GorillaFileSystem``, ``TwitterAPI``, ...), but the JSONL
# tool-doc files are snake_case and not always a literal lower-snake of the
# class (``TwitterAPI`` → ``posting_api.json``, ``TravelAPI`` →
# ``travel_booking.json``). This is the canonical mapping used by BFCL itself
# (see ``bfcl_eval/constants/executable_backend_config.py``); we vendor it as
# a constant rather than importing the upstream module to avoid pulling
# BFCL's package onto the import path at loader load time.
_CLASS_TO_DOC_FILENAME: dict[str, str] = {
    "GorillaFileSystem": "gorilla_file_system.json",
    "MathAPI": "math_api.json",
    "MessageAPI": "message_api.json",
    "TwitterAPI": "posting_api.json",
    "TicketAPI": "ticket_api.json",
    "TradingBot": "trading_bot.json",
    "TravelAPI": "travel_booking.json",
    "VehicleControlAPI": "vehicle_control.json",
    "WebSearchAPI": "web_search.json",
    "MemoryAPI_kv": "memory_kv.json",
    "MemoryAPI_vector": "memory_vector.json",
    "MemoryAPI_rec_sum": "memory_rec_sum.json",
}

_VALID_SPLITS: tuple[str, ...] = (
    "multi_turn_base",
    "multi_turn_long_context",
    "multi_turn_miss_func",
    "multi_turn_miss_param",
)

_BENCHMARK: str = "bfcl"
_DEFAULT_TURNS_MAX: int = 8


def _resolve_data_dir(data_dir: str | Path | None) -> Path:
    """Return the resolved BFCL leaderboard root as a :class:`Path`."""
    return Path(data_dir if data_dir is not None else DEFAULT_DATA_DIR)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a BFCL JSONL file and return a list of records, skipping blanks."""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _load_tool_docs(data_dir: Path) -> dict[str, dict[str, dict]]:
    """Build ``{class_name: {tool_name: tool_schema}}`` from ``multi_turn_func_doc/``.

    Keys are the **CamelCase BFCL class names** (e.g. ``GorillaFileSystem``)
    so they match what tasks list under ``involved_classes``. Filenames are
    resolved through :data:`_CLASS_TO_DOC_FILENAME`. For robustness against
    third-party / synthetic test layouts that use class names matching the
    file stem directly (e.g. ``"alpha"`` → ``alpha.json``), any *.json file
    not covered by the mapping is also indexed under its bare stem.

    Each tool entry is normalized via :func:`_normalize_bfcl_schema` so all
    ``"type": "dict"`` occurrences become ``"object"``. The ``"response"``
    field is dropped (BFCL-specific, ignored by adapters). The result is the
    canonical OpenAI-shape schema dict expected by ``Task.registry``.
    """
    docs_dir = data_dir / "bfcl_eval" / "data" / "multi_turn_func_doc"
    out: dict[str, dict[str, dict]] = {}
    if not docs_dir.is_dir():
        return out

    def _index_file(path: Path, key: str) -> None:
        per_class: dict[str, dict] = {}
        for entry in _read_jsonl(path):
            entry = dict(entry)
            entry.pop("response", None)
            normalized = _normalize_bfcl_schema(entry)
            per_class[normalized["name"]] = normalized
        out[key] = per_class

    # First pass: index each file by stem (covers synthetic / legacy layouts).
    for path in sorted(docs_dir.glob("*.json")):
        _index_file(path, path.stem)

    # Second pass: alias each known BFCL CamelCase class name to its file.
    for class_name, filename in _CLASS_TO_DOC_FILENAME.items():
        path = docs_dir / filename
        if path.is_file() and class_name not in out:
            _index_file(path, class_name)
        elif path.is_file():
            # File already indexed by stem; just mirror under class-name key.
            out[class_name] = out[path.stem]
    return out


def _load_ground_truth(data_dir: Path, split: str) -> dict[str, list[list[str]]]:
    """Return ``{task_id: ground_truth}`` from ``possible_answer/`` for a split."""
    path = data_dir / "bfcl_eval" / "data" / "possible_answer" / f"BFCL_v4_{split}.json"
    if not path.is_file():
        return {}
    return {rec["id"]: rec["ground_truth"] for rec in _read_jsonl(path)}


def _build_registry(
    involved_classes: list[str],
    excluded_function: list[str],
    tool_docs: dict[str, dict[str, dict]],
    task_id: str,
) -> dict[str, dict] | None:
    """Assemble the per-task tool registry from involved classes.

    Returns ``None`` and emits a ``UserWarning`` if any involved class is
    missing a tool-doc file (loader skips that task per spec).
    """
    excluded = set(excluded_function or [])
    registry: dict[str, dict] = {}
    for cls in involved_classes:
        if cls not in tool_docs:
            warnings.warn(
                f"BFCL task {task_id!r}: involved_class {cls!r} has no tool-doc "
                f"file; skipping task.",
                stacklevel=2,
            )
            return None
        for tool_name, schema in tool_docs[cls].items():
            if tool_name in excluded:
                continue
            if tool_name in registry:
                # Same name from a different class — should not happen for any
                # current BFCL multi-turn task, but flag if it ever does.
                warnings.warn(
                    f"BFCL task {task_id!r}: tool name collision on {tool_name!r} "
                    f"across involved_classes; later class wins.",
                    stacklevel=2,
                )
            registry[tool_name] = schema
    return registry


def _extract_initial_prompt(question: list[list[dict]]) -> str:
    """Return the first user-turn's last-user-message content as plain text.

    BFCL ``question[0]`` is a *list* of messages (typically length 1, but the
    schema permits more). We pick the last user message in turn 0 since that
    is the one the agent must respond to; non-user messages are ignored.
    """
    if not question or not question[0]:
        return ""
    user_msgs = [m for m in question[0] if m.get("role") == "user"]
    if user_msgs:
        return str(user_msgs[-1].get("content", ""))
    return str(question[0][-1].get("content", ""))


def load_bfcl(
    split: str = "multi_turn_base",
    n: int = 50,
    seed: int = 0,
    data_dir: str | Path | None = None,
) -> Iterator[Task]:
    """Yield up to ``n`` BFCL v4 multi-turn tasks.

    Args:
        split: One of ``multi_turn_base``, ``multi_turn_long_context``,
            ``multi_turn_miss_func``, ``multi_turn_miss_param``.
        n: Maximum number of tasks to yield. If the split has fewer than ``n``
            usable tasks, all available tasks are yielded without erroring.
        seed: Sampling seed; selection uses ``random.Random(seed).sample`` for
            determinism (HARNESS_SPEC §5 acceptance #6).
        data_dir: Override the default BFCL repo root.

    Yields:
        :class:`Task` instances with:
          * ``id`` prefixed ``"bfcl_"`` (e.g. ``"bfcl_multi_turn_base_0"``)
          * ``registry`` = canonical OpenAI-shape, post-normalization
          * ``initial_prompt`` = ``question[0]``'s last user message content
          * ``turns_max`` = 8 (HARNESS_SPEC default)
          * ``expected_outcome`` = ``{"ground_truth", "subsequent_user_messages",
            "initial_config", "involved_classes"}``

    Tasks whose ``involved_classes`` reference a missing tool-doc file are
    skipped with a :class:`UserWarning`; the loader does not raise.
    """
    if split not in _VALID_SPLITS:
        raise ValueError(f"Unknown BFCL split {split!r}; expected one of {_VALID_SPLITS}")

    root = _resolve_data_dir(data_dir)
    task_path = root / "bfcl_eval" / "data" / f"BFCL_v4_{split}.json"
    if not task_path.is_file():
        raise FileNotFoundError(f"BFCL task file not found: {task_path}")

    raw_tasks = _read_jsonl(task_path)
    tool_docs = _load_tool_docs(root)
    ground_truth_map = _load_ground_truth(root, split)

    # Deterministic sampling: sample by index then preserve sort order so the
    # output is stable on re-run.
    rng = Random(seed)
    k = min(n, len(raw_tasks))
    chosen_idx = sorted(rng.sample(range(len(raw_tasks)), k))

    yielded = 0
    for idx in chosen_idx:
        rec = raw_tasks[idx]
        task_id = rec["id"]
        registry = _build_registry(
            involved_classes=list(rec.get("involved_classes", [])),
            excluded_function=list(rec.get("excluded_function", [])),
            tool_docs=tool_docs,
            task_id=task_id,
        )
        if registry is None:
            continue
        question: list[list[dict]] = list(rec.get("question", []))
        initial_prompt = _extract_initial_prompt(question)
        subsequent: list[list[dict]] = question[1:]
        expected_outcome: dict[str, Any] = {
            "ground_truth": ground_truth_map.get(task_id),
            "subsequent_user_messages": subsequent,
            "initial_config": rec.get("initial_config", {}),
            "involved_classes": list(rec.get("involved_classes", [])),
        }
        # `multi_turn_miss_func` carries an extra `missed_function` payload —
        # surface it to the runner without breaking the canonical fields.
        if "missed_function" in rec:
            expected_outcome["missed_function"] = rec["missed_function"]

        yield Task(
            id=f"bfcl_{task_id}",
            benchmark=_BENCHMARK,
            registry=registry,
            initial_prompt=initial_prompt,
            turns_max=_DEFAULT_TURNS_MAX,
            expected_outcome=expected_outcome,
        )
        yielded += 1
        if yielded >= n:
            break
