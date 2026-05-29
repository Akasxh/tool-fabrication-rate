# Repo survey: apple/ToolSandbox

- URL: https://github.com/apple/ToolSandbox
- Paper: "ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities" — arXiv:2408.04682 (Apple, 2024)
- Stars: 252 | Forks: 29 | Open issues: 3 | Language: Python
- Created 2024-07-30; last push 2025-11-07 (still maintained); not archived
- License: **NOT OSI / NOT SPDX-recognized.** GitHub reports `NOASSERTION`. The
  LICENSE file is a **custom Apple Sample Code-style license** ("Copyright (C)
  2024 Apple Inc."). It grants use, reproduction, modification and
  redistribution in source/binary forms, but: (a) prohibits use of Apple's
  name/marks for endorsement, (b) grants **no patent rights**, (c) is an
  Apple-bespoke license, not Apache-2.0/MIT/BSD. Treat as research-use-permitted
  but NOT a standard permissive license — see risk below.

## What it is
Python-native, **stateful, multi-turn** tool-use benchmark. Core abstractions:
- **Execution Context** = world state (device settings like WiFi/cellular,
  contacts, messages, reminders) that persists and mutates across turns.
- **Tools** = real Python functions (contacts, messaging, reminders, settings,
  search: weather/stock/location, utilities) — not stateless web stubs.
- **Message Bus** connecting User, Agent, Execution Environment.
- **Built-in LLM user simulator** for on-policy conversational evaluation (the
  user is itself a model that responds to the agent).
- **Milestone DAG + Minefields** evaluation: trajectory is matched against
  required intermediate/final milestones (snapshot_similarity,
  addition_similarity, etc., aggregated via geometric mean) and penalized for
  hitting minefields.

Categories stress-tested: **State Dependency, Canonicalization, Insufficient
Information**, plus axes for tool-call count and user-turn count.

Models evaluated in paper: Claude 3 (Haiku/Sonnet/Opus), GPT-3.5/4/4o,
Gemini 1.0/1.5(+Flash), Cohere Command R, Gorilla, Hermes, Mistral.
Headline finding: large open-vs-proprietary gap; State Dependency /
Canonicalization / Insufficient Information remain hard for SOTA.

How to run: `pip install`, set API keys, then
`tool_sandbox --user [model] --agent [model] --scenario [name]`.

## Relevance to our paper (TEHR / RVR on BFCL multi-turn)
Strongly adjacent. ToolSandbox is the closest "stateful multi-turn tool use"
benchmark to BFCL multi-turn and tau-bench. Two specific hooks for us:
- **Tool-Existence Hallucination (TEHR)** maps cleanly onto ToolSandbox's
  "Insufficient Information" category and its **Minefield** concept — a call to a
  non-existent / unavailable tool is exactly the kind of event their minefield
  machinery is designed to flag.
- **RVR intervention** (re-prompt with tool registry on a bad call): ToolSandbox's
  on-policy user simulator + message bus is a natural second environment to show
  RVR generalizes beyond BFCL.

## Concrete verdict
- **RUN as extra benchmark: YES, medium effort.** This is the highest-value use.
  It's pip-installable Python, supports Anthropic + OpenAI out of the box, and
  measures the same multi-turn stateful tool-use we care about. Effort cost: (1)
  it uses an **LLM user simulator** (extra API spend + non-determinism — must fix
  user model and seed for reproducibility); (2) our harness loads benches via
  `harness/bench_loaders/*.py`, so we'd write a `toolsandbox.py` loader OR run
  their CLI and post-process trajectories to extract per-call TEHR; (3) MLX/local
  Qwen3 models are NOT first-class — we'd need to wrap our MLX models behind an
  OpenAI-compatible endpoint to plug into their agent interface. Budget a few
  days of integration, not hours.
- **Reuse a COMPONENT in harness: PARTIAL.** The Milestone-DAG/Minefield
  evaluator and message-bus design are worth studying, but pulling their code in
  is encumbered by the non-standard Apple license (see risk). Safer to
  re-implement the minefield-for-nonexistent-tool idea ourselves than vendor it.
- **BASELINE: YES (as a benchmark axis), not as a method.** ToolSandbox is an
  environment, not a baseline intervention to compare RVR against. Use it as an
  additional evaluation surface; RVR is still measured against no-intervention.
- **PRIOR ART / CITE: YES, mandatory.** Direct prior art on stateful conversational
  tool-use eval and on the failure taxonomy. Cite to (a) position TEHR within an
  established failure taxonomy (their "Insufficient Information"/minefields), and
  (b) justify breadth ("we evaluate on BFCL, tau-bench, and ToolSandbox").
- **PATTERN for paper-revision skill / reviewer personas: YES, light.** The
  Milestone/Minefield rubric is a good template for a reviewer persona that
  checks "is the failure mode operationalized as a checkable predicate?" and for
  arguing construct validity of TEHR.

## License risk (be honest)
Medium. The license permits research use, modification and redistribution, so
**running it and citing it for the paper is fine**. The risks are: (1) it is NOT
Apache/MIT — copying their evaluator source into our harness/repo means shipping
Apple-licensed code under non-standard terms, which complicates our own repo's
license story for an open-source artifact release; (2) **no patent grant**; (3)
endorsement clause forbids implying Apple endorsement. Recommendation: RUN it as
an external dependency / cite it; do NOT copy their source into our distributed
harness. If we want their minefield logic, re-implement from the paper.

## Bottom line
Best treated as **run-as-benchmark + cite-as-prior-art**, medium effort. It
directly broadens our main-track story (a third stateful multi-turn tool-use
benchmark) and its minefield/insufficient-info taxonomy gives TEHR external
grounding. Avoid vendoring its code due to the non-standard Apple license.

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verified against the live repo (GitHub API + raw LICENSE + README), not the survey summary.

### License — CONFIRMED, classification sharpened
- SPDX: **NOASSERTION**. GitHub API returns `license.key = "other"`,
  `spdx_id = "NOASSERTION"`. Not an OSI/SPDX-recognized license. Survey was correct.
- LICENSE file opens verbatim: *"Copyright (C) 2024 Apple Inc. All Rights Reserved."*
  followed by the Apple Sample Code-style agreement. Confirmed it is a CUSTOM
  APPLE license, NOT Apache/MIT/BSD/GPL/AGPL.
- IMPORTANT NUANCE vs the task framing: this is **NOT GPL/AGPL**. It is
  permissive-LEANING. Grant clause (verbatim): *"Apple grants you a personal,
  non-exclusive license, under Apple's copyrights in this original Apple software
  ... to use, reproduce, modify and redistribute the Apple Software, with or
  without modifications, in source and/or binary forms."* It permits source +
  binary redistribution AND commercial use — so there is no copyleft obligation
  forcing our repo to relicense.
- BUT the real encumbrances stand: (a) **explicit NO patent grant** — verbatim:
  *"no other rights or licenses, express or implied, are granted by Apple herein,
  including but not limited to any patent rights..."*; (b) trademark/endorsement
  restriction; (c) it is a non-standard text, so vendoring it into our (likely
  Apache/MIT) artifact means shipping a file under bespoke Apple terms — a
  license-hygiene headache, not a copyleft violation. Survey's "do not vendor,
  run/cite externally" recommendation is CORRECT, though its phrasing slightly
  over-weights the risk: this is closer to a permissive-with-caveats license than
  to a viral one.

### Stars / metrics — CONFIRMED
- Stars: 252 (API). Forks: 29. Open issues: 3. Language: Python. Order of
  magnitude (low hundreds) confirmed — this is a small research repo, not a
  widely-adopted standard. Survey accurate.
- Created 2024-07-30, last push 2025-11-07, not archived. "Still maintained"
  claim is defensible (push within ~6 months). Survey accurate.

### "Run-as-benchmark" claim — CONFIRMED but with a HARDER caveat the survey soft-pedaled
- pip/conda installable, Anthropic + OpenAI first-class. TRUE.
- Local/open-weight models: ONLY via vLLM's OpenAI-compatible server
  (`OPENAI_BASE_URL`). **There is NO MLX path and no Apple-Silicon model-serving
  path** — the "arm64 Miniforge" note is for the Python env only. To run our
  4-bit Qwn3 MLX models we'd have to (a) re-serve them through vLLM/an
  OpenAI-compatible shim, OR (b) stand up our own adapter. Our existing MLX
  loader does NOT plug in directly. Survey flagged this but framed it as "wrap
  behind an OpenAI endpoint, a few days" — realistic, but note MLX 4-bit weights
  may not load cleanly under vLLM, so the shim is non-trivial.
- HARDEST caveat, under-stated by survey: the **user simulator is GPT-only**
  (GPT-3.5 / GPT-4 / GPT-4o, each requiring `OPENAI_API_KEY`). Every run incurs
  mandatory OpenAI API spend for the *user* role regardless of which agent we
  test, and introduces a proprietary, version-drifting dependency in the eval
  loop (reproducibility risk if OpenAI deprecates the pinned snapshot). Our MLX
  models can only occupy the AGENT role, never the user. This is a real cost +
  reproducibility tax the survey mentioned only as "extra API spend +
  non-determinism."

### Net adjustment to recommendation
Survey's overall verdict (run-as-benchmark + cite-as-prior-art, medium effort,
do-not-vendor) holds and is NOT over-optimistic on the headline. Two corrections:
(1) license is permissive-custom, not copyleft — vendoring risk is hygiene, not
legal contamination; (2) integration effort is genuinely MEDIUM-to-HIGH for *our*
stack specifically because of the GPT-only simulator + no-MLX serving, not the
"few days, easy" tone. Recommend: **run-as-benchmark** (third stateful
multi-turn surface) + cite, but treat as a later-phase breadth item, not a
quick win, and never vendor its source.

