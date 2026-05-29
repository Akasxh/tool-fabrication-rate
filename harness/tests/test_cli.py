"""Unit tests for ``tehr-run`` CLI (``harness/runner/cli.py``)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness.runner import cli


def test_dry_run_pilot_writes_manifest(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    rc = cli.main(["--pilot", "--n", "1", "--dry-run", "--output", str(tmp_path),
                   "--run-id", "test-run-id"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Dispatch matrix" in out and "C0" in out and "C1" in out
    assert "claude-sonnet-4-6" in out
    manifest = json.loads((tmp_path / "test-run-id" / "repro_manifest.json").read_text())
    assert manifest["run_id"] == "test-run-id"
    assert manifest["addendum_version"] == "R1"
    assert manifest["n_per_cell"]["bfcl"] == 1


def test_dry_run_does_not_create_jsonl_files(tmp_path: Path):
    cli.main(["--pilot", "--n", "1", "--dry-run", "--output", str(tmp_path),
              "--run-id", "dry-no-jsonl"])
    assert list((tmp_path / "dry-no-jsonl").glob("*.jsonl")) == []


def test_filters_compose(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    cli.main(["--main", "--models", "claude-sonnet-4-6,gpt-4.1-mini",
              "--benchmark", "bfcl", "--conditions", "C0,C1", "--n", "5",
              "--dry-run", "--output", str(tmp_path), "--run-id", "filter-run"])
    out = capsys.readouterr().out
    # 2 models × 1 benchmark × 2 conditions = 4 cells.
    assert "4 cells" in out
    assert "tau_bench" not in out and "claude-haiku" not in out


def test_default_mode_is_pilot(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    cli.main(["--n", "1", "--dry-run", "--output", str(tmp_path), "--run-id", "default-run"])
    out = capsys.readouterr().out
    assert "tau_bench" not in out and "C0_5" not in out and "C0_7" not in out


def test_provider_classification():
    assert cli._provider_for_model("claude-sonnet-4-6") == "anthropic"
    assert cli._provider_for_model("gpt-4.1") == "openai"
    assert cli._provider_for_model("grok-4") == "xai"
    assert cli._provider_for_model("mlx-community/Qwen3-8B-4bit") == "local"
