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

# --- Cross-family tool-call envelopes (ADDITIVE; do NOT touch Qwen path) --- #
# Mistral v0.3 emits ``[TOOL_CALLS][{"name":..,"arguments":..}, ...]`` (a JSON
# *array*) followed by EOS. Confirmed from the model's bundled "tool_use" chat
# template (``'[TOOL_CALLS]' + message['content']``). We capture from the marker
# to end-of-string and JSON-decode the bracketed list ourselves (greedy: the
# array is the model's final output).
_MISTRAL_TOOL_CALLS_RE = re.compile(r"\[TOOL_CALLS\]\s*(\[.*\])", re.DOTALL)

# Llama-3.1 JSON tool-calling: the model emits a bare JSON object
# ``{"name":..,"parameters":..}`` (verified from saved C0 traces), optionally
# prefixed with the ``<|python_tag|>`` special token. ``parameters`` is Llama's
# spelling of ``arguments`` (handled by the shared key-aliasing below).
_PYTHON_TAG = "<|python_tag|>"

# Reasoning distills (DeepSeek-R1-Distill, Qwen3 with thinking) wrap chain-of-
# thought in ``<think>...</think>``. We strip it before parsing so a trailing
# tool-call envelope is still recoverable. For the Qwen3 path enable_thinking is
# already False, so this is a no-op there (no <think> present) — verified
# against the existing §4 fixtures.
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

