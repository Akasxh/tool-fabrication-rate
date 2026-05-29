# Repo survey: Reflexion

- **Repo:** noahshinn/reflexion
- **Canonical URL:** https://github.com/noahshinn/reflexion (URL in task is LIVE, no 404)
- **Stars:** 3,167 (gh api, 2026-05-29)
- **License:** MIT (SPDX: MIT) — Copyright (c) 2023 Noah Shinn. Permissive, no copyleft risk.
- **Paper:** Reflexion: Language Agents with Verbal Reinforcement Learning, NeurIPS 2023, arXiv:2303.11366 (Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao)
- **Status:** not archived; last push 2025-01-14. No `setup.py`/`pyproject.toml` — this is **research scaffolding, not an installable package**.
- **Category:** self-correction

## What it does
Reflexion is verbal reinforcement learning: an agent attempts a task, a (heuristic or LLM) evaluator judges the trajectory, and a "self-reflection" LLM call turns the failed trajectory into a natural-language lesson stored in episodic memory; the lesson is prepended on the next attempt at the *same* task. Improvement happens **across retries of the same task**, not within a single call. Evaluated on four separate codebases under one repo:
- `hotpotqa_runs/` — ReAct-style QA (Jupyter notebooks + agents.py)
- `alfworld_runs/` — ALFWorld embodied text agent
- `webshop_runs/` — WebShop
- `programming_runs/` — HumanEval / LeetcodeHardGym (pulls 2 git submodules: lazzzy, leetcode-hard-gym)

Each subdir is self-contained with its own `requirements.txt`, prompts, few-shot files, and run logs. There is no shared library; code is duplicated across the four task dirs (`env_history.py`, `generate_reflections.py` recur per-task).

## Concrete fit to our paper (TEHR / RVR on BFCL + tau-bench)

### Can we RUN it as an extra benchmark? NO (skip)
Different axis. Reflexion's tasks are HotPotQA/ALFWorld/WebShop/HumanEval, not tool-calling-with-a-registry. Its metric is task success across trials, not a per-call error like TEHR. It is OpenAI-completion hardcoded (`get_completion`/`llm.py`), uses git submodules and heavy env deps (ALFWorld, WebShop server), and has no loader interface compatible with our `harness/bench_loaders/*.py` (which yield `Task` with a normalized OpenAI-shape `registry`). Wiring it in would be a multi-day env-plumbing effort with no payoff for the tool-existence-hallucination story.

### Reuse a COMPONENT in our harness? NO (skip)
No package, no clean module boundary, OpenAI-only completion shim, duplicated per-task code. Nothing drops into our adapter/loader/intervention architecture. `harness/intervention/rvr.py` is already a clean pure function; importing anything from this repo would be a regression.

### Reuse as a BASELINE? YES, conceptually — this is the key value (reuse-pattern / cite-only)
Our RVR intervention (`harness/intervention/rvr.py`) is essentially **single-step, registry-grounded reflection**: on a bad (tool-not-in-registry) call, re-prompt with the available-tool list. Reflexion is the canonical *multi-trial, free-text* self-reflection method. They sit on the same family tree. Strong move for ICML main-track breadth:
  1. **Position RVR against Reflexion in related work** as the contrast: verbal-RL reflection is cross-episode, unconstrained, and memory-based; RVR is in-episode, single-shot, and grounded in the actual tool registry (verifiable feedback vs. self-generated lesson). This sharpens our novelty claim.
  2. **Optional baseline arm:** a "Reflexion-style" intervention that, instead of injecting the registry, asks the model to self-reflect on its failed call in free text and retry. Cheap to implement *in our own harness* as a new `intervention/` function (mirror the `rvr` signature, swap feedback text for a reflection prompt) — do NOT vendor their code. This gives a head-to-head: grounded re-prompt (RVR) vs. ungrounded self-reflection (Reflexion-style) on TEHR. Effort: ~half a day, fits existing intervention abstraction.

### Cite as PRIOR ART? YES — mandatory.
NeurIPS 2023, 3.1k stars, the reference for LLM self-correction/verbal-RL. Any self-correction framing of RVR must cite it. Also cite alongside Self-Refine and CRITIC for the related-work cluster.

