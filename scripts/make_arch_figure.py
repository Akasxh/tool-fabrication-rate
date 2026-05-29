"""Clean architecture figure for RVR. Pure matplotlib, no TikZ.
Simple horizontal pipeline with explicit hit/miss branching.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D


PAPER_FIG = Path("paper/figures")
PAPER_FIG.mkdir(parents=True, exist_ok=True)


def draw():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman", "Times New Roman", "DejaVu Serif"],
        "font.size": 10,
        "pdf.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.04,
    })

    fig, ax = plt.subplots(figsize=(6.8, 1.85))
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.2, 3.4)
    ax.axis("off")

    def box(x, y, w, h, label, fc, ec, fontsize=9):
        rect = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.06,rounding_size=0.10",
            facecolor=fc, edgecolor=ec, linewidth=1.0, zorder=3,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fontsize, zorder=4)

    def arrow(x1, y1, x2, y2, color="#222222", lw=1.0, style="->"):
        a = FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=12,
            color=color, lw=lw, zorder=2,
            shrinkA=0, shrinkB=0,
        )
        ax.add_patch(a)

    # Boxes: Agent -> proposed call -> membership check -> branch
    box_y = 1.4
    box_h = 0.85

    # 1. Agent
    box(0.3, box_y, 1.7, box_h, "Agent\n(LLM)",
        fc="#fef6dc", ec="#a87c1a", fontsize=9)

    # 2. Proposed call
    box(2.6, box_y, 2.0, box_h, "proposed call\n$c.\\mathrm{name}$",
        fc="#eeeeee", ec="#666666", fontsize=9)

    # 3. Membership check (the RVR layer)
    box(5.2, box_y, 2.5, box_h, "membership\n$c.\\mathrm{name} \\in \\mathcal{R}$?",
        fc="#fbe5e5", ec="#a83a3a", fontsize=9)

    # 4a. Hit -> Execute
    box(8.4, 2.45, 2.4, 0.85, "hit: \\textsc{execute}",
        fc="#dff3df", ec="#3a8a3f", fontsize=9)

    # 4b. Miss -> Re-prompt
    box(8.4, 0.35, 2.4, 0.85, "miss: re-prompt",
        fc="#fbe5e5", ec="#a83a3a", fontsize=9)

    # 5. Re-prompt content (after miss)
    box(11.3, 0.35, 2.5, 0.85,
        "\\texttt{tool\\_not\\_found}\n+ registry list",
        fc="#fbe5e5", ec="#a83a3a", fontsize=8.5)

    # Connecting arrows
    arrow(2.0, 1.82, 2.6, 1.82)               # agent -> call
    arrow(4.6, 1.82, 5.2, 1.82)               # call -> check
    # Branches from check
    arrow(7.7, 2.05, 8.4, 2.75, color="#3a8a3f")  # hit -> execute
    arrow(7.7, 1.55, 8.4, 0.85, color="#a83a3a")  # miss -> re-prompt
    arrow(10.8, 0.78, 11.3, 0.78, color="#a83a3a")  # re-prompt -> envelope

    # Branch labels
    ax.text(8.05, 2.42, "hit", fontsize=8.5, color="#3a8a3f", style="italic")
    ax.text(8.05, 1.18, "miss", fontsize=8.5, color="#a83a3a", style="italic")

    # Footer note (no overlapping arrows)
    ax.text(7.0, -0.05,
            "Membership check is in-process and $O(1)$. "
            "Bound: one re-prompt then \\textsc{abort}.",
            ha="center", fontsize=8.5, style="italic", color="#444444")

    fig.savefig(PAPER_FIG / "fig3_rvr_architecture.pdf", format="pdf")
    plt.close(fig)
    print(f"wrote {PAPER_FIG / 'fig3_rvr_architecture.pdf'}")


if __name__ == "__main__":
    draw()