# Qwen3 model ids are the only ones whose chat template accepts the
# ``enable_thinking`` kwarg as a first-class reasoning toggle. Other families
# (Llama/Mistral/Phi/gemma/DeepSeek-distill) either ignore it or would choke, so
# we gate the kwarg on the family.
_QWEN3_MARKER = "qwen3"

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
    def _merge_system_into_user(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Fold leading system message(s) into the first user turn.

        Some chat templates (Gemma-2, some Phi variants) reject a ``system``
        role outright (``TemplateError: System role not supported``). For those
        models we splice any leading system content onto the front of the first
        user message so the same instructions/registry still reach the model.
        Families whose templates accept a system role never hit this path, so
        existing results are unaffected.
        """
        out: list[dict[str, Any]] = [dict(m) for m in messages]
        sys_parts: list[str] = []
        while out and out[0].get("role") == "system":
            sys_parts.append(str(out.pop(0).get("content", "")))
        if not sys_parts:
            return out
        sys_text = "\n\n".join(p for p in sys_parts if p)
        for m in out:
            if m.get("role") == "user":
                m["content"] = f"{sys_text}\n\n{m.get('content', '')}"
                return out
        out.insert(0, {"role": "user", "content": sys_text})
        return out

    @staticmethod
    def _coerce_call(obj: Any) -> ToolCall:
        """Normalize one decoded call dict into a :class:`ToolCall`.

        Accepts both ``arguments`` (Qwen3/Mistral) and ``parameters``
        (Llama-3.1) as the argument key — they are aliases. Raises
        ``KeyError``/``TypeError`` (caught by the caller) if ``name`` is
        absent or ``obj`` isn't a mapping, so a malformed call degrades to
        ``parse_ok=False`` exactly like the legacy Qwen path.
        """
        name = obj["name"]  # KeyError → parse_fail, matching legacy behavior
        args = obj.get("arguments")
        if args is None:
            args = obj.get("parameters", {})
        if not isinstance(args, dict):
            args = {}
        return ToolCall(name=str(name), arguments=args)

    @classmethod
    def _parse_tool_calls(cls, raw: str) -> tuple[list[ToolCall], bool]:
        """Parse zero-or-more tool-call envelopes across model families.

        Family precedence (first matching family wins; the Qwen3 path is
        unchanged and still checked first so existing behavior is byte-for-byte
        preserved):

            1. Qwen3   — ``<tool_call>{json}</tool_call>`` (one or more).
            2. Mistral — ``[TOOL_CALLS][{...}, ...]`` (a JSON array).
            3. Llama   — ``<|python_tag|>{json}`` or a bare top-level
                         ``{"name":..,"parameters":..}`` object.

        ``<think>...</think>`` reasoning blocks are stripped before any of the
        bare/array forms are considered (Qwen3 runs with enable_thinking=False
        so this is a no-op there).

        Returns ``(tool_calls, parse_ok)``. ``parse_ok`` is False iff a
        recognized envelope/marker was present but its JSON failed to decode or
        lacked ``name``; in that case ``tool_calls`` is empty (no partial
        results — the runner classifies the whole response as ``parse_fail``).
        """
        # --- Tier 1: Qwen3 envelope (UNCHANGED). ---
        qwen_matches = list(_TOOL_CALL_RE.finditer(raw))
        if qwen_matches:
            tool_calls: list[ToolCall] = []
            for match in qwen_matches:
                try:
                    obj = json.loads(match.group(1))
                    tool_calls.append(cls._coerce_call(obj))
                except (json.JSONDecodeError, KeyError, TypeError):
                    return [], False
            return tool_calls, True

        # Strip reasoning so the bare/array detectors below see the final answer.
        stripped = _THINK_RE.sub("", raw).strip()

        # --- Tier 2: Mistral [TOOL_CALLS][...] array. ---
        m = _MISTRAL_TOOL_CALLS_RE.search(stripped)
        if m:
            try:
                arr = json.loads(m.group(1))
                if not isinstance(arr, list):
                    return [], False
                return [cls._coerce_call(o) for o in arr], True
            except (json.JSONDecodeError, KeyError, TypeError):
                return [], False

        # --- Tier 3: Llama bare JSON, optionally <|python_tag|>-prefixed. ---
        candidate = stripped
        if _PYTHON_TAG in candidate:
            candidate = candidate.split(_PYTHON_TAG, 1)[1].strip()
            had_marker = True
        else:
            had_marker = False
        if candidate.startswith("{") or candidate.startswith("["):
            try:
                obj = json.loads(candidate)
            except json.JSONDecodeError:
                # An explicit python_tag promised a call but the JSON is broken.
                return ([], False) if had_marker else ([], True)
            objs = obj if isinstance(obj, list) else [obj]
            # Only treat as tool calls if every element looks like one (has a
            # ``name`` key); otherwise it's incidental JSON content, not a call.
            if all(isinstance(o, dict) and "name" in o for o in objs) and objs:
                try:
                    return [cls._coerce_call(o) for o in objs], True
                except (KeyError, TypeError):
                    return [], False
            return ([], False) if had_marker else ([], True)

        # No recognized envelope/marker → legitimate no-tool-call response.
        return [], True

    @staticmethod
    def _strip_envelopes(raw: str) -> str:
        """Remove all recognized tool-call envelopes from the text channel.

        Mirrors :meth:`_parse_tool_calls`'s family coverage so downstream
        redaction / refusal classification never sees raw JSON args. The Qwen3
        ``<tool_call>`` substitution is applied exactly as before; the
        cross-family markers are additive.
        """
        out = _TOOL_CALL_RE.sub("", raw)
        out = _THINK_RE.sub("", out)
        # Mistral array: drop from the marker to end-of-string.
        out = _MISTRAL_TOOL_CALLS_RE.sub("", out)
        # Llama python_tag + trailing bare JSON object/array.
        if _PYTHON_TAG in out:
            out = out.split(_PYTHON_TAG, 1)[0]
        out = out.strip()
        # Bare Llama JSON call with no marker: if the *entire* remaining text is
        # a JSON object/array carrying a ``name`` key, it's the call itself —
        # blank the text channel (parity with the envelope families).
        if out.startswith("{") or out.startswith("["):
            try:
                obj = json.loads(out)
            except json.JSONDecodeError:
                return out
            objs = obj if isinstance(obj, list) else [obj]
            if objs and all(isinstance(o, dict) and "name" in o for o in objs):
                return ""
        return out

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

        # Render via the model's chat template. CRITICAL: enable_thinking=False
        # is a Qwen3-only knob (its reasoning toggle defaults ON and injects
        # <think> blocks that break the parser). Other families' templates don't
        # accept it, so we pass it only for Qwen3 (model_id-gated, ADDITIVE).
        template_kwargs: dict[str, Any] = {
            "tools": list(tools),
            "add_generation_prompt": True,
            "tokenize": False,
        }
        if _QWEN3_MARKER in self.model_id.lower():
            template_kwargs["enable_thinking"] = False
        try:
            prompt = self._tokenizer.apply_chat_template(
                prepared_messages, **template_kwargs
            )
        except Exception as exc:  # noqa: BLE001 - template engines raise varied types
            # Gemma-2 / some Phi templates reject a "system" role. Fold the
            # system content into the first user turn and retry once. Only the
            # exception path changes behaviour, so system-role-capable families
            # (Qwen3, Llama, Qwen2.5, Mistral) are untouched.
            if "system" in str(exc).lower():
                prepared_messages = self._merge_system_into_user(prepared_messages)
                prompt = self._tokenizer.apply_chat_template(
                    prepared_messages, **template_kwargs
                )
            else:
                raise

        start_ns = monotonic_ns()
        raw = self._generate(prompt, max_tokens)
        latency_ms = (monotonic_ns() - start_ns) // 1_000_000

        # Parse tool-call envelopes.
        tool_calls, parse_ok = self._parse_tool_calls(raw)

        # Strip envelopes from the text channel so downstream redaction /
        # refusal classification sees only natural-language content. Covers all
        # supported families (Qwen3 <tool_call>, Mistral [TOOL_CALLS], Llama
        # python_tag / bare JSON, plus <think> reasoning).
        raw_text = self._strip_envelopes(raw)

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
