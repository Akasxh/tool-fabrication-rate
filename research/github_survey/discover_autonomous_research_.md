# Discovery: Autonomous Research / Paper-Writing Agents

Cluster: "autonomous research / paper-writing agents" — systems that automate idea
generation, experiment running, manuscript drafting, and/or automated peer review.

Scope filter: repos NOT already in our known list (AI-Scientist, AI-Scientist-v2,
AgentLaboratory, paper-qa, storm, CycleReviewer, plus the eval/agent-framework set).
Preference: permissive license, active maintenance, high stars, direct utility to
either the paper's breadth narrative or the paper-revision skill + reviewer personas.

Surveyed: 2026-05-29. Star counts and metadata via GitHub API.

---

## Selected repos (6)

### 1. bytedance/deer-flow
- URL: https://github.com/bytedance/deer-flow
- Stars: ~69,900
- License: MIT
- Maintained: yes (pushed 2026-05; #1 GitHub Trending after v2 on 2026-02-28)
- Why it helps: Production-grade long-horizon "SuperAgent" harness (sub-agents,
  sandboxes, memory, skills) that researches + codes + writes. A strong, battle-tested
  reference architecture for the autonomous-research orchestration our 0-autoresearch
  skill and harness emulate; useful as a related-work cite for end-to-end research agents.

### 2. langchain-ai/open_deep_research
- URL: https://github.com/langchain-ai/open_deep_research
- Stars: ~11,500
- License: MIT
- Maintained: yes (pushed 2026-05)
- Why it helps: Clean, configurable open deep-research agent (multi-provider, MCP-aware)
  for literature review and cited report synthesis — directly reusable scaffolding for
  the related-work / survey stage of our paper-writing skill.

### 3. HKUDS/AI-Researcher
- URL: https://github.com/HKUDS/AI-Researcher
- Stars: ~5,400
- License: NONE declared (caveat — treat code as all-rights-reserved; cite the paper,
  do not vendor code without clearing licensing)
- Maintained: yes (pushed 2025-10); NeurIPS 2025 "Autonomous Scientific Innovation"
- Why it helps: End-to-end concept-to-publication system with a dedicated Writer Agent
  that integrates idea, method, and validation results into a full draft — a key
  recent baseline/related-work peer for our autonomous-research framing and a model
  for the paper-revision skill's drafting pipeline.

### 4. SkyworkAI/DeepResearchAgent
- URL: https://github.com/SkyworkAI/DeepResearchAgent
- Stars: ~3,400
- License: MIT
- Maintained: yes (pushed 2026-05)
- Why it helps: Hierarchical planner + specialized sub-agents for task decomposition;
  a permissively-licensed template for the reviewer-persona / multi-specialist
  orchestration we want (planner steering domain reviewers), and reusable in-harness.

### 5. IntologyAI/Zochi
- URL: https://github.com/IntologyAI/Zochi
- Stars: ~310
- License: MIT
- Maintained: pushed 2025-11
- Why it helps: "Artificial scientist" with peer-reviewed acceptances (ICLR 2025
  workshops, ACL 2025 main / A*), scoring 7.67 on NeurIPS guidelines — a credible,
  permissively-licensed comparator that strengthens our main-track breadth claim and
  informs the reviewer-persona scoring rubric.

### 6. Ahren09/AgentReview
- URL: https://github.com/Ahren09/AgentReview
- Stars: ~115
- License: Apache-2.0
- Maintained: yes (pushed 2026-05); EMNLP 2024 Main, Oral
- Why it helps: First LLM-agent peer-review simulation — five-phase pipeline with
  reviewer/author/area-chair roles and configurable latent traits. Directly upgrades
  our reviewer-personas skill (trait-conditioned reviewers, AC meta-review) with a
  cited, permissively-licensed design to borrow from.

---

## Strong runners-up (not selected, for reference)
- aiming-lab/AutoResearchClaw — ~12,965 stars, MIT, very active; idea-to-paper with
  anti-hallucination claim verification (overlaps thematically with deer-flow pick;
  worth a second look for the claim-verification module specifically).
- AReviewers/AgentReviewers — ICML 2025, multimodal reviewers w/ shared memory, but
  only ~5 stars and no license declared (skip until matured / licensed).
- du-nlp-lab/MLR-Copilot — ~68 stars, autonomous ML research (IdeaAgent + ExperimentAgent),
  relevant but low traction and no license.
- openags/Auto-Research — ~284 stars, MIT, generalist AI-scientist with UI.
- JinheonBaek/ResearchAgent — NAACL 2025 idea generation, ~38 stars, no license.

## Notes / caveats
- AI-Researcher has no license file: cite the NeurIPS paper as related work; do not
  copy code into our harness without resolving licensing.
- For code reuse in harness/skills, prefer the MIT/Apache picks: deer-flow,
  open_deep_research, DeepResearchAgent (all MIT), and AgentReview (Apache-2.0).
- AgentReview is the highest-leverage pick for the reviewer-personas skill upgrade
  despite modest stars, because it is the canonical, permissively-licensed,
  peer-reviewed design for trait-conditioned LLM review.
