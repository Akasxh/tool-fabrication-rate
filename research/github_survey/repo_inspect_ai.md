# Repo survey: inspect_ai (+ inspect_evals)

- Canonical URL: https://github.com/UKGovernmentBEIS/inspect_ai (URL valid, not 404)
- Companion eval suite: https://github.com/UKGovernmentBEIS/inspect_evals
- License: MIT (SPDX: MIT) for both repos — permissive, low risk
- Stars: inspect_ai 2,140; inspect_evals 517 (as of 2026-05-29 via gh api)
- Activity: very active (inspect_ai pushed 2026-05-28; inspect_evals pushed 2026-05-29)
- Author: UK AI Security Institute (AISI) + Meridian Labs
- Category: eval-harness
- Docs: https://inspect.aisi.org.uk/ ; evals index https://ukgovernmentbeis.github.io/inspect_evals/

## What it is
Inspect is a general LLM-eval framework with three abstractions: **datasets** (Samples),
**solvers** (chainable strategies / agents incl. iterative tool-call loops + critique), and
**scorers**. First-class tool-calling: custom + MCP tools, built-in bash/python/text-editor/
web-search/web-browse/computer tools. Sandboxing via Docker/K8s/Modal/Proxmox. Multi-agent
primitives + external-agent integration. ~200+ pre-built evals live in the separate
`inspect_evals` package. Broad provider coverage: OpenAI, Anthropic, Google, Mistral, Grok,
Bedrock, Azure, TogetherAI, Groq, Cloudflare, HF, **and local vLLM / Ollama / llama-cpp-python**.
No native MLX provider (relevant to our M5 local-MLX path).

## Directly relevant: BFCL + tau2 already implemented in inspect_evals
`inspect_evals/src/inspect_evals/bfcl/` is a full BFCL port (4,981 samples, version "5-B",
MIT). It pins the gorilla repo at commit `dac44e7a...` and pulls data + multi-turn
`func_source_code` from GitHub. Categories cover V1/V2/V3 incl. our exact splits:
`multi_turn_base`, `multi_turn_miss_func`, `multi_turn_miss_param`, `multi_turn_long_context`,
`multi_turn_composite` (REST not implemented). Scorers: `ast_match`, `relevance_match`,
`irrelevance_match`, `multi_turn_match`.
There is also a `tau2` eval (tau-bench v2) plus many agentic evals: agentdojo, agentharm,
agent_bench, gaia, swe_bench, swe_lancer, theagentcompany.

## How its scoring relates to our TEHR metric (honest read)
- `irrelevance_match`: scores 1 if the model makes NO tool call on an irrelevant query, 0 if
  it calls anything. `relevance_match`: complement. These measure abstention / over-calling,
  **not tool-existence hallucination**. BFCL "irrelevance" = "should not have called any
  function," whereas our TEHR = "called a tool name absent from the provided registry." Adjacent
  but not the same construct — useful to cite as the closest prior metric we differentiate from.
- `multi_turn_match` (`multi_turn_scorer.py`): **state-based** scoring — replays the GT calls and
  the model calls against backend objects and compares attributes via `getattr`. It does NOT
  emit a per-call signal for "called a nonexistent function." So Inspect's BFCL port will not
  give us TEHR for free; we'd still compute TEHR from the call trace ourselves.

## Concrete judgement
- RUN as extra benchmark: **Yes, high value, moderate effort.** `inspect_evals` gives us
  BFCL + tau2 + several agentic evals under one MIT harness. This is the cleanest path to the
  "more benchmarks/baselines/families" MAIN-TRACK breadth we want. We can run our model families
  through it (API providers + local vLLM/Ollama; MLX would need a custom provider or run via
  Ollama/llama-cpp GGUF instead of MLX). Effort: install, wire providers, and post-process the
  call trace to compute TEHR — the data/loop come for free, the TEHR overlay is ours.
- Reuse COMPONENT in our harness: **Partial.** Cleanest reuse is its BFCL data-fetch (pinned
  gorilla commit + sparse git clone in `bfcl/data.py` / `backends`) and the V3 multi-turn backend
  setup, which mirror what our `harness/bench_loaders/*.py` do. Lifting whole modules pulls the
  inspect_ai runtime in; better to either (a) adopt Inspect as the runner, or (b) borrow only the
  pinned-commit + category-split pattern. MIT permits either with attribution.
- Reuse as BASELINE: **Yes.** Inspect's `irrelevance_match`/`relevance_match` are a citable
  baseline metric to contrast against TEHR (over-calling vs nonexistent-tool calling). Also lets
  us report numbers on a recognized harness, strengthening external validity.
- Cite as PRIOR ART: **Yes, must-cite.** AISI's framework is standard in frontier-eval circles;
  cite for (i) the eval-framework landscape, (ii) BFCL/tau-bench operationalization, (iii)
  positioning TEHR as a new per-call metric not captured by existing Inspect scorers.
