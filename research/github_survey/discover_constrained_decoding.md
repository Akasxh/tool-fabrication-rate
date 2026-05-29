# GitHub Survey: Constrained Decoding / Tool-Call Validators

Cluster: constrained decoding / structured-generation engines / grammar-constrained
token masking / tool-call (function-call) validators.

Scope: repos NOT already in our known list (excludes outlines, guidance,
lm-format-enforcer, instructor, jsonformer, etc.). Preference: permissive license,
active maintenance, high stars, direct relevance to TEHR/RVR and the harness
(MLX + HF transformers + API models).

Surveyed 2026-05-29. Star counts are approximate (GitHub web UI at survey time).

---

## Selected (6)

### 1. XGrammar — `mlc-ai/xgrammar`
- URL: https://github.com/mlc-ai/xgrammar
- Stars: ~1.7k
- License: Apache-2.0
- Maintenance: very active; v0.2.1 released 2026-05-17 (XGrammar-2 era). C++/Python.
- Why it helps: The de-facto default structured-generation backend for vLLM, SGLang,
  TensorRT-LLM, and MLC-LLM. A byte-level pushdown automaton with adaptive token-mask
  cache. This is THE strongest "guaranteed-valid-tool-call" baseline to cite/run as an
  upper-bound intervention against RVR — if a tool name/schema is grammar-constrained
  at decode time, TEHR is structurally 0. Lets us frame RVR as the
  decode-engine-agnostic, API-model-compatible alternative (constrained decoding can't
  touch closed Anthropic/OpenAI APIs). Apple Silicon support means it can run in our
  MLX path for the Qwen3 4-bit family.

### 2. llguidance — `guidance-ai/llguidance`
- URL: https://github.com/guidance-ai/llguidance
- Stars: ~0.8k
- License: MIT
- Maintenance: very active; v1.0.0 (2025-06-23), adopted by OpenAI/vLLM/llama.cpp/SGLang/
  Chromium/mistral.rs. Rust core with Python bindings.
- Why it helps: Earley-parser CFG enforcement at ~50us/token; the parsing core now
  behind OpenAI Structured Outputs and Guidance. Strong, independent constrained-decoding
  baseline distinct from XGrammar's automaton approach (lets us report >1 decode-time
  method). Its "fast-forward tokens" mechanism is a clean point of comparison for
  RVR's re-prompt overhead in the cost-quality-gap analysis.

### 3. transformers-CFG — `epfl-dlab/transformers-CFG`
- URL: https://github.com/epfl-dlab/transformers-CFG
- Stars: ~140
- License: MIT
- Maintenance: active; v0.2.7 (2025-03-02). Pure Python, 100% HF-Transformers-native.
- Why it helps: Drop-in EBNF grammar constraint as a HF LogitsProcessor — the lowest-
  friction way to add a constrained-decoding arm directly inside our existing MLX/HF
  harness without a new inference engine. Backed by the EMNLP 2023 "Grammar-Constrained
  Decoding" paper, so it doubles as a citable academic baseline for the related-work /
  breadth section. Ideal for a quick "tool-registry-as-grammar" ablation on the local
  Qwen3 models where the 1.87% TEHR peak lives.

### 4. SynCode — `uiuc-focal-lab/syncode` (a.k.a. structuredllm/syncode)
- URL: https://github.com/uiuc-focal-lab/syncode
- Stars: ~330
- License: MIT
- Maintenance: active; v0.4.16 (2025-07-16). Python, HF logits-processor integration.
- Why it helps: Offline DFA mask-store with provable soundness + completeness w.r.t. the
  CFG (ICML/ML-venue framing, arXiv 2403.01632). Gives the paper a theory-grounded
  constrained-decoding comparison and a precedent for how to argue "structural error
  cannot occur" — useful contrast to our empirical TEHR-measurement framing and to
  justify why a measured intervention (RVR) is still needed for API models that can't
  use mask stores.

### 5. Formatron — `Dan-wanna-M/formatron`
- URL: https://github.com/Dan-wanna-M/formatron
- Stars: ~240
- License: MIT
- Maintenance: active; v0.5.0 (2025-05-29). Pure Python.
- Why it helps: Modular, low-overhead constrained decoder with feature-complete JSON-
  from-Pydantic and CFG support, plus a HF `create_formatter_logits_processor_list`
  integration. Because tool registries are naturally Pydantic/JSON-schema, this is the
  cleanest way to express "valid tool-call schema" as a constraint in our harness, and
  its explicit design note about NOT over-constraining whitespace/field-order is directly
  relevant to discussing why constrained decoding can degrade quality (cost-quality-gap).

### 6. AICI — `microsoft/aici`
- URL: https://github.com/microsoft/aici
- Stars: ~2.0k
- License: MIT
- Maintenance: Microsoft Research prototype (lower recent activity than the above —
  treat as a conceptual/citation reference rather than a primary baseline to run).
  Rust + Wasm.
- Why it helps: "Prompts as Wasm programs" — controllers run constrained decoding AND
  dynamic prompt editing token-by-token. This is the closest published analogue to RVR's
  "intervene on a bad call and re-steer" idea, but at the decode loop instead of the
  re-prompt loop. Strong related-work anchor to position RVR as an API-model-friendly,
  engine-agnostic instantiation of the same control idea.

---

## Considered but not selected
- `sgl-project/sglang`, `vllm-project/vllm`, `EleutherAI/...` engines — inference engines,
  not validators per se; XGrammar/llguidance are their constraint backends and are the
  better citation targets.
- `microsoft/aici` was borderline (prototype activity) but kept as #6 for its direct
  conceptual alignment with RVR.
- partial-JSON repos (`promplate/partial-json-parser`, `instructor-js/zod-stream`,
  `st3w4r/openai-partial-stream`) — useful engineering but low-star, non-research, not
  ICML-citation-grade.
- `eth-sri/lmql`, `genlm/genlm-control` — relevant but lower fit/popularity than the six
  above; revisit if we need a 7th programmable-constraint baseline.

## Suggested actions
- Add `XGrammar` + `llguidance` as the two headline decode-time baselines (engine-side).
- Add `transformers-CFG` or `Formatron` as the in-harness HF/MLX constrained-decoding arm
  for the local Qwen3 4-bit sweep (tool-registry-as-grammar ablation against RVR).
- Cite `SynCode` (soundness/completeness) and `AICI` (token-level control) in related
  work to motivate RVR as the API-compatible alternative where mask stores are impossible.
