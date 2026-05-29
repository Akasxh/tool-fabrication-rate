# Repo survey: tau-bench

- **Repo:** sierra-research/tau-bench
- **Canonical URL:** https://github.com/sierra-research/tau-bench (live, not 404)
- **Stars:** 1,249 (gh api, 2026-05-29) · forks 200 · open issues 46 · last push 2026-03-18 · not archived
- **License:** MIT (SPDX `MIT`, confirmed via `gh api .../license`; LICENSE file also vendored in our tree)
- **Category:** benchmark

## What it is
τ-bench ("A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Sierra
Research / Yao et al.). Measures an agent's ability to complete multi-turn tasks in
realistic domains (retail, airline) where the agent must (a) call domain tools against
a stateful mock DB, (b) talk to an **LLM-simulated user** that reveals info
incrementally, and (c) follow a domain policy. Scoring is **outcome-based**: a reward
oracle compares final DB state + required output strings against a gold `actions` list,
plus a `pass^k` reliability metric over repeated trials. Tools are exposed as
OpenAI-style function schemas. The companion τ²-bench extends this to dual-control.

## Integration status in OUR harness (key finding)
**This repo is already vendored and fully wired in.** It is not a candidate to evaluate —
it is a shipped dependency:
- Data clone (with its MIT LICENSE) at `/Users/cero/Desktop/PROJECTS/icml/harness/data/tau_bench_retail/` (its own `.git`).
- Loader `/Users/cero/Desktop/PROJECTS/icml/harness/bench_loaders/tau_bench.py` — yields retail tasks as our `Task` type; splits test(115)/dev(20)/train(500); stubs the `litellm`-importing package `__init__`s so we import only needed submodules; builds the canonical tool registry from `ALL_TOOLS.get_info()`.
- User-sim replacement `/Users/cero/Desktop/PROJECTS/icml/harness/bench_loaders/_tau_user_simulator_haiku.py` — `HaikuUserSimulator` drops in for τ-bench's GPT-4o `LLMUserSimulationEnv` via the Anthropic SDK, with cost metering; `patch_tau_bench_user_loader` monkey-patches `load_user` in both `tau_bench.envs.user` and `.base`.
- Runner `/Users/cero/Desktop/PROJECTS/icml/harness/runner/executors.py` (`make_tau_bench_executor`, `_resolve_tau_env_class`) owns env lifecycle; `cli.py` registers `tau_bench` in the benchmark set; `loop.py` scopes the RVR intervention + TEHR registry augmentation to `tau_bench`.

So the engineering for "run tau-bench retail as an extra benchmark" is **done**; remaining cost is just running it (API spend on agent + Haiku user-sim).

## Concrete reuse verdict
- **RUN as extra benchmark:** YES — already plumbed. τ-bench retail is our second multi-turn benchmark alongside BFCL, directly serving the "more benchmarks" ICML-breadth goal. Airline domain is an easy add (same loader pattern, just swap `tau_bench.envs.retail` → `airline` modules). Effort to add airline: low.
- **Reuse COMPONENT:** YES, already done — the mock domain env + reward oracle + tool registry are reused verbatim; we replaced only the user simulator.
- **Use as BASELINE:** YES indirectly — τ-bench's published pass^k / per-domain success numbers and its GPT-4o user-sim are prior-art reference points. Note our headline metric (per-call TEHR) is *our* instrumentation layered on top, not τ-bench's native metric, so τ-bench scores are context, not a head-to-head TEHR baseline.
- **CITE as PRIOR ART:** YES, mandatory — it's the source benchmark; cite Yao et al. τ-bench (and τ²-bench for the dual-control extension) when describing the multi-turn tool-use setting and the LLM-user-simulator design.
- **PATTERN for paper-revision skill / reviewer personas:** MARGINAL. The transferable idea is τ-bench's **outcome-based + pass^k reliability** evaluation philosophy (judge final state, measure run-to-run variance) — useful framing for a reviewer persona that probes reliability/variance claims. No code reuse for the skill.