- Pattern for paper-revision skill / reviewer personas: **Low/indirect.** It's an eval harness,
  not a writing tool. The transferable pattern is its dataset/solver/scorer separation and
  rubric-style scorers — could inform how we structure reviewer-persona rubrics as composable
  scorers, but no direct code reuse.

## Risk / caveats
- License: MIT, low risk. Attribute on any borrowed code.
- BFCL data is fetched from gorilla at a pinned commit (reproducible) — but network/git_clone at
  runtime; mirror it for offline/cluster runs.
- No MLX provider: our local MLX 4-bit Qwen3 runs would need a shim or fall back to GGUF/Ollama,
  which changes the quant stack vs our current MLX 4-bit numbers — watch for non-comparability.
- Running Inspect introduces a second runtime alongside our harness; decide whether to adopt it
  as runner or only mine its BFCL port.

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

Method: `gh api` for metadata, raw LICENSE text decoded (not the GitHub summary), provider
directory listing, and raw scorer source via WebFetch. Findings:

- **LICENSE — CONFIRMED MIT (SPDX: MIT), both repos.** Read the actual LICENSE files, not the
  summary. Full MIT grant ("use, copy, modify, merge, publish, distribute, sublicense"), only
  condition is retaining the notice. `Copyright (c) 2024 UK AI Security Institute`. NOT GPL/AGPL.
  => We CAN vendor/modify into our permissive codebase with attribution. The GPL/AGPL vendoring
  hazard called out in the brief does NOT apply here.
- **Stars — CONFIRMED order-of-magnitude.** inspect_ai 2,140 (low thousands), inspect_evals 517
  (hundreds). Matches survey exactly. Both active (pushed 2026-05-28/29), not archived, not forks.
- **BFCL + tau2 — CONFIRMED present.** `src/inspect_evals/bfcl/` exists with data.py, backends,
  prompts.py, score/, solve/, eval.yaml; `tau2` dir exists. Scorer names verified from source:
  `ast_match`, `irrelevance_match`, `relevance_match`, `multi_turn_match`,
  `tool_call_matches_possible_answers`.
- **TEHR-for-free claim — CONFIRMED HONEST (survey if anything understated it).** Verified the
  multi_turn scorer source: it is state-based (compares final backend-object attributes via
  `vars`/`getattr`, plus unordered result-subset check). An out-of-registry call is either skipped
  with a warning or returns `"Method '{name}' not found"` and silently degrades the state-match
  score — it is NOT surfaced as a per-call signal. So (a) Inspect will not give us TEHR for free,
  confirming the survey, and (b) this is actually a positioning point FOR us: TEHR isolates a
  failure mode the standard harness absorbs into pass/fail.

### CORRECTION — survey was OVER-PESSIMISTIC on the MLX path (the one place it erred)
The survey says "No native MLX provider ... MLX would need a custom provider or run via
Ollama/llama-cpp GGUF instead of MLX," and warns this "changes the quant stack vs our current
MLX 4-bit numbers." That is too negative. Verified provider list includes `openai_compatible.py`
(`openai-api/<name>/<model>` with a custom BASE_URL). `mlx_lm.server` exposes
`/v1/chat/completions` + `/v1/models`. => Our existing MLX 4-bit Qwen3 weights can be driven by
Inspect with NO quant change and NO custom provider: launch `mlx_lm.server`, point
`openai-api` at it. The non-comparability worry (forced GGUF/Ollama) is avoidable.

### PRESSURE-TEST of "run-as-benchmark": holds, but with a sharper caveat
Run-as-benchmark is REAL and high-value: MIT (vendorable), BFCL+tau2+agentic evals under one
harness, API providers first-class, and a clean MLX-via-openai-api route. The remaining risk is
NOT licensing and NOT "no MLX" — it is **tool-call fidelity on the MLX OpenAI-compatible path**.
BFCL multi-turn and TEHR both depend on parsing the model's emitted tool calls; `mlx_lm.server`'s
function-calling/tool-parse support is newer and less battle-tested than vLLM's, and Qwen3
tool-call formatting via MLX may differ from what our current `harness/bench_loaders/*.py`
expects. Since TEHR is computed FROM the call trace, a parser mismatch would corrupt the metric.
Mitigation: validate the MLX-server tool-call trace against our existing harness on a small
multi_turn_base slice before trusting any Inspect-run TEHR numbers; alternatively run the local
arm through vLLM (well-supported tool parsing) and accept it is a different quant than MLX 4-bit.
Also: BFCL data is git-cloned from gorilla at a pinned commit at runtime — mirror for offline
cluster runs (survey already flagged this).

