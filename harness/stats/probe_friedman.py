"""Friedman + Nemenyi for the §6 distractor-type probe.

Per ADDENDUM_R1 §C.5: ANOVA's normality + homoskedasticity assumptions are
violated by TEHR ∈ [0,1] at small N. Friedman is non-parametric and matches
the repeated-measures structure (each task is a "subject" tested under every
distractor type). Nemenyi is the standard rank-based post-hoc.

Falls back to Bonferroni-corrected pairwise Wilcoxon signed-rank if
``scikit_posthocs`` is unavailable.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon


def _bonferroni_wilcoxon(arr: np.ndarray, names: list[str]) -> pd.DataFrame:
    """Bonferroni-corrected pairwise Wilcoxon fallback."""
    k = arr.shape[1]
    n_pairs = k * (k - 1) // 2
    df = pd.DataFrame(np.ones((k, k)), index=names, columns=names)
    for i in range(k):
        for j in range(i + 1, k):
            xi, xj = arr[:, i], arr[:, j]
            try:
                if np.allclose(xi, xj):
                    p = 1.0
                else:
                    _, p = wilcoxon(xi, xj, zero_method="wilcox")
            except ValueError:
                p = 1.0
            p_adj = float(min(1.0, p * n_pairs))
            df.iloc[i, j] = p_adj
            df.iloc[j, i] = p_adj
    return df


def friedman_nemenyi(
    groups: dict[str, list[float]],
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Friedman omnibus + Nemenyi post-hoc on per-subject scores.

    Args:
        groups: condition_label -> list of per-subject scores (TEHR, pass-rate,
            etc.). All lists must have identical length (paired across
            subjects, e.g. tasks).
        alpha: significance threshold for ``reject_pairs``.

    Returns:
        Dict with ``chi2``, ``p_value``, ``k_groups``, ``n_subjects``,
        ``nemenyi`` (pd.DataFrame of pairwise p-values; rows/cols = group
        labels), ``reject_pairs`` (list of (a, b) tuples where the post-hoc
        rejects equality at ``alpha``), and ``posthoc_method``
        (``"nemenyi"`` or ``"bonferroni_wilcoxon"``).

    Raises:
        ValueError: if fewer than 3 groups, or group lengths differ, or any
            group is empty.
    """
    names = list(groups.keys())
    k = len(names)
    if k < 3:
        raise ValueError("Friedman requires at least 3 groups")
    lens = {len(v) for v in groups.values()}
    if len(lens) != 1:
        raise ValueError("all groups must have equal length (paired design)")
    n = lens.pop()
    if n == 0:
        raise ValueError("groups must be non-empty")

    arr = np.array([groups[name] for name in names], dtype=float).T  # n x k

    # Friedman chi-square is undefined when every subject has identical scores
    # across groups (no rank variation → divide-by-zero in scipy). Treat as
    # "no evidence against H0".
    if np.all(np.ptp(arr, axis=1) == 0):
        chi2, p = 0.0, 1.0
    else:
        chi2, p = friedmanchisquare(*[arr[:, i] for i in range(k)])
        if not np.isfinite(p):
            chi2, p = 0.0, 1.0

    posthoc_method = "nemenyi"
    try:
        import scikit_posthocs as sp  # type: ignore[import-untyped]

        nemenyi_df = sp.posthoc_nemenyi_friedman(arr)
        nemenyi_df.index = names
        nemenyi_df.columns = names
    except ImportError:
        posthoc_method = "bonferroni_wilcoxon"
        nemenyi_df = _bonferroni_wilcoxon(arr, names)

    reject_pairs: list[tuple[str, str]] = []
    for i in range(k):
        for j in range(i + 1, k):
            p_ij = float(nemenyi_df.iloc[i, j])
            if p_ij < alpha:
                reject_pairs.append((names[i], names[j]))

    return {
        "chi2": float(chi2),
        "p_value": float(p),
        "k_groups": int(k),
        "n_subjects": int(n),
        "nemenyi": nemenyi_df,
        "reject_pairs": reject_pairs,
        "posthoc_method": posthoc_method,
    }


__all__ = ["friedman_nemenyi"]
