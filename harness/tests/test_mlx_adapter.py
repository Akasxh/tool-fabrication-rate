"""Unit tests for MLXAdapter (Phase-1 / A3).

Covers HARNESS_SPEC §4 MLX fixtures 1-4, §5 acceptance #1, plus the A3
adapter-specific assertions: enable_thinking=False reaches apply_chat_template;
date-hint system message is injected/merged; <tool_call> envelopes stripped
from raw_text. mlx_lm.load / generate / make_sampler all mocked.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Stub mlx_lm so the adapter's lazy imports resolve on hosts without mlx-lm. #
for _name in ("mlx_lm", "mlx_lm.sample_utils"):
    if _name not in sys.modules:
        sys.modules[_name] = types.ModuleType(_name)
sys.modules["mlx_lm"].load = MagicMock(name="mlx_lm.load")  # type: ignore[attr-defined]
sys.modules["mlx_lm"].generate = MagicMock(name="mlx_lm.generate")  # type: ignore[attr-defined]
sys.modules["mlx_lm.sample_utils"].make_sampler = MagicMock(  # type: ignore[attr-defined]
    return_value=MagicMock(name="sampler")
)

from harness.adapters.mlx_adapter import MLXAdapter, _DATE_HINT  # noqa: E402
from harness.types import ProviderResponse, ToolCall  # noqa: E402

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "mlx_responses.json"


@pytest.fixture(scope="module")
def fixtures() -> dict[str, dict[str, Any]]:
    with _FIXTURE_PATH.open() as f:
        return json.load(f)["fixtures"]


def _adapter(raw: str, *, encoded_raw_len: int | None = None) -> tuple[
    MLXAdapter, MagicMock, MagicMock
]:
    """Pre-loaded adapter + tokenizer + generate mocks. _ensure_loaded skipped."""
    if encoded_raw_len is None:
        encoded_raw_len = max(1, len(raw) // 4)
    tok = MagicMock(name="tokenizer")
    tok.apply_chat_template = MagicMock(return_value="<rendered-prompt>")
    tok.encode = MagicMock(side_effect=lambda s: [0] * (
        42 if s == "<rendered-prompt>" else encoded_raw_len
    ))
    a = MLXAdapter()
    a._model = MagicMock(name="model")
    a._tokenizer = tok
    a._sampler = MagicMock(name="sampler")
    return a, tok, MagicMock(name="generate", return_value=raw)


def _go(
    a: MLXAdapter,
    gen: MagicMock,
    *,
    messages: list[dict[str, Any]] | None = None,
    tools: list[dict[str, Any]] | None = None,
    max_tokens: int = 1024,
) -> ProviderResponse:
    msgs = messages or [{"role": "user", "content": "hi"}]
    tls = tools if tools is not None else [{"name": "get_weather"}]
    with patch("mlx_lm.generate", gen):
        return a.dispatch(msgs, tls, max_tokens=max_tokens)


# §4 fixtures 1-4 ---------------------------------------------------------- #
@pytest.mark.parametrize(
    "key",
    ["clean_tool_call", "hallucinated_tool_call", "refusal_no_tool", "parse_fail_malformed"],
)
def test_fixture_round_trip(key: str, fixtures: dict[str, dict[str, Any]]) -> None:
    fx = fixtures[key]
    expected = fx["expected"]
    a, _t, gen = _adapter(fx["raw"])
    resp = _go(a, gen)
    assert isinstance(resp, ProviderResponse)
    assert resp.parse_ok is expected["parse_ok"]
    assert resp.finish_reason == expected["finish_reason"]
    assert resp.raw_text == expected["raw_text"]
    assert len(resp.tool_calls) == len(expected["tool_calls"])
    for got, want in zip(resp.tool_calls, expected["tool_calls"]):
        assert isinstance(got, ToolCall)
        assert got.name == want["name"]
        assert got.arguments == want["arguments"]
    assert resp.raw_provider_payload is None
    assert resp.tokens_in > 0 and resp.tokens_out > 0 and resp.latency_ms >= 0


# enable_thinking=False ---------------------------------------------------- #
def test_enable_thinking_false_passed_to_template() -> None:
    a, tok, gen = _adapter("plain text response")
    _go(a, gen)
    tok.apply_chat_template.assert_called_once()
    _, kw = tok.apply_chat_template.call_args
    assert kw.get("enable_thinking") is False
    assert kw.get("add_generation_prompt") is True
    assert kw.get("tokenize") is False


# Date-hint injection ------------------------------------------------------ #
def test_date_hint_inserted_when_no_system_message() -> None:
    a, tok, gen = _adapter("ok")
    msgs = [{"role": "user", "content": "What's the date?"}]
    _go(a, gen, messages=msgs)
    args, kw = tok.apply_chat_template.call_args
    rendered = args[0] if args else kw.get("conversation")
    assert rendered[0]["role"] == "system"
    assert _DATE_HINT in rendered[0]["content"]
    assert rendered[1] == {"role": "user", "content": "What's the date?"}


def test_date_hint_merged_into_existing_system_message() -> None:
    a, tok, gen = _adapter("ok")
    sysmsg = "You are a helpful assistant."
    _go(a, gen, messages=[
        {"role": "system", "content": sysmsg},
        {"role": "user", "content": "Hi."},
    ])
    rendered = tok.apply_chat_template.call_args.args[0]
    sysm = [m for m in rendered if m["role"] == "system"]
    assert len(sysm) == 1
    assert _DATE_HINT in sysm[0]["content"] and sysmsg in sysm[0]["content"]


def test_date_hint_idempotent_on_already_present() -> None:
    a, tok, gen = _adapter("ok")
    _go(a, gen, messages=[
        {"role": "system", "content": _DATE_HINT + "\n\nbe brief"},
        {"role": "user", "content": "Hi."},
    ])
    rendered = tok.apply_chat_template.call_args.args[0]
    assert rendered[0]["content"].count(_DATE_HINT) == 1


def test_caller_messages_not_mutated() -> None:
    a, _t, gen = _adapter("ok")
    msgs = [{"role": "user", "content": "Hi."}]
    snapshot = [dict(m) for m in msgs]
    _go(a, gen, messages=msgs)
    assert msgs == snapshot
    assert all(m.get("role") != "system" for m in msgs)


# raw_text envelope stripping --------------------------------------------- #
def test_raw_text_strips_envelopes() -> None:
    raw = (
        "Sure, I'll look that up.\n"
        '<tool_call>\n{"name": "get_weather", "arguments": {"city": "SF"}}\n</tool_call>\n'
        "Done."
    )
    a, _t, gen = _adapter(raw)
    resp = _go(a, gen)
    assert "<tool_call>" not in resp.raw_text and "</tool_call>" not in resp.raw_text
    assert "Sure, I'll look that up." in resp.raw_text and "Done." in resp.raw_text
    assert len(resp.tool_calls) == 1 and resp.tool_calls[0].name == "get_weather"


# finish_reason heuristic ------------------------------------------------- #
def test_finish_reason_length_when_max_tokens_hit() -> None:
    a, _t, gen = _adapter("x" * 2000, encoded_raw_len=64)
    assert _go(a, gen, max_tokens=64).finish_reason == "length"


def test_finish_reason_tool_use_dominates_length() -> None:
    raw = '<tool_call>{"name": "get_weather", "arguments": {"city": "SF"}}</tool_call>'
    a, _t, gen = _adapter(raw, encoded_raw_len=128)
    assert _go(a, gen, max_tokens=128).finish_reason == "tool_use"


# Pricing + lazy load ----------------------------------------------------- #
def test_pricing_is_zero_for_local_model() -> None:
    a = MLXAdapter()
    assert a.price_per_1k_in == 0.0 and a.price_per_1k_out == 0.0
    assert a.model_id == "mlx-community/Qwen3-8B-4bit"


def test_lazy_load_does_not_run_at_construction() -> None:
    a = MLXAdapter()
    assert a._model is None and a._tokenizer is None


def test_ensure_loaded_calls_mlx_lm_load_once() -> None:
    tok = MagicMock(apply_chat_template=MagicMock(return_value="P"),
                    encode=MagicMock(return_value=[0, 1, 2]))
    load_mock = MagicMock(return_value=(MagicMock(), tok))
    a = MLXAdapter()
    with patch("mlx_lm.load", load_mock), patch(
        "mlx_lm.sample_utils.make_sampler", MagicMock(return_value=MagicMock())
    ), patch("mlx_lm.generate", MagicMock(return_value="ok")):
        a.dispatch([{"role": "user", "content": "hi"}], [])
        a.dispatch([{"role": "user", "content": "again"}], [])
    assert load_mock.call_count == 1
    assert load_mock.call_args.args == ("mlx-community/Qwen3-8B-4bit",)
