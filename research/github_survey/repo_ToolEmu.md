# Repo Survey: ToolEmu

- **Repo:** ryoungj/ToolEmu
- **Canonical URL:** https://github.com/ryoungj/ToolEmu (live, not 404)
- **Stars:** 204 (gh api, 2026-05-29)
- **License:** Apache-2.0 (SPDX, permissive — safe to vendor/cite)
- **Last push:** 2024-03-22 (effectively unmaintained for ~2 years)
- **Venue:** ICLR'24 Spotlight
- **Category:** benchmark

## What it is
An LM-based **emulation** framework for surfacing *safety* risks of tool-using LM
agents. A strong LM (GPT-4 in the paper) emulates tool execution in a virtual
sandbox from tool specs + inputs alone — no real tool implementations. Two LM
judges score each trajectory: a **safety evaluator** (quantifies risk severity of
agent failures) and a **helpfulness evaluator** (effectiveness), capturing the
safety/helpfulness tradeoff.

Benchmark assets shipped in-repo:
- **36 toolkits / 311 tools** (`assets/all_toolkits.json`)
- **144 curated test cases** (`assets/all_cases.json`), many adversarial/red-team
- Includes a "standard" and an "adversarial" emulator that actively probes for
  failure-triggering tool outputs.

Code layout (Python, `pip install -e .`): `toolemu/agents/*` (zero-shot +
virtual-execution agent executors built on LangChain), `toolemu/evaluators.py`,
`toolemu/prompts/*` (heavily structured prompt library: agent / simulator /
safety+help evaluator / generator), `scripts/{emulate,evaluate,run}.py`, and a
generation pipeline to author new toolkits/cases.

## Concrete fit judgments for SCALE (TEHR / RVR paper)

### Run as an extra benchmark? NO (low value, high effort)
Different axis from ours. TEHR measures **tool-existence hallucination** (agent
calls a tool not in the registry) on BFCL/tau-bench multi-turn. ToolEmu measures
**safety risk** of agents that misuse *real* (emulated) tools. It does not emit a
per-call existence signal and has no notion of an out-of-registry call as the unit
of analysis. Wiring it as another benchmark would mean adopting its LM-judge
safety/help scoring, which is orthogonal to our headline metric.

### Reuse a component in our harness? MAYBE — the tool registry, not the runner
- **Useful:** `assets/all_toolkits.json` (36 toolkits, 311 tools) is a clean,
  large, machine-readable tool-spec corpus. We can mine it to (a) build a richer
  tool registry for a TEHR stress test, and (b) construct *distractor / decoy*
  tool names to measure hallucinated calls under registry pressure — a cheap way
  to add breadth beyond BFCL/tau-bench tool sets. Apache-2.0 makes this clean.
- **NOT useful as-is:** the agent/emulation runner is pinned to
  `langchain==0.0.277` and `anthropic==0.3.6` (pre-Messages-API, pre-Claude-3).
  It will **not** run our Anthropic 4.x or MLX/Qwen3 models without a substantial
  port off legacy LangChain. Effort to revive the runner is high; do not adopt it.

### Reuse as a baseline? NO
It is not a tool-hallucination detector or an intervention. There is no baseline
here comparable to RVR.

### Cite as prior art? YES — and differentiate
Strong, well-known related work for the "risks of tool-using agents" framing.
Cite to position SCALE: prior agent-safety eval (ToolEmu) uses an **LM judge** to
score *misuse of available tools*, whereas TEHR is a **deterministic, per-call**
metric for a *distinct* failure mode (fabricating nonexistent tools), and RVR is a
concrete, cheap intervention. Good contrast: LM-judge risk severity vs. our
ground-truth registry check (no judge variance).

### Borrow a pattern for the paper-revision skill / reviewer personas? YES (modest)
- `toolemu/prompts/text/safety_evaluator.md` and `helpfulness_evaluator.md` are
  rubric-style LM-judge prompts with explicit severity scales and step-by-step
  evaluation instructions — a good template for **reviewer-persona rubrics** and
  for structuring a "score-then-justify" critique in the paper-revision skill.
- The adversarial-simulator prompt (`adversarial_simulator.md`) is a reusable
  pattern for an **adversary reviewer persona** that actively hunts for the
  weakest failure mode rather than scoring neutrally.

## Risk / effort summary
- **License risk:** low. Apache-2.0, permissive, attribution only.
- **Maintenance risk:** high. ~2 yrs stale; pinned to obsolete LangChain/Anthropic
  SDKs. Treat code as read-only reference; only the JSON assets and prompt rubrics
  are low-effort to reuse.
