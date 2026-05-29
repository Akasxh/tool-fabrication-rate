# Repo survey: autogen

- **Repo:** microsoft/autogen
- **Canonical URL:** https://github.com/microsoft/autogen (live, not 404)
- **Stars:** 58,510 (gh api, 2026-05-29) · forks 8,825 · open issues 868 · last push 2026-04-15 · not archived
- **License:** SPLIT. Docs/content = `CC-BY-4.0` (root `LICENSE`, what the GitHub API reports). **All CODE = `MIT`** (`LICENSE-CODE` file, confirmed via `gh api .../contents/LICENSE-CODE`). For any code reuse the governing license is MIT.
- **Category:** agent-framework

## What it is
AutoGen is Microsoft's framework for building multi-agent AI applications — **not a benchmark**.
The 0.4+ rewrite is a layered Python (and .NET) stack:
- `autogen-core` — async, event-driven actor runtime for message-passing agents.
- `autogen-agentchat` — high-level conversational agents + team patterns (round-robin, selector, swarm, Magentic-One orchestrator).
- `autogen-ext` — pluggable extensions: model clients (`models`: OpenAI, Anthropic, Azure, Ollama, etc.), `tools`, `code_executors` (incl. Docker), `memory`, `teams`, `ui`.
- `autogen-studio` — low-code GUI; `magentic-one-cli`, `agbench`, `agentchat` apps.

It also ships **`agbench` (AutoGenBench)**: a Docker-isolated *task runner / harness* (run N trials from a blank slate, `agbench tabulate` for metrics). agbench is a runner over task sets (GAIA, HumanEval, etc.), not a tool-use hallucination benchmark itself.

## Relevance to OUR paper (TEHR / RVR on BFCL + tau-bench)
AutoGen is an **orchestration framework**, orthogonal to our metric (per-call Tool-Existence Hallucination Rate) and our benchmarks. It does not provide tool-existence-error tasks or a comparable metric. Its value to us is as *prior art* and as a possible *pattern* source, not as a benchmark we run or a TEHR baseline.

