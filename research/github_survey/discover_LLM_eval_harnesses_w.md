# Discovery: LLM eval harnesses with tool-use support

Query: "LLM eval harnesses with tool-use support" — repos NOT in our known list, prioritizing
permissive license + active maintenance + high stars + relevance to TEHR / RVR / ICML breadth.

Metadata captured via GitHub API on 2026-05-29 (stars approximate).

## Top picks (up to 6)

### 1. sierra-research/tau2-bench
- URL: https://github.com/sierra-research/tau2-bench
- Stars: ~1.3k (1,259)
- License: MIT (permissive)
- Maintenance: very active (pushed 2026-05-28)
- Why it helps: The v2 successor to tau-bench (our known list has the original tau-bench).
  Adds dual-control (agent + simulated user both act), new domains (telecom, retail, airline,
  plus 2026 voice/knowledge-retrieval domains), and policy-adherence scoring. A natural
  multi-turn tool-use benchmark to add for main-track breadth alongside BFCL, and the
  agent-user dynamic gives more chances to surface tool-existence hallucinations.

### 2. ethz-spylab/agentdojo
- URL: https://github.com/ethz-spylab/agentdojo
- Stars: ~585
- License: MIT (permissive)
- Maintenance: active (pushed 2026-03-30)
- Why it helps: Dynamic tool-using-agent environment with 97 realistic tasks + 629 security
  test cases over untrusted tool outputs (NeurIPS'24). Its clean Python task/tool registry maps
  directly onto our harness/bench_loaders pattern, and the untrusted-data setting is a strong
  stress test for TEHR (does the model invent tools when injected data references nonexistent
  ones?) plus a venue for evaluating RVR's re-prompt-with-registry intervention.

### 3. harbor-framework/terminal-bench
- URL: https://github.com/harbor-framework/terminal-bench
- Stars: ~2.3k (2,292)
- License: Apache-2.0 (permissive)
- Maintenance: very active (under continued development; terminal-bench-2/-3 also live)
- Why it helps: Widely-cited terminal-agent benchmark where the model issues real shell
  "tools." Adds a different tool-use modality (open-ended command invocation vs. structured
  function calling) for main-track breadth, and is a realistic setting to measure whether models
  hallucinate non-existent commands/flags — a shell analogue of TEHR.

### 4. comet-ml/opik
- URL: https://github.com/comet-ml/opik
- Stars: ~19.4k
- License: Apache-2.0 (permissive)
- Maintenance: very active (pushed 2026-05-29)
- Why it helps: Production-grade open eval + tracing platform with built-in metrics for agentic
  workflows and tool-call correctness. Useful as scaffolding for the paper-revision/reviewer
  skill upgrade and for logging/scoring multi-turn tool-call traces (hallucinated-tool
  detection, RVR before/after) without writing our own harness plumbing.

### 5. confident-ai/deepeval  — NOTE: already adjacent to known list
> deepeval IS in our known list; replaced below. Kept only for traceability, not counted.

### 5. openai/simple-evals
- URL: https://github.com/openai/simple-evals
- Stars: ~4.5k (4,505)
- License: MIT (permissive)
- Maintenance: active (pushed 2026-04-22)
- Why it helps: Distinct from openai-evals (which is in our known list) — a lightweight,
  reference reproducible eval runner OpenAI uses for its own model-card numbers (incl.
  tool-use / agentic evals). Minimal, hackable harness we can fork to add a TEHR metric and
  report apples-to-apples baseline numbers reviewers trust.

### 6. explodinggradients/ragas
- URL: https://github.com/explodinggradients/ragas
- Stars: ~14k
- License: Apache-2.0 (permissive)
- Maintenance: active
- Why it helps: Beyond RAG, now ships agentic-workflow and tool-call metrics (tool-call
  accuracy, agent goal accuracy) with an LLM-as-judge backbone. Good source of ready-made
  tool-use scoring functions and a citable comparison point for our per-call TEHR metric.

## Honorable mentions / deprioritized
- Arize-ai/phoenix (~9.9k): great agent/tool-call observability + eval, but license is
  Elastic-style (NOASSERTION, not OSI-permissive) — deprioritized on the permissive-license
  preference.
- THUDM/AgentBench (~3.5k, Apache-2.0): already in known list.
- SalesforceAIResearch/xLAM (~621, Apache-2.0): action-model training/eval; more model-family
  than eval-harness.

## Sources
- https://github.com/sierra-research/tau2-bench
- https://github.com/ethz-spylab/agentdojo
- https://github.com/harbor-framework/terminal-bench
- https://github.com/comet-ml/opik
- https://github.com/openai/simple-evals
- https://github.com/explodinggradients/ragas
- https://github.com/philschmid/ai-agent-benchmark-compendium (survey input)
- https://www.evidentlyai.com/blog/ai-agent-benchmarks (survey input)
