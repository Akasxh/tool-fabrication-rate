# Top open-source LLM paper-review repositories

Curated 2026-04-29. Ranked by usefulness for setting up a review pipeline today.

## 1. SakanaAI/AI-Scientist
- **URL:** https://github.com/SakanaAI/AI-Scientist (13.4k★, active)
- **Why use it:** End-to-end paper generation **plus** a `perform_review.py`
  that mimics NeurIPS reviewing. Mature prompts, structured 15-field JSON
  output (Soundness, Originality, Significance, Quality, Clarity, etc.).
- **Notable persona:** *"You are an AI researcher reviewing a paper for
  a prestigious ML venue. Be critical and cautious in your decision."*
- **Bonus:** Built-in Area Chair meta-reviewer that aggregates N reviews.

## 2. SakanaAI/AI-Scientist-v2
- **URL:** https://github.com/SakanaAI/AI-Scientist-v2 (5.9k★, active)
- **Why:** Refined v1 with agentic tree search. ICLR-workshop validated.

## 3. deep-diver/paper-reviewer
- **URL:** https://github.com/deep-diver/paper-reviewer (831★)
- **Why:** Powers HuggingFace Daily Papers reviews. Two-script flow
  `collect.py --arxiv-id … && convert.py`. Easiest one-paper review today.

## 4. Weixin-Liang/LLM-scientific-feedback
- **URL:** https://github.com/Weixin-Liang/LLM-scientific-feedback (531★)
- **Why:** Nature-published GPT-4 feedback pipeline. ScienceBeam PDF parser
  + feedback server. ~30-40% overlap with human reviewers (baseline).

## 5. allenai/marg-reviewer
- **URL:** https://github.com/allenai/marg-reviewer (63★, active)
- **Why:** AllenAI's MARG-S — multi-agent: leader + workers + 3 experts
  (experiments / clarity / impact). Cuts generic comments from 60% to 29%.
  Best reference for multi-agent review architecture.

## 6. UKPLab/arxiv2026-reviewfeedbackagent
- **URL:** https://github.com/UKPLab/arxiv2026-reviewfeedbackagent (66★)
- **Why:** Freshest (2026-04-21). Neurosymbolic decomposition of reviews
  into argumentative segments. Best for **auditing review quality**.

## 7. ecnu-SEA/SEA
- **URL:** https://github.com/ecnu-SEA/SEA (89★)
- **Why:** Three modules (Standardization, Evaluation, Analysis) +
  SEA-E fine-tuned on standardized reviews. For training-time approaches.

## 8. Ahren09/AgentReview
- **URL:** https://github.com/Ahren09/AgentReview (112★)
- **Why:** EMNLP'24 simulator with 5 phases — Reviewer Assessment,
  Author-Reviewer Discussion, Reviewer-AC, Meta-Review, Decision.
  For **studying review dynamics and bias**, not one-shot.

## 9. ZhaolinGao/Reviewer2
- **URL:** https://github.com/ZhaolinGao/Reviewer2 (16★)
- **Why:** Two-stage aspect-prompt-then-review. Ships **27k papers / 99k
  reviews** dataset with aspects. Mostly useful as training data.

## 10. debashis1983/agentic-paper-review
- **URL:** https://github.com/debashis1983/agentic-paper-review
- **Why:** Reimplementation of Stanford's paperreview.ai
  (Yixing Jiang + Andrew Ng). Claims Spearman 0.74 vs human reviewers
  (trained on 46,748 ICLR reviews). Includes Claude Desktop MCP.
  **Note:** third-party clone; vet before relying.

## Quickstart recipe
Fork `AI-Scientist/perform_review.py` as the reviewer core (mature prompts,
NeurIPS-aligned JSON), layer MARG's specialist-agent decomposition for
long papers, and use `paper-reviewer` for the arXiv-ingest front end.
