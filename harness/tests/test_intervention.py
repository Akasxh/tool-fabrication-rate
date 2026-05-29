"""Unit tests for the three intervention conditions + adapter base constants.

Covers HARNESS_SPEC §2 + ADDENDUM_R1 §B.2 (C0.7) + §D.1 (locked decoding).

NOTE: imports ``harness.types`` (owned by Code-A). If Code-A has not
landed those types yet, we install a minimal shim into ``sys.modules``
so this test file is runnable in isolation. The shim must be byte-equal
to the spec'd dataclasses; remove this block once Code-A lands.
"""
from __future__ import annotations

import json
import sys

# TODO-remove-when-Code-A-lands: shim for harness.types
try:
    from harness.types import Action, ActionKind, ToolCall  # type: ignore
except ImportError:  # pragma: no cover
    import types as _types
    from dataclasses import dataclass
    from enum import Enum
    from typing import Any, Optional

    @dataclass(frozen=True)
    class ToolCall:  # type: ignore[no-redef]
        name: str
        arguments: dict[str, Any]

    class ActionKind(Enum):  # type: ignore[no-redef]
        EXECUTE = "execute"
        RE_PROMPT = "re_prompt"
        ABORT = "abort"

    @dataclass(frozen=True)
    class Action:  # type: ignore[no-redef]
        kind: ActionKind
        tool_call: Optional[ToolCall] = None
        feedback: Optional[str] = None

    @dataclass(frozen=True)
    class ProviderResponse:  # type: ignore
        raw_text: str
        tool_calls: list
        parse_ok: bool
        finish_reason: str
        tokens_in: int
        tokens_out: int
        latency_ms: int
        raw_provider_payload: Optional[dict] = None

    _shim = _types.ModuleType("harness.types")
    _shim.Action = Action
    _shim.ActionKind = ActionKind
    _shim.ToolCall = ToolCall
    _shim.ProviderResponse = ProviderResponse
    sys.modules["harness.types"] = _shim
# end-shim

from harness.adapters import base  # noqa: E402
from harness.intervention.framework_default import framework_default  # noqa: E402
from harness.intervention.naive_retry import naive_retry  # noqa: E402
from harness.intervention.rvr import rvr  # noqa: E402

_REGISTRY: dict[str, dict] = {
    "get_weather": {"description": "weather", "parameters": {"type": "object"}},
    "book_flight": {"description": "flight", "parameters": {"type": "object"}},
}


# 1. RVR clean tool call → EXECUTE
def test_rvr_executes_known_tool() -> None:
    call = ToolCall(name="get_weather", arguments={"city": "SF"})
    action = rvr([call], _REGISTRY)
    assert action.kind == ActionKind.EXECUTE
    assert action.tool_call == call
    assert action.feedback is None


# 2. RVR hallucinated → RE_PROMPT with name + sorted registry list
def test_rvr_reprompts_with_registry_list() -> None:
    one_tool = {"get_weather": {"description": "w", "parameters": {"type": "object"}}}
    call = ToolCall(name="get_weather_v2", arguments={})
    action = rvr([call], one_tool)
    assert action.kind == ActionKind.RE_PROMPT
    assert action.tool_call is None
    assert action.feedback is not None
    assert "get_weather_v2" in action.feedback
    assert "['get_weather']" in action.feedback


def test_rvr_registry_list_is_sorted() -> None:
    # Insertion order ≠ sorted order, to verify sort.
    reg = {"zebra": {}, "alpha": {}, "mango": {}}
    call = ToolCall(name="missing", arguments={})
    action = rvr([call], reg)
    assert action.feedback is not None
    assert "['alpha', 'mango', 'zebra']" in action.feedback


# 3. Naive retry returns the locked feedback verbatim
def test_naive_retry_locked_feedback_string() -> None:
    locked = "Your previous tool call failed. Please try again."
    for call in (
        ToolCall(name="anything_missing", arguments={}),
        ToolCall(name="another_missing", arguments={"x": 1}),
    ):
        action = naive_retry([call], _REGISTRY)
        assert action.kind == ActionKind.RE_PROMPT
        assert action.feedback == locked


# 4. framework_default emits valid JSON with the three required keys
def test_framework_default_emits_json_with_required_keys() -> None:
    call = ToolCall(name="phantom_tool", arguments={"q": "x"})
    action = framework_default([call], _REGISTRY)
    assert action.kind == ActionKind.RE_PROMPT
    assert action.feedback is not None
    payload = json.loads(action.feedback)
    assert set(payload.keys()) == {"error", "attempted", "details"}
    assert payload["error"] == "tool_not_found"
    assert payload["attempted"] == "phantom_tool"
    assert payload["details"] == "function not in registry"


# 5. Empty parsed_calls → EXECUTE(tool_call=None) for all three
def test_empty_parsed_calls_returns_execute_none_for_all_three() -> None:
    for fn in (rvr, naive_retry, framework_default):
        action = fn([], _REGISTRY)
        assert action.kind == ActionKind.EXECUTE, f"{fn.__name__} should EXECUTE on empty"
        assert action.tool_call is None
        assert action.feedback is None


# 6. base module exposes locked decoding constants
def test_base_locked_decoding_constants() -> None:
    assert base.LOCKED_TEMPERATURE == 0.0
    assert base.LOCKED_TOP_P == 1.0
    assert base.LOCKED_MAX_TOKENS_DEFAULT == 1024


# Bonus: framework_default executes when tool is in registry
def test_framework_default_executes_known_tool() -> None:
    call = ToolCall(name="get_weather", arguments={"city": "NYC"})
    action = framework_default([call], _REGISTRY)
    assert action.kind == ActionKind.EXECUTE
    assert action.tool_call == call


# Bonus: naive_retry executes when tool is in registry
def test_naive_retry_executes_known_tool() -> None:
    call = ToolCall(name="book_flight", arguments={"from": "SFO", "to": "JFK"})
    action = naive_retry([call], _REGISTRY)
    assert action.kind == ActionKind.EXECUTE
    assert action.tool_call == call