## Effort & license risk
- **License risk: LOW.** MIT, permissive; we vendor its LICENSE. Standard attribution + retain copyright notice is sufficient. Safe to ship in artifact.
- **Effort: LOW** for what we already have (run it); **LOW** to add the airline domain; **MED** if we wanted to adopt τ²-bench dual-control.
- **Watch-outs:** (1) upstream `__init__` chain pulls `litellm` — we deliberately stub it; if we re-pull upstream, re-verify the stub targets. (2) User-sim swap means our numbers are NOT directly comparable to τ-bench leaderboard numbers (different user model: Haiku 4.5 vs GPT-4o) — must disclose in the paper. (3) Pin the vendored commit in `repro_manifest` for reproducibility (last upstream push 2026-03-18).

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent)

**Method:** Did not trust the survey summary. Re-checked license against the actual
vendored `LICENSE` file (not just the GitHub-detected label), re-pulled repo metadata,
and ran the loader + tests against our real `.venv` to pressure-test "run-as-benchmark".

**License — CONFIRMED `MIT` (SPDX).** Three independent sources agree:
- `gh api repos/sierra-research/tau-bench` → `license.spdx_id: MIT`, `license.key: mit`.
- `gh api .../license` endpoint → `MIT License`.
- Actual vendored file `/Users/cero/Desktop/PROJECTS/icml/harness/data/tau_bench_retail/LICENSE`
  read byte-for-byte: standard MIT text, "Copyright (c) 2024 Sierra". No
  Commons-Clause / no "additional terms" rider appended (a common gotcha — absent here).
- **No GPL/AGPL contamination.** Permissive; we MAY vendor it into our codebase (we
  already do). Only obligation: retain the copyright + permission notice, which we do.

**Stars — CONFIRMED order-of-magnitude (10^3).** Live count 1,249 (forks 200, open
issues 46, not archived, last push 2026-03-18). Survey's "1,249" is exact and correct.

**run-as-benchmark — CONFIRMED, not over-stated.** Pressure-tested live:
- Loader imports and yields tasks with NO litellm/API dependency: `load_tau_bench_retail(n=3)`
  returned 3 tasks, 16-tool registry, correct `env_class` and `user_simulator_model=claude-haiku-4-5`.
  The "stub the litellm-importing `__init__`s" strategy genuinely works — verified, not aspirational.
- `harness/tests/test_tau_bench_loader.py`: **9/9 pass** (run from repo root with PYTHONPATH).
- Runner (`make_tau_bench_executor`/`_resolve_tau_env_class`), CLI registration
  (`--benchmark tau_bench`, `["bfcl","tau_bench"]`), and `loop.py` RVR+TEHR scoping
  (`task.benchmark == "tau_bench"`) all present and consistent with the survey.
- Vendored git commit `59a200c` matches upstream `pushed_at` 2026-03-18 — the survey's
  reproducibility note is accurate; commit is pinnable.
- "Airline = easy add (low effort)": **plausible, partially confirmed.** Airline domain
  IS present in the vendored tree (`tau_bench/envs/airline/{env,tasks_test,tools,...}`),
  so it's a module-path swap as claimed. Caveat: not yet wired (loader hardcodes retail
  splits + `MockRetailDomainEnv`); "low effort" is fair but it is NEW code + a NEW test, not zero.

**Penalties / corrections to the survey:** Minimal. The survey was accurate and, if
anything, slightly conservative. Two nits, neither material:
- The botocore-related litellm import *warnings* in our venv are cosmetic (Bedrock/SageMaker
  stream decoding unavailable); they do not block the stubbed import path the loader uses.
- "run cost is just API spend" understates that the BASELINE comparison to τ-bench's
  published leaderboard is invalid (Haiku-4.5 user-sim ≠ GPT-4o user-sim). The survey does
  flag this under watch-out (2), but the "Use as BASELINE: YES indirectly" line should be
  read strictly as context/prior-art, never head-to-head.

**VERDICT: run-as-benchmark — endorsed.** Already fully plumbed, MIT-clean, vendorable
into our permissive harness, tests green. Confidence: HIGH.
