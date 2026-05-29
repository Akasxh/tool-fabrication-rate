"""Clean rebuild of figures for SCALE @ ICML 2026 paper.
Only matplotlib (no Unicode in text). TikZ for architecture done inline in LaTeX.
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

PAPER_FIG = Path("paper/figures")
PAPER_FIG.mkdir(parents=True, exist_ok=True)

# ICML-friendly rcParams
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman", "Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def figure_scaling_curve(out: Path) -> None:
    """Qwen3 family TEHR scaling curve."""
    sizes = ["0.6B", "1.7B", "4B", "8B", "14B", "32B"]
    rates = [0.0, 0.95, 1.33, 1.49, 1.87, 0.0]
    cp_upper = [3.92, 2.97, 3.40, 3.37, 3.88, 1.34]

    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    x = np.arange(len(sizes))

    yerr = [[r - 0 for r in rates], [u - r for u, r in zip(cp_upper, rates)]]
    ax.errorbar(x, rates, yerr=yerr, fmt="none", ecolor="#cc3333",
                alpha=0.55, capsize=3, elinewidth=0.9, zorder=2)

    ax.plot(x, rates, "o-", color="#cc3333", linewidth=1.8, markersize=7,
            markerfacecolor="#cc3333", markeredgecolor="white",
            markeredgewidth=1.0, zorder=4, label="Qwen3 pooled TEHR")

    anth_upper = 0.115
    ax.axhspan(0, anth_upper, color="#1f77b4", alpha=0.18, zorder=1)
    ax.axhline(anth_upper, color="#1f77b4", linewidth=1.2, linestyle="--",
               zorder=1.5)

    ax.text(5.1, anth_upper + 0.08,
            "Anthropic 4.x C$_0$ upper bound (0.115\\%, $N$=2,599)",
            fontsize=7.5, ha="right", va="bottom", color="#1f4f7a",
            style="italic")

    annotation_data = [
        (0, 0.0, "0/75", 14, "left"),
        (1, 0.95, "2/210", 12, "left"),
        (2, 1.33, "3/226", 12, "right"),
        (3, 1.49, "4/269", 12, "left"),
        (4, 1.87, "5/268", 12, "left"),
        (5, 0.0, "0/224", 14, "right"),
    ]
    for xi, yi, label, dy, side in annotation_data:
        dx = -10 if side == "right" else 10
        ax.annotate(label, (xi, yi), textcoords="offset points",
                    xytext=(dx, dy), ha=side, va="center",
                    fontsize=7, color="#660000", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(sizes)
    ax.set_xlabel("Qwen3 model size (4-bit MLX)")
    ax.set_ylabel("TEHR (\\%) with 95\\% Clopper--Pearson UB")
    ax.set_title("Qwen3 TEHR scaling: rises to 14B peak, returns to 0 at 32B",
                 pad=8)
    ax.set_ylim(-0.4, 5.2)
    ax.grid(alpha=0.3, linestyle="--", axis="y", zorder=0)
    ax.set_axisbelow(True)

    ax.legend(loc="upper right", frameon=False, fontsize=8)

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


def figure_ablation_ladder(out: Path) -> None:
    """4-condition ablation on Qwen3-8B: C0 -> C0.5 -> C0.7 -> C1."""
    conditions = ["$C_0$", "$C_{0.5}$", "$C_{0.7}$", "$C_1$"]
    sublabels = ["opaque\nbaseline", "naive\nretry",
                 "structured\nerror", "RVR\n(full)"]
    rates = [1.49, 0.39, 0.00, 0.00]
    nums = [(4, 269), (1, 258), (0, 253), (0, 258)]
    cp_upper = [3.37, 1.61, 1.18, 1.15]

    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    x = np.arange(len(conditions))

    colors = ["#a6324c", "#d97a5b", "#7ab85c", "#3a8a3f"]
    bars = ax.bar(x, rates, color=colors, width=0.62, edgecolor="white",
                   linewidth=0.6, zorder=3)

    yerr_up = [u - r for r, u in zip(rates, cp_upper)]
    ax.errorbar(x, rates, yerr=[[0] * 4, yerr_up], fmt="none",
                ecolor="#444444", capsize=3, elinewidth=0.8, zorder=4)

    for xi, rate, (n, d) in zip(x, rates, nums):
        rate_str = f"{rate:.2f}\\%" if rate > 0 else "0\\%"
        label = f"{rate_str}\n({n}/{d})"
        ax.text(xi, rate + 0.18, label, ha="center", va="bottom",
                fontsize=8, fontweight="bold", color="#1a1a1a",
                linespacing=1.15)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{c}\n{s}" for c, s in zip(conditions, sublabels)])
    ax.set_ylabel("TEHR (\\%) on Qwen3-8B")
    ax.set_title("4-condition ablation: structured error is the active ingredient",
                 pad=8)
    ax.set_ylim(0, 4.6)
    ax.grid(alpha=0.3, linestyle="--", axis="y", zorder=0)
    ax.set_axisbelow(True)

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    figure_scaling_curve(PAPER_FIG / "fig1_scaling_curve.pdf")
    figure_ablation_ladder(PAPER_FIG / "fig2_ablation_ladder.pdf")
    print("clean figures written")


if __name__ == "__main__":
    main()