### Borrow a PATTERN for the paper-revision skill / reviewer personas? YES (reuse-pattern, low effort)
The `_generate_reflection_query` prompt (alfworld_runs/generate_reflections.py) is a clean template: "you failed; do not summarize, identify the specific mistake, produce a concise corrective plan referencing concrete actions; here are prior attempts' plans." This is directly transferable to a **paper-revision reflection loop**: feed a failed reviewer-persona critique + prior revision attempts, ask for a concrete, non-generic revision plan that names the specific weakness. The "keep last-3 memories" episodic pattern maps to "carry forward the last N reviewer rounds." Borrow the *prompt structure and the bounded-memory idea*, written fresh in our skill — no code copied, no license entanglement.

## Effort & risk summary
- **License risk:** none (MIT). Even if we adapted a prompt verbatim, attribution-only.
- **Effort to run as benchmark:** high, not worth it (wrong axis, heavy env deps, submodules, OpenAI-locked).
- **Effort for Reflexion-style baseline in our harness:** low (~0.5 day), high paper value.
- **Effort to cite + contrast:** trivial, high value.
- **Net recommendation:** cite as prior art (mandatory) + reuse the reflection-prompt pattern for an in-harness Reflexion-style baseline and for the paper-revision skill. Do not run their repo and do not vendor their code.

---

## Adversarial verification (2026-05-29, independent)

Verified against primary sources, not the survey summary. Verdict: **survey is accurate and, if anything, slightly conservative on effort.** No over-optimistic claims found that need walking back.

**License — CONFIRMED MIT (SPDX: MIT).** Checked two ways: (1) `gh api repos/noahshinn/reflexion` → `license.spdx_id = "MIT"`; (2) raw `LICENSE` file at `main` contains the verbatim MIT body ("Permission is hereby granted, free of charge ... THE SOFTWARE IS PROVIDED 'AS IS'"), Copyright (c) 2023 Noah Shinn. Not GPL/AGPL. The copyleft caveat in the task does NOT apply here — MIT is permissive, so we *could* legally vendor with attribution. We still recommend NOT vendoring, for the architectural reasons below, not license reasons.

**Stars — CONFIRMED.** `stargazers_count = 3167` (gh api, 2026-05-29). Survey says 3,167 — exact match. Order of magnitude 10^3, correct. Not inflated.

**Repo status — CONFIRMED.** `archived: false`, `fork: false`, `pushed_at: 2025-01-14`, `default_branch: main`. Matches survey exactly.

**Structure / "not installable" — CONFIRMED.** No `setup.py` / `pyproject.toml` (verified via repo file listing). `.gitmodules` present → git submodules, as claimed. Four task dirs (alfworld_runs, hotpotqa_runs, programming_runs, webshop_runs) present. README setup is per-dir `pip install -r requirements.txt` + `OPENAI_API_KEY`. README itself flags reproduction as potentially infeasible ("GPT-4 has limited access and significant API charges") — so even the "run as benchmark = NO" verdict is reinforced by the authors' own caveat.

**OpenAI-locked — CONFIRMED.** README requires `OPENAI_API_KEY`; no Anthropic/MLX path. For our MLX-local + Anthropic-API harness this would need a completion-shim rewrite per task dir. "Run as extra benchmark" remains correctly rated NO/skip: wrong axis (task-success-across-trials, not per-call TEHR), heavy env deps (ALFWorld, WebShop server), submodules, OpenAI-only.

**Reuse-pattern claim — PRESSURE-TESTED, HOLDS (and effort is overstated, in our favor).** Inspected our `harness/intervention/`: it already has `rvr.py`, `naive_retry.py`, `decoy_list.py`, `framework_default.py` — all pure functions with the identical signature `(parsed_calls: list[ToolCall], registry: dict) -> Action`. A "Reflexion-style" ungrounded-self-reflection baseline is literally a new sibling file that returns `Action.RE_PROMPT` with a self-reflection feedback string instead of RVR's registry list — ~25 lines, no dependency on their repo at all. So the survey's "~0.5 day, do not vendor their code" is correct and conservative; realistically <1 hour. The reuse value is the *idea/prompt structure*, reimplemented natively. We confirm: nothing from their repo (no package, no module boundary, OpenAI shim, per-task duplication) should be imported — but that's an architecture call, not forced by license.

