#!/usr/bin/env python
"""Regenerate the two BODY figures from the LOCKED numbers (self-contained).

The pre-built PDFs were stale: they baked in retired 'TEHR' labels, old counts
(5/268, N=2,599), a 1.87% peak, and literal '\\%' backslashes, all contradicting
the locked aggregator data and the adjacent tables. This writes clean, correct
vector PDFs: per-call Tool Fabrication Rate (TFR), plain '%', locked data only.

Run:  harness/.venv/bin/python scripts/regen_body_figures.py
Outputs (overwrite in place):
  paper/figures/fig1_scaling_curve.pdf    Qwen3 TFR vs model size (0/75 .. 6/366 .. 0/224)
  paper/figures/fig2_ablation_ladder.pdf  Qwen3-8B 4-condition ablation (1.46% -> 0)
"""
import os
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from scipy import stats

OUT = os.path.join(os.path.dirname(__file__), "..", "paper", "figures")

plt.rcParams.update({
    "font.size": 9, "font.family": "serif",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.8, "pdf.fonttype": 42,
})


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return 100 * lo, 100 * hi


# --- Figure 1: Qwen3 scaling curve (locked: 0/75,2/210,3/226,9/615,6/366,0/224) ---
sizes = [0.6, 1.7, 4, 8, 14, 32]
events = [0, 2, 3, 9, 6, 0]
ns = [75, 210, 226, 615, 366, 224]
rates = [100 * e / n for e, n in zip(events, ns)]
los, his = zip(*[cp(e, n) for e, n in zip(events, ns)])
yerr = [[r - lo for r, lo in zip(rates, los)], [hi - r for r, hi in zip(rates, his)]]

fig, ax = plt.subplots(figsize=(3.3, 2.5))
ax.errorbar(sizes, rates, yerr=yerr, fmt="o-", color="#b2182b", ecolor="#d6a0a6",
            elinewidth=1.0, capsize=2.5, markersize=5, markerfacecolor="#b2182b",
            markeredgecolor="white", zorder=3, lw=1.6)
ax.axhline(0.14, ls="--", color="#2166ac", lw=1.0, zorder=1)
ax.text(1.05, 0.21, "Anthropic 4.x $C_0$: 0/2,592, $\\leq$0.14%",
        color="#2166ac", fontsize=6.3, va="bottom")
for x, y, e, n in zip(sizes, rates, events, ns):
    ax.annotate("%d/%d" % (e, n), (x, y), textcoords="offset points",
                xytext=(0, 8), ha="center", fontsize=6.2, color="#333333")
ax.set_xscale("log")
ax.set_xticks(sizes)
ax.set_xticklabels([("%g" % s) for s in sizes])
ax.set_xlabel("Model size (B parameters)")
ax.set_ylabel("TFR (%)")
ax.set_ylim(-0.2, 4.0)
ax.set_xlim(0.5, 40)
ax.grid(axis="y", ls=":", lw=0.5, color="#cccccc", zorder=0)
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(OUT, "fig1_scaling_curve.pdf"))
plt.close(fig)

# --- Figure 2: Qwen3-8B 4-condition ablation (locked: 9/615,1/258,0/448,0/258) ---
conds = ["$C_0$\n(baseline)", "$C_{0.5}$\n(retry)", "$C_{0.7}$\n(no list)", "$C_1$\n(real list)"]
abl = [1.46, 0.39, 0.0, 0.0]
abl_lbl = ["9/615", "1/258", "0/448", "0/258"]
colors = ["#b2182b", "#ef8a62", "#92c5de", "#2166ac"]

fig, ax = plt.subplots(figsize=(3.3, 2.4))
ax.bar(range(len(conds)), abl, color=colors, width=0.62, edgecolor="white", zorder=3)
for i, (r, lab) in enumerate(zip(abl, abl_lbl)):
    ax.text(i, r + 0.05, lab, ha="center", va="bottom", fontsize=6.6, color="#333333")
ax.set_xticks(range(len(conds)))
ax.set_xticklabels(conds, fontsize=7.5)
ax.set_ylabel("TFR (%)")
ax.set_ylim(0, 1.7)
ax.grid(axis="y", ls=":", lw=0.5, color="#cccccc", zorder=0)
fig.tight_layout(pad=0.4)
fig.savefig(os.path.join(OUT, "fig2_ablation_ladder.pdf"))
plt.close(fig)

print("Regenerated fig1_scaling_curve.pdf and fig2_ablation_ladder.pdf (TFR, plain %, locked data).")
