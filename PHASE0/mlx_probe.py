"""
Gate 0.5 — MLX + Qwen3-8B tool-calling feasibility probe.

Loads `mlx-community/Qwen3-8B-4bit`, runs 3 fixed fixture prompts against a
3-tool registry, parses Qwen3 `<tool_call>{json}</tool_call>` envelopes, and
reports raw + parsed output, parse_ok, and basic perf telemetry.

Decision target: does the local-OSS tier stay CORE in the SCALE @ ICML 2026
paper, or get DROPped?

Run:
    source /Users/cero/Desktop/PROJECTS/icml/PHASE0/.venv/bin/activate
    python /Users/cero/Desktop/PROJECTS/icml/PHASE0/mlx_probe.py
"""
from __future__ import annotations

import json
import os
import re
import resource
import sys
import time
from dataclasses import dataclass
from typing import Any

# Pin caches inside the repo so the user can see what was fetched.
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import mlx.core as mx
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler


MODEL_ID = "mlx-community/Qwen3-8B-4bit"

# 3-tool registry per prompt; JSON Schema (subset) per Qwen3 chat template
# expects {"type":"function","function":{"name":..., "description":..., "parameters":{...}}}.
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather conditions for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'San Francisco'.",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_flight",
            "description": "Book a flight between two airports on a given date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "IATA code or city name of origin airport.",
                    },
                    "destination": {
                        "type": "string",
                        "description": "IATA code or city name of destination airport.",
                    },
                    "date": {
                        "type": "string",
                        "description": "Travel date in YYYY-MM-DD format.",
                    },
                },
                "required": ["origin", "destination", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject."},
                    "body": {"type": "string", "description": "Email body text."},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
]


@dataclass
class Fixture:
    name: str
    user_prompt: str
    expected_tool: str | None  # None = should not call any tool


FIXTURES: list[Fixture] = [
    Fixture(
        name="weather_sf",
        user_prompt="What's the weather in San Francisco?",
        expected_tool="get_weather",
    ),
    Fixture(
        name="flight_jfk_lhr",
        user_prompt="Book me a flight from JFK to LHR on May 5th.",
        expected_tool="book_flight",
    ),
    Fixture(
        name="capital_of_france",
        user_prompt="What's the capital of France?",
        expected_tool=None,
    ),
]


# Qwen3 tool-call envelope: <tool_call>\n{json}\n</tool_call>  (newlines optional).
TOOL_CALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)


def parse_tool_calls(raw: str) -> tuple[list[dict[str, Any]], bool]:
    """Return (parsed_calls, parse_ok). parse_ok is True iff every regex match
    decoded as JSON. If there are zero matches, parse_ok is True (legitimate
    no-tool-call case)."""
    matches = TOOL_CALL_RE.findall(raw)
    calls: list[dict[str, Any]] = []
    parse_ok = True
    for m in matches:
        try:
            calls.append(json.loads(m))
        except json.JSONDecodeError:
            parse_ok = False
    return calls, parse_ok


def peak_rss_mb() -> float:
    """Peak resident-set size in MiB for this process (macOS reports bytes)."""
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is bytes on Darwin, kilobytes on Linux. We're on Darwin.
    return ru.ru_maxrss / (1024 * 1024)


def render_prompt(tokenizer, user_prompt: str) -> str:
    """Apply Qwen3 chat template with tools, generation prompt, thinking disabled."""
    messages = [{"role": "user", "content": user_prompt}]
    return tokenizer.apply_chat_template(
        messages,
        tools=TOOLS,
        add_generation_prompt=True,
        tokenize=False,
        # Qwen3 reasoning is on by default; we disable it so output is the
        # tool-call envelope without a leading <think>...</think> block, which
        # is what the harness MLXAdapter will want.
        enable_thinking=False,
    )


