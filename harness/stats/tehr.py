"""Tool-Existence Hallucination Rate (TEHR) + BCa bootstrap CIs.

Per ADDENDUM_R1 §C.3 the bootstrap clusters by task to respect within-task
non-iid structure of per-call observations.
"""

from __future__ import annotations

import math

import numpy as np

from .bootstrap import bca_bootstrap_ci


def tehr(num_hallucinated: int, num_total: int) -> float:
    """Per-call TEHR.

    Returns NaN when no calls have been observed (HARNESS_SPEC §2:
    ``NaN if total==0``).
    """
    if num_total == 0:
        return math.nan
    if num_hallucinated < 0 or num_total < 0:
        raise ValueError("counts must be non-negative")
    if num_hallucinated > num_total:
        raise ValueError("num_hallucinated cannot exceed num_total")
    return num_hallucinated / num_total


def tehr_with_ci(
    per_call_labels: list[bool],
    task_ids: list[str],
    n_resamples: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Cluster-bootstrap (by task) BCa CI for TEHR.

    Args:
        per_call_labels: one bool per tool call; True = hallucinated.
        task_ids: same length as ``per_call_labels``; cluster identifier.
        n_resamples: bootstrap draws (default 10k per ADDENDUM §C.2).
        alpha: two-sided coverage (default 0.05 → 95% CI).
        seed: RNG seed.

    Returns:
        (point_estimate, ci_low, ci_high). Empty input → all NaN.
    """
    if len(per_call_labels) != len(task_ids):
        raise ValueError("per_call_labels and task_ids must align")
    data = np.asarray(per_call_labels, dtype=float)
    clusters = np.asarray(task_ids)
    return bca_bootstrap_ci(
        statistic_fn=lambda x: float(np.mean(x)) if x.size else math.nan,
        data=data,
        cluster_ids=clusters,
        n_resamples=n_resamples,
        alpha=alpha,
        seed=seed,
    )


__all__ = ["tehr", "tehr_with_ci"]
