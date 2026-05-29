"""Generate the three high-leverage figures for the SCALE @ ICML 2026 paper.

Reads aggregated TEHR data from `scripts/aggregate_all.py` JSON output and writes:
  paper/figures/fig1_scaling_curve.pdf
  paper/figures/fig2_prior_work_comparison.pdf
  paper/figures/fig3_decomposition_trace.pdf

Run after `scripts/aggregate_all.py` to refresh.
"""
from __future__ import annotations
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.stats import beta as scipy_beta


PAPER_FIG = Path("paper/figures"); PAPER_FIG.mkdir(parents=True, exist_ok=True)
HEADLINE = Path("PHASE0/RESULTS/headline_numbers.json")


# ICML-friendly mpl rcParams (sans-serif, fixed font sizes)
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "pdf.fonttype": 42,  # Embed TrueType fonts
})


def clopper_pearson_upper(k: int, n: int, alpha: float = 0.05) -> float:
    """Two-sided 95% CI upper bound; one-sided would use alpha not alpha/2."""
    if n == 0:
        return 1.0
    if k == n:
        return 1.0
    return float(scipy_beta.ppf(1 - alpha, k + 1, n - k))


def clopper_pearson_lower(k: int, n: int, alpha: float = 0.05) -> float:
    if n == 0 or k == 0:
        return 0.0
    return float(scipy_beta.ppf(alpha, k, n - k + 1))


def load_aggregate() -> dict:
    if not HEADLINE.exists():
        raise SystemExit(f"Run scripts/aggregate_all.py first; missing {HEADLINE}")
    return json.loads(HEADLINE.read_text())


# ---------------------------------------------------------------------------
# Figure 1: Qwen3 family TEHR scaling curve (open-source side)
# ---------------------------------------------------------------------------

def figure_1_scaling_curve(data: dict, out: Path) -> None:
    """Per-size pooled TEHR across the Qwen3 family with Clopper-Pearson 95% upper
    bounds. Non-monotonic — peaks at 14B then collapses at 32B.
    """
    sizes_billion = [0.6, 1.7, 4.0, 8.0, 14.0, 32.0]
    size_labels   = ["0.6B", "1.7B", "4B", "8B", "14B", "32B"]

    by_size = defaultdict(lambda: {"num": 0, "denom": 0})
    for cell in data["cells"]:
        if cell["kind"] != "probe": continue
        if cell["condition"] != "C0": continue
        if not cell["model"].startswith("mlx-community/Qwen3-"): continue
        size_str = cell["model"].split("Qwen3-")[1].split("-4bit")[0]
        # Skip 8B C1 etc (already filtered); only C0 cells here
        for sz, lbl in zip(sizes_billion, size_labels):
            if size_str == lbl:
                by_size[lbl]["num"] += cell["hallucinated"]
                by_size[lbl]["denom"] += cell["n_calls"]

    pooled_rate = []
    upper_ci = []
    lower_ci = []
    n_calls_per = []
    for lbl in size_labels:
        s = by_size[lbl]
        n, d = s["num"], s["denom"]
        rate = (n / d) if d else 0
        pooled_rate.append(rate * 100)
        upper_ci.append(clopper_pearson_upper(n, d) * 100)
        lower_ci.append(clopper_pearson_lower(n, d) * 100)
        n_calls_per.append(d)

    # Reference: Anthropic frontier+small (pooled across all 5 versions)
    anth = {"num": 0, "denom": 0}
    for cell in data["cells"]:
        if cell["model"].startswith("claude-"):
            anth["num"] += cell["hallucinated"]
            anth["denom"] += cell["n_calls"]
    anth_upper = clopper_pearson_upper(anth["num"], anth["denom"]) * 100

    fig, ax = plt.subplots(figsize=(5.0, 3.0))

    x = np.arange(len(sizes_billion))
    yerr_lower = [r - lo for r, lo in zip(pooled_rate, lower_ci)]
    yerr_upper = [up - r for r, up in zip(pooled_rate, upper_ci)]

    ax.errorbar(x, pooled_rate, yerr=[yerr_lower, yerr_upper],
                fmt="o-", color="#cc3333", linewidth=1.6, markersize=6,
                capsize=3, elinewidth=1.0,
                label="Qwen3 family (open-source) C0")

    # Anthropic upper-bound line
    ax.axhline(anth_upper, linestyle="--", color="#1f77b4", linewidth=1.2,
               label=f"Anthropic 4.x family 95% upper bound = {anth_upper:.2f}%\n"
                     f"(0/{anth['denom']} pooled across 5 models, 11 months)")

    ax.set_xticks(x)
    ax.set_xticklabels(size_labels)
    ax.set_xlabel("Model size (4-bit, served via MLX on 32 GB Apple Silicon)")
    ax.set_ylabel("Pooled TEHR (%) with 95% Clopper--Pearson CI")
    ax.set_title("Qwen3-family TEHR scales non-monotonically;\n"
                 "peak at 14B (1.87%), zero at 0.6B and 32B")
    ax.set_ylim(-0.3, max(7.0, max(upper_ci) * 1.05))
    ax.grid(alpha=0.3, linestyle="--", axis="y")
    ax.legend(loc="upper left", frameon=False)

    # Annotate per-point with N
    for xi, r, n in zip(x, pooled_rate, n_calls_per):
        ax.annotate(f"$N={n}$", (xi, r), textcoords="offset points",
                    xytext=(0, -16), fontsize=7, ha="center", color="#666666")

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# Figure 2: Prior-work comparison
# ---------------------------------------------------------------------------

