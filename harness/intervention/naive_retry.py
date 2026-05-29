"""C0.5 condition: naive retry baseline.

Locked feedback string per HARNESS_SPEC §2: no registry list, no
tool-name mention. Tests retry-alone as an ablation against C1 (RVR)
and C0.7 (framework-default-style structured error).
"""
from __future__ import annotations

from harness.types import Action, ActionKind, ToolCall

_NAIVE_RETRY_FEEDBACK: str = "Your previous tool call failed. Please try again."


def naive_retry(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action:
    """Naive-retry intervention (C0.5)."""
    if not parsed_calls:
        return Action(kind=ActionKind.EXECUTE, tool_call=None)

    for call in parsed_calls:
        if call.name not in registry:
            return Action(kind=ActionKind.RE_PROMPT, feedback=_NAIVE_RETRY_FEEDBACK)

    return Action(kind=ActionKind.EXECUTE, tool_call=parsed_calls[0])
