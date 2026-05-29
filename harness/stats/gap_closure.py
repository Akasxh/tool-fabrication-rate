"""Gap-closure ratio + BCa CI on the ratio (ADDENDUM §B.4 + R1 BLOCKER B4).

R = (Pass(small+C1) − Pass(small+C0)) / (Pass(frontier+C0) − Pass(small+C0))

Denominator-near-zero policy: returns ``None`` when the small-vs-frontier gap
is at or below ``near_zero_threshold`` (inclusive boundary; acceptance test
#10 expects denom == 0.05 to return None — see report-back ambiguity note).
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy.stats import norm

_TOL = 1e-9


def gap_closure_ratio(
    pass_rate_small_c0: float,
    pass_rate_small_c1: float,
    pass_rate_frontier_c0: float,
    *,
    near_zero_threshold: float = 0.05,
) -> float | None:
    """Point estimate of the gap-closure ratio (None if denom ≤ threshold)."""
    denom = pass_rate_frontier_c0 - pass_rate_small_c0
    if denom <= near_zero_threshold + _TOL:
        return None
    return float((pass_rate_small_c1 - pass_rate_small_c0) / denom)


def _ratio(
    a: np.ndarray, b: np.ndarray, f: np.ndarray, thr: float
) -> float:
    """Ratio from indexed arrays; NaN if denom near zero."""
    denom = float(f.mean()) - float(a.mean())
    if denom <= thr + _TOL:
        return float("nan")
    return (float(b.mean()) - float(a.mean())) / denom


def gap_closure_with_ci(
    per_task_results: dict[str, dict[str, list[bool]]],
    task_ids_per_tier: dict[str, list[str]],
    n_resamples: int = 10_000,
    alpha: float = 0.05,
    seed: int = 0,
    near_zero_threshold: float = 0.05,
) -> dict:
    """Paired cluster-bootstrap (by task within tier) BCa CI on the ratio.

    Required keys: ``per_task_results["small"]`` with conditions ``"C0"``,
    ``"C1"``; ``per_task_results["frontier"]`` with condition ``"C0"``.
    ``task_ids_per_tier[tier]`` aligns row-wise with the pass-boolean lists.

    Returns ``{point_estimate, ci_low, ci_high, n_undefined_resamples,
    warning}``. When the data-level point is None, ``ci_low``/``ci_high`` are
    also None and ``warning`` is set.
    """
    for tier in ("small", "frontier"):
        if tier not in per_task_results:
            raise ValueError(f"missing tier '{tier}' in per_task_results")
    if "C0" not in per_task_results["small"] or "C1" not in per_task_results["small"]:
        raise ValueError("small tier must include both C0 and C1")
    if "C0" not in per_task_results["frontier"]:
        raise ValueError("frontier tier must include C0")

    sc0 = np.asarray(per_task_results["small"]["C0"], dtype=float)
    sc1 = np.asarray(per_task_results["small"]["C1"], dtype=float)
    fc0 = np.asarray(per_task_results["frontier"]["C0"], dtype=float)
    if sc0.shape[0] != sc1.shape[0]:
        raise ValueError("small tier C0/C1 task counts must match")

    point = gap_closure_ratio(
        float(sc0.mean()) if sc0.size else float("nan"),
        float(sc1.mean()) if sc1.size else float("nan"),
        float(fc0.mean()) if fc0.size else float("nan"),
        near_zero_threshold=near_zero_threshold,
    )
    if point is None:
        msg = (
            f"Gap-closure ratio undefined: denom <= {near_zero_threshold} "
            "(ADDENDUM §B.4)."
        )
        warnings.warn(msg, RuntimeWarning, stacklevel=2)
        return {
            "point_estimate": None, "ci_low": None, "ci_high": None,
            "n_undefined_resamples": 0, "warning": msg,
        }

    sids = np.asarray(task_ids_per_tier["small"])
    fids = np.asarray(task_ids_per_tier["frontier"])
    if sids.shape[0] != sc0.shape[0] or fids.shape[0] != fc0.shape[0]:
        raise ValueError("task_ids must align with pass arrays")

    rng = np.random.default_rng(seed)
    s_uniq, f_uniq = np.unique(sids), np.unique(fids)
    s_buckets = [np.where(sids == c)[0] for c in s_uniq]
    f_buckets = [np.where(fids == c)[0] for c in f_uniq]

    boot = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        sd = rng.integers(0, s_uniq.shape[0], size=s_uniq.shape[0])
        fd = rng.integers(0, f_uniq.shape[0], size=f_uniq.shape[0])
        si = np.concatenate([s_buckets[j] for j in sd])
        fi = np.concatenate([f_buckets[j] for j in fd])
        boot[i] = _ratio(sc0[si], sc1[si], fc0[fi], near_zero_threshold)

    n_undef = int(np.isnan(boot).sum())
    finite = boot[~np.isnan(boot)]
    if finite.size == 0:
        return {
            "point_estimate": float(point), "ci_low": None, "ci_high": None,
            "n_undefined_resamples": n_undef,
            "warning": "All bootstrap resamples had near-zero denominator.",
        }

    # BCa: bias correction from boot-vs-point + jackknife acceleration over
    # all (tier, task) cluster-removal units.
    prop_below = float(np.mean(finite < point))
    if prop_below in (0.0, 1.0):
        lo = float(np.quantile(finite, alpha / 2.0))
        hi = float(np.quantile(finite, 1.0 - alpha / 2.0))
    else:
        z0 = float(norm.ppf(prop_below))
        jacks: list[float] = []
        for c in s_uniq:
            keep = sids != c
            r = _ratio(sc0[keep], sc1[keep], fc0, near_zero_threshold)
            if not np.isnan(r):
                jacks.append(r)
        for c in f_uniq:
            keep = fids != c
            r = _ratio(sc0, sc1, fc0[keep], near_zero_threshold)
            if not np.isnan(r):
                jacks.append(r)
        ja = np.asarray(jacks, dtype=float)
        if ja.size > 1:
            jbar = float(ja.mean())
            num = float(np.sum((jbar - ja) ** 3))
            den = 6.0 * (float(np.sum((jbar - ja) ** 2)) ** 1.5)
            a_hat = 0.0 if den == 0.0 else num / den
        else:
            a_hat = 0.0
        zL, zH = norm.ppf(alpha / 2.0), norm.ppf(1.0 - alpha / 2.0)
        a1 = float(norm.cdf(z0 + (z0 + zL) / max(1e-12, 1.0 - a_hat * (z0 + zL))))
        a2 = float(norm.cdf(z0 + (z0 + zH) / max(1e-12, 1.0 - a_hat * (z0 + zH))))
        if not (0.0 < a1 < a2 < 1.0):
            lo = float(np.quantile(finite, alpha / 2.0))
            hi = float(np.quantile(finite, 1.0 - alpha / 2.0))
        else:
            lo = float(np.quantile(finite, a1))
            hi = float(np.quantile(finite, a2))

    warn_msg = (
        f"{n_undef}/{n_resamples} resamples dropped (near-zero denom)."
        if n_undef > 0 else ""
    )
    return {
        "point_estimate": float(point), "ci_low": float(lo), "ci_high": float(hi),
        "n_undefined_resamples": n_undef, "warning": warn_msg,
    }


__all__ = ["gap_closure_ratio", "gap_closure_with_ci"]
