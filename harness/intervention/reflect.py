"""A2 condition: Reflexion-style ungrounded reflection baseline.

On a registry miss, re-prompt the model to REFLECT on why its last call failed
and decide a correct next action --- but WITHOUT supplying the registry (no list
of valid names). This isolates "reflection" from "grounding": if RVR's recovery
were merely the effect of prompting the model to reflect-and-retry, this arm
should match C1/C0.7; if recovery needs the structured-rejection grounding, it
will not. Reflexion-style verbal self-reflection (Shinn et al., 2023).
"""
from __future__ import annotations

from harness.types import Action, ActionKind, ToolCall

_REFLECT_FEEDBACK: str = (
    "Your previous tool call failed. Reflect briefly on why that attempt was "
    "wrong and what a correct next action would be, then proceed. Do not assume "
    "any particular tool exists."
)


def reflect(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action:
    """Reflexion-style ungrounded-reflection intervention (A2)."""
    if not parsed_calls:
        return Action(kind=ActionKind.EXECUTE, tool_call=None)

    for call in parsed_calls:
        if call.name not in registry:
            return Action(kind=ActionKind.RE_PROMPT, feedback=_REFLECT_FEEDBACK)

    return Action(kind=ActionKind.EXECUTE, tool_call=parsed_calls[0])
