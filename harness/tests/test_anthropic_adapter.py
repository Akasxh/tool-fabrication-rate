"""Unit tests for ``harness.adapters.anthropic_adapter.AnthropicAdapter``.

Covers HARNESS_SPEC §4 Anthropic fixtures (4 cases) plus locked decoding
params (ADDENDUM_R1 §D.1) and network-error rewrap (HARNESS_SPEC §2). All
tests mock the SDK ``messages.create`` call - no real API requests.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from harness.adapters.anthropic_adapter import AnthropicAdapter
from harness.adapters.base import (
    LOCKED_MAX_TOKENS_DEFAULT,
    LOCKED_TEMPERATURE,
    LOCKED_TOP_P,
    AdapterError,
)

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "anthropic_responses.json"

_TOOL_LIST: list[dict[str, Any]] = [
    {
        "name": "get_weather",
        "description": "Look up the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
]
_MESSAGES: list[dict[str, Any]] = [
    {"role": "user", "content": "What's the weather in SF?"}
]


def _load_fixtures() -> list[dict[str, Any]]:
    with _FIXTURE_PATH.open() as fh:
        return json.load(fh)


def _build_mock_response(raw: dict[str, Any]) -> SimpleNamespace:
    """Translate a fixture's ``raw`` dict into a duck-typed SDK response.

    Adapter reads ``response.content`` (blocks), ``response.stop_reason``,
    ``response.usage.{input,output}_tokens``, and ``response.model_dump()``.
    The ``parse_fail_malformed_input`` fixture uses ``input_raw_string`` to
    feed a non-dict ``input`` (a real ``ToolUseBlock`` validates ``input`` as
    a dict, so the malformed path can only be exercised via duck typing).
    """
    blocks: list[Any] = []
    for b in raw["content"]:
        if b["type"] == "text":
            blocks.append(SimpleNamespace(type="text", text=b["text"]))
        elif b["type"] == "tool_use":
            input_value: Any = b.get("input_raw_string", b.get("input"))
            blocks.append(
                SimpleNamespace(type="tool_use", name=b["name"], input=input_value)
            )
    usage = SimpleNamespace(
        input_tokens=raw["usage"]["input_tokens"],
        output_tokens=raw["usage"]["output_tokens"],
    )
    response = SimpleNamespace(
        content=blocks, stop_reason=raw["stop_reason"], usage=usage
    )
    response.model_dump = lambda: {  # type: ignore[attr-defined]
        "stop_reason": raw["stop_reason"],
        "content": raw["content"],
        "usage": raw["usage"],
    }
    return response


def _build_adapter_with_mock(raw: dict[str, Any]) -> tuple[AnthropicAdapter, MagicMock]:
    adapter = AnthropicAdapter(model_id="claude-haiku-4-5", api_key="test-fake-key")
    mock_create = MagicMock(return_value=_build_mock_response(raw))
    adapter._client.messages.create = mock_create  # type: ignore[assignment]
    return adapter, mock_create


@pytest.mark.parametrize("fixture", _load_fixtures(), ids=lambda f: f["name"])
def test_anthropic_fixture_dispatch(fixture: dict[str, Any]) -> None:
    """Each of the 4 fixtures: dispatch → ProviderResponse field-by-field."""
    adapter, _ = _build_adapter_with_mock(fixture["raw"])
    response = adapter.dispatch(messages=_MESSAGES, tools=_TOOL_LIST)

    expected = fixture["expected"]
    assert response.raw_text == expected["raw_text"], fixture["name"]
    assert response.parse_ok is expected["parse_ok"], fixture["name"]
    assert response.finish_reason == expected["finish_reason"], fixture["name"]
    assert response.tokens_in == expected["tokens_in"], fixture["name"]
    assert response.tokens_out == expected["tokens_out"], fixture["name"]
    assert len(response.tool_calls) == len(expected["tool_calls"]), fixture["name"]
    for got, want in zip(response.tool_calls, expected["tool_calls"]):
        assert got.name == want["name"], fixture["name"]
        assert got.arguments == want["arguments"], fixture["name"]
    assert isinstance(response.latency_ms, int)
    assert response.latency_ms >= 0


def test_locked_decoding_params_are_passed_to_sdk() -> None:
    """ADDENDUM_R1 §D.1: temperature=0.0 must reach the SDK call.

    Note: ``top_p`` is intentionally NOT passed for Sonnet 4.6 / Haiku 4.5
    (the API rejects both temperature and top_p set simultaneously). At
    temperature=0.0 (greedy decoding) top_p is functionally irrelevant.
    """
    fixtures = _load_fixtures()
    adapter, mock_create = _build_adapter_with_mock(fixtures[0]["raw"])
    adapter.dispatch(messages=_MESSAGES, tools=_TOOL_LIST)

    assert mock_create.call_count == 1
    kwargs = mock_create.call_args.kwargs
    assert kwargs["temperature"] == LOCKED_TEMPERATURE
    assert "top_p" not in kwargs, "Anthropic API rejects both temperature and top_p"
    assert kwargs["max_tokens"] == LOCKED_MAX_TOKENS_DEFAULT
    assert kwargs["model"] == "claude-haiku-4-5"
    # Tool conversion: canonical OpenAI shape → Anthropic input_schema shape.
    sent_tools = kwargs["tools"]
    assert len(sent_tools) == 1
    assert sent_tools[0]["name"] == "get_weather"
    assert "input_schema" in sent_tools[0]
    assert "parameters" not in sent_tools[0]


def test_max_tokens_override_is_forwarded() -> None:
    fixtures = _load_fixtures()
    adapter, mock_create = _build_adapter_with_mock(fixtures[0]["raw"])
    adapter.dispatch(messages=_MESSAGES, tools=_TOOL_LIST, max_tokens=256)
    assert mock_create.call_args.kwargs["max_tokens"] == 256


def test_network_failure_raises_adapter_error() -> None:
    """Simulated transport drop → :class:`AdapterError` (not raw exception)."""
    fixtures = _load_fixtures()
    adapter, _ = _build_adapter_with_mock(fixtures[0]["raw"])

    def _boom(*_args: Any, **_kwargs: Any) -> None:
        raise ConnectionError("simulated network drop")

    adapter._client.messages.create = _boom  # type: ignore[assignment]
    with pytest.raises(AdapterError):
        adapter.dispatch(messages=_MESSAGES, tools=_TOOL_LIST)


def test_price_table_resolves_aliases_and_rejects_unknown() -> None:
    a = AnthropicAdapter(model_id="claude-haiku-4-5-20251001", api_key="x")
    assert (a.price_per_1k_in, a.price_per_1k_out) == (0.001, 0.005)
    s = AnthropicAdapter(model_id="claude-sonnet-4-6", api_key="x")
    assert (s.price_per_1k_in, s.price_per_1k_out) == (0.003, 0.015)
    with pytest.raises(ValueError):
        AnthropicAdapter(model_id="claude-unknown-9000", api_key="x")
