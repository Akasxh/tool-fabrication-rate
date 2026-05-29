"""C0.7 condition: framework-default-style structured error feedback.

Added per ADDENDUM_R1 §B.2. Approximates LangChain's default
tool-call-validation error path: a JSON error object with the
attempted name and an opaque ``details`` string, but NO registry list.
Sits between C0.5 (retry-alone) and C1 (full registry render).
"""
from __future__ import annotations

import json

from harness.types import Action, ActionKind, ToolCall


def framework_default(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action:
    """Framework-default structured-error intervention (C0.7)."""
    if not parsed_calls:
        return Action(kind=ActionKind.EXECUTE, tool_call=None)

    for proposed in parsed_calls:
        if proposed.name not in registry:
            feedback = json.dumps(
                {
                    "error": "tool_not_found",
                    "attempted": proposed.name,
                    "details": "function not in registry",
                }
            )
            return Action(kind=ActionKind.RE_PROMPT, feedback=feedback)

    return Action(kind=ActionKind.EXECUTE, tool_call=parsed_calls[0])
