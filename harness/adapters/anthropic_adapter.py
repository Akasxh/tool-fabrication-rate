"""Anthropic adapter for Claude Sonnet 4.6 + Haiku 4.5 via native tool-use.

Implements :class:`harness.adapters.base.ModelAdapter` against
``anthropic.Anthropic.messages.create`` with the locked decoding params
(``temperature=0.0``, ``top_p=1.0``) defined in ADDENDUM_R1 §D.1.

Design notes (HARNESS_SPEC §2 + §8.1):
    * Adapter is **silent on tool-parse failures**: if a ``ToolUseBlock`` ships
      with malformed ``input`` (e.g. an unparsed string instead of a dict), we
      set ``parse_ok=False`` and emit zero ``ToolCall`` objects. The runner
      reclassifies that turn as ``parse_fail``.
    * Refusal *classification* is the runner's job (deny-list match on the
      assistant text channel). The adapter merely emits ``raw_text`` plus
      ``finish_reason`` and lets the runner decide.
    * Network / authentication / rate-limit errors raise
      :class:`AdapterError`. All other transport-level surprises also wrap
      into ``AdapterError`` so the runner sees a single error class.
    * ``raw_provider_payload`` carries ``response.model_dump()`` so debugging
      runs (``TraceLogger(persist_raw=True)``) capture the full SDK payload.
"""
from __future__ import annotations

import os
from time import monotonic_ns
from typing import Any

import anthropic

from harness.adapters.base import (
    LOCKED_MAX_TOKENS_DEFAULT,
    LOCKED_TEMPERATURE,
    LOCKED_TOP_P,
    AdapterError,
    ModelAdapter,
)
from harness.registry import render_for_anthropic
from harness.types import ProviderResponse, ToolCall

# Per HARNESS_SPEC §8.1 the Anthropic price table is given in $/1M tokens.
# Code-C convention (CostMeter.add) is $/1k tokens, so we divide by 1000 here
# and store the per-1k figures as the adapter's public price fields.
# Sonnet 4.6:  $3/M in,  $15/M out  → $0.003 / $0.015 per 1k.
# Haiku  4.5:  $1/M in,  $5/M out   → $0.001 / $0.005 per 1k.
_PRICE_TABLE_PER_1K: dict[str, tuple[float, float]] = {
    # Tier-uniform pricing: all Opus 4.x = $15/$75, all Sonnet 4.x = $3/$15,
    # all Haiku 4.x = $1/$5. Specific entries below take precedence via
    # longest-prefix matching, but the bare-tier prefixes act as fallbacks
    # for older dated aliases (e.g. claude-opus-4-20250514 → claude-opus-4).
    "claude-opus-4-7": (0.015, 0.075),
    "claude-opus-4-6": (0.015, 0.075),
    "claude-opus-4-5": (0.015, 0.075),
    "claude-opus-4-1": (0.015, 0.075),
    "claude-opus-4": (0.015, 0.075),
    "claude-sonnet-4-6": (0.003, 0.015),
    "claude-sonnet-4-5": (0.003, 0.015),
    "claude-sonnet-4": (0.003, 0.015),
    "claude-haiku-4-5": (0.001, 0.005),
    "claude-haiku-4": (0.001, 0.005),
}

# Anthropic finish-reason normalization (HARNESS_SPEC §3 column `finish_reason`).
_FINISH_REASON_MAP: dict[str, str] = {
    "tool_use": "tool_use",
    "end_turn": "stop",
    "max_tokens": "length",
}


def _resolve_prices(model_id: str) -> tuple[float, float]:
    """Resolve per-1k input/output prices from ``model_id``.

    Accepts both the bare alias (``claude-haiku-4-5``) and the dated alias
    (``claude-haiku-4-5-20251001``) by longest-prefix match against
    :data:`_PRICE_TABLE_PER_1K`.
    """
    for prefix in sorted(_PRICE_TABLE_PER_1K, key=len, reverse=True):
        if model_id.startswith(prefix):
            return _PRICE_TABLE_PER_1K[prefix]
    raise ValueError(
        f"AnthropicAdapter: unknown model_id {model_id!r}; "
        f"price table covers {sorted(_PRICE_TABLE_PER_1K)}"
    )


