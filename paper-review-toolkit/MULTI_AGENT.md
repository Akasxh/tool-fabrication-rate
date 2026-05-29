# Multi-agent peer-review research (2024–2026)

## Key papers

1. **MARG** (arXiv:2401.04259, D'Arcy et al.) — Leader + Workers +
   3 Experts (Experiments, Clarity, Impact). Chunked long-context
   handling via leader-worker delegation.
2. **Reviewer2** (arXiv:2402.10886) — Two-stage P(aspect|paper) then
   P(review|paper, aspect). Aspect prompts prevent mode collapse.
3. **Tan et al. 2406.05688** — Authors / Reviewers / Decision-Makers
   in long-context dialogue. ReviewMT dataset (26.8k papers, 92k reviews).
4. **AgentReview** (arXiv:2406.12708, EMNLP 2024) — Reviewer trait
   axes: Commitment, Intention, Knowledgeability. AC styles:
   Authoritarian / Conformist / Inclusive. Empirically isolates
   social, authority, anchoring, echo-chamber, groupthink biases.
5. **AI Scientist v2** (Sakana) — Three stages: diverse expert
   personas → critical peer review → final synthesis. Superhuman
   F1 (0.57 vs 0.49) on accept/reject.
6. **CycleResearcher / CycleReviewer** (arXiv:2411.00816, ICLR 2025) —
   Two-policy loop, RL-trained. 26.89% MAE reduction vs human reviewers
   on score prediction.
7. **DeepReview** (arXiv:2503.08569, ACL 2025) — Three reasoning stages:
   Novelty Verification → Multi-dimension Review → Reliability Verification.
   14B model beats CycleReviewer-70B by 44.8% Rating MSE.
8. **GAR — Generative Adversarial Reviews** (arXiv:2412.10415) —
   8-trait profile module: Strictness, Expertise, Focus, Evidence,
   Open-mindedness, Tone, Technical, Ethical.
9. **ReviewAgents** (arXiv:2503.08506) — 3 reviewer agents + AC,
   three-step pipeline (summarize → analyze → conclude).
10. **ReviewRL** (arXiv:2508.10308) and **LLM-REVal** (arXiv:2510.12367)
    — RL-trained reviewers and trust-calibration audits.

## Persona archetype library (cross-paper synthesis)

For a SCALE / NeurIPS-style multi-agent panel, draw from these 12 roles:

1. **Novelty / Impact reviewer** — skeptical of contributions
   (MARG, GAR, DeepReview)
2. **Methodology / Statistical-rigor reviewer** — evidence focus,
   evaluation design (MARG, GAR)
3. **Clarity / Presentation reviewer** — curious, asks questions about
   reproducibility (MARG)
4. **Adversarial / Strict critic** — high-strictness profile (GAR;
   AgentReview "malicious" axis)
5. **Supportive / Constructive reviewer** — benign intention (AgentReview)
6. **Ethics / Responsible-research reviewer** — ethical focus axis (GAR)
7. **Literature / Related-work reviewer** — retrieval-grounded novelty
   (DeepReview, ReviewAgents)
8. **Reliability / Evidence verifier** — claim-evidence cross-check
   (DeepReview)
9. **Reproducibility / Experiments expert** — hypothetical-experiment
   comparator (MARG)
10. **Domain specialist / Statistician** — analytical archetype
11. **Area Chair / Meta-reviewer** — synthesizer; sub-styles
    Authoritarian / Conformist / Inclusive (AgentReview, AI Scientist v2)
12. **Author-rebuttal agent** — dialogue counterpart (Tan et al.)
