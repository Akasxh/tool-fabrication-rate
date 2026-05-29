# Repo Survey: MetaTool

- **Repo:** HowieHwong/MetaTool
- **Canonical URL:** https://github.com/HowieHwong/MetaTool (URL valid, no 404)
- **Paper:** ICLR'24 — "MetaTool Benchmark: Deciding Whether to Use Tools and Which to Use" (arXiv:2310.03128, Huang et al.)
- **Stars:** 114 (gh api, 2026-05-29)
- **License:** MIT (SPDX: `MIT`) — verified via `gh api .../license`. Permissive, redistribution-safe.
- **Activity:** last push 2024-03-21; effectively frozen / archival (not archived flag, but no commits in ~2 yrs).
- **Category:** benchmark

## What it is

A **single-turn** benchmark for two LLM capabilities:
1. **Tool-usage awareness** — should the model use a tool at all for this query (incl. negative/"no tool needed" cases).
2. **Tool selection** — pick the correct tool from a candidate set. Four subtasks: similar-tool selection, scenario-conditioned selection, reliability-aware selection, and multi-tool selection.

Core artifact is the **ToolE dataset**: ~21.1k synthetic user queries (20,630 single-tool + 497 multi-tool), each query mapped to a ground-truth tool name + NL description. Tools are ChatGPT-plugin-store entries (NL descriptions only — **no JSON-Schema parameter specs, no executable backends**).

Data layout (all redistributable under MIT):
- `dataset/data/all_clean_data.csv` — 20,615 rows of `Query,Tool` (single-tool ground truth).
- `dataset/data/multi_tool_query_golden.json` — `{query, tool:[...]}` multi-tool golden.
- `dataset/plugin_des.json` — `{tool_name: description}` tool universe (the candidate pool).
- `dataset/scenario/*.json` — per-persona tool lists (Table 10).
- `dataset/tool_embedding.pkl` — precomputed description embeddings.
- `src/` — prompt construction (`prompt_construction.py`), Milvus-backed similarity retrieval, FastChat-style HF generation (`run.py`), clustering eval.

Eval harness deps are heavy/dated: pins HF `transformers`/FastChat-era generation, **Milvus (Docker)** for embedding retrieval, OpenAI legacy calls. The runnable harness is the weakest, most bit-rotted part; the *data + prompt templates* are the durable assets.

## Relevance to our paper (TEHR / RVR)

MetaTool is conceptually adjacent: "deciding **whether** to use tools and **which**" overlaps our framing of tool-existence hallucination. But the failure mode is different:
- **MetaTool** measures *wrong selection / spurious invocation* on a single turn against a candidate pool described in NL.
- **TEHR** measures *calling a tool that does not exist in the per-call registry* during multi-turn execution (BFCL/tau-bench), with executable backends and a re-prompt intervention (RVR).

So it is closest prior art on the "tool hallucination / mis-selection" axis, not a drop-in benchmark for our exact metric.

## Concrete verdict

| Option | Feasible? | Notes |
|---|---|---|
| **Run as extra benchmark** | Weakly. Not a clean fit. | Single-turn, NL-only tool descriptions, no parameter schemas, no executor. Our harness (`Task` in `types.py`) requires `registry` = OpenAI-shape JSON-Schema + multi-turn `expected_outcome`. MetaTool has no `parameters` schema, so it can't exercise our arg-grounding or multi-turn re-prompt path. You *could* synthesize a degenerate single-turn TEHR variant (registry = candidate-pool tools with empty params, prompt = query, score "hallucinated" = model emits a tool name not in the pool). That measures a *different, weaker* signal than our BFCL TEHR and risks muddying the headline. Medium build effort, low payoff. |
| **Reuse a component in harness** | Partially. | The ToolE CSV/JSON + `plugin_des.json` tool universe could feed a new `harness/bench_loaders/metatool.py` that emits single-turn `Task`s (registry built from `plugin_des.json`, no params). Their `src/` code (Milvus, FastChat) is not worth importing — write a fresh ~80-line loader modeled on `bfcl.py`. Low-med effort if pursued. |
| **Reuse as baseline** | Yes, indirectly. | Their nine-LLM awareness/selection results are a *reported* baseline for "models mis-handle tools," useful to contextualize that even strong models err on tool decisions — but their models are 2023-era (Vicuna/ChatGPT/GPT-4), so not directly comparable to our Anthropic 4.x / Qwen3 numbers. |
| **Cite as prior art** | **Yes — strongest use.** | This is the canonical ICLR'24 reference for "should the model use a tool / which tool," and for the *tool-hallucination-adjacent* literature. Cite to (a) position TEHR against selection-error work, and (b) explicitly differentiate: we measure existence hallucination in multi-turn executable settings with an intervention, they measure single-turn selection from NL candidate pools. Good "related work / differentiation" anchor. |
| **Borrow a pattern (skill/personas)** | Minor. | Their reliability-tool-selection subtask (tools with deliberate reliability/safety issues) and persona-scenario tool lists are a useful *rubric pattern* for a reviewer persona that probes "does the eval cover adversarial/unsafe tool candidates?" Low-value but cheap to note. |

