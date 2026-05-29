# GitHub Survey: Agent frameworks and how they handle tool-not-found errors

Query: "agent frameworks and how they handle tool-not-found errors"
Date: 2026-05-29
Constraint: exclude repos already in the known list (BFCL, tau-bench, ToolBench, etc.).
Goal: feed MAIN-TRACK ICML breadth (more frameworks/baselines/families) for the
TEHR (Tool-Existence Hallucination Rate) paper and upgrade the paper-revision skill /
reviewer personas. Prefer permissive license, active maintenance, high stars.

Star counts and licenses verified via `gh api` on 2026-05-29.

## Top 6

### 1. pydantic/pydantic-ai
- URL: https://github.com/pydantic/pydantic-ai
- Stars: ~17.4k
- License: MIT
- Why it helps: First-class `ModelRetry` exception + typed tool registry — the canonical
  reference implementation of the exact RVR loop our paper proposes (re-prompt the model
  with the tool schema when it emits a bad/nonexistent call). Strongest existing-art
  baseline to position RVR against.

### 2. openai/openai-agents-python
- URL: https://github.com/openai/openai-agents-python
- Stars: ~26.7k
- License: MIT
- Why it helps: Highest-star production agent SDK with a documented, reproducible
  "tool not found after handoff" failure mode (issue #1671) — a real-world instance of
  tool-existence hallucination we can cite and harness as an additional model/runtime row.

### 3. microsoft/agent-framework
- URL: https://github.com/microsoft/agent-framework
- Stars: ~10.8k
- License: MIT
- Why it helps: Multi-turn tool-call failures and "Tool not found" exceptions are
  tracked openly (issues #3304, #5941) across both Responses and Chat Completions APIs;
  gives us a second major-vendor framework exhibiting TEHR-style errors for breadth.

### 4. google/adk-python
- URL: https://github.com/google/adk-python
- Stars: ~19.9k
- License: Apache-2.0
- Why it helps: Google's code-first agent toolkit ships a built-in evaluation module,
  so we can wire a Gemini family into our harness/bench_loaders and add a third vendor
  family (beyond Anthropic 4.x and Qwen3) for cross-family TEHR coverage.

### 5. zai-org/ComplexFuncBench
- URL: https://github.com/zai-org/ComplexFuncBench
- Stars: ~180
- License: none stated (treat as all-rights-reserved; email authors before redistribution)
- Why it helps: 1,000 multi-step / constrained function-calling samples in long context —
  a harder benchmark than BFCL multi-turn to measure whether TEHR rises with call
  complexity. A new bench_loader target broadening the benchmark axis.

### 6. IBM/NESTFUL
- URL: https://github.com/IBM/NESTFUL
- Stars: ~19
- License: Apache-2.0
- Why it helps: Nested-API-call benchmark (Apache-2.0, freely redistributable) where a
  hallucinated/missing inner tool cascades — an ideal stress test for measuring TEHR and
  RVR recovery under call nesting. Low stars but permissive and directly on-topic.

## Notable runners-up (not selected)
- Upsonic/Upsonic (~7.9k, MIT) — reliability-focused agent framework; less explicit
  tool-not-found semantics than pydantic-ai.
- i-am-bee/beeai-framework (~3.3k, Apache-2.0) — production agents, Python+TS.
- MadeAgents/Hammer (~119, Apache-2.0) — function masking to reduce miscalls; a
  mitigation baseline alternative to RVR but low adoption.
- facebookresearch/HalluLens (~80, NOASSERTION) — textual (not tool) hallucination bench.
- quchangle1/LLM-Tool-Survey (~484, no license) — useful related-work mining for the
  paper-revision skill, not a runnable baseline.
- ComposioHQ/Composio-Function-Calling-Benchmark (~92, MIT) — stale (last push 2024).
- ToolHop (arXiv 2501.02506) — multi-hop tool-use benchmark, no public repo found.

## Sources
- https://github.com/pydantic/pydantic-ai
- https://github.com/openai/openai-agents-python/issues/1671
- https://github.com/microsoft/agent-framework/issues/3304
- https://github.com/google/adk-python
- https://github.com/zai-org/ComplexFuncBench
- https://github.com/IBM/NESTFUL
