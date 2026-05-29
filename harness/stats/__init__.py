"""Statistical-analysis modules for the SCALE @ ICML 2026 harness.

Per HARNESS_SPEC.md §2 + ADDENDUM_R1.md §B.2 we expose a condition-key alias map
that translates between the JSONL on-disk encoding (filesystem-safe identifiers
like ``C0_5``) and the paper-rendering form (``C0.5``). C0.7 is included per
ADDENDUM §B.2 (4-condition matrix).
"""

from __future__ import annotations

CONDITION_LABEL_FOR_PAPER: dict[str, str] = {
    "C0": "C0",
    "C0_5": "C0.5",
    "C0_7": "C0.7",
    "C1": "C1",
}

CONDITION_LABEL_FOR_JSONL: dict[str, str] = {
    v: k for k, v in CONDITION_LABEL_FOR_PAPER.items()
}

__all__ = ["CONDITION_LABEL_FOR_PAPER", "CONDITION_LABEL_FOR_JSONL"]