def _canonical_to_anthropic_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert canonical-OpenAI-shape tool list to Anthropic ``tools=`` shape.

    The runner passes ``tools`` as a list of canonical schemas
    (``{"name", "description", "parameters"}``); Anthropic's API expects
    ``{"name", "description", "input_schema"}``. We funnel through
    :func:`harness.registry.render_for_anthropic` so the conversion path is
    shared with the registry layer (single source of truth).
    """
    by_name: dict[str, dict[str, Any]] = {t["name"]: t for t in tools}
    return render_for_anthropic(by_name)


class AnthropicAdapter(ModelAdapter):
    """Adapter for Claude Sonnet 4.6 / Haiku 4.5 via Anthropic SDK tool-use.

    Args:
        model_id: One of ``claude-sonnet-4-6``, ``claude-haiku-4-5``, or
            the dated alias ``claude-haiku-4-5-20251001``.
        api_key: Optional API key; falls back to ``ANTHROPIC_API_KEY`` env var.
            Passing the key explicitly bypasses environment lookup, which is
            what the unit tests do (mocked client never hits the wire anyway).
    """

    def __init__(self, model_id: str, api_key: str | None = None) -> None:
        self.model_id: str = model_id
        self.price_per_1k_in, self.price_per_1k_out = _resolve_prices(model_id)
        resolved_key = api_key if api_key is not None else os.environ.get(
            "ANTHROPIC_API_KEY"
        )
        # Anthropic SDK accepts ``api_key=None`` and will itself raise on the
        # first request if the env var is also missing; mocked tests pass an
        # explicit key so this code path stays test-clean.
        self._client: anthropic.Anthropic = anthropic.Anthropic(api_key=resolved_key)

    def dispatch(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = LOCKED_MAX_TOKENS_DEFAULT,
    ) -> ProviderResponse:
        """Single ``messages.create`` round-trip; see class docstring."""
        anthropic_tools = _canonical_to_anthropic_tools(tools)
        start_ts = monotonic_ns()
        # Opus 4.7 deprecates `temperature` — only Sonnet 4.6 / Haiku 4.5 / older
        # 3.5 family accept it. Build kwargs conditionally.
        kwargs: dict[str, Any] = {
            "model": self.model_id,
            "max_tokens": max_tokens,
            "tools": anthropic_tools,
            "messages": messages,
        }
        if not self.model_id.startswith("claude-opus-4"):
            kwargs["temperature"] = LOCKED_TEMPERATURE
        try:
            response = self._client.messages.create(**kwargs)
        except (
            anthropic.APIError,
            anthropic.AuthenticationError,
            anthropic.RateLimitError,
            anthropic.APIConnectionError,
            ConnectionError,
        ) as exc:
            raise AdapterError(
                f"AnthropicAdapter network/auth failure on {self.model_id}: {exc}"
            ) from exc
        latency_ms = int((monotonic_ns() - start_ts) // 1_000_000)

        # Walk content blocks: TextBlock → raw_text; ToolUseBlock → ToolCall.
        # Type-check by attribute / `type` field rather than isinstance so we
        # tolerate the duck-typed mock objects used in the unit tests.
        raw_text_parts: list[str] = []
        tool_calls: list[ToolCall] = []
        parse_ok = True
        for block in getattr(response, "content", []) or []:
            block_type = getattr(block, "type", None)
            if block_type == "text":
                text = getattr(block, "text", "") or ""
                raw_text_parts.append(text)
            elif block_type == "tool_use":
                name = getattr(block, "name", "")
                arguments = getattr(block, "input", None)
                if not isinstance(arguments, dict):
                    # Malformed: e.g. ``input`` is a string the SDK could not
                    # JSON-parse server-side. Surface as parse_fail.
                    parse_ok = False
                    tool_calls = []
                    break
                tool_calls.append(ToolCall(name=name, arguments=arguments))
            # Other block types (e.g. server_tool_use) are ignored for v1.

        raw_stop = getattr(response, "stop_reason", None) or ""
        finish_reason = _FINISH_REASON_MAP.get(raw_stop, raw_stop)

        usage = getattr(response, "usage", None)
        tokens_in = int(getattr(usage, "input_tokens", 0) or 0)
        tokens_out = int(getattr(usage, "output_tokens", 0) or 0)

        # ``model_dump`` on real SDK responses; tests stub it as a callable.
        try:
            raw_payload: dict[str, Any] | None = response.model_dump()
        except Exception:  # pragma: no cover - defensive only
            raw_payload = None

        return ProviderResponse(
            raw_text="".join(raw_text_parts),
            tool_calls=tool_calls,
            parse_ok=parse_ok,
            finish_reason=finish_reason,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            raw_provider_payload=raw_payload,
        )