- **Net:** cite-as-prior-art (primary), plus low-effort reuse of (a) the toolkit
  JSON for a TEHR registry/distractor stress test and (b) the evaluator-prompt
  rubric pattern for reviewer personas. Do not run it, do not adopt its runner,
  not a baseline.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verifier: independently confirmed all load-bearing claims against the live repo
via `gh api` (metadata + raw file contents) and the README.

**License — CONFIRMED Apache-2.0, with a caveat the survey missed.**
- Read the raw `LICENSE` file bytes: it is verbatim "Apache License, Version 2.0".
  `gh api .../license` returns SPDX `Apache-2.0`. So the headline is correct and
  permissive — safe to vendor with attribution.
- HOWEVER: `setup.py` classifiers declare `"License :: OSI Approved :: MIT
  License"`. This is an internal inconsistency the survey did not flag. The
  top-level LICENSE file controls (Apache-2.0), and MIT is also permissive, so
  there is no GPL/AGPL contamination risk either way — vendoring the JSON assets
  is clean. But this is a sloppiness signal; if we vendor anything, retain the
  Apache-2.0 NOTICE/attribution and do not rely on the setup.py classifier.

**Stars — CONFIRMED.** 204 (gh api, 2026-05-29). Order of magnitude 10^2
(hundreds). Survey accurate. Not archived; not a fork. Last push 2024-03-22
confirmed → ~2 yrs stale, survey accurate.

**Asset counts — survey UNDER-states the shipped data (copied paper/README
numbers, not the JSON).** Survey says "36 toolkits / 311 tools". The actual
shipped `assets/all_toolkits.json` parses to **38 toolkits / 330 tools**. The
README/paper also say "36 (311)", so the survey faithfully copied the headline
but did not verify the file. Test cases: **144 confirmed** (matches). Net effect
is favorable — the reusable corpus is slightly larger than advertised — but the
survey should have cited the JSON, not the paper.

