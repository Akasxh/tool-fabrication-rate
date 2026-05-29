"""Unit tests for ``harness/runner/loop.py`` (HARNESS_SPEC §5 + ADDENDUM §B.2)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness.adapters.base import ModelAdapter
from harness.cost_meter import CostMeter
from harness.runner.loop import run_task
from harness.runner.refusal import classify_refusal
from harness.trace_logger import TraceLogger
from harness.types import ProviderResponse, Task, ToolCall


class ScriptedAdapter(ModelAdapter):
    def __init__(self, responses, model_id="fake-anth-1"):
        self.model_id = model_id
        self.price_per_1k_in, self.price_per_1k_out = 0.001, 0.005
        self._queue, self.dispatched = list(responses), []

    def dispatch(self, messages, tools, max_tokens=1024):
        self.dispatched.append((list(messages), list(tools)))
        return self._queue.pop(0) if self._queue else _r(text="exhausted", finish="stop")


def _task(turns_max=8):
    return Task(
        id="bfcl_unit_0", benchmark="bfcl",
        registry={"get_weather": {"name": "get_weather", "description": "w",
                                  "parameters": {"type": "object", "properties": {}}}},
        initial_prompt="hello", turns_max=turns_max,
        expected_outcome={"subsequent_user_messages": [], "involved_classes": [],
                          "initial_config": {}},
    )


def _r(*, text="", tool_calls=None, parse_ok=True, finish="tool_use"):
    return ProviderResponse(raw_text=text, tool_calls=tool_calls or [], parse_ok=parse_ok,
                            finish_reason=finish, tokens_in=10, tokens_out=5, latency_ms=12)


@pytest.fixture()
def logger(tmp_path):
    return TraceLogger(tmp_path / "trace.jsonl")


@pytest.fixture()
def meter():
    return CostMeter(budget_usd=100.0)


def test_clean_execution_passes_under_c1(logger, meter):
    call = ToolCall(name="get_weather", arguments={"city": "SF"})
    adapter = ScriptedAdapter([_r(text="ok", tool_calls=[call]), _r(text="done", finish="stop")])
    seen: list = []
    summary = run_task(_task(), adapter, "C1", logger, meter,
                       lambda n, a: seen.append((n, a)) or {"output": 70}, max_turns=2)
    logger.close()
    assert summary["pass"] is True and summary["tehr_num"] == 0 and summary["tehr_denom"] == 1
    assert seen == [("get_weather", {"city": "SF"})]


def test_c1_reprompt_recovers(tmp_path, meter):
    bad = ToolCall(name="get_weather_v2", arguments={})
    good = ToolCall(name="get_weather", arguments={"city": "SF"})
    adapter = ScriptedAdapter([_r(text="t1", tool_calls=[bad]),
                               _r(text="ok", tool_calls=[good])])
    log = TraceLogger(tmp_path / "t.jsonl")
    summary = run_task(_task(), adapter, "C1", log, meter,
                       lambda n, a: {"output": "ok"}, max_turns=1)
    log.close()
    assert summary["tehr_num"] == 0 and summary["tehr_denom"] == 1
    rec = json.loads((tmp_path / "t.jsonl").read_text().splitlines()[0])
    assert rec["intervention_event"]["kind"] == "rvr_rejected"
    assert rec["tool_call_status"] == "executed"


def test_c0_no_retry_marks_hallucinated(logger, meter):
    bad = ToolCall(name="hallu_tool", arguments={})
    adapter = ScriptedAdapter([_r(text="bad", tool_calls=[bad]), _r(text="next", finish="stop")])
    summary = run_task(_task(), adapter, "C0", logger, meter,
                       lambda n, a: {"output": "x"}, max_turns=2)
    logger.close()
    assert summary["tehr_num"] == 1 and summary["tehr_denom"] == 1
    assert len(adapter.dispatched) == 2  # no retry under C0


def test_c1_multi_bad_call_single_reprompt(tmp_path, meter):
    bads = [ToolCall(name=f"bogus_{i}", arguments={}) for i in "ab"]
    good = ToolCall(name="get_weather", arguments={})
    adapter = ScriptedAdapter([_r(text="two-bad", tool_calls=bads),
                               _r(text="recovered", tool_calls=[good])])
    log = TraceLogger(tmp_path / "x.jsonl")
    summary = run_task(_task(), adapter, "C1", log, meter,
                       lambda n, a: {"output": "ok"}, max_turns=1)
    log.close()
    assert len(adapter.dispatched) == 2  # ONE re-prompt despite two bad calls
    assert summary["tehr_denom"] == 1


def test_eight_turn_cap_honored(logger, meter):
    adapter = ScriptedAdapter([_r(text=f"t{i}", finish="stop") for i in range(50)])
    summary = run_task(_task(turns_max=20), adapter, "C0", logger, meter,
                       lambda n, a: {"output": "n"}, max_turns=8)
    logger.close()
    assert summary["n_turns"] == 8


def test_timeout_aborts(tmp_path, meter):
    adapter = ScriptedAdapter([_r(text="t", finish="stop") for _ in range(20)])
    log = TraceLogger(tmp_path / "to.jsonl")
    summary = run_task(_task(), adapter, "C0", log, meter,
                       lambda n, a: {"output": "n"}, turn_timeout_s=-1.0, max_turns=8)
    log.close()
    assert summary["terminal"] == "timed_out" and summary["pass"] is False


def test_jsonl_schema_round_trip(tmp_path, meter):
    call = ToolCall(name="get_weather", arguments={})
    out = tmp_path / "rt.jsonl"
    log = TraceLogger(out)
    run_task(_task(), ScriptedAdapter([_r(text="hi", tool_calls=[call])]),
             "C1", log, meter, lambda n, a: {"output": "ok"}, max_turns=1)
    log.close()
    required = {"task_id", "model", "benchmark", "condition", "turn_idx", "agent_message",
                "parsed_tool_call", "tool_call_status", "tool_response", "intervention_event",
                "latency_ms", "tokens_in", "tokens_out", "cost_usd", "timestamp", "schema_version"}
    for line in out.read_text().splitlines():
        rec = json.loads(line)
        assert required.issubset(rec.keys()) and rec["schema_version"] == "1.0"


def test_refusal_excluded_from_denom(logger, meter):
    adapter = ScriptedAdapter([_r(text="I can't help with that.", finish="stop")])
    summary = run_task(_task(), adapter, "C1", logger, meter,
                       lambda n, a: {"output": "x"}, max_turns=1)
    logger.close()
    assert summary["tehr_denom"] == 0 and summary["tehr_num"] == 0


def test_classify_refusal_unit():
    def _pr(text, calls=None):
        return ProviderResponse(raw_text=text, tool_calls=calls or [], parse_ok=True,
                                finish_reason="stop", tokens_in=1, tokens_out=1, latency_ms=0)
    assert classify_refusal(_pr("I cannot do that.")) is True
    assert classify_refusal(_pr("Sure.")) is False
    assert classify_refusal(_pr("I can't but here", [ToolCall("x", {})])) is False


def test_parse_fail_increments_denom_only(logger, meter):
    summary = run_task(_task(), ScriptedAdapter([_r(text="oops", parse_ok=False)]),
                       "C1", logger, meter, lambda n, a: {"output": "x"}, max_turns=1)
    logger.close()
    assert summary["tehr_denom"] == 1 and summary["tehr_num"] == 0
