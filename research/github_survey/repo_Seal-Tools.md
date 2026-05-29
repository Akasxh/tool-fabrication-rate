# Repo Survey: Seal-Tools

- **Repo:** fairyshine/Seal-Tools
- **URL:** https://github.com/fairyshine/Seal-Tools
- **Stars:** 57 (gh api, 2026-05)
- **License:** Apache-2.0 (SPDX, confirmed via `gh api .../license`) — permissive, low risk
- **Category:** benchmark / tool-learning dataset
- **Last push:** 2024-11-05 (stable, not archived, no recent activity)
- **Paper:** "Seal-Tools: Self-Instruct Tool Learning Dataset for Agent Tuning and Detailed
  Benchmark" — NLPCC 2024 (arXiv:2405.08355, Springer LNCS 10.1007/978-981-97-9434-8_29)

## What it is

A self-instruct-generated tool-learning dataset + benchmark. The pipeline generates ~4076
API-like tools across many fields, then synthesizes queries whose gold answers are tool-call
sequences — including **hard instances that call multiple tools, some nested** (output of one
call feeds another, referenced as `API_call_N`).

### Dataset sizes (line counts of the jsonl)
- `tool.jsonl`: 4076 tool specs (api_name, api_description, field, typed parameters, required)
- `train.jsonl`: 12022 instances
- `dev.jsonl`, plus two test splits:
  - `test_in_domain.jsonl`: 700 instances
  - `test_out_domain.jsonl`: 654 instances (tools/fields unseen in train — generalization)
- Also ships `dataset_for_finetune` (chat-format) and `dataset_in_old_format`.

### Data format (canonical)
Query row:
```json
{"id":"test_in_domain-easy-0","query":"Retrieve information about postmodern theory.",
 "calling":[{"api":"getPostmodernTheory","parameters":{},"responses":["API_call_0"]}]}
```
Tool spec row:
```json
{"api_name":"analyzeEvidence","api_description":"...","field":"...",
 "parameters":{"evidence_type":{"type":"str","description":"..."}, ...},"required":[...]}
```

### Evaluation metrics (`LLM_Evaluation/src/llm_tools/evaluation/calculate.py::calculate_score_ToolLearning`)
Three metrics, all under "strict format control":
1. **AMOUNT** = fraction of predictions that parse as valid format (`predict[0] != -1`).
2. **API F1** (`P_api`, `R_api`, `F1_api`): precision/recall on predicted vs gold `api` names.
   `correct_api_num / predict_api_num` (precision) and `/ gold_api_num` (recall).
3. **Param F1** (`P_param`, `R_param`, `F1_param`): exact-match on `parameter_name` + stringified
   value, but only counted for APIs that matched a gold api name.

## Relevance to our paper (TEHR / tool-existence hallucination)

The scoring is order-insensitive set matching of api names against the gold answer. A predicted
api name that exists in the registry but is wrong, AND a predicted api name that does **not exist
at all**, are treated identically — both just miss the gold set and lower `P_api`. There is **no
isolated tool-existence-hallucination metric** in their code. That is precisely the gap our TEHR
defines, and Seal-Tools provides the two ingredients TEHR needs: (a) an explicit tool registry
per task (the full `tool.jsonl` or a per-query candidate set), and (b) gold calls to compute a
per-call denominator. We can compute TEHR ourselves on their data = `# predicted api names not in
the registry / # predicted calls`.

## Concrete integration judgment

- **RUN as an extra benchmark: YES (medium effort).** This is the strongest fit. The format
  (registry of typed tools + query + gold tool-call list) maps cleanly onto our
  `harness/bench_loaders/*.py` pattern, which yields `Task` objects with a normalized OpenAI-shape
  `registry`. We'd write `harness/bench_loaders/seal_tools.py` that: loads `tool.jsonl` into a
  registry, normalizes Seal-Tools param schema (`{"type":"str","description":...}`, `required`)
  to OpenAI function-tool schema (same normalization role as `_normalize_bfcl_schema`), and emits
  one Task per row of `test_in_domain` / `test_out_domain`. TEHR then drops in unchanged: count
  predicted api names absent from the registry. **It is single-turn** (no user simulator, no env
  state), so it is *easier* to run than BFCL multi-turn or tau-bench — but note it adds breadth in
  the single-turn / large-registry axis rather than the multi-turn axis, which is a good
  complementary data point (does TEHR change when the registry is 4076 tools vs BFCL's small
  per-task sets?). Effort is in schema normalization + a registry-presence check, not new infra.
