"""MLX adapter for ``mlx-community/Qwen3-8B-4bit`` (Phase-1 / A3).

Per HARNESS_SPEC §2 ``MLXAdapter`` block + §8.5 (G0.5 RESOLVED) + ADDENDUM_R1
§D.1 (decoding lock). This adapter renders messages through the Qwen3 chat
template (with ``enable_thinking=False`` and a ``Today's date is 2026-04-27.``
system hint), runs ``mlx_lm.generate`` with a greedy/locked-top-p sampler, then
parses the Qwen3 ``<tool_call>{json}</tool_call>`` envelope.

Hard contract knobs (do NOT relax without a §8.5/ADDENDUM update):
    * Repo: ``mlx-community/Qwen3-8B-4bit`` (the ``-Instruct-4bit`` variant
      doesn't exist on HF; G0.5 verified).
    * ``enable_thinking=False`` — Qwen3's reasoning toggle defaults ON and
      injects ``<think>...</think>`` blocks that break the parser regex.
    * Date hint — Qwen3 defaults relative dates to its 2023-ish cutoff; we
      prepend a system message so BFCL/τ-bench date-dependent grading works.
    * Decoding: ``LOCKED_TEMPERATURE`` (0.0) + ``LOCKED_TOP_P`` (1.0).
    * Pricing: $0/1k both directions (local model).

Heavy ``mlx_lm`` import + model load are deferred to first dispatch via
:meth:`_ensure_loaded` so that (a) test code can patch ``mlx_lm.load`` /
``mlx_lm.generate`` at module level, and (b) construction is cheap on machines
without MLX installed (e.g. linting, CI lanes that skip MLX).
"""
from __future__ import annotations

import json
import re
from time import monotonic_ns
from typing import Any

from harness.adapters.base import (
    LOCKED_MAX_TOKENS_DEFAULT,
    LOCKED_TEMPERATURE,
    LOCKED_TOP_P,
    AdapterError,
    ModelAdapter,
)
from harness.types import ProviderResponse, ToolCall

# Qwen3 tool-call envelope. ``DOTALL`` so multi-line JSON inside the envelope
# (which Qwen3 routinely emits) is captured by the ``\{.*?\}`` group. Verified
# at G0.5 (PHASE0/mlx_feasibility.md) on the live model.
_TOOL_CALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)

# Date hint locked to today's date for the run; Qwen3 hallucinates the year on
# relative-date prompts (G0.5 quirk #3).
_DATE_HINT: str = "Today's date is 2026-04-27."


