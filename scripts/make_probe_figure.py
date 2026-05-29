"""Distractor-probe schematic figure.
Shows the 4 distractor types with concrete examples.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

PAPER_FIG = Path("paper/figures")


def draw():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman", "Times New Roman", "DejaVu Serif"],
        "font.size": 9,
        "pdf.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
    })

    fig, ax = plt.subplots(figsize=(6.6, 2.3))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    def box(x, y, w, h, label, fc, ec, fontsize=8.5, mono=False):
        rect = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor=fc, edgecolor=ec, linewidth=0.7, zorder=2,
        )
        ax.add_patch(rect)
        if mono:
            ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                    fontsize=fontsize, family="monospace", zorder=3)
        else:
            ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                    fontsize=fontsize, zorder=3)

    # Original registry (left)
    ax.text(2.0, 4.05, "Original registry", ha="center", fontsize=9,
            fontweight="bold")
    box(0.4, 1.4, 3.2, 2.4, "", fc="#f5f5f5", ec="#999999")
    tools_orig = ["get\\_user", "list\\_users", "send\\_email", "create\\_event"]
    for i, t in enumerate(tools_orig):
        ax.text(2.0, 3.45 - 0.5 * i, t, ha="center", fontsize=8.5,
                family="monospace")
    # Highlight target
    ax.text(2.0, 3.45, "get\\_user", ha="center", fontsize=8.5,
            family="monospace", color="#a83a3a", fontweight="bold")
    ax.annotate("target", xy=(3.4, 3.45), xytext=(4.2, 3.45),
                fontsize=8, color="#a83a3a", style="italic", ha="left",
                arrowprops=dict(arrowstyle="-", color="#a83a3a", lw=0.6))

    # Arrow
    ax.annotate("", xy=(5.6, 2.6), xytext=(4.8, 2.6),
                arrowprops=dict(arrowstyle="->", color="#222222", lw=0.9))
    ax.text(5.2, 2.85, "remove target,", ha="center", fontsize=7.5,
            style="italic", color="#444444")
    ax.text(5.2, 2.45, "inject distractor", ha="center", fontsize=7.5,
            style="italic", color="#444444")

    # Four distractor variants (right)
    ax.text(9.1, 4.05, "Probe arms (one distractor per arm)",
            ha="center", fontsize=9, fontweight="bold")

    arms = [
        ("near\\_name", "get\\_users",        "#fbe5e5", "#a83a3a"),
        ("synonym",    "fetch\\_user",       "#fef0db", "#a87c1a"),
        ("matched\\_random", "tool\\_qzkx\\_v",  "#e7f0fb", "#1f4f7a"),
        ("unrelated",  "xyzzy\\_query",      "#e7f5e7", "#3a8a3f"),
    ]
    for i, (name, ex, fc, ec) in enumerate(arms):
        y = 3.3 - 0.85 * i
        box(5.9, y, 2.4, 0.65, name, fc=fc, ec=ec, fontsize=8.5)
        box(8.5, y, 4.0, 0.65, ex, fc="#ffffff", ec="#bbbbbb",
            fontsize=8.5, mono=True)

    fig.savefig(PAPER_FIG / "fig4_distractor_probe.pdf", format="pdf")
    plt.close(fig)
    print(f"wrote {PAPER_FIG / 'fig4_distractor_probe.pdf'}")


if __name__ == "__main__":
    draw()
