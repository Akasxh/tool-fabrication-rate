# 12 actionable style rules for top-tier ML paper submissions

Distilled from official venue guides + community wisdom + recent
ICLR best-paper-award patterns.

1. **Lead with the surprise, not the setup.** First paragraph of
   abstract and intro must state the result and the "why this is
   unexpected" in one sentence. ICLR award-winners put the punchline
   in the title.
2. **State 3-4 contributions as a numbered list at end of intro.**
   Each bullet is one falsifiable claim, not a vague "we explore."
   (ICML/NeurIPS norm.)
3. **Every figure caption begins with a one-line takeaway in bold.**
   Then describe how to read it. Reviewers should grok the paper
   from figs+captions alone.
4. **Self-contained captions; no chartjunk.** Label axes, units,
   "higher is better" arrows, $n$, error-bar definition. Bold the
   winning row in tables.
5. **Pre-empt reviewer attacks with a Limitations section.**
   NeurIPS checklist mandates it; ICLR/ICML strongly encourage. List
   failure modes, sensitivity to seeds, dataset specificity. Honest >
   defensive.
6. **Ablations are non-negotiable.** Remove each component; show it
   matters. Add a learning-curve / parameter-sensitivity plot.
   "Bake-off only" papers get rejected.
7. **Report error bars and seeds.** Mean ± std over $\geq 3$ seeds for
   headline numbers; disclose compute (GPU-hours, $). NeurIPS
   desk-rejects papers that ignore this.
8. **Math earns its place.** Use formulas only when they clarify;
   replace with pseudocode or prose when possible. Goodfellow:
   "excessive math passes review but kills impact."
9. **Tell the story, don't IMRAD-march.** Order = problem → why prior
   work fails → key insight → method → evidence. Karpathy/Weng style:
   build intuition before formalism. Write the abstract last.
10. **No HARKing, no over-claiming.** Don't retrofit hypotheses to
    results. Match abstract claims exactly to evidence. Scope honestly
    ("on these 3 benchmarks" not "in general").
11. **Self-contained for adjacent reviewers.** Assume reviewer is
    smart but not in your sub-area. Define every symbol on first use;
    don't require reading your prior paper; cite published versions
    where they exist (not arXiv-only).
12. **Reproducibility is a section, not a footnote.** Include code
    link, hyperparameters, hardware, dataset version, seed list,
    training time. Fill the NeurIPS Paper Checklist verbatim — it
    doubles as a self-audit.

**Cross-cutting (Tufte):** Maximize data-ink ratio. Every line, color,
and number must do work. If you can delete it without losing meaning,
delete it.

## Sources

- ICML "Crafting Papers on ML" (Langley): https://icml.cc/Conferences/2002/craft.html
- NeurIPS Paper Checklist: https://neurips.cc/public/guides/PaperChecklist
- ICLR 2026 Author Guide: https://iclr.cc/Conferences/2026/AuthorGuide
- Awesome ML Conference Paper Writing Style Guide:
  https://github.com/smsnobin77/awesome-ML-conference-paper-writing-style-guide
- "How To Write A Research Paper In ML" (Grigoris):
  https://grigorisg9gr.github.io/machine%20learning/research%20paper/how-to-write-a-research-paper-in-machine-learning/
- "Writing More Successful ML Research Papers" (Aubreville)
- "Ten Simple Rules for Better Figures" (Rougier et al.)
- ICLR 2025 Outstanding Paper Awards announcement:
  https://blog.iclr.cc/2025/04/22/announcing-the-outstanding-paper-awards-at-iclr-2025/
- Lil'Log (Lilian Weng): https://lilianweng.github.io/
