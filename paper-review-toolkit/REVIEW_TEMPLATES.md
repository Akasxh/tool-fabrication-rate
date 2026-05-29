# Peer-review templates from real venues + best-known LLM-reviewer prompts

## Real venue review forms

### NeurIPS 2025
- URL: https://neurips.cc/Conferences/2025/ReviewerGuidelines
- Sections: Summary | Strengths & Weaknesses (Quality / Clarity /
  Significance / Originality) | Questions | Limitations
- Scores: Soundness 1-4 | Presentation 1-4 | Contribution 1-4 |
  **Overall 1-6** (Strong Reject → Strong Accept) | Confidence 1-5
- Mandatory: Limitations question, Ethical Concerns

### ICLR 2025
- URL: https://iclr.cc/Conferences/2025/ReviewerGuide
- Four anchor questions: (1) specific problem, (2) approach motivation
  and lit-placement, (3) claim support / scientific rigor,
  (4) significance
- Output: Strengths list, Weaknesses list, Questions, Recommendation +
  1-2 reasons, separate "suggestions to improve" not tied to decision

### ACL ARR (Feb 2025+)
- URL: http://aclrollingreview.org/reviewform
- **Headline scores: Soundness 1-5, Excitement 1-5, Overall 1-5**
  (Award / Main / Findings / Resubmit / Do-not-resubmit)
- Plus Confidence, Reproducibility, Datasets, Software, Author-Identity
- Notable: **decouples soundness from excitement** ("a paper can be
  main-conference worthy even if you're not excited")

### JMLR
- URL: https://jmlr.org/reviewer-guide.html
- No numeric scale; recommendation categories: accept / minor / major /
  reject. Lighter rubric: clarity & style, examples,
  contribution-statement, theoretical-vs-practical relevance.

## Open-source LLM reviewer prompts

### Reviewer2 (arXiv:2402.10886)
Two-stage Prompt-Generation-Evaluation (PGE) → review:
- PGE: *"Analyzing the provided review, identify a set of questions
  that the reviewer is attempting to address regarding the paper
  without being too specific."*
- Evaluation: *"Evaluate the quality of the questions. Are the
  questions a good match to the candidate answer?"* (5-pt)
- Aspects are dynamically generated, NOT a fixed taxonomy.
- Repo: https://github.com/ZhaolinGao/Reviewer2

### MARG (arXiv:2401.04259)
Multi-agent: **Leader** (planner) + **Workers** (chunk-readers) +
3 **Experts**:
- *Experiments Expert*: "design high-quality experiments given the
  paper's main claims; use predictions as baseline."
- *Clarity Expert*: "be highly curious; ask questions to identify
  missing explanations or reproducibility details."
- *Impact Expert*: "be skeptical; ask questions to determine if the
  paper actually makes a significant contribution."
- Full prompts in Appendix A.1-A.4 of the PDF.
- Repo: https://github.com/allenai/marg-reviewer

### AI Scientist (Sakana)
- Reviewer: *"You are an AI researcher reviewing a paper for a
  prestigious ML venue. Be critical and cautious in your decision."*
- Area Chair: *"You are an Area Chair at a machine learning conference
  aggregating {reviewer_count} reviews..."*
- Output: structured 15-field JSON (Soundness, Originality, etc.)
  with reflection rounds.

## Most extractable templates for personas/

1. **NeurIPS 4-axis** (Quality / Clarity / Significance / Originality, 1-4)
   — clean dimensional scaffold
2. **ARR Soundness-vs-Excitement split** (1-5 each) — decouples
   correctness from enthusiasm
3. **MARG three-expert split** (Experiments / Clarity / Impact) —
   drop-in multi-persona prompts
4. **Reviewer2 PGE one-liner** — generator for paper-specific aspect
   questions
5. **ICLR 4-question anchor + strengths/weaknesses split** — minimal
   universal template

## Benchmark studies (quality of LLM reviewers)

- Liang et al. 2023 — Stanford. ~30-39% overlap with human reviewers
  on a single-prompt baseline. arXiv:2310.01783
- "When Your Reviewer is an LLM" — arXiv:2509.09912 — quantifies
  bias/divergence vs humans, prompt-injection risk
- TreeReview — arXiv:2506.07642 — dynamic question-tree extending Reviewer2
- Generative Reviewer Agents (EMNLP-Industry 2025) — scalable simulacra
  with per-axis sub-agents
