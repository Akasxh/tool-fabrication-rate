"""Token-cost tracker with 90 percent budget threshold callback and hard abort.

Implements ``CostMeter`` per HARNESS_SPEC.md §2 and §8.7.

Unit convention
---------------
All prices passed to :meth:`CostMeter.add` are in **USD per 1,000 tokens**
(i.e. ``$/1k``). HARNESS_SPEC §8.1 lists prices as ``$/1M`` for human
readability; callers MUST divide by 1000 before handing them to this meter.
Concretely, Claude Sonnet 4.6 at $3.00 per 1M input tokens is passed as
``price_in_per_1k=0.003``. The arithmetic is therefore::

    delta_usd = (tokens_in / 1000) * price_in_per_1k
              + (tokens_out / 1000) * price_out_per_1k

This convention is locked because the parameter name itself is
``price_in_per_1k``; mixing in $/1M values would silently overcharge by
1000x and trip the abort 1000x too early.
"""
from __future__ import annotations

import threading
from typing import Callable, Optional


class BudgetAbort(RuntimeError):
    """Raised by :meth:`CostMeter.add` when cumulative spend reaches budget."""


class CostMeter:
    """Thread-safe USD cost accumulator with one-shot 90 percent threshold.

    Args:
        budget_usd: Hard ceiling in USD. ``add`` raises :class:`BudgetAbort`
            once cumulative spend ``>= budget_usd``.
        on_threshold: Optional callback invoked exactly once the first time
            cumulative spend crosses ``0.9 * budget_usd``. Receives the
            post-update total spent in USD. Subsequent crossings (e.g. after
            a reset, which is not supported here) do not re-fire.
    """

    def __init__(
        self,
        budget_usd: float,
        on_threshold: Optional[Callable[[float], None]] = None,
    ) -> None:
        self._budget: float = float(budget_usd)
        self._on_threshold: Optional[Callable[[float], None]] = on_threshold
        self._spent: float = 0.0
        self._threshold_fired: bool = False
        self._lock: threading.Lock = threading.Lock()
        # Per-call history for diagnostics: (tokens_in, tokens_out, delta_usd).
        self._history: list[tuple[int, int, float]] = []

    def add(
        self,
        tokens_in: int,
        tokens_out: int,
        price_in_per_1k: float,
        price_out_per_1k: float,
    ) -> float:
        """Charge a single provider call against the budget.

        Returns:
            The delta in USD added by this call.

        Raises:
            BudgetAbort: if the post-update cumulative spend ``>= budget_usd``.
        """
        delta: float = (tokens_in / 1000.0) * price_in_per_1k + (
            tokens_out / 1000.0
        ) * price_out_per_1k
        fire_callback: bool = False
        with self._lock:
            self._spent += delta
            self._history.append((tokens_in, tokens_out, delta))
            if (
                not self._threshold_fired
                and self._spent >= 0.9 * self._budget
                and self._on_threshold is not None
            ):
                self._threshold_fired = True
                fire_callback = True
            spent_snapshot: float = self._spent
        # Fire callback OUTSIDE the lock so user code can be slow / re-enter.
        if fire_callback and self._on_threshold is not None:
            self._on_threshold(spent_snapshot)
        if spent_snapshot >= self._budget:
            raise BudgetAbort(
                f"CostMeter budget exhausted: ${spent_snapshot:.4f} >= ${self._budget:.4f}"
            )
        return delta

    def total(self) -> float:
        """Return cumulative USD spent."""
        with self._lock:
            return self._spent

    def over_budget(self) -> bool:
        """Return True iff cumulative spend has reached the budget ceiling."""
        with self._lock:
            return self._spent >= self._budget
