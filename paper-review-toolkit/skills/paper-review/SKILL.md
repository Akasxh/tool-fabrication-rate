---
name: paper-review
description: Multi-persona structured peer review for ML/AI scientific papers. Spawns judges (hostile statistician, adversarial reviewer, production engineer) and advocates (workshop chair, industry practitioner, open-source champion), synthesizes findings into a fix list ranked by reviewer-rejection risk.
disable-model-invocation: true
---

# Paper-Review Skill

Use this skill when the user asks for a peer review of a scientific
paper (PDF, .tex sources, or repository).

## Inputs
- Path to paper (`.pdf` or `.tex` root file)
- Venue (e.g., NeurIPS, ICLR, ICML, SCALE)
- Round (first-pass / revision / pre-submission final)

## Process

### Round A — Judges (parallel, 4-6 agents)
Spawn judges that try hard to REJECT the paper. Each must end with
a concrete acceptance probability + the single killing objection.

Default judge roster (pick 4-6 based on paper type):
1. **Hostile statistician** — verifies every p-value, CI, and test
2. **Adversarial reviewer** — finds the worst three objections that
   would convince other reviewers to reject
3. **Production engineer** — checks deployability of the proposed
   method (only if paper claims production relevance)
4. **Tool-use literature expert** (or domain equivalent) — checks
   novelty vs. prior art
5. **Reproducibility skeptic** — audits whether the paper is
   reproducible from its supplementary alone
6. **Contamination researcher** — checks whether benchmark dates
   predate the models tested

### Round B — Advocates (parallel, 3 agents, AFTER fixes)
Spawn advocates that try to ACCEPT the paper. Each gives an
acceptance probability + the strongest reason to accept.

Default advocate roster:
1. **Workshop/conference strategist** — assesses fit + impact
2. **Industry practitioner** — would they cite it?
3. **Open-source champion** — is the artifact a real contribution?

### Round C — Meta (single agent, after Round B)
Brutally honest area chair gives the final pre-submit verdict and
the SINGLE most important final fix.

## Outputs
- `review_round_A.md` — judges' raw findings + cross-cutting fixes
- `review_round_B.md` — advocates' positive verdicts
- `review_round_C.md` — final AC verdict + single critical fix
- `review_synthesis.md` — ranked fix list

## Reusable persona prompts
See `personas/` directory. Each persona is a self-contained Markdown
file with:
- The persona's role and biases
- Specific things they check
- Output format requirements
- Word limit (typically 250-600 words)

## Notes
- Never spawn more than ~8 agents in parallel — past that, signal
  starts repeating.
- Always include at least one adversarial reviewer and one advocate.
- The meta-review (Round C) is the most useful single artifact;
  if you only have time for one, run Round A's hostile statistician
  + Round C's brutally-honest AC.
