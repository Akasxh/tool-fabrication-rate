"""Acceptance tests for cost_meter, trace_logger, and repro_manifest.

Run with::

    PYTHONPATH=/Users/cero/Desktop/PROJECTS/icml \\
        pytest harness/tests/test_logging_cost.py -v
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from harness.cost_meter import BudgetAbort, CostMeter
from harness.repro_manifest import generate_manifest
from harness.trace_logger import TraceLogger, TraceSchemaError


# --------------------------------------------------------------------------- #
# CostMeter                                                                   #
# --------------------------------------------------------------------------- #

def test_cost_meter_per_1k_unit_convention() -> None:
    """Acceptance #1: $/1k convention → returns 10.5 USD for the spec call."""
    meter = CostMeter(budget_usd=100.0)
    delta = meter.add(
        tokens_in=1000, tokens_out=500,
        price_in_per_1k=3.0, price_out_per_1k=15.0,
    )
    # (1000/1000)*3 + (500/1000)*15 = 3.0 + 7.5 = 10.5 USD per the locked
    # per-1k convention (see cost_meter.py module docstring).
    assert delta == pytest.approx(10.5, abs=1e-9)
    assert meter.total() == pytest.approx(10.5, abs=1e-9)
    assert meter.over_budget() is False


def test_cost_meter_threshold_fires_exactly_once() -> None:
    """Acceptance #2: 10 successive adds near budget → callback fires once."""
    fired: list[float] = []
    meter = CostMeter(budget_usd=10.0, on_threshold=lambda spent: fired.append(spent))
    # Each add costs $1 → after 10 adds we'd be AT budget. Stop at 9 adds so
    # the threshold (0.9 * 10 = $9) trips on the 9th and we don't BudgetAbort.
    for _ in range(9):
        meter.add(tokens_in=1000, tokens_out=0, price_in_per_1k=1.0, price_out_per_1k=0.0)
    assert len(fired) == 1
    assert fired[0] == pytest.approx(9.0, abs=1e-9)
    assert meter.over_budget() is False


def test_cost_meter_threshold_does_not_refire() -> None:
    """Threshold callback fires once even on multiple post-90% adds."""
    fired: list[float] = []
    meter = CostMeter(budget_usd=100.0, on_threshold=lambda spent: fired.append(spent))
    # Cross 90% on the first add ($90), then add more without re-firing.
    meter.add(tokens_in=90_000, tokens_out=0, price_in_per_1k=1.0, price_out_per_1k=0.0)
    meter.add(tokens_in=1_000, tokens_out=0, price_in_per_1k=1.0, price_out_per_1k=0.0)
    meter.add(tokens_in=1_000, tokens_out=0, price_in_per_1k=1.0, price_out_per_1k=0.0)
    assert len(fired) == 1


def test_cost_meter_budget_abort() -> None:
    """Acceptance #3: spend >= budget raises BudgetAbort."""
    meter = CostMeter(budget_usd=5.0)
    with pytest.raises(BudgetAbort):
        meter.add(tokens_in=10_000, tokens_out=0, price_in_per_1k=1.0, price_out_per_1k=0.0)
    assert meter.over_budget() is True


def test_cost_meter_history_tracked() -> None:
    """Per-call history is preserved for diagnostics."""
    meter = CostMeter(budget_usd=100.0)
    meter.add(tokens_in=100, tokens_out=50, price_in_per_1k=1.0, price_out_per_1k=2.0)
    meter.add(tokens_in=200, tokens_out=10, price_in_per_1k=1.0, price_out_per_1k=2.0)
    assert len(meter._history) == 2
    assert meter._history[0][0] == 100
    assert meter._history[1][0] == 200


# --------------------------------------------------------------------------- #
# TraceLogger                                                                 #
# --------------------------------------------------------------------------- #

def _valid_record(**overrides: Any) -> dict[str, Any]:
    """Build a §3-compliant 16-field record, optionally overriding fields."""
    rec: dict[str, Any] = {
        "task_id": "bfcl_mt_0042",
        "model": "claude-sonnet-4-6",
        "benchmark": "bfcl",
        "condition": "C1",
        "turn_idx": 2,
        "agent_message": "I'll look up the weather using get_weather.",
        "parsed_tool_call": {"name": "get_weather", "arguments": {"city": "SF"}},
        "tool_call_status": "executed",
        "tool_response": {"temp_c": 18},
        "intervention_event": None,
        "latency_ms": 842,
        "tokens_in": 1203,
        "tokens_out": 74,
        "cost_usd": 0.0042,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0",
    }
    rec.update(overrides)
    return rec


def test_trace_logger_roundtrip(tmp_path: Path) -> None:
    """Acceptance #4: write valid record → read back identical content."""
    out = tmp_path / "trace.jsonl"
    logger = TraceLogger(out)
    rec = _valid_record()
    logger.write(rec)
    logger.close()

    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    # All 16 required fields present.
    for k in (
        "task_id", "model", "benchmark", "condition", "turn_idx",
        "agent_message", "parsed_tool_call", "tool_call_status",
        "tool_response", "intervention_event", "latency_ms",
        "tokens_in", "tokens_out", "cost_usd", "timestamp", "schema_version",
    ):
        assert k in parsed, f"missing field {k}"
    # Lossless on the fields we care about.
    assert parsed["task_id"] == rec["task_id"]
    assert parsed["parsed_tool_call"] == rec["parsed_tool_call"]
    assert parsed["schema_version"] == "1.0"
    # raw_provider_payload dropped by default.
    assert "raw_provider_payload" not in parsed