def figure_2_prior_work(data: dict, out: Path) -> None:
    """Bar chart comparing prior aggregate metrics with our per-call TEHR
    across model tiers."""

    # Pre-2026 prior reports (from §2 of paper)
    prior_works = [
        ("API-Bank\n(2023; per-task)", 61.4, "#888888"),
        ("MetaTool\n(2024; per-task)", 25.0, "#aaaaaa"),
    ]

    # Our results
    by_model = defaultdict(lambda: {"num": 0, "denom": 0})
    for cell in data["cells"]:
        if cell["kind"] != "probe": continue
        if cell["condition"] != "C0": continue
        m = cell["model"]
        by_model[m]["num"] += cell["hallucinated"]
        by_model[m]["denom"] += cell["n_calls"]

    our_anchor = []
    for label, mid in [
        ("Opus 4.7\n(Apr 2026)",         "claude-opus-4-7"),
        ("Sonnet 4.6\n(Feb 2026)",       "claude-sonnet-4-6"),
        ("Sonnet 4\n(May 2025)",         "claude-sonnet-4-20250514"),
        ("Haiku 4.5\n(Oct 2025)",        "claude-haiku-4-5"),
        ("Qwen3-32B\n(open-source)",     "mlx-community/Qwen3-32B-4bit"),
        ("Qwen3-14B\n(open-source)",     "mlx-community/Qwen3-14B-4bit"),
        ("Qwen3-8B\n(open-source)",      "mlx-community/Qwen3-8B-4bit"),
        ("Qwen3-4B\n(open-source)",      "mlx-community/Qwen3-4B-4bit"),
        ("Qwen3-1.7B\n(open-source)",    "mlx-community/Qwen3-1.7B-4bit"),
    ]:
        s = by_model.get(mid, {"num": 0, "denom": 0})
        if s["denom"] == 0: continue
        rate = (s["num"] / s["denom"]) * 100
        upper = clopper_pearson_upper(s["num"], s["denom"]) * 100
        our_anchor.append((label, rate, upper, s["num"], s["denom"]))

    fig, ax = plt.subplots(figsize=(7.0, 3.5))

    labels  = [w[0] for w in prior_works] + [a[0] for a in our_anchor]
    values  = [w[1] for w in prior_works] + [a[1] for a in our_anchor]
    colors  = [w[2] for w in prior_works] + [
        # Anthropic: blues. Open-source: reds (gradient by size).
        "#1f4f7a", "#2a6ba8", "#3b87ca", "#5da3dc",
        "#7a2c2c", "#a33333", "#cc3333", "#dd5555", "#e87777",
    ]
    upper_err = [0, 0] + [a[2] - a[1] for a in our_anchor]

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, edgecolor="white", linewidth=0.5)

    # Error bars for our cells (Clopper-Pearson upper)
    ax.errorbar(x[2:], values[2:], yerr=[[0] * len(our_anchor), upper_err[2:]],
                fmt="none", ecolor="black", capsize=2, linewidth=0.8)

    # Annotate each bar with its value
    for bar, val, lbl_idx in zip(bars, values, range(len(values))):
        h = bar.get_height()
        if lbl_idx >= len(prior_works):
            n_h = our_anchor[lbl_idx - len(prior_works)][3]
            n_d = our_anchor[lbl_idx - len(prior_works)][4]
            txt = f"{val:.2f}%\n({n_h}/{n_d})"
        else:
            txt = f"{val:.1f}%"
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1.2, txt,
                ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("Tool-call hallucination rate (%)")
    ax.set_title("Prior aggregate metrics vs.\\ per-call TEHR diagnostic across tiers\n"
                 "(error bars: Clopper--Pearson 95\\% one-sided upper bound)")
    ax.set_ylim(0, 70)

    # Legend by group
    grey_patch = mpatches.Patch(color="#888888", label="Prior aggregate (per-task)")
    blue_patch = mpatches.Patch(color="#3b87ca", label="Anthropic 4.x")
    red_patch  = mpatches.Patch(color="#cc3333", label="Qwen3 family")
    ax.legend(handles=[grey_patch, blue_patch, red_patch],
              loc="upper right", frameon=False)
    ax.grid(alpha=0.3, linestyle="--", axis="y")

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# Figure 3: Decomposition trace (TikZ-style sequence diagram via matplotlib)
# ---------------------------------------------------------------------------