- **Reuse a COMPONENT in our harness: PARTIAL / NOT RECOMMENDED to import.** Their
  `LLM_Evaluation` code is self-described as "not well organized," uses Python `match` (3.10+),
  `eval()` on stored strings, and is intermingled with unrelated NLP benchmarks (TableEE, NER,
  event extraction). Don't vendor it. Reimplement the simple API-F1 / Param-F1 metrics ourselves
  (a few lines) so we can report numbers comparable to their paper without inheriting their code.
- **Reuse as a BASELINE: YES (cite + optionally reproduce).** Their paper reports several LLMs and
  a finetuned model on these splits, so it gives published comparison numbers. We can position
  Seal-Tools api-F1 as the "standard" tool-selection metric and TEHR as the missing
  hallucination-specific complement.
- **Cite as PRIOR ART: YES.** Relevant prior tool-learning benchmark; useful to differentiate —
  it measures correctness/F1 of tool selection, not existence-hallucination rate per call, and
  does not separate hallucinated-nonexistent from merely-wrong tools.
- **Borrow a PATTERN for the paper-revision skill / personas: WEAK.** Nothing directly. The only
  transferable idea is their self-instruct dataset-construction pipeline (`Dataset_Construct/`) if
  we ever wanted to synthesize adversarial nonexistent-tool stress tests — out of scope for the
  revision skill.

## Risk / caveats

- License Apache-2.0: safe to redistribute derived loaders / report numbers with attribution.
- Data is synthetic (self-instruct via LLM), so tools are plausible-but-fictional; the "responses"
  are placeholders (`API_call_N`), i.e. no executable backend — fine for TEHR (we only inspect
  emitted call names), but means we can't run a real multi-turn execution loop on it.
- The benchmark's own metric conflates wrong-existing vs hallucinated-nonexistent tools — a
  weakness we should name explicitly as our motivation, not a flaw to fix in their repo.
- Single-turn only; complements but does not extend our multi-turn (BFCL/tau-bench) axis.

## Recommended action

Add `harness/bench_loaders/seal_tools.py` (analogous to `bfcl.py`) for the in-domain + out-domain
test splits; compute TEHR via registry-presence on emitted api names; report their api-F1 / param-F1
alongside as the conventional metric; cite the NLPCC 2024 paper as prior art and differentiate on
the existence-hallucination measurement. Effort: ~medium (schema normalization is the main work).

---

## ADVERSARIAL VERIFICATION (2026-05-29, independent re-check)

Verifier: independently re-ran `gh api`, downloaded the raw data, read the LICENSE body and the
scoring code. Verdict: **survey is accurate and not over-optimistic on the load-bearing claims.**
Two minor framing nits below.

### License — CONFIRMED Apache-2.0 (SPDX), permissive, vendor-safe
- `gh api repos/fairyshine/Seal-Tools/license` → `spdx_id: "Apache-2.0"`, name "Apache License 2.0".
- Pulled the actual `LICENSE` file body (default branch is **`master`**, not `main`): begins
  "Apache License / Version 2.0, January 2004 / http://www.apache.org/licenses/". Grep for
  GNU/GPL/Affero/copyleft → no hits (only false positive was "Version 2.0"). The file is the
  genuine Apache-2.0 text, not a relicensed body.
- **No GPL/AGPL concern.** We MAY vendor a derived loader + redistribute reported numbers into our
  (permissive) codebase with attribution + NOTICE. The copyleft caveat in the task prompt does NOT
  apply here.

