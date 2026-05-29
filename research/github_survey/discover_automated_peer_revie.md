# GitHub Survey: Automated Peer-Review / Reviewer-Rubric Repos

Cluster: automated peer-review / reviewer-rubric repos.
Excludes all repos in the known list (gorilla-BFCL, tau-bench, ToolBench, ..., CycleReviewer, etc.).
Selection bias: permissive license, active maintenance, high stars, direct relevance to our reviewer-persona / paper-revision skill and the RVR re-prompt theme.
Verified via `gh api repos/<r>` on 2026-05-29.

## Top 6

| # | Repo | Stars | License | Last push | Why it helps |
|---|------|-------|---------|-----------|--------------|
| 1 | [Weixin-Liang/LLM-scientific-feedback](https://github.com/Weixin-Liang/LLM-scientific-feedback) | ~531 | CC-BY-4.0 | 2024-01 | Large-scale empirical study + pipeline for LLM feedback on papers; the canonical baseline/citation for "can an LLM review a paper" — grounds our reviewer-persona claims and gives a ready review-generation pipeline to adapt. |
| 2 | [Ahren09/AgentReview](https://github.com/Ahren09/AgentReview) | ~115 | Apache-2.0 | 2026-05 (active) | EMNLP'24 oral; first multi-agent peer-review *simulation* (reviewer/author/AC roles with configurable latent traits). Directly upgradable into our reviewer-persona set; permissive + actively maintained. |
| 3 | [allenai/marg-reviewer](https://github.com/allenai/marg-reviewer) | ~64 | Apache-2.0 | 2026-03 (active) | MARG multi-agent review generation: distributes full paper text across specialized agents (experiments/clarity/impact). Template for specialized reviewer personas and full-text handling in our revision skill. |
| 4 | [microsoft/LLM-Rubric](https://github.com/microsoft/LLM-Rubric) | ~32 | MIT | 2026-03 (active) | ACL'24 calibrated multi-dimensional rubric scoring (LLM produces distributions per rubric question + calibration network). Gives a principled, calibrated rubric scorer for our reviewer rubric instead of raw scalar scores. |
| 5 | [ZhaolinGao/Reviewer2](https://github.com/ZhaolinGao/Reviewer2) | ~16 | Apache-2.0 | 2024-04 | Two-stage prompt-generation review framework (aspect-prompt model -> review model) + 27k-paper/99k-review aspect-annotated dataset. Aspect prompts map cleanly onto rubric dimensions; dataset useful for skill few-shots. |
| 6 | [EigenTom/ReviewGrounder](https://github.com/EigenTom/ReviewGrounder) | ~14 | none (no LICENSE file) | 2026-05 (active) | ACL'26 main: rubric-guided, *tool-integrated* multi-agent reviewer that grounds critiques in retrieved prior work — closest analogue to our RVR "re-prompt with registry on a bad call" loop. NOTE: no license; treat as design reference, not code to vendor, until license clarified. |

## Honorable mentions / not selected
- [PKU-YuanGroup/PiCO](https://github.com/PKU-YuanGroup/PiCO) (~36 stars, ICLR'25) — peer-review-among-LLMs via consistency optimization; highly relevant but **no license file**, so excluded from top picks on the permissive-license preference.
- [maxidl/openreviewer](https://github.com/maxidl/openreviewer) (~11 stars, no license) — Llama-OpenReviewer-8B fine-tuned on 79k reviews; strong critical-review model but low stars and no license.
- [UKPLab/arxiv2026-reviewfeedbackagent](https://github.com/UKPLab/arxiv2026-reviewfeedbackagent) (~2 stars, Apache-2.0) — "reviewing the reviewer" feedback agent; very fresh/low-star, watch for growth.

## Notes for our use
- Items 1-5 are permissively licensed (CC-BY/Apache/MIT) and safe to adapt for the paper-revision skill and reviewer personas.
- AgentReview (2) + MARG (3) are the best persona/multi-agent scaffolds; LLM-Rubric (4) is the best calibrated rubric scorer; ReviewGrounder (6) is the best conceptual match to RVR's tool-grounded re-prompt but is license-blocked for vendoring.
