"""OpenAI / xAI adapter (single class, two providers).

Implements :class:`OpenAIAdapter` per HARNESS_SPEC §2 and ADDENDUM_R1 §D.1
(locked decoding params). The same class also serves xAI by passing
``base_url="https://api.x.ai/v1"`` (deferred to G2 per HARNESS_SPEC §8.1).

Tool-parse failures (malformed ``arguments`` JSON) do NOT raise — they are
surfaced as ``ProviderResponse(parse_ok=False, tool_calls=[])``. Network and
auth errors raise :class:`AdapterError` so the runner can decide retry policy.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Optional

import openai

from harness.adapters.base import (
    LOCKED_MAX_TOKENS_DEFAULT,
    LOCKED_TEMPERATURE,
    LOCKED_TOP_P,
    AdapterError,
    ModelAdapter,
)
from harness.types import ProviderResponse, ToolCall

# Per HARNESS_SPEC §8.1: $/1M divided by 1000 → $/1k tokens.
_PRICE_PER_1K: dict[str, tuple[float, float]] = {
    # OpenAI gpt-4.1 family (chat-completions; size ladder for cross-vendor test)
    "gpt-4.1": (0.002, 0.008),
    "gpt-4.1-2025-04-14": (0.002, 0.008),
    "gpt-4.1-mini": (0.0004, 0.0016),
    "gpt-4.1-mini-2025-04-14": (0.0004, 0.0016),
    "gpt-4.1-nano": (0.0001, 0.0004),
    # gpt-4o family
    "gpt-4o": (0.0025, 0.01),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4-turbo": (0.01, 0.03),
    # gpt-5 family (reasoning; size ladder + frontier)
    "gpt-5": (0.00125, 0.01),
    "gpt-5-mini": (0.00025, 0.002),
    "gpt-5-nano": (0.00005, 0.0004),
    "gpt-5.5": (0.00125, 0.01),
    "gpt-5.4": (0.00125, 0.01),
    "gpt-5-chat-latest": (0.00125, 0.01),
    # o-series reasoning
    "o3": (0.002, 0.008),
    "o4-mini": (0.0011, 0.0044),
    # xAI tier (same adapter class, base_url switches provider)
    "grok-4": (0.003, 0.015),
    "grok-4-0709": (0.003, 0.015),
    "grok-4-fast": (0.0002, 0.0005),
}

# Reasoning models: reject temperature/top_p != default and require
# max_completion_tokens instead of max_tokens.
_REASONING_PREFIXES = ("gpt-5", "o1", "o3", "o4")

_XAI_BASE_URL = "https://api.x.ai/v1"


class OpenAIAdapter(ModelAdapter):
    """OpenAI Chat Completions adapter; xAI variant via ``base_url`` arg.

    Args:
        model_id: One of HARNESS_SPEC §8.1 pinned IDs (gpt-4.1, gpt-4.1-mini,
            their dated aliases, or the grok-4 family for xAI mode).
        api_key: Optional explicit API key. If ``None``, reads ``XAI_API_KEY``
            when ``base_url`` points at xAI, else ``OPENAI_API_KEY``.
        base_url: Optional alternative endpoint. Pass
            ``"https://api.x.ai/v1"`` for xAI; leave ``None`` for OpenAI.
    """

    def __init__(
        self,
        model_id: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self.model_id: str = model_id
        self.base_url: Optional[str] = base_url

        # Auto-select env var by base_url. xAI gets XAI_API_KEY; everything
        # else (default OpenAI endpoint) gets OPENAI_API_KEY.
        is_xai = base_url is not None and _XAI_BASE_URL in base_url
        env_key = "XAI_API_KEY" if is_xai else "OPENAI_API_KEY"
        resolved_key = api_key if api_key is not None else os.environ.get(env_key)
        self._api_key: Optional[str] = resolved_key
        self._is_xai: bool = is_xai

        # Known models get exact pricing; unknown (e.g. dated aliases of the
        # frontier ladder) fall back to a conservative default so the probe is
        # never blocked by a missing price entry. Cost tracking is advisory.
        self.price_per_1k_in, self.price_per_1k_out = _PRICE_PER_1K.get(
            model_id, (0.005, 0.015)
        )
        # Reasoning models (gpt-5*, o*) need a different param surface.
        self._is_reasoning: bool = any(
            model_id.startswith(p) for p in _REASONING_PREFIXES
        )

        client_kwargs: dict[str, Any] = {}
        if resolved_key is not None:
            client_kwargs["api_key"] = resolved_key
        if base_url is not None:
            client_kwargs["base_url"] = base_url
        self._client: openai.OpenAI = openai.OpenAI(**client_kwargs)

    def dispatch(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = LOCKED_MAX_TOKENS_DEFAULT,
    ) -> ProviderResponse:
        """Single round-trip to ``chat.completions.create``.

        ``tools`` MUST be in canonical OpenAI shape (use
        :func:`harness.registry.render_for_openai` upstream). Locked decoding
        params from :mod:`harness.adapters.base` are applied verbatim.
        """
        # Chat Completions requires tools as {"type":"function","function":{...}}.
        # The runner passes canonical inner schemas ({name,description,parameters});
        # wrap any that are not already in function-tool envelope shape.
        def _wrap(t: dict[str, Any]) -> dict[str, Any]:
            # Already a function-tool envelope: pass through.
            if t.get("type") == "function" and "function" in t:
                return t
            # Some shapes carry {"type":"function"} with the inner schema fields
            # flattened alongside (or empty). Prefer an inner "function" dict if
            # present, else read the bare inner schema fields off the top level.
            inner = t["function"] if isinstance(t.get("function"), dict) else t
            return {"type": "function", "function": {
                "name": inner.get("name", ""),
                "description": inner.get("description", ""),
                "parameters": inner.get(
                    "parameters", {"type": "object", "properties": {}}
                ),
            }}
        wrapped_tools = [_wrap(t) for t in tools] if tools else None

        start_ns = time.monotonic_ns()
        create_kwargs: dict[str, Any] = {
            "model": self.model_id,
            "messages": messages,
            "tools": wrapped_tools if wrapped_tools else openai.NOT_GIVEN,
        }
        if self._is_reasoning:
            # gpt-5*/o*: default temperature only, max_completion_tokens.
            create_kwargs["max_completion_tokens"] = max_tokens
        else:
            create_kwargs["temperature"] = LOCKED_TEMPERATURE
            create_kwargs["top_p"] = LOCKED_TOP_P
            create_kwargs["max_tokens"] = max_tokens
        # Retry on rate limits (low org TPM caps throttle the frontier ladder);
        # bounded backoff so a throttled task degrades gracefully rather than
        # dropping silently. Other API errors fail fast.
        response = None
        for attempt in range(5):
            try:
                response = self._client.chat.completions.create(**create_kwargs)
                break
            except openai.RateLimitError as exc:
                if attempt == 4:
                    raise AdapterError(
                        f"OpenAIAdapter rate-limited for {self.model_id!r}: {exc!r}"
                    ) from exc
                time.sleep(min(30.0, 3.0 * (2 ** attempt)))  # 3,6,12,24,30
            except (
                openai.APIError,
                openai.AuthenticationError,
                openai.APIConnectionError,
                ConnectionError,
            ) as exc:
                raise AdapterError(
                    f"OpenAIAdapter dispatch failed for model {self.model_id!r}: {exc!r}"
                ) from exc

        latency_ms = int((time.monotonic_ns() - start_ns) / 1_000_000)

        choice = response.choices[0]
        message = choice.message
        raw_text: str = message.content or ""

        # Refusal channel takes precedence over finish_reason mapping below.
        refusal_text = getattr(message, "refusal", None)
        is_refusal = bool(refusal_text)
        if is_refusal and not raw_text:
            raw_text = refusal_text or ""

        # Parse tool_calls; arguments arrive as a JSON-encoded string. On any
        # JSONDecodeError we fail closed: parse_ok=False, tool_calls=[].
        parse_ok = True
        parsed_calls: list[ToolCall] = []
        sdk_tool_calls = message.tool_calls or []
        for tc in sdk_tool_calls:
            try:
                args_obj = json.loads(tc.function.arguments)
            except (json.JSONDecodeError, TypeError):
                parse_ok = False
                parsed_calls = []
                break
            if not isinstance(args_obj, dict):
                # tools spec requires arguments to deserialize to an object.
                parse_ok = False
                parsed_calls = []
                break
            parsed_calls.append(ToolCall(name=tc.function.name, arguments=args_obj))

        # finish_reason mapping. OpenAI emits: stop | length | tool_calls |
        # content_filter | function_call (legacy). We normalize "tool_calls"
        # → "tool_use" so the runner sees one token across all 3 adapters.
        provider_finish = choice.finish_reason or ""
        if is_refusal:
            finish_reason = "refusal"
        elif provider_finish == "tool_calls":
            finish_reason = "tool_use"
        elif provider_finish == "content_filter":
            finish_reason = "refusal"
        else:
            finish_reason = provider_finish

        usage = response.usage
        tokens_in = int(usage.prompt_tokens) if usage is not None else 0
        tokens_out = int(usage.completion_tokens) if usage is not None else 0

        # raw_provider_payload: TraceLogger drops this at log-time unless
        # persist_raw=True. Defensive: model_dump may fail on mocks.
        try:
            raw_payload: Optional[dict] = response.model_dump()
        except Exception:  # pragma: no cover - defensive against non-pydantic mocks
            raw_payload = None

        return ProviderResponse(
            raw_text=raw_text,
            tool_calls=parsed_calls,
            parse_ok=parse_ok,
            finish_reason=finish_reason,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            raw_provider_payload=raw_payload,
        )
