"""Full per-cell + pooled statistics for the SCALE @ ICML 2026 paper.

Reads PHASE0/RESULTS/headline_numbers.json (per-call TEHR cells: hallucinated
out of n_calls) and emits, for the paper:

  (a) Clopper--Pearson 95% CI for EVERY probe cell and every pooled rate.
      Every 0-event cell still gets an exact upper bound, so the paper never
      prints a bare 0%.
  (b) Fisher's exact one-sided pooled C0-vs-C1 (does C1 reduce TEHR?), plus
      per-tier where both arms exist, with Holm-Bonferroni across the tier
      family (reusing harness.stats.paired_mcnemar.holm_bonferroni).
  (c) The Qwen3 C0 hallucination curve with a Clopper--Pearson CI per size.

Conventions follow harness/stats/*: scipy-based, terse, BCa CIs for non-zero
cells via harness.stats.tehr.tehr_with_ci. CP via scipy.stats.beta (exact
binomial). Read-only on harness; this is a standalone reporting script.

Run from repo root:
    PYTHONPATH=. harness/.venv/bin/python scripts/run_stats_full.py

Writes paper/_staging/stats_table.md and paper/_staging/stats_full.json.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path

from scipy.stats import beta, fisher_exact

from harness.stats import CONDITION_LABEL_FOR_PAPER
from harness.stats.paired_mcnemar import holm_bonferroni

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "PHASE0" / "RESULTS" / "headline_numbers.json"
OUT_MD = REPO / "paper" / "_staging" / "stats_table.md"
OUT_JSON = REPO / "paper" / "_staging" / "stats_full.json"

ALPHA = 0.05  # 95% intervals


# --------------------------------------------------------------------------- #
# Clopper--Pearson exact binomial CI                                          #
# --------------------------------------------------------------------------- #
def clopper_pearson(k: int, n: int, alpha: float = ALPHA) -> tuple[float, float]:
    """Exact Clopper--Pearson two-sided (1-alpha) CI for a binomial rate.

    Returns (lower, upper) in [0, 1]. Handles the boundary cases:
      k == 0  -> lower = 0
      k == n  -> upper = 1
    n == 0 -> (nan, nan).
    """
    if n == 0:
        return (math.nan, math.nan)
    if k < 0 or k > n:
        raise ValueError("k must be in [0, n]")
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2.0, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1.0 - alpha / 2.0, k + 1, n - k))
    return (lo, hi)


def cp_upper(k: int, n: int, alpha: float = ALPHA) -> float:
    """Clopper--Pearson upper bound only (the number the paper prints)."""
    return clopper_pearson(k, n, alpha)[1]


def pct(x: float, places: int = 2) -> str:
    """Format a rate in [0,1] as a percentage string."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{100.0 * x:.{places}f}\\%"


# --------------------------------------------------------------------------- #
# Tier-name helpers                                                           #
# --------------------------------------------------------------------------- #
def short_model(model: str) -> str:
    """Compact model label for tables."""
    if model.startswith("mlx-community/"):
        return model.split("/", 1)[1].replace("-4bit", "").replace("-Instruct", "")
    return model


def qwen3_size_b(model: str) -> float | None:
    """Parameter size in billions for a Qwen3 model id, else None."""
    m = re.search(r"Qwen3-([\d.]+)B-4bit", model)
    return float(m.group(1)) if m else None


# --------------------------------------------------------------------------- #
# Load + index probe cells (TEHR is only defined where n_calls > 0)           #
# --------------------------------------------------------------------------- #
def load_probe_cells(doc: dict) -> list[dict]:
    """Probe cells with a defined denominator (n_calls > 0)."""
    cells = []
    for c in doc["cells"]:
        if c["kind"] != "probe":
            continue
        if c["n_calls"] == 0 or c.get("tehr") is None:
            continue
        cells.append(c)
    return cells