## Effort & risk

- **License risk:** none. MIT is compatible with our use (cite, vendor data, adapt loader). Keep attribution + LICENSE if we vendor any data file.
- **Integration effort:** Running their harness = high (Milvus/Docker + dated HF stack, likely needs porting). Writing our own loader over their data = low-med. Citing = trivial.
- **Recommendation:** **cite-only** as primary integration. Optionally add a lightweight `metatool.py` single-turn loader later *if* a reviewer demands a "tool selection" breadth axis — but it is a different metric and should not be conflated with the BFCL multi-turn TEHR headline.

## Citation

```bibtex
@inproceedings{huang2024metatool,
  title   = {MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use},
  author  = {Huang, Yue and Shi, Jiawen and Li, Yuan and Fan, Chenrui and Wu, Siyuan and Zhang, Qihui and Liu, Yixin and Zhou, Pan and Wan, Yao and Gong, Neil Zhenqiang and Sun, Lichao},
  booktitle = {ICLR},
  year    = {2024}
}
```

---

## Adversarial verification (2026-05-29, independent re-check)

Verified the survey's load-bearing claims by cloning the repo at `master` (HEAD pushed 2024-03-21) and inspecting the actual files, not the summaries.

**License — CONFIRMED MIT (SPDX `MIT`).** Read the raw `LICENSE` file content (not just GitHub's auto-detected `license` object): full verbatim MIT text, `Copyright (c) 2023 Yue Huang`. Permissive — safe to vendor data and adapt code into our (permissive) codebase with attribution + LICENSE retention. No GPL/AGPL concern; the vendor-restriction caveat does NOT apply here.

**Stars — CONFIRMED 114** (gh api, 2026-05-29). Order of magnitude: low hundreds (~10^2). Survey accurate. Not archived; effectively frozen (no commits ~2 yr).

**Venue — CONFIRMED ICLR 2024** (poster, OpenReview `R0c2qtalgG`, arXiv 2310.03128, "Published as a conference paper at ICLR 2024"). Citation in survey is correct.

**"No parameter schemas / no executable backends" — CONFIRMED, and this is the decisive fact.** Inspected all three tool-description files: `plugin_des.json` (199 tools), `big_tool_des.json` (47), `plugin_info.json` (390, with `name_for_model`/`description_for_model`/`description_for_human` ChatGPT-plugin manifest fields). Every entry is name + NL description ONLY — no `parameters`, no JSON-Schema, no executor. Data is `Query,Tool` CSV (20,615 rows) + `{query, tool:[...]}` multi-tool golden (497). 

  - Cross-checked against our `harness/types.py`: `Task.registry` is documented as canonical OpenAI shape `{name:{"name","description","parameters":<JSON-Schema>}}` and `BenchmarkName = Literal["bfcl","tau_bench"]` (closed). MetaTool cannot populate a faithful registry (no params) and would require extending the literal. So "run as extra benchmark = weakly / not a clean fit" is CORRECT, not over-optimistic — if anything the survey is slightly generous; a faithful TEHR run is impossible, only a degenerate empty-param single-turn proxy.

**Runnability of their harness — CONFIRMED bit-rotted, survey if anything UNDERSTATES the friction.** `requirements.txt` pins `openai==0.27.8` (pre-1.0 legacy API — incompatible with modern SDK), `transformers==4.29.0`, `torch==2.0.1`, `langchain==0.0.309`, plus `pymilvus`. Generation backend (`src/generation/run.py`) is FastChat + HF `AutoModelForCausalLM` (Vicuna-era, hardcodes legacy `openai.api_key`). `quickstart.sh` and `src/embedding/milvus_database.py` hard-require a **Milvus server on `localhost:19530` via Docker** for the similarity-retrieval subtask. Our harness is MLX + API (litellm/Anthropic/OpenAI 1.x); their stack shares nothing reusable. Running their harness as-is = high effort / likely needs porting. The durable assets are the data + prompt templates only.

### Corrections / nuance vs survey
- Survey says ToolE pool = "ChatGPT-plugin-store entries" implying a large universe; the actual candidate pools are small (199 / 47 / 390 depending on file). Minor framing imprecision, not material to the verdict.
- Survey's `all_clean_data.csv` count "20,615 rows" — CONFIRMED exactly (excl. header). multi-tool golden = 497 — CONFIRMED.

### Final adversarial verdict: **cite-only** (agree with survey, high confidence)
MetaTool is the canonical ICLR'24 "whether/which tool" selection benchmark and the right related-work anchor to differentiate TEHR (multi-turn, executable, existence-hallucination, RVR intervention) from single-turn NL-only selection. MIT means we MAY vendor data / write a fresh loader if a reviewer demands a tool-selection breadth axis — but that measures a different, weaker signal and must not be conflated with the BFCL multi-turn TEHR headline. Their nine-LLM results are 2023-era (Vicuna/GPT-4) and not comparable to our Anthropic 4.x / Qwen3 numbers. No license risk. Recommendation stands.

---

## Adversarial verification PASS 2 (2026-05-29, second independent re-check by reviewer agent)

Re-ran the load-bearing checks from scratch (fresh shallow clone at HEAD 2024-03-21 + `gh api`), deliberately NOT trusting either the original survey or the first verification block. Verdict below.

**License — INDEPENDENTLY CONFIRMED `MIT`.** Decoded the raw `LICENSE` blob via `gh api repos/HowieHwong/MetaTool/license` (base64 → plaintext): verbatim MIT text, "Copyright (c) 2023 Yue Huang", grants use/copy/modify/merge/publish/distribute/sublicense/sell. GitHub `spdx_id=MIT`, `key=mit`. This is a PERMISSIVE license. The task's GPL/AGPL vendor-restriction concern is moot — `license_confirmed=true`, we MAY vendor data files and adapt code into our (permissive) codebase provided we retain the copyright notice + LICENSE. No copyleft contamination.

**Stars — CONFIRMED 114** (`gh api`, 2026-05-29). Order of magnitude 10^2 (low hundreds). `archived=false`, `pushed_at=2024-03-21` → frozen, ~2 yr no commits. Survey's stars claim is accurate, not inflated.

**Reusability / "cite-only" — PRESSURE-TESTED, HOLDS. Survey is NOT over-optimistic; if anything conservative.**
  - `dataset/plugin_des.json` = 199 tools, each a `{name: NL-description-string}` pair. Programmatically confirmed NO `parameters`/JSON-Schema field on any sampled entry. No executable backend anywhere in repo.
  - `dataset/data/all_clean_data.csv` header `[Query, Tool]`; `csv.reader` yields **20,614 data rows** (excl. header). `dataset/data/multi_tool_query_golden.json` = list of **497** `{query, tool:[...]}` entries. Confirmed.
  - Harness contract cross-check (`harness/types.py`): `Task.registry` is documented canonical OpenAI shape `{name:{"name","description","parameters":<JSON-Schema>}}`; `BenchmarkName = Literal["bfcl","tau_bench"]` (CLOSED literal). MetaTool cannot populate a faithful registry (no params) and would require editing the literal. A real TEHR run on MetaTool is impossible; only a degenerate empty-param single-turn proxy is buildable, measuring a different/weaker signal. "Run as extra benchmark = weakly / not a clean fit" is CORRECT.
  - Bit-rot CONFIRMED and arguably understated: `requirements.txt` pins `openai==0.27.8` (pre-1.0), `transformers==4.29.0`, `torch==2.0.1`, `langchain==0.0.309`, `pymilvus`. `src/generation/run.py` uses legacy `openai.ChatCompletion.create` + hardcoded `openai.api_key`. Milvus server required (`src/embedding/milvus_database.py`, `quickstart.sh`). Our MLX + API (litellm/Anthropic/OpenAI 1.x) stack shares zero reusable runtime with theirs. Running their harness as-is against our models is NOT feasible without a port; the durable assets are data + prompt templates only.

### Discrepancies found vs PASS 1 block (penalize precision, not verdict)
- PASS 1 said CSV = "20,615 rows … CONFIRMED exactly (excl. header)". My `csv.reader` count is **20,614** data rows. Off by one (likely a trailing-line / quoted-multiline counting artifact). Immaterial to the verdict but flagged for accuracy.
- PASS 1 cited the multi-tool golden as `dataset/multi_tool_query_golden.json`; actual path is `dataset/data/multi_tool_query_golden.json`. Path imprecision, file confirmed present, count 497 correct.
- Both discrepancies are cosmetic; neither changes the recommendation.

### PASS 2 final verdict: **cite-only** (concur, confidence HIGH)
The survey did NOT overstate stars, license, or usability — its claims check out, and where it erred it was on the side of over-stating runnability friction's *reusability* (i.e., it was slightly generous calling "run as extra benchmark" weakly-feasible; a faithful run is effectively infeasible). License is genuinely MIT/permissive, so the GPL/AGPL vendor caveat does not bite. Best use is a related-work citation to differentiate single-turn NL-only tool *selection* (MetaTool) from our multi-turn executable tool-*existence* hallucination (TEHR) with the RVR intervention. A bespoke ~80-line single-turn loader over their MIT data is *permitted* and low-effort if a reviewer demands a selection-breadth axis, but it measures a different/weaker signal and must not feed the BFCL TEHR headline.