---

## ADVERSARIAL VERIFICATION #2 (2026-05-29, second independent re-check, Opus)

Re-verified from PRIMARY sources (live GitHub API, raw LICENSE, raw README, and
source files in `tool_sandbox/roles/`) — NOT from the survey or the prior
addendum. Also cross-checked against OUR harness code. The task framing
hypothesised a "GPL/AGPL" license; that is FALSE for this repo (see below) —
but the underlying do-not-vendor instinct still applies for a different reason.

### License — INDEPENDENTLY CONFIRMED
- GitHub API `/license`: `key="other"`, `name="Other"`, **`spdx_id="NOASSERTION"`**,
  `url=null`. There is NO valid SPDX identifier. Anyone writing `Apache-2.0`/`MIT`
  in a survey would be wrong.
- Raw LICENSE first line (verbatim): *"Copyright (C) 2024 Apple Inc. All Rights
  Reserved."* It is the **Apple Sample Code-style license**. Grant (verbatim):
  *"Apple grants you a personal, non-exclusive license ... to use, reproduce,
  modify and redistribute the Apple Software, with or without modifications, in
  source and/or binary forms."* Explicitly **NO patent grant** (verbatim: *"no
  other rights or licenses ... including but not limited to any patent rights"*)
  and a trademark/endorsement restriction.
