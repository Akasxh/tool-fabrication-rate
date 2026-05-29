"""Acceptance tests for harness/stats/* modules.

Spec: contract from Code-D acceptance criteria + ADDENDUM_R1 §C.
Run:
    PYTHONPATH=/Users/cero/Desktop/PROJECTS/icml \\
        pytest /Users/cero/Desktop/PROJECTS/icml/harness/tests/test_stats.py -v
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.stats import binom

from harness.stats import (
    CONDITION_LABEL_FOR_JSONL,
    CONDITION_LABEL_FOR_PAPER,
)
from harness.stats.bootstrap import bca_bootstrap_ci
from harness.stats.gap_closure import gap_closure_ratio, gap_closure_with_ci
from harness.stats.paired_mcnemar import (
    holm_bonferroni,
    paired_mcnemar_midp,
    pooled_paired_mcnemar,
)
from harness.stats.probe_friedman import friedman_nemenyi
from harness.stats.tehr import tehr, tehr_with_ci
from harness.stats.tost import tost_paired_proportions


# ---------- McNemar mid-p ----------


def test_mcnemar_zero_discordance_returns_one() -> None:
    """Criterion 1: ``paired_mcnemar_midp(0, 0) == 1.0`` (zero-discordance guard)."""
    assert paired_mcnemar_midp(0, 0) == 1.0


def test_mcnemar_matches_hand_reference() -> None:
    """Criterion 2: ``paired_mcnemar_midp(10, 2)`` matches hand reference within 1e-6.

    Reference: ``2 * (binom.cdf(1, 12, 0.5) + 0.5 * binom.pmf(2, 12, 0.5))``
    ≈ 0.02246093750000.
    """
    reference = 2.0 * (binom.cdf(1, 12, 0.5) + 0.5 * binom.pmf(2, 12, 0.5))
    got = paired_mcnemar_midp(10, 2)
    assert abs(got - float(reference)) < 1e-6


@pytest.mark.parametrize(
    "b,c",
    [(0, 0), (0, 1), (1, 0), (1, 1), (5, 5), (10, 2), (50, 50), (100, 0), (3, 30)],
)
def test_mcnemar_in_unit_interval(b: int, c: int) -> None:
    """Criterion 3: result must always be in [0, 1] for any non-negative b, c."""
    p = paired_mcnemar_midp(b, c)
    assert 0.0 <= p <= 1.0


def test_mcnemar_symmetric() -> None:
    """Sanity: swapping b and c yields the same two-sided p-value."""
    assert abs(paired_mcnemar_midp(7, 3) - paired_mcnemar_midp(3, 7)) < 1e-12


def test_pooled_paired_mcnemar_pools_before_test() -> None:
    """ADDENDUM §C.4: pool b, c across tiers, then apply McNemar once."""
    pairs = {"frontier": (5, 1), "small": (5, 1), "frontier_alt": (0, 0)}
    b_total, c_total, p = pooled_paired_mcnemar(pairs)
    assert b_total == 10
    assert c_total == 2
    assert abs(p - paired_mcnemar_midp(10, 2)) < 1e-12


# ---------- Holm-Bonferroni ----------


def test_holm_bonferroni_standard_pattern() -> None:
    """Criterion 4: standard Holm rejection pattern for [0.001, 0.04, 0.10]."""
    rejects = holm_bonferroni([0.001, 0.04, 0.10], 0.05)
    # ranks: 0.001 (test 1: 0.05/3=0.0167, reject), 0.04 (test 2: 0.05/2=0.025, fail),
    # 0.10 (halted). Expected: [True, False, False].
    assert rejects == [True, False, False]


def test_holm_bonferroni_preserves_order() -> None:
    """Output order matches input order even when sort permutes internally."""
    p = [0.10, 0.001, 0.04]
    rejects = holm_bonferroni(p, 0.05)
    # Internal sort: [0.001 (idx 1), 0.04 (idx 2), 0.10 (idx 0)]; after step-down:
    # idx 1 reject, idx 2 fail (0.04 > 0.025), idx 0 halted.
    assert rejects == [False, True, False]


def test_holm_bonferroni_empty() -> None:
    assert holm_bonferroni([], 0.05) == []


# ---------- BCa bootstrap ----------


def test_bca_tight_ci_on_constant_data() -> None:
    """Criterion 5: constant data → CI tightly brackets the point estimate."""
    point, lo, hi = bca_bootstrap_ci(
        statistic_fn=lambda x: float(np.mean(x)),
        data=np.array([0.5] * 100),
        cluster_ids=np.arange(100),
        n_resamples=1000,
        seed=0,
    )
    assert abs(point - 0.5) < 1e-12
    assert abs(lo - 0.5) < 0.01
    assert abs(hi - 0.5) < 0.01


def test_bca_zero_variance_when_one_cluster() -> None:
    """Criterion 6: all rows in a single cluster → variance across resamples = 0."""
    data = np.array([0.0, 1.0, 0.0, 1.0, 1.0])
    cluster_ids = np.zeros(5, dtype=int)
    point, lo, hi = bca_bootstrap_ci(
        statistic_fn=lambda x: float(np.mean(x)),
        data=data,
        cluster_ids=cluster_ids,
        n_resamples=200,
        seed=0,
    )
    # Drawing the only cluster always returns the same rows → degenerate.
    assert lo == hi == point


def test_bca_empty_returns_nan() -> None:
    point, lo, hi = bca_bootstrap_ci(
        statistic_fn=lambda x: float(np.mean(x)) if x.size else float("nan"),
        data=np.array([]),
        n_resamples=10,
        seed=0,
    )
    assert math.isnan(point) and math.isnan(lo) and math.isnan(hi)


def test_bca_brackets_point_for_balanced_sample() -> None:
    """CI should bracket the point estimate on a balanced random sample."""
    rng = np.random.default_rng(0)
    data = rng.binomial(1, 0.3, size=500).astype(float)
    point, lo, hi = bca_bootstrap_ci(
        statistic_fn=lambda x: float(np.mean(x)),
        data=data,
        cluster_ids=None,
        n_resamples=1000,
        seed=0,
    )
    assert lo <= point <= hi
    assert hi - lo < 0.15  # reasonable width given N=500


# ---------- TOST ----------


def test_tost_all_pass_non_inferior() -> None:
    """Criterion 7: identical all-pass arrays → non_inferior=True."""
    res = tost_paired_proportions([True] * 20, [True] * 20, margin=0.05)
    assert res["non_inferior"] is True
    assert res["mean_diff"] == 0.0


def test_tost_identical_mixed_non_inferior() -> None:
    """Criterion 8: identical samples (mixed) → non_inferior=True."""
    a = [True] * 20 + [False] * 20
    b = list(a)
    res = tost_paired_proportions(a, b, margin=0.05)
    assert res["non_inferior"] is True
    assert res["mean_diff"] == 0.0


def test_tost_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        tost_paired_proportions([True, False], [True], margin=0.05)


def test_tost_effective_n_drops_double_failures() -> None:
    a = [True, False, False, True]
    b = [True, False, True, False]
    res = tost_paired_proportions(a, b, margin=0.05)
    # only pair index 1 is (False, False) → effective_n = 3
    assert res["effective_n"] == 3


# ---------- Friedman ----------


def test_friedman_no_difference_returns_high_p() -> None:
    """Criterion 9: identical group scores → p ≈ 1.0."""
    res = friedman_nemenyi(
        {"a": [1, 2, 3, 4, 5], "b": [1, 2, 3, 4, 5], "c": [1, 2, 3, 4, 5]}
    )
    assert res["k_groups"] == 3
    assert res["n_subjects"] == 5
    # With identical inputs Friedman returns p=1.0 (no rank variation).
    assert res["p_value"] >= 0.95
    assert res["reject_pairs"] == []


def test_friedman_clear_difference_rejects() -> None:
    """Sanity: a clear separation should be detected."""
    res = friedman_nemenyi(
        {
            "near_name": [0.5, 0.6, 0.55, 0.58, 0.62, 0.5, 0.6, 0.55, 0.58, 0.62],
            "synonym": [0.3, 0.32, 0.35, 0.31, 0.33, 0.3, 0.32, 0.35, 0.31, 0.33],
            "matched_random": [0.05, 0.06, 0.04, 0.07, 0.05, 0.05, 0.06, 0.04, 0.07, 0.05],
        }
    )
    assert res["p_value"] < 0.05


def test_friedman_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        friedman_nemenyi({"a": [1, 2, 3], "b": [1, 2], "c": [1, 2, 3]})


def test_friedman_too_few_groups_raises() -> None:
    with pytest.raises(ValueError):
        friedman_nemenyi({"a": [1, 2, 3], "b": [1, 2, 3]})


# ---------- Gap closure ----------


def test_gap_closure_denominator_at_threshold_returns_none() -> None:
    """Criterion 10: ``(0.5, 0.7, 0.55)`` → denom 0.05 == threshold → None.

    Per acceptance contract, threshold is treated as inclusive (denom <=
    threshold → None) so that a frontier-vs-small gap of exactly 5pp is
    classified as "near zero" alongside truly-near-zero values.
    """
    assert gap_closure_ratio(0.5, 0.7, 0.55) is None


def test_gap_closure_normal_case() -> None:
    """Criterion 11: ``(0.5, 0.7, 0.8)`` → 0.2 / 0.3 = 0.667."""
    val = gap_closure_ratio(0.5, 0.7, 0.8)
    assert val is not None
    assert abs(val - (0.2 / 0.3)) < 1e-9


def test_gap_closure_with_ci_finite_run() -> None:
    """Smoke: gap_closure_with_ci returns a finite point + CI on synthetic data."""
    rng = np.random.default_rng(0)
    small_c0 = (rng.random(50) < 0.30).tolist()
    small_c1 = (rng.random(50) < 0.55).tolist()
    frontier_c0 = (rng.random(50) < 0.75).tolist()
    res = gap_closure_with_ci(
        per_task_results={
            "small": {"C0": small_c0, "C1": small_c1},
            "frontier": {"C0": frontier_c0},
        },
        task_ids_per_tier={
            "small": [f"t{i}" for i in range(50)],
            "frontier": [f"f{i}" for i in range(50)],
        },
        n_resamples=500,
        seed=0,
    )
    assert res["point_estimate"] is not None
    assert res["ci_low"] is not None and res["ci_high"] is not None
    # BCa intervals can occasionally fall slightly off the point on a ratio
    # statistic; allow a small tolerance.
    tol = 0.02
    assert res["ci_low"] - tol <= res["point_estimate"] <= res["ci_high"] + tol
    assert res["ci_high"] > res["ci_low"]


def test_gap_closure_with_ci_undefined_denominator() -> None:
    """When the data give a near-zero denominator, return point=None + warning."""
    res = gap_closure_with_ci(
        per_task_results={
            "small": {"C0": [True] * 10, "C1": [True] * 10},
            "frontier": {"C0": [True] * 10},
        },
        task_ids_per_tier={
            "small": [f"t{i}" for i in range(10)],
            "frontier": [f"f{i}" for i in range(10)],
        },
        n_resamples=100,
        seed=0,
    )
    assert res["point_estimate"] is None
    assert res["ci_low"] is None and res["ci_high"] is None
    assert res["warning"]


# ---------- TEHR ----------


def test_tehr_basic() -> None:
    assert tehr(3, 10) == 0.3
    assert math.isnan(tehr(0, 0))


def test_tehr_with_ci_brackets_point() -> None:
    rng = np.random.default_rng(0)
    n_tasks = 30
    labels: list[bool] = []
    ids: list[str] = []
    for t in range(n_tasks):
        for _ in range(5):
            labels.append(bool(rng.random() < 0.2))
            ids.append(f"task_{t}")
    point, lo, hi = tehr_with_ci(labels, ids, n_resamples=500, seed=0)
    assert lo <= point <= hi
    assert 0.0 <= point <= 1.0


def test_tehr_with_ci_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        tehr_with_ci([True, False], ["a"], n_resamples=10)


# ---------- Condition alias map ----------


def test_condition_alias_roundtrip() -> None:
    for jsonl, paper in CONDITION_LABEL_FOR_PAPER.items():
        assert CONDITION_LABEL_FOR_JSONL[paper] == jsonl
    assert CONDITION_LABEL_FOR_PAPER["C0_7"] == "C0.7"
