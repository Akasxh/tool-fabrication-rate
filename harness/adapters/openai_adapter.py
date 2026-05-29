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
    # OpenAI tier
    "gpt-4.1": (0.002, 0.008),
    "gpt-4.1-2025-04-14": (0.002, 0.008),
    "gpt-4.1-mini": (0.0004, 0.0016),
    "gpt-4.1-mini-2025-04-14": (0.0004, 0.0016),
    # xAI tier (deferred to G2; same adapter class, base_url switches provider)
    "grok-4": (0.003, 0.015),
    "grok-4-0709": (0.003, 0.015),
    "grok-4-fast": (0.0002, 0.0005),
}

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

        if model_id not in _PRICE_PER_1K:
            raise ValueError(
                f"OpenAIAdapter: unknown model_id {model_id!r}; "
                f"expected one of {sorted(_PRICE_PER_1K)}"
            )
        self.price_per_1k_in, self.price_per_1k_out = _PRICE_PER_1K[model_id]

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
        start_ns = time.monotonic_ns()
        try:
            response = self._client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                tools=tools if tools else openai.NOT_GIVEN,
                temperature=LOCKED_TEMPERATURE,
                top_p=LOCKED_TOP_P,
                max_tokens=max_tokens,
            )
        except (
            openai.APIError,
            openai.AuthenticationError,
            openai.RateLimitError,
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
