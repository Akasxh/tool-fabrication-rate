"""Unit tests for ``harness/runner/executors.py``."""
from __future__ import annotations

import sys
import types as _types

import pytest

from harness.runner import executors
from harness.types import Task


class _SyntheticFS:
    def __init__(self) -> None:
        self.scenario: dict = {}

    def _load_scenario(self, scenario):
        self.scenario = scenario

    def cat(self, file_name):
        return f"contents-of-{file_name}"

    def boom(self):
        raise ValueError("intentional")


@pytest.fixture()
def synthetic_bfcl(monkeypatch):
    qn = "bfcl_eval.eval_checker.multi_turn_eval.func_source_code.synthetic_fs"
    mod = _types.ModuleType(qn)
    mod.SyntheticFS = _SyntheticFS  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, qn, mod)
    monkeypatch.setitem(executors._BFCL_CLASS_TO_MODULE, "SyntheticFS", qn)
    return qn


def _bfcl_task():
    return Task(id="bfcl_unit", benchmark="bfcl", registry={}, initial_prompt="x", turns_max=8,
                expected_outcome={"involved_classes": ["SyntheticFS"],
                                  "initial_config": {"SyntheticFS": {"root": "/tmp"}}})


def test_bfcl_executor_dispatches(synthetic_bfcl):
    exe = executors.make_bfcl_executor(_bfcl_task())
    assert exe("cat", {"file_name": "report.txt"}) == {"output": "contents-of-report.txt"}


def test_bfcl_executor_unknown_method(synthetic_bfcl):
    exe = executors.make_bfcl_executor(_bfcl_task())
    assert exe("does_not_exist", {})["type"] == "AttributeError"


def test_bfcl_executor_catches_method_exception(synthetic_bfcl):
    out = executors.make_bfcl_executor(_bfcl_task())("boom", {})
    assert out["type"] == "ValueError" and "intentional" in out["error"]


class _StubResp:
    def __init__(self, observation="hi", reward=0.0, done=False):
        self.observation, self.reward, self.done, self.info = observation, reward, done, {}


class _StubEnv:
    def __init__(self, **kw):
        self.kw = kw

    def step(self, action):
        return _StubResp(observation="ok", reward=1.0, done=True)


def _stub_module(monkeypatch, name, **attrs):
    m = _types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    monkeypatch.setitem(sys.modules, name, m)
    return m


def test_tau_executor_patches_user_loader_then_steps(monkeypatch):
    state = {"patch_called": False}
    _stub_module(monkeypatch, "harness.bench_loaders._tau_user_simulator_haiku",
                 patch_tau_bench_user_loader=lambda anthropic_client=None:
                     state.__setitem__("patch_called", True))

    class _Action:
        def __init__(self, name, kwargs):
            self.name, self.kwargs = name, kwargs

    _stub_module(monkeypatch, "tau_bench")
    _stub_module(monkeypatch, "tau_bench.types", Action=_Action)
    _stub_module(monkeypatch, "tau_bench.envs")
    _stub_module(monkeypatch, "tau_bench.envs.fake", MockEnv=_StubEnv)

    task = Task(id="tau_unit", benchmark="tau_bench", registry={}, initial_prompt="hi",
                turns_max=8,
                expected_outcome={"env_class": "tau_bench.envs.fake.MockEnv",
                                  "env_init_kwargs": {"task_index": 0}})
    exe = executors.make_tau_bench_executor(task)
    assert state["patch_called"] is True
    out = exe("get_user_details", {"user_id": "u_1"})
    assert out["output"] == "ok" and out["reward"] == 1.0 and out["done"] is True
    assert exe("anything", {})["type"] == "RuntimeError"
