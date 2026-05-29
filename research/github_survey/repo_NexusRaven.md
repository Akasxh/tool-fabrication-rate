# Repo survey: NexusRaven

- **Repo:** nexusflowai/NexusRaven
- **Canonical URL:** https://github.com/nexusflowai/NexusRaven (URL is live, no 404)
- **Stars:** 323 (gh api, 2026-05-29)
- **License (SPDX):** split — **CODE: Apache-2.0** (`CODE_LICENSE`); **DATA: CC-BY-NC-4.0**
  (`DATA_LICENSE`, NonCommercial). This split is the single most important fact below.
- **Active:** NO. Created 2023-09-28, last push 2023-09-29 — a one-shot release dump,
  effectively abandoned for ~2.5 years. Not formally archived but dead.
- **Category:** benchmark (companion eval repo for the NexusRaven-13B model)

## What it is
The reproduction/eval framework for **NexusRaven-13B**, a 2023 open-source
single-attempt function-calling LLM from Nexusflow. The repo is not itself a
maintained benchmark suite; it's the artifact bundle that backs the model's blog
post / leaderboard claims (95% on CVE/CPE + VirusTotal cybersecurity tools vs
GPT-4's 64%, and zero-shot generalization to unseen tools at ~GPT-3.5 level).

Contents:
- `raven/eval/` — `evaluator.py`, `run_toolllm.py`, `raven_utils.py`. The eval
  harness. **Built entirely on 2023-era LangChain** (`langchain.agents`,
  `langchain.llms.HuggingFaceTextGenInference`, `OpenAIChat`, `StructuredTool`) —
  these imports are broken against any modern langchain.
- `raven/data/` — dataset standardization for ToolLLM / ToolAlpaca formats plus
  curated query/function-definition resources (`cve_cpe_*`, `virustotal_*`,
  `emailrep_*`, `toolalpaca_*`, `toolllm_*`). These pull from the HF dataset
  `Nexusflow/NexusRaven_API_evaluation` — the CC-BY-NC data.
- `scripts/` — per-baseline shell runners (`evaluate_gpt4.sh`, `evaluate_gpt3_5.sh`,
  `evaluate_gpt3_5_instruct.sh`, `evaluate_codellamainstruct.sh`,
  `evaluate_toolllm.sh`, `evaluate_toolalpaca.sh`, `evaluate_nexusraven.sh`) plus
  langchain/non-langchain usage examples.
- `docs/prompting_readme.md` — the prompt format.

Crucial structural point for us: it is **single-attempt, single-turn**
function calling. There is no multi-turn / stateful evaluation — orthogonal to our
BFCL multi-turn TEHR substrate.

## The one genuinely interesting detail
NexusRaven's prompt presents the model with **multiple `OPTION:` function blocks**
(`<func_start>...<func_end>` + docstring) and asks it to *pick one and fill args*.
This is an explicit forced-choice-over-a-tool-registry format. Conceptually it is a
clean setup for a tool-existence/selection signal, and it resembles our RVR
intervention (re-prompt with the tool registry). But it is just a prompt template,
not a metric — there's no hallucination-rate scoring here.

## Concrete judgments

### RUN as an extra benchmark? — NO (not worth it)
Three blockers: (1) the harness is dead 2023 LangChain and would need a near-total
rewrite to run; (2) it's single-turn only, so it adds no multi-turn breadth to our
story; (3) the eval data is **CC-BY-NC-4.0**, which is a poor fit for a paper that
wants clean, commercially-unencumbered, reproducible artifacts. The headline tasks
(CVE/CPE, VirusTotal) also require live external API keys. Effort to revive: HIGH;
payoff: LOW. Skip as a runnable benchmark.

### Reuse a COMPONENT in our harness? — NO
`evaluator.py` is langchain-coupled and reflects a 2023 agent abstraction we don't
use. Nothing here is cleaner than what our `harness/bench_loaders/*.py` already
does. The data-standardization utilities target ToolLLM/ToolAlpaca formats we don't
load. No component to lift.

### Reuse as a BASELINE? — Weak / historical only
NexusRaven-13B is a 2023 model long superseded on BFCL and every modern function-
calling leaderboard. It is not a meaningful contemporary baseline against Anthropic
4.x or Qwen3. At most it's a *historical reference point* ("early open-source FC
SOTA") if we want a one-line lineage sentence. Not a baseline to run or table.

### Cite as PRIOR ART? — YES, light citation
Worth a single citation as an early (2023) open-source function-calling model +
eval that argued for forced-choice-over-provided-functions and zero-shot
generalization to unseen tools. Useful to (a) establish that "pick the right tool
from a provided set" framing predates us, and (b) **differentiate**: NexusRaven
measures single-attempt task success; we isolate a *per-call Tool-Existence
Hallucination Rate (TEHR)* on *multi-turn* BFCL and add the RVR re-prompt
intervention — neither of which NexusRaven addresses. Low priority vs BFCL/tau-bench
citations, but a legitimate prior-art anchor for the "tool registry forced choice"
idea.

### Borrow a PATTERN for the paper-revision skill / personas? — Minor, one idea
The multi-`OPTION` prompt is a reusable reviewer-persona seed: a skeptic asking
"is TEHR just a side effect of how you present the tool registry? NexusRaven (2023)
already presented functions as forced-choice options — show your hallucination
result isn't an artifact of registry presentation format." That sharpens an ablation
(vary how the registry is shown to the model) and a robustness defense for RVR.
Treat as a reviewer-prompt seed, not a code pattern.

## Effort & risk summary
- **License risk:** MEDIUM. Code is clean Apache-2.0, but the **evaluation DATA is
  CC-BY-NC-4.0 (NonCommercial)** — do NOT vendor or redistribute that data in our
  harness/paper artifacts; even quoting numbers is fine for citation but the dataset
  itself is off-limits for any commercial/redistributable use. This NC restriction
  alone is reason enough not to integrate the data.
- **Effort to run:** HIGH (dead langchain rewrite + external API keys), payoff LOW.
- **Maintenance:** abandoned since 2023-09; no upstream support.
- **Verdict:** **cite-only** as light prior art (lineage + forced-choice-registry
  framing + one reviewer-persona/ablation seed). Do not run, do not vendor code or
  data, not a usable baseline.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verifier independently confirmed every load-bearing claim against ground truth
(`gh api`, raw LICENSE files, raw `pyproject.toml`, raw eval source). Survey is
ACCURATE and, if anything, not over-optimistic. Findings:

- **License — CONFIRMED, split is real and correctly stated.**
  - `CODE_LICENSE` = verbatim **Apache-2.0** (header "Apache License Version 2.0").
  - `DATA_LICENSE` = verbatim **CC-BY-NC-4.0** ("Attribution-NonCommercial 4.0
    International Public License"). The NonCommercial restriction is genuine.
  - GitHub's API only surfaces the top-level Apache-2.0 (`spdx_id: Apache-2.0`)
    and silently ignores `DATA_LICENSE`. A survey trusting the GitHub/API license
    field alone would have MISSED the NC data restriction. The survey did not — it
    read both files. Good.
  - **SPDX for our records:** code `Apache-2.0`; data `CC-BY-NC-4.0`. Because the
    most-restrictive component governs any bundled artifact, treat the repo's
    evaluation *data* as effectively non-vendorable. (Note: NC, not GPL/AGPL — so
    the *code* is permissive and could in principle be vendored; the blocker is the
    DATA license + staleness, not copyleft. The "GPL/AGPL → cite-only" concern
    raised in the task does not apply here; the functional outcome is the same
    cite-only verdict but for a different reason — NC data, not copyleft code.)

- **Stars — CONFIRMED.** `gh api` returns `stargazers_count = 323` (2026-05-29).
  Order of magnitude (hundreds) is correct; this is a low-popularity, single-drop
  repo, not a widely-adopted tool. No inflation in the survey.

- **Abandoned — CONFIRMED.** created `2023-09-28`, last push `2023-09-29`
  (~30 hours of activity, then nothing for ~2.5 yrs). `archived = false` (so "not
  formally archived" is accurate). Effectively dead.

- **Dead-LangChain coupling — CONFIRMED and stronger than the summary implies.**
  `pyproject.toml` hard-pins `langchain==0.0.294` (a Sept-2023 release).
  `raven/eval/evaluator.py` imports `langchain.tools.base.StructuredTool`,
  `langchain.llms.{OpenAI,HuggingFaceTextGenInference,OpenAIChat}`,
  `langchain.chat_models.ChatOpenAI`, `langchain.agents`, `langchain.chains.LLMChain`
  — all pre-split namespaces that DO NOT EXIST in modern langchain
  (≥0.1 / langchain-community / langchain-openai). It would not import in our env
  without a near-total rewrite. The "HIGH effort to run" judgment is correct.

- **"Can we run/reuse it given MLX+API harness?" — pressure-tested: NO, beyond just
  effort.** Even after a rewrite, (a) the LLM backends are langchain `OpenAI` /
  `HuggingFaceTextGenInference` — no MLX path and no Anthropic path; we'd be
  reimplementing the runner anyway against our own loaders. (b) It is single-turn /
  single-attempt, so it contributes zero multi-turn breadth to the TEHR story.
  (c) The eval payload is the CC-BY-NC HF dataset `Nexusflow/NexusRaven_API_evaluation`
  pulled via `load_dataset` inside the data utils — non-commercial, so not safe to
  vendor/redistribute in our artifacts. Reusing it as a runnable benchmark is not
  worth it; the cite-only call stands.

- **Reviewer-persona / ablation seed — endorsed.** The multi-`OPTION:` forced-choice
  prompt is real and is a legitimate seed for a "is TEHR an artifact of registry
  presentation?" ablation/skeptic persona. This is the one genuinely reusable idea,
  and it's a *concept*, not code or data — no license exposure.

**Adversarial verdict: AGREE with cite-only.** No survey claim was overstated.
The single correction is framing: the integration blocker is the **CC-BY-NC-4.0
DATA** license (+ dead 2023 langchain + single-turn scope), NOT a copyleft code
license — the code itself is clean Apache-2.0. Outcome unchanged: cite as light
prior art, do not run, do not vendor code or data, not a usable baseline.
Confidence: HIGH (all facts checked against raw upstream sources).

---

## ADVERSARIAL RE-VERIFICATION (2026-05-29, second independent pass)

Re-checked all load-bearing facts directly against upstream ground truth (`gh api`
repo metadata + raw file contents), without trusting the prior verification block.
All confirmed:

- **Stars = 323** (`gh api repos/nexusflowai/NexusRaven` → `stargazers_count: 323`).
  Hundreds — correct, no inflation.
- **License = SPLIT, confirmed by reading raw files (NOT trusting the API field).**
  - `CODE_LICENSE` opens verbatim "Apache License / Version 2.0, January 2004" → **Apache-2.0**.
  - `DATA_LICENSE` opens verbatim "# Attribution-NonCommercial 4.0 International" →
    **CC-BY-NC-4.0**, NonCommercial restriction is real.
  - GitHub API reports only `license.spdx_id = Apache-2.0` and silently drops the
    NC data license — a survey trusting the API alone would have missed it. This one
    did not.
- **Abandoned**: `created_at 2023-09-28`, `pushed_at 2023-09-29`, `archived: false`.
  ~30h of activity then dead. Correct.
- **Dead langchain**: `pyproject.toml` pins `langchain==0.0.294`; `evaluator.py`
  imports `langchain.llms.{OpenAI,HuggingFaceTextGenInference,OpenAIChat}`,
  `langchain.chat_models.ChatOpenAI`, `langchain.tools.base.StructuredTool`,
  `langchain.agents`, `langchain.chains.LLMChain` + `datasets.load_dataset` — all
  pre-split namespaces broken on modern langchain. Confirmed.
- **No MLX / no Anthropic backend**: LLM backends are langchain `OpenAI` /
  `HuggingFaceTextGenInference` only. Our MLX+API harness shares no runner with it;
  reusing means a full rewrite against our own loaders. Confirmed.
- **Forced-choice OPTION prompt**: confirmed in `raven/eval/raven_utils.py`
  (`prompt += f'\nOPTION:\n<func_start>def {func_signature}<func_end>...'`) and
  `docs/prompting_readme.md`. Real; usable only as an ablation/reviewer-persona seed
  (a concept, no license exposure).

**Pressure-test of cite-only / "can we run it?":** NO, and not merely on effort.
(1) single-turn/single-attempt → zero multi-turn TEHR breadth; (2) dead 2023
langchain + no MLX/Anthropic path → full rewrite to run anything; (3) eval payload
is the CC-BY-NC HF dataset `Nexusflow/NexusRaven_API_evaluation` → non-vendorable.

**Correction to task framing:** there is NO GPL/AGPL here. The code is permissive
Apache-2.0 (vendorable in principle); the integration blocker is the **CC-BY-NC-4.0
DATA** license + 2.5-yr-dead langchain + single-turn scope. Same cite-only outcome,
different cause than the copyleft scenario the task anticipated.

**Second-pass verdict: AGREE — cite-only.** Survey did not overstate stars, license,
or usability. Confidence: HIGH (every fact verified against raw upstream sources).
