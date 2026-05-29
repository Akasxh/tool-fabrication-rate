"""Acceptance tests for ``harness.bench_loaders.bfcl`` (Phase-1 D).

Coverage:
  * synthetic 3-task dataset round-trips, IDs prefixed ``bfcl_``.
  * ``_normalize_bfcl_schema`` applied — no surviving ``"type": "dict"``.
  * deterministic sampling: same seed → same IDs in same order.
  * missing involved_classes file → warning + skipped task (no raise).
  * ``n`` larger than dataset → all available tasks yielded.
  * happy path against real ``multi_turn_base`` on disk.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import pytest

from harness.bench_loaders.bfcl import DEFAULT_DATA_DIR, load_bfcl
from harness.types import Task


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")


@pytest.fixture()
def synthetic_data_dir(tmp_path: Path) -> Path:
    """Build a 3-task BFCL-shaped dataset rooted at ``tmp_path``."""
    data = tmp_path / "bfcl_eval" / "data"
    docs, answers = data / "multi_turn_func_doc", data / "possible_answer"
    _write_jsonl(docs / "alpha.json", [
        {"name": "alpha_one", "description": "a1",
         "parameters": {"type": "dict", "properties": {"x": {"type": "string"}}, "required": ["x"]},
         "response": {"type": "dict", "properties": {}}},
        {"name": "alpha_two", "description": "a2",
         "parameters": {"type": "dict", "properties": {
             "nested": {"type": "dict", "properties": {"k": {"type": "string"}}}}, "required": []}},
    ])
    _write_jsonl(docs / "beta.json", [
        {"name": "beta_one", "description": "b1",
         "parameters": {"type": "dict", "properties": {}, "required": []}},
    ])
    _write_jsonl(data / "BFCL_v4_multi_turn_base.json", [
        {"id": "multi_turn_base_0",
         "question": [[{"role": "user", "content": "Alpha turn 0"}],
                      [{"role": "user", "content": "Alpha turn 1"}]],
         "initial_config": {"AlphaCls": {"k": 1}}, "path": [],
         "involved_classes": ["alpha"], "excluded_function": []},
        {"id": "multi_turn_base_1",
         "question": [[{"role": "user", "content": "Beta turn 0"}]],
         "initial_config": {}, "path": [],
         "involved_classes": ["beta"], "excluded_function": ["beta_one"]},
        {"id": "multi_turn_base_2",
         "question": [[{"role": "user", "content": "Mixed turn 0"}],
                      [{"role": "user", "content": "Mixed turn 1"}],
                      [{"role": "user", "content": "Mixed turn 2"}]],
         "initial_config": {}, "path": [],
         "involved_classes": ["alpha", "beta"], "excluded_function": ["alpha_two"]},
    ])
    _write_jsonl(answers / "BFCL_v4_multi_turn_base.json", [
        {"id": "multi_turn_base_0", "ground_truth": [["alpha_one(x='hi')"]]},
        {"id": "multi_turn_base_1", "ground_truth": [[]]},
        {"id": "multi_turn_base_2", "ground_truth": [["alpha_one(x='go')"]]},
    ])
    return tmp_path


# ---------------------------------------------------------------------------
# Synthetic-data tests.
# ---------------------------------------------------------------------------

def test_yields_three_tasks_with_prefixed_ids(synthetic_data_dir: Path) -> None:
    tasks = list(load_bfcl(n=10, seed=0, data_dir=synthetic_data_dir))
    assert len(tasks) == 3
    assert {t.id for t in tasks} == {
        "bfcl_multi_turn_base_0", "bfcl_multi_turn_base_1", "bfcl_multi_turn_base_2"}
    for t in tasks:
        assert isinstance(t, Task)
        assert t.benchmark == "bfcl"
        assert t.turns_max == 8


def test_registry_normalization_and_exclusion(synthetic_data_dir: Path) -> None:
    tasks = {t.id: t for t in load_bfcl(n=10, seed=0, data_dir=synthetic_data_dir)}

    # Normalization: top-level + nested rewritten to "object".
    schema = tasks["bfcl_multi_turn_base_0"].registry["alpha_two"]
    assert schema["parameters"]["type"] == "object"
    assert schema["parameters"]["properties"]["nested"]["type"] == "object"
    blob = json.dumps([t.registry for t in tasks.values()])
    assert '"type": "dict"' not in blob and '"type":"dict"' not in blob

    # excluded_function removes named tools (task 1: only beta_one excluded).
    assert tasks["bfcl_multi_turn_base_1"].registry == {}
    # Task 2 excludes alpha_two → keeps alpha_one + beta_one.
    assert set(tasks["bfcl_multi_turn_base_2"].registry) == {"alpha_one", "beta_one"}


def test_initial_prompt_and_subsequent_user_messages(synthetic_data_dir: Path) -> None:
    tasks = {t.id: t for t in load_bfcl(n=10, seed=0, data_dir=synthetic_data_dir)}
    assert tasks["bfcl_multi_turn_base_0"].initial_prompt == "Alpha turn 0"
    assert tasks["bfcl_multi_turn_base_2"].initial_prompt == "Mixed turn 0"
    sub2 = tasks["bfcl_multi_turn_base_2"].expected_outcome["subsequent_user_messages"]
    assert [m[0]["content"] for m in sub2] == ["Mixed turn 1", "Mixed turn 2"]
    # Single-turn task has empty subsequent list.
    assert tasks["bfcl_multi_turn_base_1"].expected_outcome["subsequent_user_messages"] == []


def test_expected_outcome_carries_ground_truth_and_config(synthetic_data_dir: Path) -> None:
    tasks = {t.id: t for t in load_bfcl(n=10, seed=0, data_dir=synthetic_data_dir)}
    eo = tasks["bfcl_multi_turn_base_0"].expected_outcome
    assert eo["ground_truth"] == [["alpha_one(x='hi')"]]
    assert eo["initial_config"] == {"AlphaCls": {"k": 1}}
    assert eo["involved_classes"] == ["alpha"]


def test_determinism_same_seed_same_order(synthetic_data_dir: Path) -> None:
    a = [t.id for t in load_bfcl(n=10, seed=0, data_dir=synthetic_data_dir)]
    b = [t.id for t in load_bfcl(n=10, seed=0, data_dir=synthetic_data_dir)]
    assert a == b


def test_n_larger_than_dataset_yields_all(synthetic_data_dir: Path) -> None:
    assert len(list(load_bfcl(n=999, seed=0, data_dir=synthetic_data_dir))) == 3


def test_missing_class_warns_and_skips(synthetic_data_dir: Path) -> None:
    bad = {"id": "multi_turn_base_3",
           "question": [[{"role": "user", "content": "ghost"}]],
           "initial_config": {}, "path": [],
           "involved_classes": ["ghost_class"], "excluded_function": []}
    task_path = synthetic_data_dir / "bfcl_eval" / "data" / "BFCL_v4_multi_turn_base.json"
    with task_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(bad) + "\n")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ids = {t.id for t in load_bfcl(n=10, seed=0, data_dir=synthetic_data_dir)}
    assert "bfcl_multi_turn_base_3" not in ids
    assert any("ghost_class" in str(w.message) for w in caught)


def test_unknown_split_and_missing_file_raise(
    synthetic_data_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    with pytest.raises(ValueError, match="Unknown BFCL split"):
        list(load_bfcl(split="bogus", n=1, data_dir=synthetic_data_dir))
    empty = tmp_path_factory.mktemp("empty")
    with pytest.raises(FileNotFoundError):
        list(load_bfcl(n=1, data_dir=empty))


# ---------------------------------------------------------------------------
# Real-data happy path. Auto-skips if BFCL clone is absent.
# ---------------------------------------------------------------------------

_REAL_TASK_FILE = (
    Path(DEFAULT_DATA_DIR) / "bfcl_eval" / "data" / "BFCL_v4_multi_turn_base.json"
)
_REAL_AVAILABLE = _REAL_TASK_FILE.is_file()


@pytest.mark.skipif(not _REAL_AVAILABLE, reason="BFCL clone not on disk")
def test_loads_three_tasks_from_real_multi_turn_base() -> None:
    tasks = list(load_bfcl(split="multi_turn_base", n=3, seed=0))
    assert len(tasks) == 3
    for t in tasks:
        assert t.id.startswith("bfcl_multi_turn_base_")
        assert t.benchmark == "bfcl" and t.turns_max == 8
        assert isinstance(t.registry, dict) and t.registry
        # Normalization invariant on real data.
        blob = json.dumps(t.registry)
        assert '"type": "dict"' not in blob and '"type":"dict"' not in blob
        for tool_name, schema in t.registry.items():
            assert schema["name"] == tool_name
            assert schema["parameters"]["type"] == "object"
        assert isinstance(t.initial_prompt, str) and t.initial_prompt
        eo = t.expected_outcome
        assert {"subsequent_user_messages", "initial_config", "involved_classes"} <= eo.keys()


@pytest.mark.skipif(not _REAL_AVAILABLE, reason="BFCL clone not on disk")
def test_real_data_determinism() -> None:
    a = [t.id for t in load_bfcl(split="multi_turn_base", n=10, seed=0)]
    b = [t.id for t in load_bfcl(split="multi_turn_base", n=10, seed=0)]
    assert a == b
    assert len(set(a)) == len(a)