### Stars — CONFIRMED order-of-magnitude
- 57 stars, 5 forks, not archived, last push 2024-11-05. Survey's "57" and "stable, not archived"
  are exact. This is a small/niche repo (tens of stars), correctly represented — no inflation.

### Data files — CONFIRMED exactly
- `wc -l`: tool.jsonl=**4076**, test_in_domain=**700**, test_out_domain=**654**, train=**12022**.
  All four match the survey's stated counts precisely.
- Formats match the quoted examples (tool spec with typed `parameters` + `required` + spec-only
  `responses`; query rows with `calling` = list of `{api, parameters, responses:["API_call_N"]}`).

### Eval-code caveats — CONFIRMED (survey's warnings are real)
- `LLM_Evaluation/src/.../calculate.py` uses `match/case` (Python 3.10+), uses `eval()` on stored
  strings (line 515), and is intermingled with unrelated NLP tasks (TableEE, ABSA, NER, RE, EE).
  "Do not vendor; reimplement the few-line metric" is the right call.
- Read `calculate_score_ToolLearning` body directly: it matches predicted api **only against the
  gold answer's api list**, never against the tool registry. A hallucinated (nonexistent) api and
  a real-but-wrong api are scored identically (both miss gold, lower P_api). **There is no
  tool-existence-hallucination metric** — survey's central TEHR-gap claim is verified correct.

### Run-as-benchmark — HOLDS, with two refinements
- TEHR is cleanly computable: all gold api names are present in the 4076-tool registry
  (0 gold calls missing from registry), so any predicted name absent from `tool.jsonl` is an
  unambiguous hallucination. Ground truth is sound.
- Harness fit verified against the real `harness/bench_loaders/bfcl.py`: it yields `Task` objects
  with a normalized OpenAI-shape `registry` via `_normalize_bfcl_schema`, env-overridable data dir.
  Seal-Tools' `{"type":"str","description":...}` + `required` schema maps onto this directly.
  A `seal_tools.py` loader is genuinely **medium effort** (schema normalize + registry-presence
  check). No executable backend needed — `responses` are spec-only placeholders, which is fine for
  TEHR (we only inspect emitted call names). MLX + API models run it via the same adapters as BFCL.
- **NIT 1 — "single-turn ⇒ easier than BFCL" undersells difficulty.** 500/700 (71%) of
  test_in_domain rows require a **multi-tool** call plan; ~30 have **nested dataflow** (params
  referencing prior `API_call_N` outputs). It is single-*turn* (one user query, no user simulator
  / env state) — that part is true and it IS infra-simpler than BFCL multi-turn — but the gold
  target is a multi-call plan, not a single call. Don't describe the task itself as "easy."
