"""Tool-executor factories for BFCL (stateful classes) + τ-bench (Env).

Each factory returns ``Callable[[str, dict], dict]``: success →
``{"output": ...}``, failure → ``{"error": str, "type": exc_class}``. Lifecycle
is per-task. See HARNESS_SPEC §7 + PHASE0 §3.2/§4.2.
"""
from __future__ import annotations

import copy
import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from harness.types import Task

_BFCL_ROOT = (
    Path(__file__).resolve().parent.parent / "data" / "bfcl_v4" / "repo"
    / "berkeley-function-call-leaderboard"
)
# Class-name → module-suffix (under the BFCL func_source_code package).
_BFCL_PKG = "bfcl_eval.eval_checker.multi_turn_eval.func_source_code"
_BFCL_CLASS_TO_MODULE: dict[str, str] = {
    f"{cls}": f"{_BFCL_PKG}.{stem}"
    for cls, stem in (
        ("GorillaFileSystem", "gorilla_file_system"), ("MathAPI", "math_api"),
        ("MessageAPI", "message_api"), ("TwitterAPI", "posting_api"),
        ("TicketAPI", "ticket_api"), ("TradingBot", "trading_bot"),
        ("TravelAPI", "travel_booking"), ("VehicleControlAPI", "vehicle_control"),
        ("WebSearchAPI", "web_search"), ("MemoryAPI_kv", "memory_kv"),
        ("MemoryAPI_vector", "memory_vector"), ("MemoryAPI_rec_sum", "memory_rec_sum"),
    )
}
_BFCL_STATELESS: frozenset[str] = frozenset({"MathAPI"})


def _ensure_bfcl_on_path() -> None:
    if _BFCL_ROOT.is_dir() and str(_BFCL_ROOT) not in sys.path:
        sys.path.insert(0, str(_BFCL_ROOT))


def _instantiate_bfcl_class(class_name: str, init_config: dict | None) -> Any:
    module_path = _BFCL_CLASS_TO_MODULE.get(class_name, f"{_BFCL_PKG}.{class_name}")
    cls = getattr(importlib.import_module(module_path), class_name)
    instance = cls()
    if class_name not in _BFCL_STATELESS and init_config is not None:
        loader = getattr(instance, "_load_scenario", None)
        if callable(loader):
            scenario = copy.deepcopy(init_config)
            try:
                loader(scenario)
            except TypeError:
                loader(scenario, False)  # some classes take a long_context arg
    return instance


def make_bfcl_executor(task: Task) -> Callable[[str, dict], dict]:
    """Build a BFCL tool executor for ``task``; dispatches via ``getattr``."""
    _ensure_bfcl_on_path()
    expected = task.expected_outcome or {}
    involved: list[str] = list(expected.get("involved_classes", []))
    initial_config: dict = dict(expected.get("initial_config", {}) or {})

    method_owner: dict[str, Any] = {}
    for cls_name in involved:
        inst = _instantiate_bfcl_class(cls_name, initial_config.get(cls_name, {}))
        for attr in dir(inst):
            if attr.startswith("_"):
                continue
            if callable(getattr(inst, attr, None)) and attr not in method_owner:
                method_owner[attr] = inst

    def executor(name: str, args: dict) -> dict:
        owner = method_owner.get(name)
        if owner is None:
            return {"error": f"AttributeError: {name!r}", "type": "AttributeError"}
        try:
            return {"output": getattr(owner, name)(**(args or {}))}
        except Exception as exc:  # noqa: BLE001 — runner classifies; never crash
            return {"error": str(exc), "type": type(exc).__name__}

    return executor


def _resolve_tau_env_class(fqn: str) -> Any:
    """Resolve the τ-bench env class for ``fqn`` (e.g.
    ``tau_bench.envs.retail.MockRetailDomainEnv``).

    The loader stubs the ``...retail`` package ``__init__`` (which would import
    litellm at import time) with an empty namespace module, so the class is NOT
    an attribute of the package object. We therefore try the package attribute
    first, then fall back to the ``...retail.env`` submodule that actually
    defines the class. Stubs are (re)installed defensively in case the executor
    is constructed before the loader ran in this process."""
    from harness.bench_loaders.tau_bench import (
        DEFAULT_DATA_DIR,
        _install_namespace_stubs,
    )

    _install_namespace_stubs(Path(DEFAULT_DATA_DIR))
    module_name, _, class_name = fqn.rpartition(".")
    mod = importlib.import_module(module_name)
    cls = getattr(mod, class_name, None)
    if cls is not None:
        return cls
    # Fallback: the real definition lives in the `.env` submodule.
    submod = importlib.import_module(f"{module_name}.env")
    return getattr(submod, class_name)


def make_tau_bench_executor(
    task: Task, anthropic_client: Optional[Any] = None,
) -> Callable[[str, dict], dict]:
    """Build a τ-bench env-step executor for ``task``.

    Patches τ-bench's GPT-4o user simulator with the Haiku replacement BEFORE
    the env class is imported (HARNESS_SPEC §8.9). Calls ``env.reset(task_index)``
    so the env loads the task DB + user instruction; the resulting initial
    observation (the user's first message) is exposed on
    ``executor.state["initial_observation"]`` for the runner to seed history.

    The agent talks to the user simulator via the ``respond`` pseudo-tool
    (τ-bench ``RESPOND_ACTION_NAME``); a ``respond`` call is stepped through the
    env exactly like a real tool, routing ``content`` to the user sim.
    """
    from harness.bench_loaders._tau_user_simulator_haiku import (
        patch_tau_bench_user_loader,
    )

    expected = task.expected_outcome or {}
    fqn: str = expected.get("env_class", "tau_bench.envs.retail.MockRetailDomainEnv")
    init_kwargs: dict = dict(expected.get("env_init_kwargs", {}) or {})
    task_index: Optional[int] = expected.get("task_index")

    patch_tau_bench_user_loader(anthropic_client=anthropic_client)
    EnvCls = _resolve_tau_env_class(fqn)
    env = EnvCls(**init_kwargs)

    state: dict[str, Any] = {
        "done": False, "reward": 0.0, "last_info": None,
        "initial_observation": "", "reset_ok": False, "reset_error": None,
    }
    # Reset loads the task DB and returns the user's opening message. Never let a
    # reset failure crash the runner — record it so the cell surfaces a system
    # failure instead.
    try:
        reset_resp = env.reset(task_index=task_index)
        state["initial_observation"] = getattr(reset_resp, "observation", "") or ""
        state["last_info"] = getattr(reset_resp, "info", None)
        state["reset_ok"] = True
    except Exception as exc:  # noqa: BLE001
        state["reset_error"] = f"{type(exc).__name__}: {exc}"

    def executor(name: str, args: dict) -> dict:
        if state["done"]:
            return {"error": "env is done", "type": "RuntimeError"}
        try:
            from tau_bench.types import Action  # type: ignore[import-not-found]

            resp = env.step(Action(name=name, kwargs=dict(args or {})))
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc), "type": type(exc).__name__}
        observation = getattr(resp, "observation", "")
        reward = float(getattr(resp, "reward", 0.0) or 0.0)
        done = bool(getattr(resp, "done", False))
        state.update({"done": done, "reward": reward,
                      "last_info": getattr(resp, "info", None)})
        return {"output": observation, "reward": reward, "done": done}

    executor.env = env  # type: ignore[attr-defined]
    executor.state = state  # type: ignore[attr-defined]
    return executor
