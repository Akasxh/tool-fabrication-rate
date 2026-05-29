# Pinned Model IDs and Smoke-Test Plan

*Generated 2026-04-27. Sources cited inline; all WebFetch / WebSearch only — zero paid API calls made.*

## Anthropic
Source: <https://platform.claude.com/docs/en/docs/about-claude/models> (canonical, post-redirect from `docs.anthropic.com`).

| Tier | Production alias | Dated alias | $/1M in | $/1M out | Context | Max out |
|---|---|---|---|---|---|---|
| Frontier (mid) | `claude-sonnet-4-6` | `claude-sonnet-4-6` *(no public dated snapshot listed; alias is canonical)* | $3.00 | $15.00 | 1M tokens | 64k |
| Small | `claude-haiku-4-5` | `claude-haiku-4-5-20251001` | $1.00 | $5.00 | 200k tokens | 64k |

Tool-use / function-calling: confirmed yes (both). Both expose `tools` parameter via Messages API; both support extended thinking; both on Priority Tier.
Deprecation warnings: none for 4.6 / 4.5. *(Sonnet 4 / Opus 4 with `-20250514` are deprecated and retire 2026-06-15 — irrelevant here.)*

## OpenAI
Source: <https://developers.openai.com/api/docs/models/gpt-4.1> and `.../gpt-4.1-mini`.

| Tier | Production alias | Dated alias | $/1M in | $/1M out | Context | Max out |
|---|---|---|---|---|---|---|
| Frontier (mid) | `gpt-4.1` | `gpt-4.1-2025-04-14` | $2.00 | $8.00 | 1,047,576 | 32,768 |
| Small | `gpt-4.1-mini` | `gpt-4.1-mini-2025-04-14` | $0.40 | $1.60 | 1,047,576 | 32,768 |

Cached-input rates: $0.50 (4.1) / $0.10 (4.1-mini) per 1M — relevant if we enable prompt caching for the registry list.
Tool-use / function-calling: confirmed yes (both). Streaming + structured outputs + fine-tuning supported. Knowledge cutoff: 2024-06-01.
Deprecation warnings: none. (OpenAI nudges users to GPT-5 for "complex tasks" but 4.1 remains generally available and is the right pick for our cost-quality-gap framing.)

## xAI (deferred to Gate 2)
Sources: <https://docs.x.ai/developers/models>, <https://docs.x.ai/developers/models/grok-4-0709>, <https://mem0.ai/blog/xai-grok-api-pricing>.
Base URL: `https://api.x.ai/v1` (OpenAI-compatible — use `openai` SDK with `base_url=`).

| Tier | Production alias | Dated alias | $/1M in | $/1M out | Context |
|---|---|---|---|---|---|
| Frontier | `grok-4` | `grok-4-0709` | $3.00 | $15.00 | 256k |
| Small / fast | `grok-4-fast` *(non-reasoning)* | `grok-4-fast` *(no public dated snapshot)* | $0.20 | $0.50 | 2M |

Tool-use / function-calling: confirmed yes (custom function calling token-priced; built-in tools `web_search`/`x_search`/`code_execution` carry $2.50–5.00 / 1k surcharge — not used in our experiment). Reasoning is always-on for `grok-4`; `grok-4-fast` has reasoning + non-reasoning variants.
Deprecation warnings: none for grok-4. Newer `grok-4-1-fast` exists but `grok-4` + `grok-4-fast` are the stable production picks for reproducibility.

## SDKs
Pin in `harness/pyproject.toml`:
```toml
dependencies = [
    "anthropic>=0.96.0,<1.0.0",   # latest stable as of 2026-04-23
    "openai>=2.32.0,<3.0.0",      # latest stable as of 2026-04-15; used for both OpenAI and xAI
]
```
Sources: <https://pypi.org/project/anthropic/>, <https://github.com/openai/openai-python/releases>.

## Auth smoke tests (RUN AFTER CREDITS REDEEMED — not run by agent)
```python
# anthropic_ping.py — expected cost ~$0.0001 per call
import os, anthropic
c = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
r = c.messages.create(model="claude-haiku-4-5", max_tokens=1, messages=[{"role":"user","content":"hi"}])
print("OK", r.id)
```
```python
# openai_ping.py — expected cost ~$0.0001 per call
import os
from openai import OpenAI
c = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
r = c.chat.completions.create(model="gpt-4.1-mini", max_tokens=1, messages=[{"role":"user","content":"hi"}])
print("OK", r.id)
```
```python
# xai_ping.py — expected cost ~$0.0001 per call (uses openai SDK + base_url override)
import os
from openai import OpenAI
c = OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")
r = c.chat.completions.create(model="grok-4-fast", max_tokens=1, messages=[{"role":"user","content":"hi"}])
print("OK", r.id)
```

## Per-task cost estimates (~20K in / ~3K out per task, 8-turn agent)
Computed as `20 * $/1M_in + 3 * $/1M_out`:

- Sonnet 4.6: 20·$3 + 3·$15 = **$0.105 / task**
- Haiku 4.5: 20·$1 + 3·$5 = **$0.035 / task**
- GPT-4.1: 20·$2 + 3·$8 = **$0.064 / task**
- GPT-4.1-mini: 20·$0.40 + 3·$1.60 = **$0.013 / task**
- Grok-4: 20·$3 + 3·$15 = **$0.105 / task**
- Grok-4-fast: 20·$0.20 + 3·$0.50 = **$0.0055 / task**

Sanity: full main run = ~600 API tasks × 2 cond ≈ 1200 calls. Worst-case (all Sonnet 4.6) ≈ $126; realistic mixed = ~$60-110. Matches PAPER_PLAN_v3.1 §4.5.

## Cost-meter calibration (HARNESS_SPEC `CostMeter` abort thresholds)
Conservative 90%-of-credit ceilings, per-provider:
- **Anthropic**: abort at **$400** (of $500 redeemed)
- **OpenAI**: abort at **$2000** (of $2500 redeemed)
- **xAI**: abort at **$2000** (of $2500 redeemed; only debited if Grok activated at G2)

Soft warnings at 50% and 75%. Hard abort raises `CostBudgetExceeded` and flushes partial results.

## Pre-Phase-1 checklist
1. `export ANTHROPIC_API_KEY=…`, `OPENAI_API_KEY=…`, `XAI_API_KEY=…` in `~/.zshrc` (or session-only for safety).
2. Run the three smoke-test snippets above; verify `OK <id>` from each.
3. Pin SDK versions in `harness/pyproject.toml` exactly as shown in §SDKs.
4. Confirm credit balances in each provider console match expected: Anthropic ~$500, OpenAI ~$2500, xAI ~$2500.
5. Wire `model_ids.md` constants into `harness/adapters/{anthropic,openai,xai}.py` as the canonical model strings.

## Sources cited
- Anthropic models: <https://platform.claude.com/docs/en/docs/about-claude/models>
- OpenAI GPT-4.1: <https://developers.openai.com/api/docs/models/gpt-4.1>
- OpenAI GPT-4.1-mini: <https://developers.openai.com/api/docs/models/gpt-4.1-mini>
- xAI models page: <https://docs.x.ai/developers/models>
- xAI grok-4-0709: <https://docs.x.ai/developers/models/grok-4-0709>
- xAI base URL / OpenAI compat: <https://docs.x.ai/docs/tutorial>
- xAI pricing supplement: <https://mem0.ai/blog/xai-grok-api-pricing>
- Anthropic SDK: <https://pypi.org/project/anthropic/>
- OpenAI SDK: <https://github.com/openai/openai-python/releases>