- **NIT 2 — published baselines are in the PAPER, not the repo.** The repo README is a stub (no
  results table); GPT-3.5/4 / LLaMA / finetuned-model numbers live in the NLPCC 2024 paper PDF.
  "Reuse as a baseline" still holds (cite the paper's numbers), but they are not machine-readable
  from the repo — slightly more manual than the survey implies.

### Verdict
**recommend = run-as-benchmark** (medium effort), confidence **high**. License Apache-2.0 confirmed
and vendor-safe (no copyleft restriction). Survey did not overstate stars, license, or usability;
only minor framing nits on task difficulty and baseline provenance.

---

## ADVERSARIAL VERIFICATION #2 (2026-05-29, second independent re-check)

Second verifier, fully independent re-run (did not trust the prior block; re-pulled all primary
sources: `gh api`, decoded LICENSE body, downloaded the four jsonl files, read the scoring code
line-by-line, diffed against the real `harness/bench_loaders/bfcl.py`). **Confirms the survey AND
the first verification block on every load-bearing claim.** No over-optimism found.

### License — CONFIRMED Apache-2.0 (SPDX `Apache-2.0`), permissive, vendor-safe
- `gh api .../license` → `spdx_id: "Apache-2.0"`, name "Apache License 2.0".
- Did NOT trust the API summary: decoded the actual `LICENSE` blob (base64) — body is the genuine
  "Apache License / Version 2.0, January 2004 / http://www.apache.org/licenses/" text.
- Grepped the decoded body for `GNU|GPL|Affero|copyleft|LGPL` → zero hits.
- **The task prompt's GPL/AGPL copyleft caveat does NOT apply.** We MAY vendor a derived loader and
  redistribute reported numbers into our permissive codebase (attribution + NOTICE per Apache-2.0).

### Stars / repo state — CONFIRMED
- `stargazers_count = 57`, `forks = 5`, `archived = false`, `pushed_at = 2024-11-05`,
  `default_branch = master`. Order-of-magnitude (tens of stars) correct; no inflation.

### Data files — CONFIRMED by direct download + `wc -l`
- tool.jsonl=**4076**, test_in_domain=**700**, test_out_domain=**654**, train=**12022**. Exact match.
- Tool-spec and query-row formats match the quoted examples (typed `parameters`+`required`+spec-only
  `responses`; query `calling` = list of `{api, parameters, responses:["API_call_N"]}`).

### TEHR computability — CONFIRMED by independent script (strongest evidence)
- Parsed all 4076 tool names into a registry set, then checked every gold call in both test splits:
  **0 gold api names missing from the registry** (in-domain: 0/1795 calls; out-domain: 0/1937 calls).
  Ground truth is fully covered → any predicted name absent from `tool.jsonl` is an unambiguous
  existence-hallucination. TEHR is cleanly, soundly computable on this data.

### Scoring code — CONFIRMED TEHR-gap is real
- Read `calculate_score_ToolLearning` (calc.py L500-553) line-by-line. The api-match inner loop
  compares `predict_api["api"]` **only against `gold_answer[idx]["api"]`** (the per-query gold list).
  Grep for `tool.jsonl|registry|exist` across the whole 553-line file → **zero hits**. A nonexistent
  (hallucinated) api and a real-but-wrong api both fail the same `gold_idx != -1` test and identically
  lower `P_api`. There is NO existence metric — the survey's central motivation gap is verified.
- Code-hygiene warnings CONFIRMED: `match/case` at L15+ (Python 3.10+), `eval()` on a stored string
  at L515, and intermixed with TableEE/ABSA/NER/RE/EE. "Don't vendor; reimplement the few-line
  metric" remains correct.

### Harness fit — CONFIRMED against real bfcl.py
- `harness/bench_loaders/bfcl.py` yields `Task(registry={tool_name: OpenAI-shape schema}, ...)` via
  `_normalize_bfcl_schema`, env-overridable data dir, deterministic sampling. Seal-Tools'
  `{"type":"str","description":...}`+`required` schema maps directly onto this. A `seal_tools.py`
  loader (schema-normalize + registry-presence check, single-turn so simpler control flow than
  BFCL multi-turn) is genuinely **medium effort**. MLX + API models run it via the same adapters.

### Both prior nits — CONFIRMED accurate
- NIT 1 (single-turn ≠ easy): **71%** of in-domain rows and **86%** of out-domain rows require >1
  tool call; 38 (in) / 32 (out) rows have nested dataflow (params referencing `API_call_N`). It is
  single-*turn* (no user sim / env state, infra-simpler than BFCL multi-turn) but the gold target is
  a multi-call plan. Out-domain is actually harder (86% multi-tool) than in-domain.
- NIT 2 (baselines in paper, not repo): README is a **37-line stub** with no results table and no
  GPT/LLaMA/F1 numbers. Published baselines must be cited from the NLPCC 2024 paper; not
  machine-readable from the repo.

### Final verdict (verifier #2)
**recommend = run-as-benchmark** (medium effort), **confidence = high**, **license = Apache-2.0
(confirmed via decoded LICENSE body, not just API summary), vendor-safe**. The survey did not
overstate stars, license, or usability. The only corrections are the two framing nits already
captured (task is multi-call though single-turn; baselines live in the paper PDF). No copyleft
restriction applies — full include/vendor is permitted.