**Net adversarial verdict:** recommend **cite-only** for the repo as an artifact (mandatory prior-art citation, NeurIPS 2023, arXiv:2303.11366), with the "reuse-pattern" being a clean-room reimplementation of the reflection idea as a new in-harness intervention + paper-revision-skill prompt. License is genuinely permissive (MIT confirmed at file level), confidence HIGH. No survey claim required correction.

---

## Second independent adversarial pass (2026-05-29, Akash session, re-verified from primary sources)

Re-ran every load-bearing claim against the GitHub API and our own repo, NOT trusting the prior verification section. All confirmed; one nuance added.

- **License — CONFIRMED MIT, file-level.** `gh api repos/noahshinn/reflexion` → `license_spdx: "MIT"`, `license_name: "MIT License"`. Decoded raw `/contents/LICENSE` blob → begins "MIT License / Copyright (c) 2023 Noah Shinn / Permission is hereby granted, free of charge ...". SPDX = **MIT**. The GPL/AGPL copyleft caveat in the task is **moot here** — MIT is permissive, vendoring is legally allowed with attribution. (We still advise against vendoring on architecture grounds, not license grounds.)
- **Stars — CONFIRMED.** `stargazers_count = 3167` (gh api, 2026-05-29). Survey's "3,167" is exact. Order of magnitude 10^3. Not inflated.
- **Status — CONFIRMED.** `archived: false`, `fork: false`, `pushed_at: 2025-01-14T07:54:02Z`, `default_branch: main`.
- **"Not installable" — CONFIRMED.** Root contents = `.gitignore, .gitmodules, LICENSE, README.md, alfworld_runs, figures, hotpotqa_runs, programming_runs, webshop_runs`. Explicitly checked: `setup.py` absent, `pyproject.toml` absent, root `requirements.txt` absent. Per-task `requirements.txt` only (e.g. `alfworld_runs/requirements.txt`, `hotpotqa_runs/requirements.txt`). Research scaffolding, not a package.
- **Submodules — CONFIRMED.** `.gitmodules` declares two: `programming_runs/lazzzy` → GammaTauAI/lazzzy, and `programming_runs/executors/leetcode_env` → GammaTauAI/leetcode-hard-gym.
- **Per-task duplication — CONFIRMED.** `env_history.py` and `generate_reflections.py` both present under `alfworld_runs/` (recur per task dir; no shared lib).
- **OpenAI-locked — CONFIRMED and reinforced by authors.** README: "Set `OPENAI_API_KEY` ... export OPENAI_API_KEY=<your key>" and the authors' own caveat: "it may not be feasible for individual developers to rerun the results as GPT-4 has limited access and significant API charges." No Anthropic/MLX path. "Run as benchmark = NO/skip" is correct and reinforced by the authors themselves.
- **Reuse-pattern — PRESSURE-TESTED, HOLDS; effort overstated in our favor.** Verified `harness/intervention/` contains `rvr.py, naive_retry.py, decoy_list.py, framework_default.py`, all pure functions with the identical signature `(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action` (confirmed by reading `rvr.py` and `naive_retry.py` directly). A Reflexion-style ungrounded-self-reflection baseline is a new sibling file returning `Action(kind=ActionKind.RE_PROMPT, feedback=<self-reflection prompt>)` instead of RVR's registry list — ~25 lines, zero import from their repo. Survey's "~0.5 day, do not vendor" is correct and conservative; realistically <1 hour. Reuse value is the *prompt structure / bounded-memory idea*, reimplemented clean-room.

**Over-optimism check:** none found. The survey is, if anything, conservative on effort and is appropriately pessimistic on "run as benchmark." No claim overstated stars, license permissiveness, or usability. The only correction I'd flag is purely framing: the task's GPL/AGPL copyleft worry does not apply (license is MIT), so the "can cite/run-externally but not vendor" restriction is NOT license-imposed here — any do-not-vendor recommendation is an architecture/cleanliness choice.

**Verdict:** `cite-only` (repo as artifact; mandatory NeurIPS 2023 prior-art citation), with a clean-room Reflexion-style reflection baseline implemented natively in our harness. SPDX **MIT**, license_confirmed TRUE, confidence **HIGH**.