### Verdict
recommend = run-as-benchmark (and include-parts: BFCL data-fetch + category-split pattern are
MIT-vendorable). license_confirmed = true, MIT. confidence = high on license/stars/eval-presence;
the only execution risk is MLX-server tool-call parsing fidelity, which is testable up front.

## SECOND INDEPENDENT ADVERSARIAL PASS (2026-05-29, re-verified from primary sources)

Re-ran every load-bearing check from scratch (gh api + base64-decoded raw LICENSE + provider dir
listing + scorer source). I did NOT trust the prior verification block.

- **LICENSE — RE-CONFIRMED MIT (SPDX: MIT) on BOTH repos from raw decoded LICENSE text.**
  Both read `MIT License / Copyright (c) 2024 UK AI Security Institute`, full grant incl. modify +
  sublicense, sole condition = retain notice. `gh api` `.license.spdx_id` also returns `MIT` for
  both. NOT GPL/AGPL. The vendoring hazard in the brief does not apply: we MAY vendor/modify into
  our permissive codebase with attribution. license_confirmed = true.
- **Stars — RE-CONFIRMED.** inspect_ai 2,140; inspect_evals 517. Order-of-magnitude (low-thousands
  / hundreds) is right; survey not inflated. Both active, not archived, not forks.
- **eval presence — RE-CONFIRMED.** `src/inspect_evals/bfcl/` (data.py, backends, score/, solve/,
  prompts.py, eval.yaml) and `src/inspect_evals/tau2/` both exist.
- **Scorer is state-based — RE-CONFIRMED from multi_turn_scorer.py source.** An out-of-registry
  method returns the internal string `"Method '{name}' not found in any backend instance"`
  (line 206), is logged as a warning during replay (line 146), then the final Score collapses to
  0/1 by comparing backend-object attributes via `vars()`/`getattr()` (lines 263-267) plus an
  unordered result-subsequence check. There is NO per-call "called a nonexistent tool" signal.
  => Inspect does NOT give TEHR for free; we compute it ourselves from the trace. Survey HONEST.

### CORRECTION to the FIRST verification block (it was too optimistic on the MLX path)
The first block claimed our MLX 4-bit runs plug into Inspect "with NO quant change and NO custom
provider: launch `mlx_lm.server`, point `openai-api` at it." Checked against our ACTUAL harness:
`harness/adapters/mlx_adapter.py` drives MLX **in-process** via `mlx_lm.load` + `mlx_lm.generate`,
does its OWN `apply_chat_template(enable_thinking=False)`, injects a date-hint system message, and
parses tool calls with bespoke regexes (`<tool_call>{json}</tool_call>` for Qwen3, `[TOOL_CALLS]`
for Mistral, Llama handler). We do NOT run an HTTP server and do NOT use OpenAI-compatible tool
parsing for the local arm. Inspect's `openai_compatible.py` DOES exist and supports a custom
base_url, so the mlx_lm.server route is *technically available* — but adopting it means REPLACING
our whole local generation+parse path (in-process generate + our regex envelope parser) with
`mlx_lm.server`'s HTTP tool-parse layer. That is a material swap, not a free drop-in, and it moves
the tool-call parsing off the exact code that produced our published MLX 4-bit TEHR numbers. Since
TEHR is derived entirely from the parsed call trace, any divergence in how mlx_lm.server emits/
parses Qwen3 tool calls vs our regex parser would silently shift TEHR. So the first block's "no
custom provider, no risk" framing understates the integration cost and the comparability risk.

### Net assessment of "run-as-benchmark"
HOLDS, and is the strongest reason to engage this repo, BUT with the realistic shape:
- API families (Anthropic/OpenAI/Google/etc.): clean, first-class, low risk. Real breadth win.
- Local Qwen3 via Inspect: either (a) run through vLLM/Ollama (well-supported tool parsing) and
  accept it is a DIFFERENT quant/stack than our MLX 4-bit headline numbers, or (b) wire
  mlx_lm.server behind `openai_compatible` and re-validate the tool-call trace against our
  in-process MLXAdapter on a multi_turn_base slice before trusting any number. Do not present
  Inspect-run local numbers as drop-in comparable to our existing MLX 4-bit TEHR without that
  validation.
- BFCL data is git-cloned from gorilla at a pinned commit at RUNTIME — mirror for offline cluster.
- TEHR overlay is ours to compute regardless of harness; the harness gives data+loop, not TEHR.

### Final verdict (this pass)
recommend = run-as-benchmark, plus include-parts (BFCL pinned-commit fetch + category-split
pattern are MIT and safe to vendor with attribution). license_spdx = MIT, license_confirmed =
true. confidence = HIGH on license + stars + eval-presence + scorer-is-state-based; the residual
risk is execution-side (local/MLX tool-call parsing fidelity and quant comparability), which is
real but testable up front and does NOT change the recommend.
