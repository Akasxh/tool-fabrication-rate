"""C1 condition: Registry-Validated Re-prompt (RVR).

Per HARNESS_SPEC §2 and paper §3.2 / §4.1. Pure function. Inspects each
parsed tool call against the registry; if any name is absent, returns a
RE_PROMPT Action whose feedback rendres the sorted available-tool list.
"""
from __future__ import annotations

from harness.types import Action, ActionKind, ToolCall


def rvr(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action:
    """Registry-Validated Re-prompt intervention (C1).

    - Empty ``parsed_calls`` → ``Action.EXECUTE(tool_call=None)`` (no-tool turn).
    - Any ``call.name not in registry`` → ``Action.RE_PROMPT`` with locked
      feedback containing the offending name and the sorted registry keys.
    - Otherwise → ``Action.EXECUTE`` with the first parsed call.
    """
    if not parsed_calls:
        return Action(kind=ActionKind.EXECUTE, tool_call=None)

    available = sorted(registry.keys())
    for call in parsed_calls:
        if call.name not in registry:
            feedback = (
                f"Tool '{call.name}' is not in the registry.\n"
                f"Available tools: {available}.\n"
                f"Choose one of these or explain why none apply."
            )
            return Action(kind=ActionKind.RE_PROMPT, feedback=feedback)

    return Action(kind=ActionKind.EXECUTE, tool_call=parsed_calls[0])
