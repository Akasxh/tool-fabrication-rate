# Paper Review & Writing Toolkit — Catalog

Built 2026-04-29. Curated from 8 deep parallel agents that scraped
GitHub repos, arXiv papers, venue review forms, official style guides,
and AI-detection literature.

## Catalog

| File | What |
|------|------|
| `README.md`                | Quick start |
| `INDEX.md` (this file)     | Master catalog |
| `REPOS.md`                 | Top 10 OSS repos for LLM paper review |
| `WRITING_TOOLS.md`         | Top OSS paper-writing agents (Sakana, AgentLab, AutoResearchClaw, ...) |
| `LATEX_TOOLS.md`           | LaTeX-aware editors / linters (Overleaf AI, Cursor + rules, checkcites) |
| `REVIEW_TEMPLATES.md`      | Real venue review forms + extracted templates (NeurIPS, ICLR, ARR, MARG, Reviewer2, AI Scientist) |
| `MULTI_AGENT.md`           | Multi-agent peer-review research papers + reusable persona archetype library |
| `STYLE_GUIDE.md`           | 12 actionable style rules from ICLR award-winners + Langley + Karpathy + NeurIPS Paper Checklist |
| `SUBMISSION_TOOLS.md`      | OpenReview API, arXiv anonymization, anonymous.4open.science, citation-graph, viz tools |
| `AI_SCRUB.md`              | Banned-word list + em-dash sed + detector-bypass tools (humanizers, adversarial paraphrasing) |

## Personas (drop-in reviewer prompts)

| File | Role | Origin |
|------|------|--------|
| `personas/01_hostile_statistician.md`        | Stats-rigor judge          | tried-and-true |
| `personas/02_adversarial_reviewer.md`        | Worst-case judge           | from review research |
| `personas/03_marg_experiments_expert.md`     | Experiments judge          | MARG (arXiv:2401.04259) |
| `personas/04_marg_clarity_expert.md`         | Clarity judge              | MARG |
| `personas/05_marg_impact_expert.md`          | Significance judge         | MARG |
| `personas/06_workshop_strategist.md`         | Acceptance-prob advocate   | venue-aware |
| `personas/07_industry_practitioner.md`       | Would-cite advocate        | industry-aware |
| `personas/08_open_source_champion.md`        | Artifact-quality advocate  | OSS-aware |
| `personas/09_brutally_honest_AC.md`          | Final meta-review          | meta |
| `personas/10_reproducibility_skeptic.md`     | Reproducibility judge      | reproducibility-crisis |
| `personas/11_contamination_researcher.md`    | Data-leakage judge         | Magar & Schwartz line |
| `personas/12_three_line_skim.md`             | Title + abstract reader    | senior-AC simulation |

## Skills

| File | What |
|------|------|
| `skills/paper-review/SKILL.md` | Claude Code skill for orchestrated multi-persona review |

## How to use this toolkit

### Quick review of a paper
1. Read `STYLE_GUIDE.md` — make sure your draft follows the 12 rules
2. Run `AI_SCRUB.md` `sed` one-liner to fix em-dashes and smart quotes
3. Grep for the banned words; rewrite each hit
4. Pick 4-6 personas from `personas/` and run them in parallel against
   your paper
5. Apply fixes from cross-cutting concerns
6. Re-run with 3 advocate personas (06, 07, 08)
7. Final pass with the brutally-honest AC (09)

### Drop into Claude Code as a skill
```bash
mkdir -p ~/.claude/skills/paper-review/
cp skills/paper-review/SKILL.md ~/.claude/skills/paper-review/
# Then invoke with /paper-review in Claude Code
```

### Submit-day pipeline (deadline triage)
1. `arxiv-latex-cleaner` on the source
2. `exiftool + qpdf` on the compiled PDF
3. `rebiber` on the .bib
4. `checkcites && chktex && refcheck` for LaTeX hygiene
5. Push code to anonymous.4open.science
6. `openreview-py` script to verify upload + anonymization

## Key external resources

- **MARG** — multi-agent review architecture: https://github.com/allenai/marg-reviewer
- **AI Scientist v2** (Sakana) — perform_review.py + perform_writeup.py:
  https://github.com/SakanaAI/AI-Scientist-v2
- **Orchestra-Research/AI-Research-SKILLs** — `20-ml-paper-writing` is
  a drop-in Claude Code skill: https://github.com/Orchestra-Research/AI-Research-SKILLs
- **NeurIPS Paper Checklist** — fill it verbatim:
  https://neurips.cc/public/guides/PaperChecklist
- **anonymous.4open.science** — anonymous code mirror for double-blind:
  https://anonymous.4open.science/
- **Wikipedia: Signs of AI writing** — best free AI-tell checklist:
  https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
