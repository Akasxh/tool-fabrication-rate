"""TOST non-inferiority for paired binary outcomes.

Per ADDENDUM_R1 §C.1 the default non-inferiority margin is widened from 1pp to
**5pp** because the original margin would have required ~1100 paired
observations whereas our strict subsets are ~30-50.

Procedure: paired difference d_i = A_i - B_i ∈ {-1, 0, 1}; normal approximation
on the mean of d_i; lower one-sided test H0: mean_diff <= -margin vs.
H1: mean_diff > -margin; upper one-sided test H0: mean_diff >= +margin vs.
H1: mean_diff < +margin. Non-inferiority of A relative to B is declared when
**both** one-sided tests reject at level ``alpha`` (i.e. the (1-2*alpha) CI on
mean_diff lies inside ``(-margin, +margin)``).
"""

from __future__ import annotations

import math
from typing import Sequence

from scipy.stats import norm


def tost_paired_proportions(
    success_a: Sequence[bool],
    success_b: Sequence[bool],
    margin: float = 0.05,
    alpha: float = 0.05,
) -> dict:
    """TOST non-inferiority on paired Bernoulli outcomes.

    Args:
        success_a: pass/fail booleans under condition A (e.g. C1).
        success_b: pass/fail booleans under condition B (e.g. C0).
        margin: equivalence margin in proportion units (default 0.05).
        alpha: per-test one-sided level.

    Returns:
        Dict with:
          - ``p_lower`` (test of mean_diff > -margin)
          - ``p_upper`` (test of mean_diff < +margin)
          - ``non_inferior`` (both p < alpha)
          - ``mean_diff`` (sample mean of A - B)
          - ``ci_low``, ``ci_high`` (1-2*alpha CI bounds on mean_diff)
          - ``effective_n`` (pairs where at least one of A, B was True;
            reported separately to be honest about power per ADDENDUM §C.1).

    Raises:
        ValueError: if ``len(success_a) != len(success_b)`` or input empty.
    """
    if len(success_a) != len(success_b):
        raise ValueError("success_a and success_b must have equal length")
    n = len(success_a)
    if n == 0:
        raise ValueError("inputs must be non-empty")
    if margin <= 0.0:
        raise ValueError("margin must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")

    diffs = [int(bool(a)) - int(bool(b)) for a, b in zip(success_a, success_b)]
    mean_diff = sum(diffs) / n

    # Sample variance with Bessel correction; if degenerate use 0.
    if n > 1:
        var = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    else:
        var = 0.0
    se = math.sqrt(var / n) if var > 0 else 0.0

    if se == 0.0:
        # Degenerate: every pair has identical diff. p-values are 0 or 1.
        p_lower = 0.0 if mean_diff > -margin else 1.0
        p_upper = 0.0 if mean_diff < margin else 1.0
        ci_low = ci_high = mean_diff
    else:
        z_lower = (mean_diff - (-margin)) / se  # for H1: diff > -margin
        z_upper = (margin - mean_diff) / se  # for H1: diff < +margin
        p_lower = float(norm.sf(z_lower))
        p_upper = float(norm.sf(z_upper))
        z_crit = float(norm.ppf(1.0 - alpha))
        ci_low = mean_diff - z_crit * se
        ci_high = mean_diff + z_crit * se

    non_inferior = (p_lower < alpha) and (p_upper < alpha)

    # Effective n drops fully-False pairs, where the comparison carries no
    # signal about the question (both treatments failed regardless).
    effective_n = sum(1 for a, b in zip(success_a, success_b) if a or b)

    return {
        "p_lower": p_lower,
        "p_upper": p_upper,
        "non_inferior": bool(non_inferior),
        "mean_diff": float(mean_diff),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
        "effective_n": int(effective_n),
    }


__all__ = ["tost_paired_proportions"]
