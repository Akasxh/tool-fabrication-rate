"""Per-task ReAct loop (HARNESS_SPEC §2 + ADDENDUM §B.2). Wires adapter →
classify → intervention (C0/C0.5/C0.7/C1) → executor → trace → cost meter.
Hard caps: 120s wall-clock, 8 turns, one re-prompt per offending turn. Pass
criterion: BFCL → no executor error + no timeout (trajectory-equivalence
checker deferred to Phase-2 offline scorer); τ-bench → terminal reward==1.0.
"""
from __future__ import annotations

import json as _json
import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from harness.adapters.base import ModelAdapter
from harness.cost_meter import BudgetAbort, CostMeter
from harness.intervention import decoy_list, framework_default, naive_retry, rvr
from harness.registry import (
    render_for_anthropic,
    render_for_mlx,
    render_for_openai,
)
from harness.runner.refusal import classify_refusal
from harness.trace_logger import TraceLogger
from harness.types import (
    Action,
    ActionKind,
    ConditionLabel,
    ProviderResponse,
    Task,
    ToolCall,
    ToolCallStatus,
)

_INTERVENTIONS: dict[str, Optional[Callable[..., Action]]] = {
    "C0": None,
    "C0_5": naive_retry.naive_retry,
    "C0_7": framework_default.framework_default,
    "C0_8": decoy_list.decoy_list,
    "C1": rvr.rvr,
}
_INTERVENTION_KIND: dict[str, str] = {
    "C0_5": "naive_retry", "C0_7": "framework_default",
    "C0_8": "decoy_list", "C1": "rvr_rejected",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _render_tools(adapter: ModelAdapter, registry: dict[str, dict]) -> list[dict]:
    """Pass canonical-inner tool schemas to the adapter; each adapter does its
    own provider-specific rendering internally (Anthropic→input_schema,
    OpenAI→{type:function,function:{...}}, MLX→passthrough). The earlier
    pre-render here caused a double-render KeyError for Anthropic.
    """
    return [dict(schema) for schema in registry.values()]


def _append_user_turn(history, subsequent, turn_idx):
    """Push BFCL staged user batch for ``turn_idx`` (≥1) into ``history``."""
    if turn_idx < 1 or (turn_idx - 1) >= len(subsequent):
        return
    for msg in subsequent[turn_idx - 1] or []:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            history.append({"role": msg["role"], "content": msg["content"]})


def _meter(cost_meter, adapter, response):
    cost_meter.add(
        tokens_in=int(response.tokens_in or 0),
        tokens_out=int(response.tokens_out or 0),
        price_in_per_1k=float(getattr(adapter, "price_per_1k_in", 0.0)),
        price_out_per_1k=float(getattr(adapter, "price_per_1k_out", 0.0)),
    )


def _last_turn_cost(cost_meter, retry_used):
    history = getattr(cost_meter, "_history", None)
    if not history:
        return 0.0
    take = 2 if retry_used else 1
    return float(sum(delta for _, _, delta in history[-take:]))


def _classify_and_execute(
    response: ProviderResponse,
    registry: dict[str, dict],
    tool_executor: Callable[[str, dict], dict],
) -> tuple[ToolCallStatus, Optional[dict[str, Any]], Optional[dict[str, Any]]]:
    """Multi-call turn: any hallucinated call → whole turn ``hallucinated``;
    else first call is executed. (One status per turn per HARNESS_SPEC §3.)"""
    if not response.parse_ok:
        return "parse_fail", None, None
    if not response.tool_calls:
        return ("refused", None, None) if classify_refusal(response) else ("executed", None, None)
    for call in response.tool_calls:
        if call.name not in registry:
            return "hallucinated", {"name": call.name, "arguments": dict(call.arguments)}, None
    first = response.tool_calls[0]
    parsed = {"name": first.name, "arguments": dict(first.arguments)}
    try:
        result = tool_executor(first.name, dict(first.arguments))
    except Exception as exc:  # noqa: BLE001
        result = {"error": str(exc), "type": type(exc).__name__}
    if not isinstance(result, dict):
        result = {"output": result}
    return "executed", parsed, result


def run_task(
    task: Task,
    adapter: ModelAdapter,
    condition: ConditionLabel,
    logger: TraceLogger,
    cost_meter: CostMeter,
    tool_executor: Callable[[str, dict], dict],
    turn_timeout_s: float = 120.0,
    max_turns: int = 8,
) -> dict:
    """Run one task end-to-end. Returns ``{pass, tehr_num, tehr_denom, n_turns, terminal}``."""
    if condition not in _INTERVENTIONS:
        raise ValueError(f"Unknown condition {condition!r}; expected {list(_INTERVENTIONS)}")

    deadline = time.monotonic() + float(turn_timeout_s)
    turn_cap = min(int(max_turns), int(getattr(task, "turns_max", max_turns) or max_turns))

    tehr_num = tehr_denom = n_turns = 0
    terminal = "ok"
    saw_executor_error = env_done = False
    env_reward: Optional[float] = None

    subsequent_users: list[list[dict[str, Any]]] = (
        list((task.expected_outcome or {}).get("subsequent_user_messages", []) or [])
        if task.benchmark == "bfcl" else []
    )
    history: list[dict[str, Any]] = [{"role": "user", "content": task.initial_prompt}]
    tools_rendered = _render_tools(adapter, task.registry)
    intervention_fn = _INTERVENTIONS[condition]

    for turn_idx in range(turn_cap):
        if time.monotonic() > deadline:
            terminal = "timed_out"
            break

        if task.benchmark == "bfcl":
            _append_user_turn(history, subsequent_users, turn_idx)

        response = adapter.dispatch(messages=list(history), tools=list(tools_rendered))
        _meter(cost_meter, adapter, response)
        intervention_event: Optional[dict[str, Any]] = None
        retry_used = False

        # At most one re-prompt per turn (HARNESS_SPEC §2).
        if intervention_fn is not None and response.parse_ok and response.tool_calls:
            decision = intervention_fn(list(response.tool_calls), task.registry)
            if decision.kind == ActionKind.RE_PROMPT and decision.feedback:
                intervention_event = {
                    "kind": _INTERVENTION_KIND[condition],
                    "feedback": decision.feedback,
                }
                history.append({"role": "user", "content": decision.feedback})
                response = adapter.dispatch(messages=list(history), tools=list(tools_rendered))
                _meter(cost_meter, adapter, response)
                retry_used = True

        status, parsed_call, tool_response = _classify_and_execute(
            response, task.registry, tool_executor
        )

        # TEHR: refused→excluded; parse_fail→denom only; hallucinated→num+denom;
        # executed-with-call→denom only; executed-no-call→neither.
        if status == "parse_fail":
            tehr_denom += 1
        elif status == "hallucinated":
            tehr_num += 1
            tehr_denom += 1
        elif status == "executed" and parsed_call is not None:
            tehr_denom += 1

        if isinstance(tool_response, dict) and "error" in tool_response:
            saw_executor_error = True

        if task.benchmark == "tau_bench":
            state = getattr(tool_executor, "state", None)
            if isinstance(state, dict):
                env_done = bool(state.get("done", env_done))
                if state.get("reward") is not None:
                    env_reward = float(state["reward"])

        logger.write({
            "task_id": task.id, "model": adapter.model_id, "benchmark": task.benchmark,
            "condition": condition, "turn_idx": turn_idx,
            "agent_message": response.raw_text or "",
            "parsed_tool_call": parsed_call, "tool_call_status": status,
            "tool_response": tool_response, "intervention_event": intervention_event,
            "latency_ms": int(response.latency_ms),
            "tokens_in": int(response.tokens_in), "tokens_out": int(response.tokens_out),
            "cost_usd": float(_last_turn_cost(cost_meter, retry_used)),
            "timestamp": _now_iso(), "schema_version": "1.0",
        })

        # Provider-specific history append. Anthropic requires content-blocks
        # AND a tool_result for EVERY tool_use block in the prior assistant
        # message, even hallucinated ones — otherwise the next dispatch fails
        # with "tool_use ids without tool_result blocks". OpenAI uses role:"tool";
        # MLX uses role:"tool" or plain user.
        adapter_name = type(adapter).__name__
        is_anthropic = "Anthropic" in adapter_name
        if is_anthropic and response.raw_provider_payload:
            assistant_blocks = response.raw_provider_payload.get("content") or []
            if isinstance(assistant_blocks, list) and assistant_blocks:
                history.append({"role": "assistant", "content": assistant_blocks})
                tool_use_blocks = [
                    b for b in assistant_blocks
                    if isinstance(b, dict) and b.get("type") == "tool_use"
                ]
                if tool_use_blocks:
                    tool_results: list[dict[str, Any]] = []
                    chosen_name = parsed_call.get("name") if parsed_call else None
                    for tb in tool_use_blocks:
                        tu_id = tb.get("id"); tu_name = tb.get("name")
                        if (status == "executed" and chosen_name and tu_name == chosen_name
                                and isinstance(tool_response, dict)):
                            content_str = _json.dumps(tool_response, default=str)
                        elif tu_name not in task.registry:
                            content_str = _json.dumps(
                                {"error": "tool_not_found", "name": tu_name}, default=str)
                        else:
                            # In-registry but not the executed one (multi-call turn)
                            content_str = _json.dumps(
                                {"error": "not_executed_first_call_policy",
                                 "name": tu_name}, default=str)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tu_id,
                            "content": content_str,
                        })
                    history.append({"role": "user", "content": tool_results})
            else:
                history.append({"role": "assistant", "content": response.raw_text or ""})
        else:
            history.append({"role": "assistant", "content": response.raw_text or ""})
            if status == "executed" and parsed_call is not None and isinstance(tool_response, dict):
                history.append({
                    "role": "tool", "name": parsed_call["name"],
                    "content": _json.dumps(tool_response, default=str),
                })

        n_turns = turn_idx + 1
        if env_done:
            break
        # If the agent emitted no tool calls AND we have no more staged user
        # messages for the next turn, breaking avoids an Anthropic API error
        # ("conversation must end with a user message") from dispatching with
        # assistant as the last message. We restrict this to the Anthropic
        # path because the constraint is provider-specific; OpenAI and the
        # ScriptedAdapter used in synthetic tests tolerate empty-tail dispatches.
        if (status == "executed" and parsed_call is None
                and task.benchmark == "bfcl"
                and turn_idx >= len(subsequent_users)
                and "Anthropic" in type(adapter).__name__):
            terminal = "agent_stopped"
            break

    if task.benchmark == "tau_bench":
        passed = bool(env_reward == 1.0)
        if not env_done and terminal == "ok":
            terminal = "max_turns"
    else:
        if terminal == "timed_out":
            passed = False
        else:
            passed = not saw_executor_error
            if n_turns >= turn_cap and terminal == "ok":
                terminal = "max_turns"

    return {"pass": passed, "tehr_num": tehr_num, "tehr_denom": tehr_denom,
            "n_turns": n_turns, "terminal": terminal}


__all__ = ["run_task"]