def main() -> int:
    print("=" * 78)
    print("MLX + Qwen3-8B tool-calling feasibility probe (Gate 0.5)")
    print("=" * 78)
    print(f"model_id        : {MODEL_ID}")
    print(f"mlx.core        : {mx.__version__ if hasattr(mx, '__version__') else 'n/a'}")
    print(f"python          : {sys.version.split()[0]}")
    print(f"default_device  : {mx.default_device()}")
    print()

    print("Loading model + tokenizer (first run downloads ~5-6 GB)...")
    t_load_0 = time.perf_counter()
    model, tokenizer = load(MODEL_ID)
    t_load_1 = time.perf_counter()
    load_secs = t_load_1 - t_load_0
    print(f"Model loaded in {load_secs:.2f}s.")
    print(f"Peak RSS after load: {peak_rss_mb():.0f} MiB")
    print()

    # Greedy sampler so the probe is deterministic across reruns.
    sampler = make_sampler(temp=0.0)

    results: list[dict[str, Any]] = []
    total_gen_tokens = 0
    total_gen_secs = 0.0

    for fx in FIXTURES:
        print("-" * 78)
        print(f"FIXTURE: {fx.name}")
        print(f"  user_prompt    : {fx.user_prompt!r}")
        print(f"  expected_tool  : {fx.expected_tool!r}")

        prompt = render_prompt(tokenizer, fx.user_prompt)
        prompt_tokens = len(tokenizer.encode(prompt))

        t0 = time.perf_counter()
        raw = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=512,
            sampler=sampler,
            verbose=False,
        )
        t1 = time.perf_counter()
        gen_secs = t1 - t0
        gen_tokens = len(tokenizer.encode(raw))
        tps = gen_tokens / gen_secs if gen_secs > 0 else float("nan")
        total_gen_tokens += gen_tokens
        total_gen_secs += gen_secs

        calls, parse_ok = parse_tool_calls(raw)

        # "Did the model do the right thing?" check
        if fx.expected_tool is None:
            expectation_met = len(calls) == 0
        else:
            expectation_met = any(c.get("name") == fx.expected_tool for c in calls)

        print(f"  prompt_tokens  : {prompt_tokens}")
        print(f"  gen_tokens     : {gen_tokens}")
        print(f"  gen_secs       : {gen_secs:.2f}")
        print(f"  tokens/sec     : {tps:.1f}")
        print(f"  parse_ok       : {parse_ok}")
        print(f"  parsed_calls  : {json.dumps(calls)}")
        print(f"  expectation_met: {expectation_met}")
        print(f"  --- raw generation begin ---")
        print(raw)
        print(f"  --- raw generation end ---")

        results.append(
            {
                "fixture": fx.name,
                "user_prompt": fx.user_prompt,
                "expected_tool": fx.expected_tool,
                "raw": raw,
                "parsed_calls": calls,
                "parse_ok": parse_ok,
                "expectation_met": expectation_met,
                "prompt_tokens": prompt_tokens,
                "gen_tokens": gen_tokens,
                "gen_secs": gen_secs,
                "tokens_per_sec": tps,
            }
        )

    print("-" * 78)
    print("SUMMARY")
    print(f"  fixtures run               : {len(results)}")
    print(f"  parse_ok                   : {sum(r['parse_ok'] for r in results)}/{len(results)}")
    print(f"  expectation_met            : {sum(r['expectation_met'] for r in results)}/{len(results)}")
    print(f"  total gen tokens           : {total_gen_tokens}")
    print(f"  total gen secs             : {total_gen_secs:.2f}")
    if total_gen_secs > 0:
        print(f"  aggregate tokens/sec       : {total_gen_tokens/total_gen_secs:.1f}")
    print(f"  model load secs            : {load_secs:.2f}")
    print(f"  peak RSS (process, MiB)    : {peak_rss_mb():.0f}")
    print()

    # Persist a machine-readable summary alongside the human log.
    out_json = "/Users/cero/Desktop/PROJECTS/icml/PHASE0/mlx_probe_results.json"
    with open(out_json, "w") as f:
        json.dump(
            {
                "model_id": MODEL_ID,
                "load_secs": load_secs,
                "peak_rss_mib": peak_rss_mb(),
                "fixtures": results,
            },
            f,
            indent=2,
        )
    print(f"Wrote machine-readable results: {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