def test_trace_logger_drops_raw_payload_by_default(tmp_path: Path) -> None:
    out = tmp_path / "trace.jsonl"
    logger = TraceLogger(out, persist_raw=False)
    rec = _valid_record()
    rec["raw_provider_payload"] = {"hidden": "do-not-persist"}
    logger.write(rec)
    logger.close()
    parsed = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert "raw_provider_payload" not in parsed


def test_trace_logger_persist_raw_keeps_payload(tmp_path: Path) -> None:
    out = tmp_path / "trace.jsonl"
    logger = TraceLogger(out, persist_raw=True)
    rec = _valid_record()
    rec["raw_provider_payload"] = {"sdk_id": "abc"}
    logger.write(rec)
    logger.close()
    parsed = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert parsed.get("raw_provider_payload") == {"sdk_id": "abc"}


def test_trace_logger_missing_field_raises(tmp_path: Path) -> None:
    """Acceptance #5: missing required field → TraceSchemaError."""
    out = tmp_path / "trace.jsonl"
    logger = TraceLogger(out)
    rec = _valid_record()
    del rec["latency_ms"]
    with pytest.raises(TraceSchemaError) as excinfo:
        logger.write(rec)
    assert "latency_ms" in str(excinfo.value)


def test_trace_logger_bad_schema_version_raises(tmp_path: Path) -> None:
    out = tmp_path / "trace.jsonl"
    logger = TraceLogger(out)
    rec = _valid_record(schema_version="2.0")
    with pytest.raises(TraceSchemaError):
        logger.write(rec)


def test_trace_logger_redaction(tmp_path: Path) -> None:
    """Acceptance #6: redact_keys substring scrubbing on agent_message."""
    out = tmp_path / "trace.jsonl"
    secret = "my_email@example.com"
    logger = TraceLogger(out, redact_keys=[secret])
    rec = _valid_record(
        agent_message=f"Hi please contact {secret} about weather.",
        tool_response={"echo": secret, "ok": True},
    )
    logger.write(rec)
    logger.close()
    text = out.read_text(encoding="utf-8")
    assert secret not in text
    assert "[REDACTED]" in text
    parsed = json.loads(text.splitlines()[0])
    assert "[REDACTED]" in parsed["agent_message"]
    assert parsed["tool_response"]["echo"] == "[REDACTED]"


def test_trace_logger_appends(tmp_path: Path) -> None:
    """Re-opening the same path appends; never truncates."""
    out = tmp_path / "trace.jsonl"
    TraceLogger(out).write(_valid_record(task_id="t1"));
    logger2 = TraceLogger(out)
    logger2.write(_valid_record(task_id="t2"))
    logger2.close()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["task_id"] == "t1"
    assert json.loads(lines[1])["task_id"] == "t2"


# --------------------------------------------------------------------------- #
# repro_manifest                                                              #
# --------------------------------------------------------------------------- #

def test_generate_manifest_writes_and_returns(tmp_path: Path) -> None:
    """Acceptance #7: generate_manifest writes file + returns dict with all keys."""
    out = tmp_path / "manifest.json"
    manifest = generate_manifest(
        run_id="test",
        n_per_cell={"bfcl": 100, "tau_bench": 50, "probe": 100},
        conditions=["C0", "C0_5", "C0_7", "C1"],
        out_path=out,
    )

    expected_top_level = {
        "run_id", "started_at", "git_commit", "python_version", "os",
        "sdks", "datasets", "models", "decoding", "seeds",
        "n_per_cell", "conditions", "addendum_version",
    }
    assert expected_top_level.issubset(manifest.keys())
    assert manifest["run_id"] == "test"
    assert manifest["addendum_version"] == "R1"
    assert manifest["conditions"] == ["C0", "C0_5", "C0_7", "C1"]
    assert manifest["n_per_cell"]["bfcl"] == 100
    assert manifest["decoding"] == {
        "temperature": 0.0, "top_p": 1.0, "max_tokens": 1024,
    }
    assert manifest["seeds"] == {
        "loader_seed": 0, "bootstrap_seed": 0, "permutation_seed": 0,
    }
    # claude-sonnet-4-6 placeholder left null for runner to fill in.
    assert (
        manifest["models"]["claude-sonnet-4-6"]["resolved_via_models_api"]
        is None
    )
    assert "claude-haiku-4-5-20251001" in manifest["models"]
    assert "bfcl_v4" in manifest["datasets"]
    assert manifest["datasets"]["bfcl_v4"]["license"] == "Apache-2.0"

    # File written and matches.
    assert out.exists()
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert on_disk == manifest
