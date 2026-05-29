"""Tests for ``bench_loaders/tau_bench.py`` and the Haiku user-sim override.
No real Anthropic API calls — all SDK paths mocked."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from harness.bench_loaders._tau_user_simulator_haiku import (
    HaikuUserSimulator,
    patch_tau_bench_user_loader,
)
from harness.bench_loaders.tau_bench import (
    DEFAULT_DATA_DIR,
    USER_SIMULATOR_MODEL,
    load_tau_bench_retail,
)
from harness.types import Task


def _fake_client(text: str = "ok") -> MagicMock:
    c = MagicMock()
    c.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(text=text, type="text")],
        usage=SimpleNamespace(input_tokens=42, output_tokens=7),
    )
    return c


def test_default_data_dir_exists() -> None:
    assert Path(DEFAULT_DATA_DIR).exists(), DEFAULT_DATA_DIR


def test_loader_yields_valid_tasks_with_canonical_registry() -> None:
    tasks = list(load_tau_bench_retail(n=3, seed=0))
    assert len(tasks) == 3
    for t in tasks:
        assert isinstance(t, Task)
        assert t.benchmark == "tau_bench" and t.id.startswith("tau_retail_")
        assert isinstance(t.initial_prompt, str) and t.initial_prompt
        assert t.turns_max == 8
        assert isinstance(t.registry, dict) and len(t.registry) == 16
        for name, schema in t.registry.items():
            assert schema["type"] == "function"
            assert schema["function"]["name"] == name
            assert schema["function"]["parameters"]["type"] == "object"


def test_expected_outcome_carries_env_config_and_router() -> None:
    [task] = list(load_tau_bench_retail(n=1, seed=0))
    eo = task.expected_outcome
    assert eo["user_simulator_model"] == "claude-haiku-4-5"
    assert eo["env_class"] == "tau_bench.envs.retail.MockRetailDomainEnv"
    eik = eo["env_init_kwargs"]
    assert eik["user_model"] == "claude-haiku-4-5"
    assert eik["user_provider"] == "anthropic"
    assert eik["task_split"] == "test"
    assert isinstance(eik["task_index"], int)
    assert isinstance(eo["actions"], list) and eo["actions"]
    assert all("name" in a and "kwargs" in a for a in eo["actions"])
    assert isinstance(eo["user_id"], str) and eo["user_id"]


def test_determinism_and_seed_sensitivity() -> None:
    a = [t.id for t in load_tau_bench_retail(n=5, seed=0)]
    b = [t.id for t in load_tau_bench_retail(n=5, seed=0)]
    assert a == b
    c = [t.expected_outcome["task_index"] for t in load_tau_bench_retail(n=10, seed=0)]
    d = [t.expected_outcome["task_index"] for t in load_tau_bench_retail(n=10, seed=42)]
    assert c != d


def test_unknown_split_raises() -> None:
    with pytest.raises(ValueError):
        list(load_tau_bench_retail(n=1, seed=0, split="bogus"))


def test_haiku_simulator_respond_returns_string() -> None:
    sim = HaikuUserSimulator(anthropic_client=_fake_client("hi agent"))
    out = sim.respond([{"role": "user", "content": "hello"}])
    assert isinstance(out, str) and out == "hi agent"


def test_haiku_simulator_reset_step_match_protocol() -> None:
    client = _fake_client("first")
    sim = HaikuUserSimulator(anthropic_client=client)
    assert sim.reset(instruction="You want a refund.") == "first"
    ck = client.messages.create.call_args.kwargs
    assert "Instruction: You want a refund." in ck["system"]
    assert ck["model"] == USER_SIMULATOR_MODEL
    client.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(text="second", type="text")],
        usage=SimpleNamespace(input_tokens=10, output_tokens=4),
    )
    assert sim.step("How can I help?") == "second"
    assert sim.get_total_cost() > 0


def test_haiku_simulator_handles_empty_content() -> None:
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        content=[], usage=SimpleNamespace(input_tokens=0, output_tokens=0)
    )
    assert HaikuUserSimulator(anthropic_client=client).respond(
        [{"role": "user", "content": "x"}]
    ) == ""


def test_patch_tau_bench_user_loader_swaps_load_user() -> None:
    pytest.importorskip("litellm")  # τ-bench user.py imports litellm
    import tau_bench.envs.user as tb_user  # type: ignore[import-not-found]

    original = tb_user.load_user
    try:
        patch_tau_bench_user_loader(anthropic_client=_fake_client())
        sim = tb_user.load_user("llm", model="ignored", provider="ignored")
        assert isinstance(sim, HaikuUserSimulator)
    finally:
        tb_user.load_user = original