**"Cite-only / do-not-run" pressure test — UPHELD, and the runnability barrier is
WORSE than a dependency pin.** Confirmed `requirements.txt` pins
`langchain==0.0.277`, `anthropic==0.3.6` (pre-Messages-API, pre-Claude-3),
`openai` unpinned, `python_requires=">=3.6"`. Beyond stale pins:
- Running the emulator AND both LM judges REQUIRES GPT-4 (README: "a strong LM
  (e.g. GPT-4)"; cost ~$1.2/test case). The framework is OpenAI-API-first.
- Anthropic is only a legacy alternative via the pinned `anthropic==0.3.6` SDK —
  it will NOT drive our Anthropic 4.x (Messages API) without a port, and there is
  **no path at all** to drive MLX/Qwen3 local models: the agent/simulator/judge
  stack is hard-wired to hosted LangChain LLM wrappers, not a local-inference
  backend. Our MLX+API harness cannot adopt this runner as-is.
- Conclusion: we CAN cite it and, if we ever wanted its numbers, run it
  externally against GPT-4 (cost + a LangChain revival). We should NOT try to
  wire it into our harness as a benchmark or baseline. The survey's
  "cite-as-prior-art + reuse JSON assets + reuse prompt rubrics, do not run"
  verdict holds.

**Verdict:** `include-parts` — cite as prior art (primary use) AND vendor the
Apache-2.0 JSON assets (`all_toolkits.json` = 38 toolkits/330 tools;
`all_cases.json` = 144 cases) for a TEHR registry/distractor stress test, plus
optionally borrow the evaluator-prompt rubric pattern for reviewer personas. Do
NOT run the emulator in-harness; do NOT use as a baseline (it is a safety-risk LM
judge, orthogonal to per-call TEHR). License permits vendoring (Apache-2.0,
permissive — NOT a GPL/AGPL situation). Confidence: high.

---

## ADVERSARIAL RE-VERIFICATION #2 (2026-05-29, second independent pass)

Second verifier: re-checked every load-bearing claim from scratch against the
live repo (raw file bytes + `gh api`), did NOT trust the survey or the first
verification block. All four targets re-confirmed; one prior claim sharpened.

**License — CONFIRMED Apache-2.0 (SPDX), read from the actual LICENSE file.**
- Raw `LICENSE` bytes begin verbatim: "Apache License / Version 2.0, January
  2004 / http://www.apache.org/licenses/". `gh api repos/ryoungj/ToolEmu/license`
  → spdx `Apache-2.0`, name "Apache License 2.0". The top-level LICENSE controls.
- Independently re-confirmed the setup.py inconsistency: `setup.py` classifier is
  literally `"License :: OSI Approved :: MIT License"`. Apache-2.0 (LICENSE) vs
  MIT (classifier) — both OSI permissive, NEITHER is GPL/AGPL. There is **no
  copyleft contamination risk**; vendoring the JSON assets into our permissive
  codebase is clean. Practical hygiene: keep the Apache-2.0 NOTICE/attribution on
  anything vendored; ignore the stray MIT classifier.

**Stars — CONFIRMED, order of magnitude correct.** `gh api` → 204 stars
(2026-05-29) = 10^2, "hundreds". `archived:false`, `fork:false`. `pushed_at`
2024-03-22 → ~2 yrs stale. Survey's stars/staleness claims are accurate, not
inflated.

**Asset counts — survey is WRONG-LOW; corrected counts re-confirmed.** Pulled
both JSONs and parsed them myself: `all_toolkits.json` = **38 toolkits / 330
tools** (survey/paper say "36 / 311" — survey copied the paper headline and never
parsed the file). `all_cases.json` = **144 cases** (matches). The error is
favorable (more reusable data than advertised) but is a real "trust-the-paper-
not-the-artifact" miss in the original survey.

**Runnability / "cite-only" pressure test — UPHELD and HARDENED. The original
survey UNDER-stated the barrier.** I read `toolemu/utils/llm.py` directly:
- LLM loading is `from langchain.chat_models import ChatOpenAI, ChatAnthropic`
  and `from langchain.llms import VLLM, OpenAI` — the **pre-0.1 LangChain import
  path that no longer exists in modern LangChain**. The whole agent/simulator/
  dual-judge stack routes through these legacy wrappers (`load_openai_llm`
  switches on model-name substrings: "claude"→ChatAnthropic, "vicuna"→VLLM,
  else→ChatOpenAI).
- This is NOT merely a stale pin (the framing in the first block). It is
  **architectural coupling to a removed LangChain API**. There is NO local-
  inference backend: the only "local-ish" path is the legacy `langchain.llms.VLLM`
  wrapper expecting a vLLM *server* — there is **no MLX path and no MLX-compatible
  abstraction** to add one cheaply. Driving our Anthropic 4.x (Messages API) or
  MLX/Qwen3 requires a from-scratch port of the executor/judge stack off
  `langchain==0.0.277` + `anthropic==0.3.6`.
- Cost/orientation re-confirmed: emulator + both judges are designed around a
  strong hosted LM (GPT-4 in the paper); it is OpenAI-API-first. Even running it
  "externally" against our API keys means reviving dead LangChain, not a
  drop-in.
- Net: our MLX+API harness **cannot** run or reuse the *runner* without a
  substantial port. "Do not run in-harness; do not use as a baseline" holds, and
  if anything the original survey was too generous in calling this a dependency-
  pin problem.

**Over-optimism audit (penalties applied):**
1. Asset counts copied from the paper, not verified against the JSON (36/311 vs
   actual 38/330) — minor, favorable direction, but a verification miss.
2. setup.py MIT-vs-LICENSE-Apache inconsistency unflagged in the original survey
   — caught by verification block #1, re-confirmed here; immaterial to risk
   (both permissive) but a sloppiness signal.
3. Runnability framed as "stale pins / high effort" understated the real blocker
   (coupling to a deleted LangChain API + zero local/MLX backend). Verdict
   unchanged but the reason is stronger.
None of these flip the recommendation.

**FINAL VERDICT (verifier #2):** `include-parts`, confidence **high**.
- USE: (a) cite as prior art — LM-judge agent-*safety* eval, explicitly
  orthogonal to per-call deterministic TEHR; good contrast (judge variance vs
  ground-truth registry check). (b) Vendor the Apache-2.0 JSON assets
  (`all_toolkits.json` = 38 toolkits/330 tools; `all_cases.json` = 144 cases) as
  a tool-spec corpus for a TEHR registry/distractor stress test — license-clean,
  low effort. (c) Optionally borrow the evaluator-prompt rubric pattern for
  reviewer personas.
- DO NOT: run the emulator in our harness, use it as a baseline (not a
  hallucination detector, no RVR-comparable intervention), or drive it with
  MLX/Qwen3 (no local backend) or Anthropic 4.x (legacy SDK) without a full port.
- License: Apache-2.0 confirmed (SPDX), permissive — vendoring into our codebase
  is permitted. NOT GPL/AGPL, so no "external-only" copyleft restriction applies.
