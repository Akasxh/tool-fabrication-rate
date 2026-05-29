"""Abstract ModelAdapter interface.

Per HARNESS_SPEC §2 and ADDENDUM_R1 §D.1: all concrete adapters
(Anthropic, OpenAI/xAI, MLX) MUST honor the locked decoding params
defined here. Tool-parse failures are reported via
``ProviderResponse(parse_ok=False)`` rather than raised; only network
or auth errors raise (as ``AdapterError``).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from harness.types import ProviderResponse

# Locked decoding params (ADDENDUM_R1 §D.1). All adapters MUST use these.
LOCKED_TEMPERATURE: float = 0.0
LOCKED_TOP_P: float = 1.0
LOCKED_MAX_TOKENS_DEFAULT: int = 1024


class AdapterError(RuntimeError):
    """Raised by adapters on network or authentication failures.

    Tool-parse failures do NOT raise; they are surfaced as
    ``ProviderResponse(parse_ok=False, tool_calls=[])``.
    """


class ModelAdapter(ABC):
    """Abstract provider adapter; concrete subclasses ship per provider."""

    model_id: str
    price_per_1k_in: float
    price_per_1k_out: float

    @abstractmethod
    def dispatch(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = LOCKED_MAX_TOKENS_DEFAULT,
    ) -> ProviderResponse:
        """Single provider round-trip. MUST use LOCKED_TEMPERATURE / LOCKED_TOP_P."""
        raise NotImplementedError
