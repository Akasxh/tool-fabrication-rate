"""Paired McNemar mid-p test + Holm-Bonferroni step-down.

Per ADDENDUM_R1 §C.6 (clamp to [0,1] + ``b+c==0`` guard) and §C.4 (pool
discordance counts across tiers BEFORE the headline test).
"""

from __future__ import annotations

from scipy.stats import binom


def paired_mcnemar_midp(b: int, c: int) -> float:
    """Two-sided paired McNemar mid-p value.

    Args:
        b: count of pairs that passed in A and failed in B.
        c: count of pairs that failed in A and passed in B.

    Returns:
        Two-sided mid-p in [0, 1]. Per ADDENDUM §C.6:
        - ``b + c == 0`` → 1.0 (no discordance, no evidence vs. H0).
        - Result is clamped to [0, 1].
    """
    if b < 0 or c < 0:
        raise ValueError("b and c must be non-negative")
    if b + c == 0:
        return 1.0
    n = b + c
    k = min(b, c)
    p_strict = float(binom.cdf(k - 1, n, 0.5)) if k > 0 else 0.0
    p_eq = float(binom.pmf(k, n, 0.5))
    p_one_sided = p_strict + 0.5 * p_eq
    p_two_sided = 2.0 * p_one_sided
    if p_two_sided < 0.0:
        return 0.0
    if p_two_sided > 1.0:
        return 1.0
    return p_two_sided


def holm_bonferroni(
    pvalues: list[float], alpha: float = 0.05
) -> list[bool]:
    """Holm step-down rejection booleans aligned to input order.

    Args:
        pvalues: list of raw p-values.
        alpha: family-wise error rate.

    Returns:
        List of booleans, same length & order as ``pvalues``: True iff the
        corresponding hypothesis is rejected at the Holm-adjusted threshold.
    """
    m = len(pvalues)
    if m == 0:
        return []
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    order = sorted(range(m), key=lambda i: pvalues[i])
    rejects = [False] * m
    # Step-down: stop rejecting once any test fails.
    halted = False
    for rank, idx in enumerate(order):
        threshold = alpha / (m - rank)
        if not halted and pvalues[idx] <= threshold:
            rejects[idx] = True
        else:
            halted = True
    return rejects


def pooled_paired_mcnemar(
    discordance_pairs: dict[str, tuple[int, int]],
) -> tuple[int, int, float]:
    """Pool ``b, c`` across tiers, then compute mid-p (ADDENDUM §C.4).

    Args:
        discordance_pairs: tier_label -> (b, c).

    Returns:
        ``(b_total, c_total, p_value)``. With no tiers, returns ``(0, 0, 1.0)``.
    """
    b_total = sum(b for b, _ in discordance_pairs.values())
    c_total = sum(c for _, c in discordance_pairs.values())
    return b_total, c_total, paired_mcnemar_midp(b_total, c_total)


__all__ = [
    "paired_mcnemar_midp",
    "holm_bonferroni",
    "pooled_paired_mcnemar",
]
