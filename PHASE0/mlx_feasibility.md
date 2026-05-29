# Gate 0.5 — MLX + Qwen3-8B Feasibility Probe

**Decision target**: does the local-OSS tier (Qwen3-8B via MLX on Apple M5) stay CORE in PAPER_PLAN_v3.1, or get DROPped at Gate 0.5?

## VERDICT: **CORE**

The local-OSS tier stays in. Qwen3-8B-4bit on MLX clears the Gate 0.5 bar comfortably (3/3 fixtures parsed and dispatched correctly; envelope shape matches the harness contract verbatim; total wall-clock incl. cold download ~3.5 min, well under the 30-min abort budget).

## HF repo ID confirmed (Phase-1 MLXAdapter must use this string)

```
mlx-community/Qwen3-8B-4bit
```

Notes for A3:
- The originally-named `mlx-community/Qwen3-8B-Instruct-4bit` referenced in HARNESS_SPEC §2 (Open Question #2) **does not exist on HF**. The Qwen3 family ships chat-tuned weights under the unsuffixed name; there is no separate `-Instruct` variant. The `mlx-community/Qwen3-8B-4bit` repo *is* the chat-tuned model.
- `tokenizer_config.json` confirms a tools-aware Jinja chat template with `{%- if tools %}`, `<tools>...</tools>` system block, and `<tool_call>{json}</tool_call>` output envelope (verified: 3 occurrences of `<tool_call>`, 16 of `tool_call`, 6 of `tools` in the template).
- Other working candidates (verified live): `Qwen3-8B-bf16`, `Qwen3-8B-8bit`, `Qwen3-8B-6bit`, `Qwen3-8B-4bit-DWQ`, `Qwen3-8B-4bit-AWQ`. Only `4bit` was downloaded for this probe (~5 GB).

## Generation samples (verbatim)

### Fixture 1: weather_sf — *"What's the weather in San Francisco?"* (expected `get_weather`)
```
<tool_call>
{"name": "get_weather", "arguments": {"city": "San Francisco"}}
</tool_call>
```
Parsed: `[{"name": "get_weather", "arguments": {"city": "San Francisco"}}]` — parse_ok=True, expectation_met=True.

### Fixture 2: flight_jfk_lhr — *"Book me a flight from JFK to LHR on May 5th."* (expected `book_flight`)
```
<tool_call>
{"name": "book_flight", "arguments": {"origin": "JFK", "destination": "LHR", "date": "2023-05-05"}}
</tool_call>
```
Parsed: `[{"name": "book_flight", "arguments": {"origin": "JFK", "destination": "LHR", "date": "2023-05-05"}}]` — parse_ok=True, expectation_met=True.

### Fixture 3: capital_of_france — *"What's the capital of France?"* (expected: NO tool call)
```
The capital of France is Paris.
```
Parsed: `[]` — parse_ok=True, expectation_met=True (no `<tool_call>` envelope emitted, model answered from parametric memory as desired).

## Parse success rate

**3/3** — all three fixtures returned a parseable structure where expected. Expectation-met = 3/3 (right tool chosen on tool-warranted prompts; no spurious tool call on the trivia prompt).

## Performance (Apple M5, 32 GB unified memory)

| Metric | Value |
|---|---|
| Cold model load (incl. ~5 GB HF download over 9 files) | 202.7 s |
| Peak process RSS (after load + 3 generations) | 5,154 MiB (`ru_maxrss`); `time -l` reported 5.40 GB peak memory footprint |
| Per-fixture tokens/sec (small N — first-token latency dominates) | 7.4 / 10.0 / 18.9 |
| **Steady-state tokens/sec** (separate 360-token generation) | **26.7 tok/s** |
| Total fixture generation (3 prompts, 69 tokens) | 5.18 s |
| Total wall-clock incl. download (`/usr/bin/time -l`) | **211 s real, 13 user, 20 sys** |
| Disk consumed | ~5 GB under `~/.cache/huggingface/hub/models--mlx-community--Qwen3-8B-4bit/` |

**Implications for the main run** (Plan §4.5 budgets 1.5 h for 150 M5 runs across BFCL+τ-bench × 2 conditions). At 27 tok/s steady-state with typical BFCL responses ≤200 tokens, per-call generation ~7-15 s plus ReAct overhead → 150 calls comfortably fit inside 1.5 h. Memory headroom of ~26 GiB free on a 32 GB box leaves plenty of room for prompt-buffer growth at long contexts.

## Quirks discovered (Phase-1 must know)

1. **`enable_thinking` defaults to ON.** Qwen3's chat template injects `<think>...</think>` reasoning blocks unless `enable_thinking=False` is passed to `apply_chat_template`. With thinking on, the tool-call envelope still appears, but is preceded by free-form reasoning text — this would break naive regex-only parsing if the regex isn't anchored to the envelope. **Recommendation: A3's MLXAdapter must pass `enable_thinking=False`** (this probe does) for clean tool-calling, OR strip `<think>...</think>` blocks before applying the envelope regex. Locked default: thinking OFF.
2. **No `Qwen3-8B-Instruct-4bit` repo on HF.** HARNESS_SPEC §2.MLXAdapter line `model_id="mlx-community/Qwen3-8B-Instruct-4bit"` is wrong; A3 must use `mlx-community/Qwen3-8B-4bit`. (Filed as a one-line spec correction.)
3. **Date hallucination on Fixture 2.** Model rendered "May 5th" as `"2023-05-05"`, not 2026-05-05 — i.e., it doesn't know the current year and defaulted to its training-cutoff. Not a tool-existence problem (correct tool, correct schema, correct args), but worth noting: BFCL-style date arguments may need either a system-prompt date hint or a tolerant grader. For this paper's TEHR metric this doesn't matter — TEHR only scores name-in-registry — but downstream pass-rate scoring may need a date-tolerant comparator.
4. **No refusals or formatting drift observed** across 3 fixtures. No leakage of `<|im_end|>`, no extra commentary outside the envelope when a tool was used, no double tool-calls, no malformed JSON.
5. **First-token latency is high** (≈1-2 s for first decode after KV-cache warmup), but steady-state throughput is healthy (~27 tok/s). For BFCL where most tool-call responses are <100 tokens, expect ~3-5 s per dispatch.
6. **MLX runs cleanly on M5 / Mac17,3** — no Metal kernel errors, default device `Device(gpu, 0)`, mlx 0.31.2 / mlx-metal 0.31.2 / mlx-lm 0.31.3. No M5-specific quirks observed.

## Recommendation for Phase-1 MLXAdapter agent (A3)

The HARNESS_SPEC parser regex `<tool_call>{json}</tool_call>` is **correct and sufficient** for this model — Qwen3-8B-4bit emits exactly that envelope, no `<|tool_call|>` / `[TOOL_CALL]` / OpenAI-style channels.

Concretely:

1. **Use `MODEL_ID = "mlx-community/Qwen3-8B-4bit"`** (not `-Instruct-4bit`); update HARNESS_SPEC §2.MLXAdapter signature accordingly.
2. **Pass `enable_thinking=False` to `apply_chat_template`** by default; expose it as a kwarg only if §6 probe needs comparison. This is the single most important config knob for parse stability.
3. **Parser regex** (already in `mlx_probe.py`):
   ```python
   TOOL_CALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)
   ```
   Use `findall`, then `json.loads` per match, set `parse_ok=False` on `JSONDecodeError`, leave classification (executed / hallucinated / refused) to the runner per §2.MLX contract.
4. **Sampler**: use `make_sampler(temp=0.0)` (greedy) for determinism in main runs. Probe used this; outputs were stable.
5. **Pricing**: `price_per_1k_in = price_per_1k_out = 0.0` per spec. Cost meter never trips on this adapter.
6. **Latency budget**: at 27 tok/s steady-state, the 120 s per-task wall-clock cap in `runner/loop.py` is comfortable; expect typical per-turn dispatch of 2-6 s on BFCL.
7. **Fixture #4 (`parse_fail_malformed`) for `tests/fixtures/mlx_responses.json`**: keep the spec's example (`<tool_call>{"name":"x", "arguments": {oops}</tool_call>`); the regex matches, `json.loads` raises, adapter returns `parse_ok=False, tool_calls=[]`. Verified working with this probe's `parse_tool_calls()`.

## Files produced

- `/Users/cero/Desktop/PROJECTS/icml/PHASE0/mlx_probe.py` — probe script (re-runnable)
- `/Users/cero/Desktop/PROJECTS/icml/PHASE0/mlx_probe_output.txt` — full stdout/stderr from probe run
- `/Users/cero/Desktop/PROJECTS/icml/PHASE0/mlx_probe_results.json` — machine-readable per-fixture results
- `/Users/cero/Desktop/PROJECTS/icml/PHASE0/mlx_feasibility.md` — this verdict
- `/Users/cero/Desktop/PROJECTS/icml/PHASE0/.venv/` — uv venv (Python 3.12.13, mlx-lm 0.31.3, mlx 0.31.2, mlx-metal 0.31.2)
- `~/.cache/huggingface/hub/models--mlx-community--Qwen3-8B-4bit/` — ~5 GB cached weights (outside repo per HF convention)