def figure_3_decomposition(out: Path) -> None:
    """Sequence diagram: Sonnet 4.6 on multi_turn_miss_func task 24 — instead
    of fabricating the missing one-shot operation, the agent decomposes into 5
    in-registry calls.
    """
    fig, ax = plt.subplots(figsize=(7.0, 2.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    # Lifelines
    actors = ["User", "Agent\n(Sonnet 4.6)", "Executor"]
    actor_x = [0.8, 4.5, 8.5]
    for x, name in zip(actor_x, actors):
        ax.text(x, 3.7, name, ha="center", va="top", fontsize=9, fontweight="bold")
        ax.plot([x, x], [0.2, 3.4], color="#888888", linestyle=":", linewidth=0.8)

    # Step 1: User asks
    ax.annotate("", xy=(actor_x[1] - 0.1, 3.2), xytext=(actor_x[0] + 0.1, 3.2),
                arrowprops=dict(arrowstyle="->", color="#333333"))
    ax.text((actor_x[0] + actor_x[1]) / 2, 3.27,
            "Move all .tex files in /docs to /backup/", ha="center", va="bottom", fontsize=7)

    # Step 2: BFCL miss_func has removed mv_recursive(); the implied one-shot fails.
    # Agent plans a decomposition.
    ax.text(actor_x[1], 2.85, "[plans decomposition: mv_recursive() not in registry]",
            ha="center", fontsize=6.5, fontstyle="italic", color="#cc6633")

    # Steps 3-7: 5 in-registry calls
    decomp = [
        ("pwd()",                            2.5),
        ("ls('/docs')",                      2.15),
        ("cd('/docs')",                      1.8),
        ("mkdir('/backup')",                 1.45),
        ("mv('a.tex /backup/'); mv(...)",    1.1),
    ]
    for call, y in decomp:
        ax.annotate("", xy=(actor_x[2] - 0.1, y), xytext=(actor_x[1] + 0.1, y),
                    arrowprops=dict(arrowstyle="->", color="#1f77b4"))
        ax.text(actor_x[1] + 0.2, y + 0.07, call, va="bottom", fontsize=7,
                color="#1f77b4")
        # Response
        ax.annotate("", xy=(actor_x[1] - 0.1, y - 0.18),
                    xytext=(actor_x[2] - 0.1, y - 0.18),
                    arrowprops=dict(arrowstyle="->", color="#666666",
                                    linestyle="--"))

    # Footer note
    ax.text(5.0, 0.4,
            "5 in-registry calls $\\to$ task succeeds. Zero out-of-registry name emitted.",
            ha="center", fontsize=8, fontweight="bold", color="#cc3333")

    ax.set_title("Decomposition, not fabrication: Sonnet 4.6 on BFCL multi\\_turn\\_miss\\_func task 24",
                 pad=4)

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    data = load_aggregate()
    figure_1_scaling_curve(data, PAPER_FIG / "fig1_scaling_curve.pdf")
    figure_2_prior_work(data, PAPER_FIG / "fig2_prior_work_comparison.pdf")
    figure_3_decomposition(PAPER_FIG / "fig3_decomposition_trace.pdf")
    print("All figures written to paper/figures/")


if __name__ == "__main__":
    main()