## Concrete reuse verdict
- **RUN as extra benchmark:** NO. AutoGen is a framework, not a benchmark; it yields no tasks/gold-tool registry/oracle for TEHR. `agbench` is a generic runner (GAIA/HumanEval/code tasks), not tool-existence-error tasks — running it would not produce a TEHR number and would require Docker-per-trial plumbing that duplicates our harness. Not worth it.
- **Reuse COMPONENT in harness:** WEAK MAYBE / not recommended. `autogen-ext.models` (unified Anthropic + OpenAI + Ollama model clients) and `autogen-ext.tools` overlap with what our `harness/adapters/` + `registry.py` already do. Adopting them means inheriting the whole `autogen-core` actor runtime — heavy dependency for marginal gain. Our adapters are lighter and already wired to MLX + API + cost_meter. Keep ours.
- **Use as BASELINE:** PLAUSIBLE but optional. The honest framing: an AutoGen `AssistantAgent` (or the Magentic-One team) is a *representative production agent scaffold*. We could run our TEHR instrumentation around an AutoGen agent on BFCL/tau-bench to show "even a real framework hallucinates non-existent tools, and RVR cuts it." That is a stronger systems story than ad-hoc loops. Cost: MED (wrap AutoGen agent in our runner, intercept tool calls for TEHR scoring + RVR re-prompt). Worth considering for ICML breadth if time allows; not core.
- **CITE as PRIOR ART:** YES. Cite AutoGen (Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation", 2023) as the leading multi-agent tool-use framework — context for why per-call tool hallucination matters in deployed agent stacks, and to differentiate (frameworks orchestrate tool calls but ship no guardrail against calling tools that do not exist; RVR fills that gap).
- **PATTERN for paper-revision skill / reviewer personas:** MARGINAL-USEFUL. Two transferable ideas: (1) AutoGen's **team patterns** (round-robin / selector / Magentic-One orchestrator-critic) map onto a multi-persona reviewer ensemble with a moderator — useful structure for the reviewer-personas design. (2) `agbench`'s **blank-slate, N-trial, tabulate** discipline is a clean reproducibility pattern (fresh state per run, aggregate, report variance) worth echoing in a reviewer persona that probes reproducibility. No direct code reuse for the skill.

## Effort & license risk
- **License risk: LOW for code reuse** (MIT on all `LICENSE-CODE`-governed source). **WATCH-OUT:** the GitHub API and root `LICENSE` advertise **CC-BY-4.0**, which governs *docs/content*, not code — do not let that scare off code reuse, but if we copy any **documentation/figures/prose**, CC-BY-4.0 attribution applies. Retain both notices if we vendor anything.
- **Effort:** RUN-as-benchmark = N/A (wrong tool). COMPONENT swap = HIGH (drags in actor runtime), not recommended. BASELINE (wrap an AutoGen agent in our harness) = MED. CITE = trivial. PATTERN = low (design inspiration only).
- **Bottom line:** Best uses are **cite as prior art** (mandatory) and **optional MED-effort baseline** (TEHR/RVR around a real AutoGen agent for systems credibility). Do NOT run agbench and do NOT graft autogen-core into the harness.

---

## Adversarial verification (2026-05-29, independent re-check)

**Method:** Re-pulled `gh api repos/microsoft/autogen`; decoded BOTH `LICENSE` and `LICENSE-CODE` from raw base64 (did not trust survey or API summary); listed `python/packages/` and `autogen-ext/src/autogen_ext/models/`; searched for MLX support.

- **Stars — CONFIRMED.** API returns `58,510` exactly (survey value matches to the digit, not just order of magnitude). Forks 8,825, open issues 868, pushed 2026-04-15, not archived — all match. The survey did NOT overstate popularity; it is a genuine, very-high-star (~58k) actively-maintained repo.
- **License — CONFIRMED with the split correctly characterized.** Root `LICENSE` decodes to **CC-BY-4.0** ("Attribution 4.0 International" / Creative Commons), which is also what the GitHub API `.license.spdx_id` reports. `LICENSE-CODE` decodes to a verbatim **MIT** license (Copyright Microsoft Corporation). The survey's central claim — *code is MIT, docs/content is CC-BY-4.0* — is accurate and not over-optimistic. **Governing SPDX for code reuse = MIT.** This is permissive, NOT GPL/AGPL: vendoring autogen CODE into our (permissive) codebase is allowed with MIT notice retention. The GPL/AGPL contamination concern raised in the task does NOT apply here. Only caveat: if we copy any docs/figures/prose, CC-BY-4.0 attribution applies separately.
- **Component/baseline reuse claims — CONFIRMED and slightly UNDERSTATED in breadth, but one MLX gap the survey missed.** `autogen-ext/.../models/` really does ship `anthropic`, `openai`, `azure`, `ollama`, `llama_cpp`, `semantic_kernel`, `cache`, `replay` clients. So the "unified Anthropic + OpenAI + Ollama clients" claim is true (survey even slightly under-counted — `llama_cpp` is also present). **MLX FLAG (survey omitted this):** code search for `mlx` in the repo returns **0 hits** — autogen has NO MLX model client. Our harness's MLX path (the 4-bit Qwen3 curve) is exactly the half autogen cannot serve. This *strengthens* the survey's "keep our own adapters" conclusion: swapping in autogen-ext models would lose MLX and force the whole actor runtime. COMPONENT-swap = correctly rated not-recommended.
- **"cite-only" pressure-test — the survey's nuance holds; pure cite-only is the safe default, baseline is genuinely optional.** Can we actually run/reuse it under our MLX+API harness + (permissive) license?
  - *Vendor code into our repo:* legally YES (MIT), but practically NOT WORTH IT — heavy `autogen-core` actor-runtime dependency, no MLX, duplicates our lighter adapters. Agree with survey.
  - *Run externally as a baseline scaffold (API models only):* FEASIBLE at MED effort — wrap an `AssistantAgent` on BFCL/tau-bench, intercept tool calls for TEHR + RVR. License permits it; no vendoring needed. BUT it would only cover our API-model rows; the MLX/Qwen3 rows (our headline non-monotonic curve) cannot be driven through autogen. So the baseline is genuinely *partial-coverage* and *optional*, not a clean drop-in. The survey's "PLAUSIBLE but optional / not core" rating is well-calibrated, not over-optimistic.
  - *agbench as a benchmark:* CONFIRMED N/A — it is a generic Docker N-trial task runner (GAIA/HumanEval), yields no tool-existence oracle, no TEHR number. Survey correct.
- **Citation string — plausibly correct, verify before camera-ready.** Survey cites Wu et al. 2023, "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (arXiv 2308.08155). This matches the widely known canonical reference; the repo README did not surface a BibTeX block in this check, so confirm the exact author list/venue at write time (it is a workshop/arXiv paper, not a main-conference proceedings — do not mis-cite as ICLR/NeurIPS).

**VERDICT: include-parts.** Mandatory CITE as prior art (permissive MIT code, ~58k stars — a legitimate, high-credibility framework to position against). Optionally reuse as a MED-effort, API-only TEHR/RVR baseline scaffold (license permits external run; no vendoring; MLX rows excluded). Do NOT vendor autogen-core and do NOT run agbench. No GPL/AGPL risk. Survey was accurate and NOT over-optimistic; the only correction is the **missing MLX-client gap**, which actually reinforces its "keep our adapters" stance.

---

## Adversarial re-verification #2 (2026-05-29, second independent pass — task-mandated)

**Method:** Re-pulled `gh api repos/microsoft/autogen` live; decoded BOTH `LICENSE` and `LICENSE-CODE` from raw base64 (did not trust survey, prior verification block, or API summary); listed `autogen-ext/.../models/` clients; ran `gh api search/code?q=mlx+repo:microsoft/autogen` for the MLX claim; inspected OUR `harness/adapters/` + `bench_loaders/`; checked our repo for a LICENSE file; verified the citation against arXiv directly.

**Every falsifiable survey claim independently re-confirmed:**
- **Stars — CONFIRMED to the digit.** API returns `58510` (not just ~58k order-of-magnitude — exact). Forks `8825`, open issues `868`, pushed `2026-04-15`, `archived: false`. No popularity overstatement.
- **License — CONFIRMED, split correctly characterized.** Root `LICENSE` decodes to "Attribution 4.0 International / Creative Commons" = **CC-BY-4.0** (also the API `.license.spdx_id`). `LICENSE-CODE` decodes to a **verbatim MIT** license, "Copyright (c) Microsoft Corporation." **Governing SPDX for CODE reuse = MIT** (permissive). The task's GPL/AGPL contamination concern does **NOT apply** — MIT permits vendoring into a permissive codebase with notice retention. CC-BY-4.0 governs only docs/figures/prose (separate attribution if copied). The survey did NOT over-state license permissiveness; it correctly disambiguated the misleading API/root-LICENSE CC-BY-4.0 signal.
- **Model clients — CONFIRMED.** `autogen-ext/.../models/` contains: `anthropic`, `azure`, `cache`, `llama_cpp`, `ollama`, `openai`, `replay`, `semantic_kernel` (+ `_utils`). Matches survey; survey under-counted (`llama_cpp` present) but that direction is conservative, not over-optimistic.
- **MLX gap — CONFIRMED (the survey's only real correction stands).** `search/code?q=mlx` over the repo = **0 hits**. autogen ships NO MLX client. Cross-checked against OUR harness: `harness/adapters/` has a first-class `mlx_adapter.py` (plus `anthropic_adapter.py`, `openai_adapter.py`) and `registry.py`/`cost_meter.py`. Our MLX/Qwen3-4bit non-monotonic-curve rows — the paper's headline — literally cannot be driven through autogen. Reinforces "keep our adapters; do not swap in autogen-ext.models."
- **agbench ≠ benchmark — CONFIRMED.** Package list confirms `agbench`, `autogen-core`, `autogen-ext`, `autogen-agentchat`, `autogen-studio`, `autogen-magentic-one`, `magentic-one-cli`, `pyautogen`. agbench is a generic Docker N-trial task runner (GAIA/HumanEval), yields no tool-existence oracle / no TEHR number. RUN-as-benchmark = correctly N/A.
- **Citation — CONFIRMED against arXiv directly.** arXiv 2308.08155, Wu, Bansal, Zhang, Wu, Li, Zhu, Jiang, Zhang, Zhang, Liu, Awadallah, White, Burger, Wang (2023), exact title "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." It is an arXiv/COLM-lineage paper, NOT a NeurIPS/ICLR/ICML proceedings — survey's "don't mis-cite the venue" caveat is correct.

**"cite-only" pressure-test — survey is well-calibrated; the SAFE DEFAULT is cite-only, baseline is genuinely optional and partial.** Under OUR MLX+API harness:
  - *Vendor autogen code into our repo:* legally YES (MIT) — BUT note **our repo currently has NO LICENSE file** (root `LICENSE*` absent), so our outbound license is undeclared; before vendoring any MIT code we must (a) declare our own license and (b) retain MIT notice. Practically still NOT WORTH IT (drags autogen-core actor runtime, no MLX, duplicates lighter adapters). Agree with survey, with this added housekeeping flag.
  - *Run externally as an API-only baseline scaffold:* FEASIBLE at MED effort, license-clean (no vendoring). But covers ONLY API-model rows — the MLX/Qwen3 headline rows are excluded. So "baseline" = partial-coverage, optional, not a clean drop-in. Survey's "PLAUSIBLE but optional / not core" is honest, not over-optimistic.
  - *Run agbench as a TEHR benchmark:* N/A — confirmed.

**FINAL VERDICT (this pass): include-parts.** Recommendation unchanged and upheld after adversarial re-check. Mandatory CITE as prior art; OPTIONAL API-only MED-effort baseline scaffold (license-clean, MLX rows excluded). Do NOT vendor autogen-core, do NOT run agbench. No GPL/AGPL risk (code = MIT). The survey was accurate and NOT over-optimistic on stars, license, or usability; its sole correction (no MLX client) is real and *strengthens* its conclusions. Added flag the survey missed: **our own repo lacks a declared LICENSE**, which must be resolved before any MIT vendoring. License confidence: HIGH (decoded both files byte-for-byte).
