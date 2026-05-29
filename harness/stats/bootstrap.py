"""BCa bootstrap with optional task-level cluster resampling.

Per ADDENDUM_R1 §C.2 (BCa replaces percentile) and §C.3 (cluster-resample at
the task level so within-task per-call observations stay non-iid).
Reference: Efron, B. (1987). "Better Bootstrap Confidence Intervals." JASA.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.stats import norm


def _resample_indices(
    rng: np.random.Generator,
    n_rows: int,
    cluster_ids: np.ndarray | None,
) -> np.ndarray:
    """Row indices for one bootstrap resample (clustered if cluster_ids set)."""
    if cluster_ids is None:
        return rng.integers(0, n_rows, size=n_rows)
    uniq = np.unique(cluster_ids)
    drawn = rng.integers(0, uniq.shape[0], size=uniq.shape[0])
    buckets = [np.where(cluster_ids == c)[0] for c in uniq]
    return np.concatenate([buckets[i] for i in drawn])


def _jackknife_kept_indices(
    cluster_ids: np.ndarray | None, n_rows: int
) -> list[np.ndarray]:
    """Per-unit kept-index arrays for leave-one-out jackknife."""
    if cluster_ids is None:
        return [np.delete(np.arange(n_rows), i) for i in range(n_rows)]
    return [np.where(cluster_ids != c)[0] for c in np.unique(cluster_ids)]


def bca_bootstrap_ci(
    statistic_fn: Callable[[np.ndarray], float],
    data: np.ndarray,
    cluster_ids: np.ndarray | None = None,
    n_resamples: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    """BCa percentile bootstrap CI.

    Args:
        statistic_fn: takes a 1-D ndarray of selected rows, returns a scalar.
        data: 1-D ndarray of per-observation values.
        cluster_ids: optional cluster labels (same length as data). When set,
            resample clusters with replacement (ADDENDUM §C.3).
        n_resamples: bootstrap draws (default 10_000 per §C.2).
        alpha: two-sided coverage; CI is (alpha/2, 1-alpha/2).
        seed: RNG seed.

    Returns:
        (point, ci_low, ci_high). All NaN on empty input. Falls back to
        percentile when BCa correction is degenerate.
    """
    data = np.asarray(data)
    if data.size == 0:
        return (float("nan"), float("nan"), float("nan"))

    rng = np.random.default_rng(seed)
    point = float(statistic_fn(data))
    n_rows = data.shape[0]
    if cluster_ids is not None:
        cluster_ids = np.asarray(cluster_ids)
        if cluster_ids.shape[0] != n_rows:
            raise ValueError("cluster_ids must align with data length")

    theta_b = np.empty(n_resamples, dtype=float)
    for b in range(n_resamples):
        idx = _resample_indices(rng, n_rows, cluster_ids)
        theta_b[b] = statistic_fn(data[idx])

    if np.all(theta_b == theta_b[0]):
        return (point, float(theta_b[0]), float(theta_b[0]))

    prop_below = float(np.mean(theta_b < point))
    if prop_below in (0.0, 1.0):
        lo = float(np.quantile(theta_b, alpha / 2.0))
        hi = float(np.quantile(theta_b, 1.0 - alpha / 2.0))
        return (point, lo, hi)
    z0 = float(norm.ppf(prop_below))

    kept = _jackknife_kept_indices(cluster_ids, n_rows)
    jack = np.array([statistic_fn(data[idx]) for idx in kept], dtype=float)
    jbar = float(jack.mean())
    num = float(np.sum((jbar - jack) ** 3))
    den = 6.0 * (float(np.sum((jbar - jack) ** 2)) ** 1.5)
    a_hat = 0.0 if den == 0.0 else num / den

    z_lo, z_hi = norm.ppf(alpha / 2.0), norm.ppf(1.0 - alpha / 2.0)

    def _adj(zq: float) -> float:
        d = 1.0 - a_hat * (z0 + zq)
        return float("nan") if d == 0.0 else float(norm.cdf(z0 + (z0 + zq) / d))

    a1, a2 = _adj(z_lo), _adj(z_hi)
    if not (np.isfinite(a1) and np.isfinite(a2)) or a1 >= a2:
        lo = float(np.quantile(theta_b, alpha / 2.0))
        hi = float(np.quantile(theta_b, 1.0 - alpha / 2.0))
        return (point, lo, hi)
    return (point, float(np.quantile(theta_b, a1)), float(np.quantile(theta_b, a2)))


__all__ = ["bca_bootstrap_ci"]
