"""Shared dataclasses for the TEHR harness.

Single source of truth for cross-module types: Task, ToolCall, ProviderResponse,
Action, ActionKind, plus the small typed literals used in the JSONL trace schema.
All adapters, bench loaders, the runner, and the stats layer import from here.

See HARNESS_SPEC.md §2 (types.py) and ADDENDUM_R1.md §B.2 for ConditionLabel.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, Optional

# JSONL trace `tool_call_status` field (HARNESS_SPEC §3).
ToolCallStatus = Literal[
    "executed",
    "hallucinated",
    "refused",
    "timed_out",
    "parse_fail",
]

# Condition labels used in JSONL traces. ADDENDUM B.2 added C0_7 (framework-style
# structured-error feedback) so we now carry four conditions, not three. The
# `stats/__init__.py` alias map renders these as "C0", "C0.5", "C0.7", "C1" for
# the paper.
ConditionLabel = Literal["C0", "C0_5", "C0_7", "C1"]

# Which benchmark a Task came from.
BenchmarkName = Literal["bfcl", "tau_bench"]


@dataclass(frozen=True)
class ToolCall:
    """A single parsed tool invocation extracted from a model response.

    Attributes:
        name: Tool name as emitted by the model (may be hallucinated;
            classification is the runner's job, not the adapter's).
        arguments: Already-parsed JSON object with the tool arguments. Adapters
            MUST `json.loads` provider-side string args before constructing
            this; on parse failure the adapter sets ``parse_ok=False`` on the
            owning :class:`ProviderResponse` and emits no ToolCall.
    """

    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Task:
    """A single benchmark task ready to feed into the runner loop.

    Attributes:
        id: Stable benchmark-scoped identifier (e.g. ``"bfcl_mt_0042"``).
        benchmark: Source benchmark; routes the runner to the right
            tool-executor flavor.
        registry: Tool registry in canonical OpenAI shape
            (``{name: {"name", "description", "parameters": <JSON-Schema>}}``).
            BFCL loader applies ``_normalize_bfcl_schema`` so ``"type": "dict"``
            is rewritten to ``"type": "object"`` before this lands here.
        initial_prompt: First user message; for BFCL multi-turn this is
            ``question[0]``.
        turns_max: Per-task turn cap (runner also enforces a global 8-turn cap).
        expected_outcome: Benchmark-shaped grading payload. For BFCL multi-turn
            this carries ``subsequent_user_messages`` (list of message lists,
            one per turn after the first); for τ-bench it carries the env
            config plus reward sha256-hash oracle.
    """

    id: str
    benchmark: BenchmarkName
    registry: dict[str, dict]
    initial_prompt: str
    turns_max: int
    expected_outcome: dict


@dataclass(frozen=True)
class ProviderResponse:
    """Normalized output of a single ``adapter.dispatch`` call.

    All three adapters (Anthropic, OpenAI/xAI, MLX/Qwen3) MUST emit this exact
    shape so the runner stays adapter-agnostic.

    Attributes:
        raw_text: Concatenated assistant text channel (excluding tool-call
            blocks). Used for refusal detection.
        tool_calls: Zero or more parsed tool calls; empty list if the model
            chose plain text or if parsing failed.
        parse_ok: ``False`` iff the adapter saw a tool-call envelope but could
            not parse its arguments (malformed JSON etc.). Adapters MUST NOT
            raise on parse failure; they set this flag instead.
        finish_reason: Provider-normalized stop reason
            (``"end_turn" | "tool_use" | "max_tokens" | "refusal" | ...``).
        tokens_in: Prompt-side token count for cost accounting.
        tokens_out: Completion-side token count for cost accounting.
        latency_ms: Wall-clock latency of the dispatch call.
        raw_provider_payload: Optional raw SDK response object (or its dict
            form). Dropped by ``TraceLogger`` unless ``persist_raw=True``.
    """

    raw_text: str
    tool_calls: list[ToolCall]
    parse_ok: bool
    finish_reason: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    raw_provider_payload: Optional[dict] = None


class ActionKind(Enum):
    """What the runner does next after seeing a parsed model response.

    Members:
        EXECUTE: Forward the (possibly None) tool_call to the tool executor.
        RE_PROMPT: Send a feedback message back to the model (RVR / C0.5 /
            C0.7 paths); at-most-one retry per turn enforced by the runner.
        ABORT: Terminate the task immediately (budget, hard timeout, etc.).
    """

    EXECUTE = "execute"
    RE_PROMPT = "re_prompt"
    ABORT = "abort"


@dataclass(frozen=True)
class Action:
    """Runner-facing decision returned by an intervention policy.

    Attributes:
        kind: Which branch the runner should take (see :class:`ActionKind`).
        tool_call: Tool call to execute when ``kind == EXECUTE``; may be
            ``None`` if the model chose no tool that turn.
        feedback: Message text appended to conversation history when
            ``kind == RE_PROMPT``; ``None`` for other kinds.
    """

    kind: ActionKind
    tool_call: Optional[ToolCall] = None
    feedback: Optional[str] = None
