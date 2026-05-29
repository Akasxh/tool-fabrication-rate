# §2 Related Work — Source Notes (Phase 0)

Compiled 2026-04-27. All sources accessed via WebFetch / WebSearch. Notes are
quotation-faithful; quotes preserved verbatim where used.

---

## S1. Czapla — "The Unauthorized Tool Call Problem" (Answer.AI blog)

- **Author/venue**: Piotr Czapla, Answer.AI blog post.
- **URL**: https://www.answer.ai/posts/2026-01-20-toolcalling.html
- **Date**: 2026-01-20 (canonical date per URL slug; v3.1 §9 checklist locks single-date convention).
- **Summary**: An industry post documenting that frontier-tier LLMs invoke
  tools that were never declared. Czapla reproduces the behavior on Claude,
  Gemini, and Grok; frames it as a security risk because hallucinated tool
  names sometimes resolve against ambient functions in the runtime.
- **Verbatim quotes**:
  1. *"Claude 4.5 hallucinated access to a tool I hadn't given it yet... I've
     reproduced similar behavior with Gemini and Grok."*
  2. *"Your carefully architected LLM, designed to never mix tools with
     secrets, can hallucinate a new capability and if that function happens
     to exist in your environment, the call goes through."*
- **Why it matters**: Provides the cross-vendor industry observation that
  motivates TEHR. Names the failure across four labs, but does not quantify
  it on a benchmark or propose a recovery intervention.
- **Differentiation**: We formalize what Czapla describes anecdotally into a
  per-call metric (TEHR), measure it on BFCL-v4 + tau-bench across three
  capability tiers, and evaluate a training-free recovery (RVR).

---

## S2. L-ICL — Kumar & Cohen, "Localizing and Correcting Errors for
LLM-based Planners" (arXiv 2602.00276)

- **Authors**: Aditya Kumar, William W. Cohen.
- **Summary**: Introduces Localized In-Context Learning (L-ICL): identifies
  the first constraint violation in a plan trace and injects a minimal
  input/output example targeting that step. Tested on gridworld, mazes,
  Sokoban, BlocksWorld across multiple LLMs.
- **Verbatim quote**: *"On an 8x8 gridworld, L-ICL produces valid plans 89%
  of the time with only 60 training examples, compared to 59% for the best
  baseline."*
- **Why it matters**: This is the paper's anchor for the "minimal targeted
  intervention beats verbose context" shape. RVR follows the same shape:
  intervene precisely where the failure is detected, not earlier.
- **Differentiation**: L-ICL targets symbolic planners and uses curated
  example pairs as the corrective signal; RVR targets tool-using agents and
  uses the runtime registry list as the corrective signal. L-ICL pre-loads
  examples into the prompt; RVR is reactive at the message level.

---

## S3. Empirical Bug Study — Zhu et al., "An Empirical Study of Bugs in
Modern LLM Agent Frameworks" (arXiv 2602.21806)

- **Authors**: Xinxue Zhu, Jiacong Wu, Xiaoyu Zhang, Tianlin Li, Yanzhou Mu,
  Juan Zhai, Chao Shen, Chunrong Fang, Yang Liu.
- **Summary**: Mines 998 bug reports from CrewAI and LangChain; derives a
  taxonomy of 15 root causes and 7 symptoms across 5 lifecycle stages.
  "API misuse," "API incompatibility," and "Documentation Desync" are the
  three top root causes; the "Self-Action" stage carries the largest share.
- **Verbatim quote**: *"agent framework bugs mainly arise from 'API misuse',
  'API incompatibility', and 'Documentation Desync'."*
- **Why it matters**: Provides empirical grounding that tool/API-shaped
  failures dominate agent bug reports in the wild — i.e., the failure
  surface RVR addresses is not niche.
- **Differentiation**: Their study is a post-hoc taxonomy of human-filed
  bugs; we run a controlled benchmark probe and target a specific subclass
  of API misuse (calling tools that do not exist) with a measured
  intervention.

---

## S4. Engländer et al. — "Agents Explore but Agents Ignore: LLMs Lack
Environmental Curiosity" (arXiv 2604.17609)

- **Authors**: Leon Engländer, Sophia Althammer, Ahmet Üstün, Matthias
  Gallé, Tom Sherborne.
- **Summary**: Shows agents discover task-relevant solutions in their
  environment 79–81% of the time but only exploit them 37–50% of the time.
  In AppWorld, agents see a documented "complete-solution" command in >90%
  of trials but use it in <7%.
- **Verbatim quote**: *"agents use the environment to fetch expected
  information, but not to revise their strategy or maximally exploit useful
  stimuli."*
- **Why it matters**: Closest neighbor in the "agent perceives a signal
  but does not act on it" space. The paper's finding is the dual of ours:
  they show agents ignore information that *is* present in the
  environment; we show agents fabricate tools that are *not* present.
- **Differentiation**: Different failure class (under-exploitation of
  observed info vs. over-confident invocation of unobserved tools);
  Engländer characterizes, we intervene; their analysis is observational,
  ours is a paired causal test (C1 vs. C0.5). NOTE: the paper's published
  framing is "environmental curiosity deficit," not "first-hypothesis
  anchoring" — we will cite it under its own framing.

---

## S5. Fission-GRPO — Zhang et al., "Robust Tool Use via Fission-GRPO:
Learning to Recover from Execution Errors" (arXiv 2601.15625)

- **Authors**: Zhiwei Zhang et al. (9 authors total).
- **Summary**: An RL recipe (variant of GRPO) for teaching tool-using
  agents to recover from execution errors. Failed trajectories are
  "fissioned" with diagnostic feedback from a finetuned Error Simulator,
  and recovery rollouts are resampled on-policy. Reports a +5.7pp absolute
  error-recovery improvement and +4pp accuracy on BFCL-v4 multi-turn for
  Qwen3-8B.
- **Why it matters**: Direct contrast — a *training-time* fix for a
  related family of tool-use failures. Same benchmark (BFCL-v4 multi-turn).
- **Differentiation**: Training-time vs. inference-time; requires SFT of an
  error simulator and on-policy RL; we require neither — RVR is a
  message-level intervention deployable behind any black-box API. We can
  even apply RVR on top of a Fission-GRPO-trained model; the two are
  orthogonal.

---

## Status notes for §2 author

- All 5 sources accessed successfully.
- The Czapla post URL was not surfaced by initial search; located by
  fetching the Answer.AI post index. Quotes verified verbatim.
- Engländer paper exists and matches the "agents-ignore" theme but uses the
  term *environmental curiosity deficit* rather than *first-hypothesis
  anchoring*. §2 cites its actual framing; §1/§6 should follow suit.
- arXiv IDs above match what the WebFetch loaded; cross-verify before
  camera-ready.
