# Paper Review & Writing Toolkit

A curated collection of personas, skills, prompts, and scripts for
reviewing and writing scientific papers with LLM agents. Built from
research across GitHub, arXiv, OpenReview, and venue style guides.

## Quick start

```bash
# Use a persona on your paper:
cat personas/hostile_statistician.md | pbcopy
# Then paste into Claude with your paper attached

# Install as a Claude Code skill:
mkdir -p ~/.claude/skills/paper-review/
cp skills/paper-review/SKILL.md ~/.claude/skills/paper-review/

# Run a multi-agent review locally (requires API key):
python scripts/multi_agent_review.py --pdf my_paper.pdf
```

## Layout

```
personas/        25+ proven reviewer personas (judge + advocate)
skills/          Claude Code SKILL.md files ready to drop in
prompts/         Reusable prompt templates (intro polish, abstract trim, etc.)
checklists/      Venue-specific checklists (ICML, NeurIPS, ICLR)
scripts/         Python scripts for orchestration
```

See `INDEX.md` for the full catalog.
