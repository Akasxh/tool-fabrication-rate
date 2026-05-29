"""Add two new figures to the paper:
  fig2_ablation_ladder.pdf  - 4-condition ablation bar chart (C0/C0.5/C0.7/C1)
  fig3_rvr_architecture.pdf - RVR system flow diagram

Run after scripts/aggregate_all.py.
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

PAPER_FIG = Path("paper/figures")
PAPER_FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "pdf.fonttype": 42,
})


def figure_ablation_ladder(out: Path) -> None:
    """4-condition ablation on Qwen3-8B: C0 -> C0.5 -> C0.7 -> C1."""
    conditions = ["$C_0$\n(opaque)", "$C_{0.5}$\n(naive retry)",
                  "$C_{0.7}$\n(structured err)", "$C_1$\n(RVR)"]
    rates_pct = [1.49, 0.39, 0.00, 0.00]
    nums = [(4, 269), (1, 258), (0, 253), (0, 258)]
    upper_bounds = [3.37, 1.61, 1.18, 1.15]  # Clopper-Pearson 95% upper one-sided

    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    x = np.arange(len(conditions))
    colors = ["#a6324c", "#d97a5b", "#7ab85c", "#3a8a3f"]
    bars = ax.bar(x, rates_pct, color=colors, width=0.62, edgecolor="white",
                   linewidth=0.6)

    yerr_lower = [0] * len(rates_pct)
    yerr_upper = [up - r for r, up in zip(rates_pct, upper_bounds)]
    ax.errorbar(x, rates_pct, yerr=[yerr_lower, yerr_upper],
                fmt="none", ecolor="#444444", capsize=3, linewidth=0.9)

    for xi, rate, (n, d) in zip(x, rates_pct, nums):
        ax.text(xi, rate + 0.18, f"{n}/{d}", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold")
        ax.text(xi, rate + 0.05, f"{rate:.2f}%" if rate > 0 else "0%",
                ha="center", va="bottom", fontsize=7.5, color="#222222",
                style="italic")

    annot_y = max(upper_bounds) * 1.05
    ax.annotate("", xy=(3, annot_y), xytext=(0, annot_y),
                arrowprops=dict(arrowstyle="->", color="#444444", lw=0.9))
    ax.text(1.5, annot_y + 0.25, "monotone reduction with structured signal",
            ha="center", va="bottom", fontsize=8, style="italic", color="#444444")

    ax.set_xticks(x)
    ax.set_xticklabels(conditions)
    ax.set_ylabel("TEHR (\\%) on Qwen3-8B")
    ax.set_title("4-condition ablation ladder isolates the active ingredient")
    ax.set_ylim(0, max(upper_bounds) * 1.25)
    ax.grid(alpha=0.3, linestyle="--", axis="y", zorder=0)
    ax.set_axisbelow(True)

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


def figure_rvr_architecture(out: Path) -> None:
    """RVR system flow: agent -> proposed tool call -> membership check ->
    {execute | re-prompt with registry list} -> (one retry max).
    """
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis("off")

    def box(x, y, w, h, label, color="#dde8f3", edge="#1f4f7a", fontsize=8.5,
            bold=False):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.10",
                               facecolor=color, edgecolor=edge, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold" if bold else "normal")

    def arrow(x1, y1, x2, y2, color="#1f4f7a", style="->", lw=1.0):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=lw))

    box(0.1, 4.0, 1.8, 1.0, "Agent\n(LLM)", color="#fdf3df", edge="#a06a1f")
    box(2.4, 4.0, 2.2, 1.0, "Proposed call\n$c.\\mathrm{name}$", color="#eaeaea",
        edge="#555555")
    arrow(1.95, 4.5, 2.4, 4.5)

    box(5.1, 4.0, 2.2, 1.0, "Membership\ncheck $\\in \\mathcal{R}$?", color="#f4d6d6",
        edge="#a3403a", bold=True)
    arrow(4.6, 4.5, 5.1, 4.5)

    box(8.0, 5.0, 2.5, 0.85, "Yes → EXECUTE", color="#dff3df", edge="#3a8a3f")
    arrow(7.3, 4.7, 8.0, 5.4)

    box(8.0, 3.05, 2.5, 0.85, "No → RE-PROMPT", color="#fcdcdc", edge="#a3403a")
    arrow(7.3, 4.3, 8.0, 3.5)

    box(11.0, 3.05, 2.8, 0.85, "registry list\n+ structured err",
        color="#fcdcdc", edge="#a3403a")
    arrow(10.5, 3.5, 11.0, 3.5)

    arrow(12.4, 3.05, 12.4, 1.0, color="#a3403a", style="->", lw=1.2)
    box(2.4, 0.5, 10.0, 1.0, "$k\\!=\\!1$ retry budget then ABORT • "
        "membership check is in-process O(1) • zero provider round-trip when no violation",
        color="#fbf3e8", edge="#888888", fontsize=7.8)
    arrow(2.4, 1.0, 0.0, 1.0)
    arrow(0.0, 1.0, 0.0, 4.5, color="#1f4f7a")
    arrow(0.0, 4.5, 0.1, 4.5)

    ax.set_title("Registry-Visible Reprompting (RVR) middleware",
                 pad=2, fontsize=9.5)

    legend_handles = [
        mpatches.Patch(facecolor="#fdf3df", edgecolor="#a06a1f", label="Agent"),
        mpatches.Patch(facecolor="#f4d6d6", edgecolor="#a3403a", label="RVR layer"),
        mpatches.Patch(facecolor="#dff3df", edgecolor="#3a8a3f", label="Execute"),
        mpatches.Patch(facecolor="#fcdcdc", edgecolor="#a3403a", label="Re-prompt"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", frameon=False,
              ncol=2, bbox_to_anchor=(1.0, -0.05), fontsize=7.5)

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


def figure_scaling_curve_pretty(out: Path) -> None:
    """Refined scaling curve with annotations + per-arm peak markers."""
    sizes_billion = [0.6, 1.7, 4.0, 8.0, 14.0, 32.0]
    size_labels = ["0.6B", "1.7B", "4B", "8B", "14B", "32B"]
    pooled_pct = [0.0, 0.95, 1.33, 1.49, 1.87, 0.0]
    cp_upper_pct = [3.92, 2.97, 3.40, 3.37, 3.88, 1.34]
    bca_upper_pct = [None, 3.06, 6.76, 3.36, 9.46, None]
    peak_arm = [None, "near_name", "matched_random", "matched_random", "synonym", None]
    peak_pct = [None, 3.7, 5.4, 3.0, 7.2, None]

    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    x = np.arange(len(sizes_billion))

    # Pooled-rate line
    ax.plot(x, pooled_pct, "o-", color="#cc3333", linewidth=1.8, markersize=7,
            markerfacecolor="#cc3333", markeredgecolor="white",
            zorder=4, label="Qwen3 pooled TEHR (%)")

    # Per-size CP upper bound errorbar
    yerr = [[r - 0 for r in pooled_pct], [u - p for u, p in zip(cp_upper_pct, pooled_pct)]]
    ax.errorbar(x, pooled_pct, yerr=yerr, fmt="none", ecolor="#cc3333",
                alpha=0.5, capsize=3, elinewidth=0.9, zorder=3)

    # Anthropic upper bound shaded region
    anth_upper = 0.115
    ax.axhspan(0, anth_upper, color="#1f77b4", alpha=0.13, zorder=1,
                label=f"Anthropic 4.x C$_0$ 95\\% upper bound\n($\\leq\\!{anth_upper}\\%$, $N\\!=\\!2{{,}}599$)")

    # Per-size peak-arm annotations
    for xi, p, arm in zip(x, peak_pct, peak_arm):
        if p is not None:
            ax.scatter(xi, p, marker="^", s=55, color="#ffc107",
                        edgecolor="#aa7100", linewidth=1.0, zorder=5)
            ax.text(xi + 0.05, p + 0.15, arm, fontsize=7,
                    color="#604000", style="italic", rotation=0)

    # Sweet-spot annotation
    ax.annotate("capability\nsweet spot",
                xy=(4, 1.87), xytext=(2.3, 4.5),
                ha="center", fontsize=8, color="#770000", style="italic",
                arrowprops=dict(arrowstyle="-", color="#770000", lw=0.6, ls="--"))

    ax.set_xticks(x)
    ax.set_xticklabels(size_labels)
    ax.set_xlabel("Qwen3 model size (4-bit MLX)")
    ax.set_ylabel("TEHR (\\%) with 95\\% Clopper--Pearson UB")
    ax.set_title("Qwen3 family TEHR is non-monotone:\n"
                 "rises 0.6B$\\to$14B, returns to 0\\% at 32B")
    ax.set_ylim(-0.3, 5.5)
    ax.grid(alpha=0.3, linestyle="--", axis="y", zorder=0)
    ax.set_axisbelow(True)

    legend_handles = [
        plt.Line2D([0], [0], color="#cc3333", marker="o", linewidth=1.8,
                    label="Qwen3 pooled TEHR"),
        plt.Line2D([0], [0], color="#ffc107", marker="^", linewidth=0,
                    markersize=8, markeredgecolor="#aa7100",
                    label="per-size peak distractor arm"),
        mpatches.Patch(facecolor="#1f77b4", alpha=0.13,
                        label=f"Anthropic upper bound region"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", frameon=False, fontsize=7.5)

    fig.savefig(out, format="pdf")
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    figure_ablation_ladder(PAPER_FIG / "fig2_ablation_ladder.pdf")
    figure_rvr_architecture(PAPER_FIG / "fig3_rvr_architecture.pdf")
    figure_scaling_curve_pretty(PAPER_FIG / "fig1_scaling_curve.pdf")
    print("all figures written")


if __name__ == "__main__":
    main()