- VERDICT ON TASK FRAMING: **Not GPL, not AGPL, not copyleft.** It is
  permissive-LEANING but non-standard. So the task's "GPL/AGPL → cite/run only,
  never vendor" rule does not apply on copyleft grounds. HOWEVER the practical
  conclusion is the same: do NOT vendor it, because (a) shipping a bespoke
  Apple-licensed file inside our (intended Apache/MIT) artifact is a
  license-hygiene problem reviewers/legal will flag, and (b) the no-patent-grant
  clause is worth avoiding in a redistributed research artifact. Cite + run
  externally; re-implement the minefield idea from the paper if we want it.
- Side note: our repo currently has NO root LICENSE file
  (`/Users/cero/Desktop/PROJECTS/icml/LICENSE*` does not exist). We must add our
  own (permissive) license before any artifact release regardless.

### Stars / metrics — INDEPENDENTLY CONFIRMED
- API live values: **stars 252, forks 29, open issues 3, language Python,
  archived=false, created 2024-07-30, pushed 2025-11-07.** Order of magnitude
  (low hundreds) confirmed — a small Apple research repo, NOT a community
  standard like BFCL. No inflation in the survey.

### "Run-as-benchmark" — CONFIRMED runnable in general, but NOT cleanly on OUR stack
Verified at source-file granularity (`tool_sandbox/roles/`):
- Agent roles are provider-specific Python classes: `anthropic_api_agent.py`,
  `openai_api_agent.py`, `cohere_agent.py`, `gemini_agent.py`,
  `gorilla_api_agent.py`, `hermes_api_agent.py`, `mistral_api_agent.py`. Anthropic
  + OpenAI are first-class. CONFIRMED.
