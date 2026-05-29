"""Unit tests for :class:`harness.adapters.openai_adapter.OpenAIAdapter`.

Covers HARNESS_SPEC §4 OpenAI fixtures (clean / hallucinated / refusal /
parse_fail), ADDENDUM_R1 §D.1 locked decoding params, AdapterError on
network failures, and the xAI ``base_url`` env-var routing. NO real API
calls — ``chat.completions.create`` is mocked.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import openai
import pytest
from openai.types.chat import ChatCompletion

from harness.adapters import base
from harness.adapters.openai_adapter import OpenAIAdapter
from harness.types import ToolCall

_FIXTURES: dict[str, Any] = json.loads(
    (Path(__file__).parent / "fixtures" / "openai_responses.json").read_text()
)


def _hydrate(name: str) -> ChatCompletion:
    return ChatCompletion.model_validate(_FIXTURES[name]["response"])


def _adapter(monkeypatch: pytest.MonkeyPatch, response: Any, **kw: Any) -> tuple[OpenAIAdapter, MagicMock]:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    a = OpenAIAdapter(model_id=kw.pop("model_id", "gpt-4.1-2025-04-14"), **kw)
    m = MagicMock(return_value=response)
    a._client.chat.completions.create = m  # type: ignore[assignment]
    return a, m


# §4 fixture acceptance items 1-4 ------------------------------------------------
def test_clean_tool_call(monkeypatch: pytest.MonkeyPatch) -> None:
    a, _ = _adapter(monkeypatch, _hydrate("clean_tool_call"))
    out = a.dispatch(messages=[{"role": "user", "content": "x"}], tools=[{"type": "function"}])
    assert out.parse_ok and out.finish_reason == "tool_use"
    assert len(out.tool_calls) == 1
    assert out.tool_calls[0] == ToolCall(name="get_weather", arguments={"city": "SF"})
    assert out.tokens_in == 42 and out.tokens_out == 11
    assert out.raw_text == "" and out.latency_ms >= 0


def test_hallucinated_tool_call(monkeypatch: pytest.MonkeyPatch) -> None:
    a, _ = _adapter(monkeypatch, _hydrate("hallucinated_tool_call"))
    out = a.dispatch(messages=[], tools=[])
    # Adapter is non-classifying; runner decides hallucinated by name ∉ registry.
    assert out.parse_ok and out.finish_reason == "tool_use"
    assert out.tool_calls[0].name == "lookup_weather_api"
    assert out.tool_calls[0].arguments == {"city": "SF"}


def test_refusal_safety(monkeypatch: pytest.MonkeyPatch) -> None:
    a, _ = _adapter(monkeypatch, _hydrate("refusal_safety"))
    out = a.dispatch(messages=[], tools=[])
    assert out.parse_ok and out.finish_reason == "refusal"
    assert out.tool_calls == []
    assert "cannot help" in out.raw_text.lower()
    assert out.tokens_in == 30 and out.tokens_out == 8


def test_parse_fail_bad_json(monkeypatch: pytest.MonkeyPatch) -> None:
    a, _ = _adapter(monkeypatch, _hydrate("parse_fail_bad_json"))
    out = a.dispatch(messages=[], tools=[])
    assert out.parse_ok is False
    assert out.tool_calls == []
    assert out.finish_reason == "tool_use"


# Locked decoding params (ADDENDUM_R1 §D.1) -------------------------------------
def test_locked_decoding_params_in_call_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    a, m = _adapter(monkeypatch, _hydrate("clean_tool_call"))
    a.dispatch(messages=[{"role": "user", "content": "x"}], tools=[])
    kw = m.call_args.kwargs
    assert kw["temperature"] == base.LOCKED_TEMPERATURE == 0.0
    assert kw["top_p"] == base.LOCKED_TOP_P == 1.0
    assert kw["max_tokens"] == base.LOCKED_MAX_TOKENS_DEFAULT
    assert kw["model"] == "gpt-4.1-2025-04-14"


def test_max_tokens_override_passes_through(monkeypatch: pytest.MonkeyPatch) -> None:
    a, m = _adapter(monkeypatch, _hydrate("clean_tool_call"))
    a.dispatch(messages=[], tools=[], max_tokens=256)
    assert m.call_args.kwargs["max_tokens"] == 256


def test_empty_tools_passes_not_given_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    a, m = _adapter(monkeypatch, _hydrate("refusal_safety"))
    a.dispatch(messages=[], tools=[])
    assert m.call_args.kwargs["tools"] is openai.NOT_GIVEN


# AdapterError on simulated network/auth exceptions -----------------------------
def test_adapter_error_on_network_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    a, m = _adapter(monkeypatch, _hydrate("clean_tool_call"))
    m.side_effect = openai.APIConnectionError(request=MagicMock())
    with pytest.raises(base.AdapterError):
        a.dispatch(messages=[], tools=[])


def test_adapter_error_on_authentication_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    a, m = _adapter(monkeypatch, _hydrate("clean_tool_call"))
    m.side_effect = openai.AuthenticationError(
        message="bad key", response=MagicMock(status_code=401, request=MagicMock()), body=None
    )
    with pytest.raises(base.AdapterError):
        a.dispatch(messages=[], tools=[])


# xAI base_url path: env-var routing --------------------------------------------
def test_xai_base_url_uses_xai_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("XAI_API_KEY", "xai-secret-zzz")
    a = OpenAIAdapter(model_id="grok-4-0709", base_url="https://api.x.ai/v1")
    assert a._is_xai is True and a._api_key == "xai-secret-zzz"
    assert a.base_url == "https://api.x.ai/v1"
    assert a.price_per_1k_in == 0.003 and a.price_per_1k_out == 0.015


def test_default_base_url_uses_openai_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-secret")
    a = OpenAIAdapter(model_id="gpt-4.1-mini-2025-04-14")
    assert a._is_xai is False and a._api_key == "sk-openai-secret"
    assert a.price_per_1k_in == 0.0004 and a.price_per_1k_out == 0.0016


def test_unknown_model_id_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with pytest.raises(ValueError):
        OpenAIAdapter(model_id="gpt-5-not-real")
