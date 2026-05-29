"""LOCKED refusal classifier (HARNESS_SPEC §8.2).

The runner is the single source of truth for classifying a turn's
``tool_call_status``; this module owns the ``refused`` branch via a frozen
deny-list of prefix phrases applied case-insensitively to ``raw_text`` ONLY
when no tool call is present.
"""
from __future__ import annotations

from harness.types import ProviderResponse

# Frozen per HARNESS_SPEC §8.2 — do not edit without an ADDENDUM bump.
REFUSAL_PHRASES: tuple[str, ...] = (
    "i can't",
    "i cannot",
    "i'm not able",
    "i won't",
)


def classify_refusal(response: ProviderResponse) -> bool:
    """True iff no tool call AND ``raw_text`` (lower-stripped) starts with a phrase."""
    if response.tool_calls:
        return False
    text = (response.raw_text or "").strip().lower()
    if not text:
        return False
    return any(text.startswith(phrase) for phrase in REFUSAL_PHRASES)