- **USER SIMULATOR IS GPT-ONLY AND HARDCODED.** The only user role file is
  `openai_api_user.py`; it pins base URL `https://api.openai.com/v1` and exposes
  exactly `GPT_3_5_0125_User`, `GPT_4_0125_User`, `GPT_4_o_2024_05_13_User`. There
  is NO provider abstraction — using a non-OpenAI user requires writing a new
  subclass/role. CONFIRMED HARDER than the survey implied: every ToolSandbox run
  incurs MANDATORY OpenAI spend for the user turn + a version-drifting proprietary
  dependency in the eval loop. Reproducibility tax is real.
- **No MLX / Apple-Silicon serving path.** Local/open-weight models are supported
  ONLY via vLLM's OpenAI-compatible server (`OPENAI_BASE_URL`). NEW, CONCRETE
  blocker found by reading OUR code: our `harness/adapters/mlx_adapter.py` calls
  `mlx_lm.generate` IN-PROCESS (default `mlx-community/Qwen3-8B-4bit`); it is not
  an HTTP server. To put our 4-bit Qwen3 in the AGENT seat we must either (a) front
  `mlx_lm` with an OpenAI-compatible HTTP shim AND author a new ToolSandbox agent
  role (their OSS roles hardcode Gorilla/Hermes/Mistral prompt+tool-parse formats,
  so Qwen3 won't drop into an existing role), or (b) re-serve via vLLM — but
  vLLM cannot load MLX 4-bit weights (different quant format), so we'd re-quantize.
  Either path is real engineering, NOT a few hours.
- ADDITIONAL stack mismatch: our tau-bench loader already uses an Anthropic
  Haiku user simulator (`harness/bench_loaders/_tau_user_simulator_haiku.py`).
  ToolSandbox forces the OPPOSITE convention (GPT user). So we cannot reuse our
  existing user-sim plumbing; the eval loops are not interoperable.

### FINAL VERDICT (this re-check)
Prior survey + addendum are directionally correct and NOT over-optimistic on the
headline; both correctly say run-as-benchmark + cite + do-not-vendor. My
corrections/sharpenings: (1) license is permissive-custom Apple Sample Code,
spdx=NOASSERTION — explicitly NOT GPL/AGPL, so vendoring concern is hygiene +
no-patent-grant, not copyleft; (2) the run-as-benchmark claim survives but the
effort is MEDIUM-HIGH and *front-loaded with cost/repro risk* for OUR MLX+API
harness specifically — GPT-only hardcoded user simulator (mandatory OpenAI spend
every run) + no MLX serving path + need for a new Qwen3 agent role. Recommend:
**run-as-benchmark** as a later-phase breadth surface + **cite as prior art**;
do NOT vendor its source; budget it as a non-trivial integration, not a quick win.
Confidence: HIGH (all claims checked against primary sources + our own code).
