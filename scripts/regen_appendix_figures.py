#!/usr/bin/env python
"""Generate supplementary APPENDIX figures from the LOCKED numbers.

The appendix has no page-limit pressure, so we add visual summaries of data
that otherwise lives only in tables/prose. Every number here is the locked
aggregator value (see paper); labels use TFR and plain '%'.

Run:  harness/.venv/bin/python scripts/regen_appendix_figures.py
Outputs (vector PDF) to paper/figures/:
  figA_commercial_open.pdf   commercial-vs-open TFR gap (the headline)
  figB_severity.pdf          what gets fabricated: state-changing vs read-only
  figC_qwen25_ablation.pdf   Qwen2.5 ablation ladder (powered mechanism)
  figD_controls.pdf          precision ladder + cross-family controls
"""
import os
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from scipy import stats

OUT = os.path.join(os.path.dirname(__file__), "..", "paper", "figures")
plt.rcParams.update({
    "font.size": 8.5, "font.family": "serif",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "pdf.fonttype": 42,
})
BLUE, RED, ORANGE, GREY = "#2166ac", "#b2182b", "#ef8a62", "#888888"


def cp_hi(k, n):
    return 100.0 * (1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k))


# ---- Figure A: commercial vs open TFR (the headline gap) ----
rows = [  # (label, events, N, is_commercial)
    ("Anthropic 4.x", 0, 2592, True),
    ("OpenAI gpt-4.x/4o", 0, 2117, True),
    ("OpenAI gpt-5 gen.", 0, 1311, True),
    ("Llama-3.1-8B", 5, 400, False),
    ("Qwen3-8B", 9, 615, False),
    ("Qwen3-14B", 6, 366, False),
    ("Qwen2.5-7B", 28, 459, False),
]
labels = [r[0] for r in rows]
rates = [100.0 * r[1] / r[2] for r in rows]
errs = [cp_hi(r[1], r[2]) - 100.0 * r[1] / r[2] for r in rows]
colors = [BLUE if r[3] else RED for r in rows]
counts = ["%d/%d" % (r[1], r[2]) for r in rows]

fig, ax = plt.subplots(figsize=(4.2, 2.7))
y = range(len(rows))
ax.barh(list(y), rates, xerr=[[0] * len(rows), errs], color=colors, height=0.62,
        edgecolor="white", error_kw=dict(elinewidth=0.8, capsize=2, ecolor="#555"))
for i, (r, c) in enumerate(zip(rates, counts)):
    ax.text(max(r, 0) + 0.12 + errs[i], i, c, va="center", fontsize=6.6, color="#333")
ax.set_yticks(list(y))
ax.set_yticklabels(labels, fontsize=7.6)
ax.invert_yaxis()
ax.set_xlabel("TFR (%) on the target-removed probe ($C_0$)")
ax.set_xlim(0, 9)
ax.axvline(0.14, ls=":", color=BLUE, lw=0.8)
ax.text(6.2, len(rows) - 1.4, "worst per-arm:\n10.4% (Qwen2.5)", fontsize=6.3,
        color=RED, ha="left", va="center")
ax.text(0.02, 0.98, "commercial", color=BLUE, fontsize=7, transform=ax.transAxes, va="top")
ax.text(0.02, 0.62, "open-weight", color=RED, fontsize=7, transform=ax.transAxes, va="top")
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(OUT, "figA_commercial_open.pdf"))
plt.close(fig)

# ---- Figure B: severity composition of the 53 open-weight fabrications ----
fig, ax = plt.subplots(figsize=(4.2, 1.5))
ax.barh([0], [11], color=RED, height=0.5, edgecolor="white", label="irreversible txn (11)")
ax.barh([0], [26], left=[11], color=ORANGE, height=0.5, edgecolor="white", label="other state-changing (26)")
ax.barh([0], [16], left=[37], color=GREY, height=0.5, edgecolor="white", label="read-only (16)")
ax.text(5.5, 0, "11", ha="center", va="center", color="white", fontsize=8, fontweight="bold")
ax.text(24, 0, "26", ha="center", va="center", color="white", fontsize=8, fontweight="bold")
ax.text(45, 0, "16", ha="center", va="center", color="white", fontsize=8, fontweight="bold")
ax.set_xlim(0, 53)
ax.set_ylim(-0.6, 0.6)
ax.set_yticks([])
ax.set_xlabel("Open-weight fabrication events (53 total); 37 (70%) are state-changing")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.55), ncol=3, frameon=False, fontsize=6.4)
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(OUT, "figB_severity.pdf"))
plt.close(fig)