def main() -> None:
    doc = json.loads(DATA.read_text())
    probe = load_probe_cells(doc)
    regime = [c for c in doc["cells"] if c["kind"] == "regime"]

    report: dict = {
        "alpha": ALPHA,
        "ci_method": "Clopper-Pearson exact binomial (two-sided 95%)",
        "source": str(DATA.relative_to(REPO)),
    }

    # ----------------------------------------------------------------- #
    # (a) Per-cell CP CIs for every probe cell                          #
    # ----------------------------------------------------------------- #
    per_cell = []
    for c in probe:
        k, n = c["hallucinated"], c["n_calls"]
        lo, hi = clopper_pearson(k, n)
        per_cell.append(
            {
                "model": c["model"],
                "model_short": short_model(c["model"]),
                "condition": CONDITION_LABEL_FOR_PAPER.get(
                    c["condition"], c["condition"]
                ),
                "distractor": c["distractor"],
                "hallucinated": k,
                "n_calls": n,
                "tehr": k / n,
                "cp_lower": lo,
                "cp_upper": hi,
            }
        )
    report["per_cell"] = per_cell

    # Per-cell CP CIs for every regime cell (all 0-event but must not print 0%)
    regime_cells = []
    for c in regime:
        k, n = c["hallucinated"], c["n_calls"]
        if n == 0:
            continue
        lo, hi = clopper_pearson(k, n)
        regime_cells.append(
            {
                "model": c["model"],
                "model_short": short_model(c["model"]),
                "split": c["split"],
                "condition": CONDITION_LABEL_FOR_PAPER.get(
                    c["condition"], c["condition"]
                ),
                "hallucinated": k,
                "n_calls": n,
                "tehr": k / n,
                "cp_lower": lo,
                "cp_upper": hi,
            }
        )
    report["regime_cells"] = regime_cells

    # ----------------------------------------------------------------- #
    # Pooled rates: by model, by condition, by population, grand        #
    # ----------------------------------------------------------------- #
    def pool(cells: list[dict]) -> tuple[int, int]:
        return sum(c["hallucinated"] for c in cells), sum(c["n_calls"] for c in cells)

    pooled: dict = {}

    by_model: dict[str, list[dict]] = defaultdict(list)
    for c in probe:
        by_model[c["model"]].append(c)
    pooled["by_model"] = {}
    for model, cs in by_model.items():
        k, n = pool(cs)
        lo, hi = clopper_pearson(k, n)
        pooled["by_model"][model] = {
            "model_short": short_model(model),
            "hallucinated": k,
            "n_calls": n,
            "tehr": k / n if n else math.nan,
            "cp_lower": lo,
            "cp_upper": hi,
        }

    def is_anthropic(m: str) -> bool:
        return m.startswith("claude")

    anth = [c for c in probe if is_anthropic(c["model"])]
    qwen = [c for c in probe if not is_anthropic(c["model"])]
    for name, cs in (("anthropic_probe", anth), ("qwen_probe", qwen)):
        k, n = pool(cs)
        lo, hi = clopper_pearson(k, n)
        pooled[name] = {
            "hallucinated": k,
            "n_calls": n,
            "tehr": k / n if n else math.nan,
            "cp_lower": lo,
            "cp_upper": hi,
        }

    # Anthropic pooled over probe + regime (the "zero-event regime" claim)
    anth_all = anth + [
        c for c in regime if is_anthropic(c["model"]) and c["n_calls"] > 0
    ]
    k, n = pool(anth_all)
    lo, hi = clopper_pearson(k, n)
    pooled["anthropic_probe_plus_regime"] = {
        "hallucinated": k,
        "n_calls": n,
        "tehr": k / n if n else math.nan,
        "cp_lower": lo,
        "cp_upper": hi,
    }

    # Regime grid pooled (all Anthropic C0 across the three BFCL splits)
    k, n = pool([c for c in regime if c["n_calls"] > 0])
    lo, hi = clopper_pearson(k, n)
    pooled["regime_grid"] = {
        "hallucinated": k,
        "n_calls": n,
        "tehr": k / n if n else math.nan,
        "cp_lower": lo,
        "cp_upper": hi,
    }
    # Worst (largest) per-cell regime CP upper bound, for the §5 "<= X%" claim
    if regime_cells:
        worst = max(regime_cells, key=lambda r: r["cp_upper"])
        pooled["regime_worst_cell_cp_upper"] = {
            "model_short": worst["model_short"],
            "split": worst["split"],
            "n_calls": worst["n_calls"],
            "cp_upper": worst["cp_upper"],
        }
    report["pooled"] = pooled

    # ----------------------------------------------------------------- #
    # (b) Fisher's exact one-sided pooled C0-vs-C1 + per-tier + Holm    #
    #                                                                   #
    # H1: TEHR(C1) < TEHR(C0). Fisher table rows = condition, cols =    #
    # [hallucinated, clean]. one-sided 'less' tests the (C1,hall) cell  #
    # being lower than expected -> C1 reduces fabrication.              #
    # ----------------------------------------------------------------- #
    def cond_counts(cells: list[dict], cond: str) -> tuple[int, int]:
        sel = [c for c in cells if c["condition"] == cond]
        k, n = pool(sel)
        return k, n

    def fisher_c0_c1(c0: tuple[int, int], c1: tuple[int, int]) -> dict:
        k0, n0 = c0
        k1, n1 = c1
        # rows: C0, C1 ; cols: hallucinated, clean. Odds ratio of this table
        # is (k0 * clean1) / (clean0 * k1); H1 "C1 reduces TEHR" means C0's
        # hallucination odds are elevated -> OR > 1 -> alternative='greater'.
        table = [[k0, n0 - k0], [k1, n1 - k1]]
        _, p = fisher_exact(table, alternative="greater")
        return {
            "c0_hallucinated": k0,
            "c0_calls": n0,
            "c1_hallucinated": k1,
            "c1_calls": n1,
            "p_one_sided": float(p),
        }

    # Tiers that actually have both C0 and C1 arms in the probe data.
    tiers_with_both = []
    for model, cs in by_model.items():
        conds = {c["condition"] for c in cs}
        if "C0" in conds and "C1" in conds:
            tiers_with_both.append(model)
    tiers_with_both.sort()

    per_tier_fisher = {}
    tier_pvals = []
    tier_order = []
    for model in tiers_with_both:
        cs = by_model[model]
        res = fisher_c0_c1(cond_counts(cs, "C0"), cond_counts(cs, "C1"))
        per_tier_fisher[model] = res
        tier_pvals.append(res["p_one_sided"])
        tier_order.append(model)

    rejects = holm_bonferroni(tier_pvals, alpha=ALPHA) if tier_pvals else []
    for model, rej in zip(tier_order, rejects):
        per_tier_fisher[model]["holm_reject"] = bool(rej)

    # Pooled C0-vs-C1 over the tiers that have both arms (apples-to-apples).
    both = [c for c in probe if c["model"] in set(tiers_with_both)]
    pooled_fisher = fisher_c0_c1(cond_counts(both, "C0"), cond_counts(both, "C1"))

    # Headline framing: pool C0 fabrications across the four Qwen3 tiers with
    # TEHR>0 (1.7/4/8/14B), all of which go to 0 under C1.
    nonzero_tiers = [
        m for m in tiers_with_both
        if cond_counts(by_model[m], "C0")[0] > 0
    ]
    nz = [c for c in probe if c["model"] in set(nonzero_tiers)]
    pooled_fisher_nonzero = fisher_c0_c1(
        cond_counts(nz, "C0"), cond_counts(nz, "C1")
    )

    report["fisher"] = {
        "hypothesis": "one-sided H1: TEHR(C1) < TEHR(C0)",
        "pooled_tiers_with_both_arms": {
            "tiers": [short_model(m) for m in tiers_with_both],
            **pooled_fisher,
        },
        "pooled_nonzero_c0_tiers": {
            "tiers": [short_model(m) for m in nonzero_tiers],
            **pooled_fisher_nonzero,
        },
        "per_tier": {
            short_model(m): per_tier_fisher[m] for m in tier_order
        },
        "holm_family_size": len(tier_pvals),
    }

    # ----------------------------------------------------------------- #
    # (c) Qwen3 C0 curve with CP CIs per size                           #
    # ----------------------------------------------------------------- #
    qwen3_c0: dict[float, list[dict]] = defaultdict(list)
    for c in probe:
        size = qwen3_size_b(c["model"])
        if size is not None and c["condition"] == "C0":
            qwen3_c0[size].append(c)
    curve = []
    for size in sorted(qwen3_c0):
        k, n = pool(qwen3_c0[size])
        lo, hi = clopper_pearson(k, n)
        curve.append(
            {
                "size_b": size,
                "hallucinated": k,
                "n_calls": n,
                "tehr": k / n if n else math.nan,
                "cp_lower": lo,
                "cp_upper": hi,
            }
        )
    report["qwen3_c0_curve"] = curve

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2))

    # ----------------------------------------------------------------- #
    # Markdown                                                          #
    # ----------------------------------------------------------------- #
    L: list[str] = []
    L.append("# SCALE statistics (auto-generated by scripts/run_stats_full.py)")
    L.append("")
    L.append(f"Source: `{report['source']}`. CI: {report['ci_method']}.")
    L.append("Every 0-event cell carries an exact Clopper--Pearson upper bound; ")
    L.append("no bare 0% should ever be printed.")
    L.append("")

    # (c) Qwen3 C0 curve
    L.append("## (c) Qwen3 C0 TEHR curve, per size, with 95% CP CIs")
    L.append("")
    L.append("| size | hall/calls | TEHR | CP 95% CI |")
    L.append("|---|---|---|---|")
    for r in curve:
        ci = f"[{pct(r['cp_lower'])}, {pct(r['cp_upper'])}]"
        L.append(
            f"| {r['size_b']:g}B | {r['hallucinated']}/{r['n_calls']} "
            f"| {pct(r['tehr'])} | {ci} |"
        )
    L.append("")

    # (a) per-model pooled
    L.append("## (a) Pooled per-model TEHR with 95% CP CIs (probe)")
    L.append("")
    L.append("| model | hall/calls | TEHR | CP 95% CI | CP upper |")
    L.append("|---|---|---|---|---|")
    for model in sorted(pooled["by_model"]):
        r = pooled["by_model"][model]
        ci = f"[{pct(r['cp_lower'])}, {pct(r['cp_upper'])}]"
        L.append(
            f"| {r['model_short']} | {r['hallucinated']}/{r['n_calls']} "
            f"| {pct(r['tehr'])} | {ci} | **{pct(r['cp_upper'])}** |"
        )
    L.append("")

    # Pooled population summaries
    L.append("## Pooled population summaries (the bounds to drop into the paper)")
    L.append("")
    L.append("| pool | hall/calls | TEHR | CP 95% upper |")
    L.append("|---|---|---|---|")
    name_map = [
        ("anthropic_probe", "Anthropic (probe only)"),
        ("anthropic_probe_plus_regime", "Anthropic (probe + regime, zero-event)"),
        ("regime_grid", "Regime grid (Anthropic C0, 3 BFCL splits)"),
        ("qwen_probe", "Qwen/open (probe)"),
    ]
    for key, label in name_map:
        r = pooled[key]
        L.append(
            f"| {label} | {r['hallucinated']}/{r['n_calls']} "
            f"| {pct(r['tehr'])} | **{pct(r['cp_upper'])}** |"
        )
    if "regime_worst_cell_cp_upper" in pooled:
        w = pooled["regime_worst_cell_cp_upper"]
        L.append("")
        L.append(
            f"Worst single regime cell CP upper bound: **{pct(w['cp_upper'])}** "
            f"({w['model_short']}, {w['split']}, 0/{w['n_calls']})."
        )
    L.append("")

    # (a) every regime cell
    L.append("## (a) Per-cell CP upper bounds, regime grid (all 0-event)")
    L.append("")
    L.append("| model | split | hall/calls | CP 95% upper |")
    L.append("|---|---|---|---|")
    for r in sorted(regime_cells, key=lambda x: (x["model_short"], x["split"])):
        L.append(
            f"| {r['model_short']} | {r['split']} "
            f"| {r['hallucinated']}/{r['n_calls']} | {pct(r['cp_upper'])} |"
        )
    L.append("")

    # (a) every probe cell
    L.append("## (a) Per-cell CP CIs, every probe cell")
    L.append("")
    L.append("| model | cond | distractor | hall/calls | TEHR | CP 95% upper |")
    L.append("|---|---|---|---|---|---|")
    for r in sorted(
        per_cell, key=lambda x: (x["model_short"], x["condition"], x["distractor"] or "")
    ):
        L.append(
            f"| {r['model_short']} | {r['condition']} | {r['distractor']} "
            f"| {r['hallucinated']}/{r['n_calls']} | {pct(r['tehr'])} "
            f"| {pct(r['cp_upper'])} |"
        )
    L.append("")

    # (b) Fisher
    f = report["fisher"]
    L.append("## (b) Fisher's exact one-sided, C0 vs C1 (H1: TEHR(C1) < TEHR(C0))")
    L.append("")
    p = f["pooled_nonzero_c0_tiers"]
    L.append(
        f"**Headline (pooled over Qwen3 tiers with C0 TEHR>0: "
        f"{', '.join(p['tiers'])}):** "
        f"C0 = {p['c0_hallucinated']}/{p['c0_calls']}, "
        f"C1 = {p['c1_hallucinated']}/{p['c1_calls']}, "
        f"one-sided p = {p['p_one_sided']:.4g}."
    )
    p2 = f["pooled_tiers_with_both_arms"]
    L.append("")
    L.append(
        f"Pooled over ALL tiers that ran both arms ({', '.join(p2['tiers'])}): "
        f"C0 = {p2['c0_hallucinated']}/{p2['c0_calls']}, "
        f"C1 = {p2['c1_hallucinated']}/{p2['c1_calls']}, "
        f"one-sided p = {p2['p_one_sided']:.4g}."
    )
    L.append("")
    L.append(
        f"Per-tier, Holm-Bonferroni across family of {f['holm_family_size']}:"
    )
    L.append("")
    L.append("| tier | C0 hall/calls | C1 hall/calls | p (1-sided) | Holm reject |")
    L.append("|---|---|---|---|---|")
    for tier, res in f["per_tier"].items():
        L.append(
            f"| {tier} | {res['c0_hallucinated']}/{res['c0_calls']} "
            f"| {res['c1_hallucinated']}/{res['c1_calls']} "
            f"| {res['p_one_sided']:.4g} "
            f"| {'yes' if res['holm_reject'] else 'no'} |"
        )
    L.append("")

    OUT_MD.write_text("\n".join(L) + "\n")

    # Console summary
    print(f"wrote {OUT_MD.relative_to(REPO)}")
    print(f"wrote {OUT_JSON.relative_to(REPO)}")
    a = pooled["anthropic_probe_plus_regime"]
    print(
        f"Anthropic pooled (probe+regime): {a['hallucinated']}/{a['n_calls']}, "
        f"CP 95% upper = {pct(a['cp_upper'])}"
    )
    print(
        f"Headline Fisher (nonzero C0 tiers): "
        f"p = {p['p_one_sided']:.4g}, "
        f"C0={p['c0_hallucinated']}/{p['c0_calls']} -> "
        f"C1={p['c1_hallucinated']}/{p['c1_calls']}"
    )


if __name__ == "__main__":
    main()
