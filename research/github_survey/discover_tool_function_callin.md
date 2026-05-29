# GitHub Survey: Tool / Function-Calling Benchmarks (esp. tool-existence / nonexistent-tool hallucination)

Date: 2026-05-29
Scope: Find the most popular / useful repos in the tool-calling-benchmark cluster that are NOT in our known list, with an emphasis on benchmarks that measure tool-existence / nonexistent-tool hallucination (directly adjacent to our TEHR metric and RVR intervention).

Known list excluded (deduped against): gorilla-BFCL, tau-bench, ToolBench, API-Bank, MetaTool, StableToolBench, ToolBeHonest, ToolSandbox, AgentBench, ToolEmu, AppWorld, RestGPT, NexusRaven, Seal-Tools, ToolACE, lm-evaluation-harness, inspect_ai, deepeval, helm, openai-evals, promptfoo, outlines, guidance, lm-format-enforcer, instructor, jsonformer, langgraph, autogen, crewAI, dspy, letta, smolagents, AutoGPT, reflexion, AI-Scientist(-v2), paper-qa, AgentLaboratory, storm, CycleReviewer.

## Top picks (ranked by relevance to TEHR + RVR)

### 1. NVIDIA/When2Call  — STRONGEST MATCH
- URL: https://github.com/NVIDIA/When2Call
- Stars: ~63 | License: Apache-2.0 | Active (pushed 2025-04, NAACL 2025) | HF dataset: nvidia/When2Call
- Why it helps: Directly measures the "when NOT to call" decision, including the case where the answer requires a tool that does not exist / is unavailable. MCQ format pits 4 behaviors (call a tool / ask for info / say "can't answer" / hallucinate an answer). This is the closest published analog to our tool-existence hallucination axis and gives us a ready-made, commercially-licensed negative-example benchmark + training regime (DPO-style preference data) to (a) add a breadth benchmark and (b) stress-test RVR as a "don't fabricate a tool" intervention.

### 2. zai-org/ComplexFuncBench  (a.k.a. THUDM/ComplexFuncBench)
- URL: https://github.com/zai-org/ComplexFuncBench
- Stars: ~180 | License: NONE DETECTED (caveat: no LICENSE file = all-rights-reserved; check before redistribution) | pushed 2025-01 (ICML-cycle paper, arXiv 2501.10132)
- Why it helps: 1,000 hard multi-step / constrained / long-context (128k) function-calling samples with the ComplexEval auto-evaluator. Adds a high-difficulty breadth axis beyond BFCL multi-turn and a credible baseline to report; its eval harness style (param-value reasoning, implicit-info extraction) gives us additional failure-mode categories adjacent to tool-existence errors.

### 3. Accenture/mcp-bench
- URL: https://github.com/Accenture/mcp-bench
- Stars: ~486 (highest-star fresh repo here) | License: NONE DETECTED (caveat: confirm before redistribution) | Actively maintained (pushed 2025-10)
- Why it helps: Benchmarks tool-using agents over real MCP servers with complex multi-tool tasks. MCP framing is timely for main-track breadth and lets us test TEHR/RVR in a realistic, large-tool-registry setting where nonexistent-tool hallucination is more likely (many similarly-named tools). Good "real-world deployment" baseline. License is the only friction.

### 4. sunblaze-ucb/mirage-bench
- URL: https://github.com/sunblaze-ucb/mirage-bench
- Stars: ~9 (new, low) | License: Apache-2.0 | Active (pushed 2026-01; arXiv 2507.21017, 2025)
- Why it helps: First unified benchmark for *agentic hallucination* with a 3-part taxonomy (actions unfaithful to instructions / history / observations) and a snapshot strategy that isolates decision points deterministically. Conceptually frames our TEHR as one instance of a broader hallucination taxonomy — useful for positioning/related-work and for borrowing their LLM-as-judge risk-aware eval into our harness. Low stars but Berkeley/sunblaze provenance and permissive license.

### 5. IBM/NESTFUL
- URL: https://github.com/IBM/NESTFUL
- Stars: ~19 | License: Apache-2.0 | Active (pushed 2025-09; EMNLP 2025; HF: ibm-research/nestful)
- Why it helps: 1,800+ executable *nested* API-call sequences (output of one call feeds the next). Adds a compositional / executable breadth axis distinct from BFCL and tau-bench, with a permissive license and a clean executable-grounding signal. Useful as an additional model-family stress test (low SOTA scores → headroom to show RVR effects).

### 6. Junjie-Ye/RoTBench
- URL: https://github.com/Junjie-Ye/RoTBench
- Stars: ~15 | License: Apache-2.0 | EMNLP 2024 (pushed 2025-05)
- Why it helps: Multi-level *robustness* benchmark with 5 controlled noise environments (Clean→Slight→Medium→Heavy→Union) across tool selection, parameter identification, and content filling. Gives us a knob to inject distractor/near-miss tools and measure how TEHR and RVR behave under increasing registry noise — a natural robustness ablation for the main-track version.

## Honorable mentions / notes
- sierra-research/tau2-bench (~1,259 stars, MIT, very active): excellent and high-star, but it is the direct successor to tau-bench (already in known list), so treated as out-of-scope rather than a new cluster entry. Worth adopting anyway for breadth if redundancy is acceptable.
- philschmid/ai-agent-benchmark-compendium (~151, no license): meta-list of 50+ agent/tool benchmarks — useful as a discovery index, not a benchmark itself.
- thunlp/ToLeaP (~4, MIT): tool-learning platform aggregator; too early-stage/low-star to prioritize.
- License caveat: ComplexFuncBench and mcp-bench have NO detected LICENSE file (default = all rights reserved). Prefer the Apache-2.0 repos (When2Call, mirage-bench, NESTFUL, RoTBench) for anything we redistribute or fold into the harness.

## Recommendation for the paper / skill
- Highest-leverage add for the TEHR/RVR story: **When2Call** (explicit unavailable-tool / don't-fabricate axis, permissive, training data included), backed by **RoTBench** (noise ablation) and **mirage-bench** (taxonomy framing).
- Highest-leverage adds for main-track breadth: **ComplexFuncBench** and **NESTFUL** (harder, executable, different difficulty axes); **mcp-bench** for a realistic large-registry setting (pending license check).