class MLXAdapter(ModelAdapter):
    """Local-tier adapter for Qwen3-8B-4bit running on Apple Silicon via MLX.

    Args:
        model_id: HuggingFace repo id for ``mlx_lm.load``. Default is the
            G0.5-confirmed ``mlx-community/Qwen3-8B-4bit``.

    Attributes:
        model_id: As above.
        price_per_1k_in: Always ``0.0`` (local model).
        price_per_1k_out: Always ``0.0`` (local model).
    """

    def __init__(self, model_id: str = "mlx-community/Qwen3-8B-4bit") -> None:
        self.model_id: str = model_id
        self.price_per_1k_in: float = 0.0
        self.price_per_1k_out: float = 0.0
        # Lazy-loaded on first dispatch; cold load is ~3.5 min on M5 (G0.5).
        self._model: Any = None
        self._tokenizer: Any = None
        self._sampler: Any = None

    def _ensure_loaded(self) -> None:
        """Load the MLX model + tokenizer + sampler exactly once.

        Imports are local so a process that never dispatches doesn't pay the
        ~3.5 min cold-load tax (and so test code can monkey-patch the
        ``mlx_lm`` import surface before this method runs).
        """
        if self._model is not None:
            return
        try:
            from mlx_lm import load  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised on no-MLX hosts
            raise AdapterError(
                "mlx_lm is not installed; install mlx-lm>=0.31.0 to use MLXAdapter"
            ) from exc
        self._model, self._tokenizer = load(self.model_id)
        # Sampler is built once and reused; greedy at temp=0.0 (top_p irrelevant
        # but passed for explicitness per ADDENDUM §D.1).
        try:
            from mlx_lm.sample_utils import make_sampler  # type: ignore[import-not-found]

            self._sampler = make_sampler(temp=LOCKED_TEMPERATURE, top_p=LOCKED_TOP_P)
        except ImportError:  # pragma: no cover - older mlx-lm without sample_utils
            self._sampler = None

    @staticmethod
    def _inject_date_hint(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return a copy of ``messages`` with the date hint installed.

        If a system message already exists at index 0, prepend the hint to its
        content (idempotent: no-op if the hint is already present). Otherwise
        insert a fresh system message at index 0. Never mutates the caller's
        list.
        """
        out: list[dict[str, Any]] = [dict(m) for m in messages]
        if out and out[0].get("role") == "system":
            existing = str(out[0].get("content", ""))
            if _DATE_HINT in existing:
                return out
            joined = f"{_DATE_HINT}\n\n{existing}" if existing else _DATE_HINT
            out[0] = {**out[0], "content": joined}
            return out
        out.insert(0, {"role": "system", "content": _DATE_HINT})
        return out

    @staticmethod
    def _parse_tool_calls(raw: str) -> tuple[list[ToolCall], bool]:
        """Parse zero-or-more ``<tool_call>{json}</tool_call>`` envelopes.

        Returns:
            ``(tool_calls, parse_ok)``. ``parse_ok`` is False iff at least one
            envelope was present but its JSON failed to decode or lacked
            ``name``; in that case ``tool_calls`` is the empty list (we
            DON'T emit partial results — runner classifies the whole response
            as ``parse_fail``).
        """
        tool_calls: list[ToolCall] = []
        for match in _TOOL_CALL_RE.finditer(raw):
            try:
                obj = json.loads(match.group(1))
                name = obj["name"]
            except (json.JSONDecodeError, KeyError, TypeError):
                return [], False
            arguments = obj.get("arguments", {}) if isinstance(obj, dict) else {}
            if not isinstance(arguments, dict):
                arguments = {}
            tool_calls.append(ToolCall(name=str(name), arguments=arguments))
        return tool_calls, True

    def _generate(self, prompt: str, max_tokens: int) -> str:
        """Wrap ``mlx_lm.generate`` so test code only needs to patch one symbol.

        ``mlx_lm.generate`` has a moving signature across versions — pre-0.31
        it accepted ``temp=`` directly; 0.31+ pushes sampling kwargs into a
        ``sampler`` callable built via ``mlx_lm.sample_utils.make_sampler``.
        We build the sampler lazily in :meth:`_ensure_loaded` and pass it
        only when present, falling back to the bare-kwargs form otherwise.
        """
        from mlx_lm import generate  # type: ignore[import-not-found]

        kwargs: dict[str, Any] = {"max_tokens": max_tokens, "verbose": False}
        if self._sampler is not None:
            kwargs["sampler"] = self._sampler
        return generate(self._model, self._tokenizer, prompt=prompt, **kwargs)

    def dispatch(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = LOCKED_MAX_TOKENS_DEFAULT,
    ) -> ProviderResponse:
        """Run a single Qwen3 round-trip and normalize to :class:`ProviderResponse`.

        Args:
            messages: Conversation in canonical OpenAI shape
                (``[{"role": "user"|"assistant"|"system", "content": str}, ...]``).
            tools: Already in canonical OpenAI tool shape (the runner will
                have called :func:`harness.registry.render_for_mlx` upstream).
                Passed through verbatim to ``apply_chat_template(tools=...)``.
            max_tokens: Cap on generation length; also drives the ``"length"``
                finish-reason heuristic.

        Returns:
            A :class:`ProviderResponse` whose shape matches the Anthropic /
            OpenAI adapters exactly (per HARNESS_SPEC §2 acceptance #1).
            ``raw_text`` has all envelope strings stripped so the trace
            redaction layer doesn't double-count the JSON args.
        """
        self._ensure_loaded()

        # Date-hint injection per §D.1 / §8.5.
        prepared_messages = self._inject_date_hint(messages)

        # Render via Qwen3 chat template; CRITICAL: enable_thinking=False.
        prompt = self._tokenizer.apply_chat_template(
            prepared_messages,
            tools=list(tools),
            add_generation_prompt=True,
            tokenize=False,
            enable_thinking=False,
        )

        start_ns = monotonic_ns()
        raw = self._generate(prompt, max_tokens)
        latency_ms = (monotonic_ns() - start_ns) // 1_000_000

        # Parse tool-call envelopes.
        tool_calls, parse_ok = self._parse_tool_calls(raw)

        # Strip envelopes from the text channel so downstream redaction /
        # refusal classification sees only natural-language content.
        raw_text = _TOOL_CALL_RE.sub("", raw).strip()

        # Token accounting — encode prompt + raw via the same tokenizer that
        # produced them. ``encode`` returns a list[int] for both
        # PreTrainedTokenizerBase-style and mlx_lm's TokenizerWrapper.
        tokens_in = len(self._tokenizer.encode(prompt))
        tokens_out = len(self._tokenizer.encode(raw))

        # Finish-reason heuristic per the spec:
        #   * tool calls present → "tool_use"
        #   * generation hit max_tokens (token count >= cap) → "length"
        #   * else → "stop". Refusal classification lives in the runner.
        finish_reason = self._classify_finish(tool_calls, tokens_out, max_tokens)

        return ProviderResponse(
            raw_text=raw_text,
            tool_calls=tool_calls,
            parse_ok=parse_ok,
            finish_reason=finish_reason,
            tokens_in=int(tokens_in),
            tokens_out=int(tokens_out),
            latency_ms=int(latency_ms),
            raw_provider_payload=None,
        )

    @staticmethod
    def _classify_finish(
        tool_calls: list[ToolCall], tokens_out: int, max_tokens: int
    ) -> str:
        """Map the local generation outcome onto the cross-adapter vocabulary."""
        if tool_calls:
            return "tool_use"
        if tokens_out >= max_tokens:
            return "length"
        return "stop"


__all__ = ["MLXAdapter"]
