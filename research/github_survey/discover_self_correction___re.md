# Cluster discovery: self-correction / reflection methods

Goal: find the most popular / useful GitHub repos in the "self-correction / reflection" cluster
that are NOT already in our known list, to broaden baselines/related-work for the TEHR + RVR paper
(RVR = re-prompt with the tool registry on a bad tool call) and to inform the paper-revision skill +
reviewer personas. Prefer permissive licenses, active maintenance, high stars.

Excluded (already known): gorilla-BFCL, tau-bench, ToolBench, API-Bank, MetaTool, StableToolBench,
ToolBeHonest, ToolSandbox, AgentBench, ToolEmu, AppWorld, RestGPT, NexusRaven, Seal-Tools, ToolACE,
lm-evaluation-harness, inspect_ai, deepeval, helm, openai-evals, promptfoo, outlines, guidance,
lm-format-enforcer, instructor, jsonformer, langgraph, autogen, crewAI, dspy, letta, smolagents,
AutoGPT, reflexion, AI-Scientist, AI-Scientist-v2, paper-qa, AgentLaboratory, storm, CycleReviewer.

Stars/license/last-push verified via GitHub API (gh CLI) on 2026-05-29.

## Top 6 (new) repos

### 1. CRITIC — microsoft/ProphetNet (CRITIC subdir)
- URL: https://github.com/microsoft/ProphetNet/tree/master/CRITIC
- Stars: ~745 (parent ProphetNet repo) | License: MIT | Last push: 2024-07 (stable)
- Why it helps: The closest published analogue to RVR. CRITIC = "LLMs Can Self-Correct with
  Tool-Interactive Critiquing" (ICLR'24): the model verifies its output against an external tool,
  gets feedback, then revises. Our RVR (re-prompt with the tool registry after a bad call) is
  exactly tool-interactive critiquing specialized to tool-existence errors — cite CRITIC as the
  generic method we instantiate, and contrast intrinsic vs. tool-grounded correction.

### 2. Self-Refine — madaan/self-refine
- URL: https://github.com/madaan/self-refine
- Stars: ~804 | License: Apache-2.0 | Last push: 2024-10 (stable)
- Why it helps: Canonical *intrinsic* (no external feedback) self-correction baseline. Lets us draw
  the key paper distinction: intrinsic reflection (Self-Refine) vs. grounded reflection (RVR with the
  registry). Useful as a cheap, no-tool baseline that should NOT fix tool-existence hallucinations,
  motivating why registry grounding is needed.

### 3. TextGrad — zou-group/textgrad
- URL: https://github.com/zou-group/textgrad
- Stars: ~3,575 | License: MIT | Last push: 2025-07 (active)
- Why it helps: Highest-star recent self-correction framework — "textual gradients" backpropagate
  natural-language feedback to revise outputs. Strong, well-maintained baseline/related-work entry,
  and a candidate harness component for an automated feedback-driven correction loop in our skill.

### 4. ToRA — microsoft/ToRA
- URL: https://github.com/microsoft/ToRA
- Stars: ~1,117 | License: MIT | Last push: 2024-02 (stable)
- Why it helps: Tool-integrated reasoning agent that interleaves tool calls with rationale and
  *rectifies* outputs using tool/execution feedback. Relevant tool-use family member that shows the
  "execute → observe → correct" loop on a different task (math), broadening the baseline set beyond
  pure QA toward our tool-calling setting.

### 5. FacTool — GAIR-NLP/factool
- URL: https://github.com/GAIR-NLP/factool
- Stars: ~929 | License: Apache-2.0 | Last push: 2024-08 (stable)
- Why it helps: Tool-augmented factuality/hallucination *detection* across tasks. The detector
  pattern (tool-grounded claim verification) parallels how we detect tool-existence hallucinations;
  good related work on hallucination measurement and a template for a detect-then-correct stage.

### 6. SelfCheckGPT — potsawee/selfcheckgpt
- URL: https://github.com/potsawee/selfcheckgpt
- Stars: ~615 | License: MIT | Last push: 2024-06 (stable)
- Why it helps: Widely-cited zero-resource, black-box hallucination detection via self-consistency.
  Cheap baseline detector for our TEHR metric framing and a reviewer-anticipation citation ("did you
  compare against consistency-based detection?"). Pairs with FacTool to cover detection breadth.

## Notes / runners-up considered
- noahshinn/reflexion (3.2k, MIT) — excluded (already in known list).
- All-Hands-AI/OpenHands (~75k, MIT-ish/NOASSERTION) — coding agent, only tangential to self-correction;
  license is non-standard (NOASSERTION).
- OpenBMB/AgentVerse (~5k, Apache-2.0) — multi-agent framework, weaker fit to the correction cluster.
- princeton-nlp/intercode (248, MIT) — interactive-coding feedback loops; lower stars, kept as backup.
- RUCAIBox/HaluEval (585, MIT) — hallucination benchmark; overlaps FacTool/SelfCheckGPT detection theme.

## Selection rationale
Prioritized (a) direct conceptual overlap with RVR/tool-grounded correction (CRITIC, ToRA),
(b) the intrinsic-vs-grounded contrast our paper needs (Self-Refine, TextGrad), and
(c) hallucination-detection baselines reviewers will expect (FacTool, SelfCheckGPT). All six are
permissively licensed (MIT/Apache-2.0) and either actively maintained or stable reference implementations.