# ---- Figure C: Qwen2.5 ablation ladder (powered mechanism) ----
conds = ["$C_0$\nbaseline", "$C_{0.5}$\nretry", "$C_{0.7}$\nno list", "$C_{0.8}$\nwrong list", "$C_1$\nreal list"]
rates_c = [6.10, 1.71, 0.97, 0.25, 0.31]
labels_c = ["28/459", "7/410", "4/412", "1/405", "1/320"]
cols_c = [RED, ORANGE, "#92c5de", "#67a9cf", BLUE]
fig, ax = plt.subplots(figsize=(4.2, 2.4))
ax.bar(range(5), rates_c, color=cols_c, width=0.64, edgecolor="white", zorder=3)
for i, (r, l) in enumerate(zip(rates_c, labels_c)):
    ax.text(i, r + 0.1, l, ha="center", va="bottom", fontsize=6.6, color="#333")
ax.set_xticks(range(5))
ax.set_xticklabels(conds, fontsize=7)
ax.set_ylabel("TFR (%)")
ax.set_ylim(0, 6.8)
ax.grid(axis="y", ls=":", lw=0.5, color="#ccc", zorder=0)
ax.text(2.5, 5.2, "a wrong list ($C_{0.8}$) recovers\nas well as the real one ($C_1$): $p=1.0$",
        fontsize=6.4, ha="center", color="#333")
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(OUT, "figC_qwen25_ablation.pdf"))
plt.close(fig)

# ---- Figure D: precision ladder + cross-family controls ----
fig, (a1, a2) = plt.subplots(1, 2, figsize=(4.6, 2.2))
# precision
pr = [1.44, 0.46, 0.63]
pl = ["9/623", "2/435", "2/316"]
a1.bar(range(3), pr, color=["#b2182b", "#ef8a62", "#fddbc7"], width=0.62, edgecolor="white", zorder=3)
for i, (r, l) in enumerate(zip(pr, pl)):
    a1.text(i, r + 0.04, l, ha="center", va="bottom", fontsize=6.2, color="#333")
a1.set_xticks(range(3)); a1.set_xticklabels(["4-bit", "8-bit", "bf16"], fontsize=7)
a1.set_ylabel("TFR (%)"); a1.set_ylim(0, 2.0)
a1.set_title("Qwen3-8B precision", fontsize=7.5)
a1.grid(axis="y", ls=":", lw=0.5, color="#ccc", zorder=0)
# cross-family C0
cf = [1.46, 1.64, 1.25, 6.10]
cfl = ["9/615", "6/366", "5/400", "28/459"]
cfx = ["Qwen3-8B", "Qwen3-14B", "Llama-8B", "Qwen2.5-7B"]
a2.bar(range(4), cf, color=RED, width=0.62, edgecolor="white", zorder=3)
for i, (r, l) in enumerate(zip(cf, cfl)):
    a2.text(i, r + 0.12, l, ha="center", va="bottom", fontsize=6.0, color="#333")
a2.set_xticks(range(4)); a2.set_xticklabels(cfx, fontsize=6.3, rotation=20, ha="right")
a2.set_ylim(0, 7.0)
a2.set_title("Open lineages ($C_0$)", fontsize=7.5)
a2.grid(axis="y", ls=":", lw=0.5, color="#ccc", zorder=0)
fig.tight_layout(pad=0.5)
fig.savefig(os.path.join(OUT, "figD_controls.pdf"))
plt.close(fig)

print("Wrote figA_commercial_open, figB_severity, figC_qwen25_ablation, figD_controls (locked data, TFR, plain %).")
