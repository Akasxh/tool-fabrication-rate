"""Acceptance tests for `harness.types` and `harness.registry` (Phase-1 Code-A)."""
from __future__ import annotations

import pytest

from harness.registry import (
    RegistryError,
    _normalize_bfcl_schema,
    render_for_anthropic,
    render_for_mlx,
    render_for_openai,
    validate_registry,
)
from harness.types import (
    Action,
    ActionKind,
    ProviderResponse,
    Task,
    ToolCall,
)


# ---------------------------------------------------------------------------
# Acceptance #1 + #2: imports work as listed in the spec.
# ---------------------------------------------------------------------------

def test_types_imports_resolve() -> None:
    assert ToolCall is not None
    assert Task is not None
    assert Action is not None
    assert ActionKind.EXECUTE.value == "execute"
    assert ActionKind.RE_PROMPT.value == "re_prompt"
    assert ActionKind.ABORT.value == "abort"
    assert ProviderResponse is not None


def test_registry_imports_resolve() -> None:
    assert callable(_normalize_bfcl_schema)
    assert callable(validate_registry)
    assert callable(render_for_anthropic)
    assert callable(render_for_openai)
    assert callable(render_for_mlx)


# ---------------------------------------------------------------------------
# Acceptance #3: dict→object rewrite, including nested.
# ---------------------------------------------------------------------------

def test_normalize_rewrites_top_level_dict_to_object() -> None:
    out = _normalize_bfcl_schema({"type": "dict", "properties": {"x": {"type": "dict"}}})
    assert out == {"type": "object", "properties": {"x": {"type": "object"}}}


def test_normalize_preserves_non_dict_types() -> None:
    src = {"type": "string", "enum": ["a", "b"]}
    assert _normalize_bfcl_schema(src) == src


def test_normalize_walks_lists_of_subschemas() -> None:
    src = {"anyOf": [{"type": "dict"}, {"type": "string"}]}
    out = _normalize_bfcl_schema(src)
    assert out == {"anyOf": [{"type": "object"}, {"type": "string"}]}


def test_normalize_does_not_rewrite_dict_string_in_non_type_keys() -> None:
    # The key 'description' carrying the literal value "dict" must not change.
    src = {"description": "dict", "type": "string"}
    assert _normalize_bfcl_schema(src) == src


# ---------------------------------------------------------------------------
# Acceptance #4: idempotency.
# ---------------------------------------------------------------------------

def test_normalize_is_idempotent() -> None:
    src = {
        "type": "dict",
        "properties": {
            "items": {
                "type": "array",
                "items": {"type": "dict", "properties": {"k": {"type": "string"}}},
            }
        },
    }
    once = _normalize_bfcl_schema(src)
    twice = _normalize_bfcl_schema(once)
    assert once == twice


# ---------------------------------------------------------------------------
# validate_registry + renderers.
# ---------------------------------------------------------------------------

def _sample_registry() -> dict:
    return {
        "get_weather": {
            "name": "get_weather",
            "description": "Look up the weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        }
    }


def test_validate_registry_passes_on_clean_input() -> None:
    validate_registry(_sample_registry())


def test_validate_registry_rejects_unnormalized_dict_type() -> None:
    bad = {
        "x": {
            "name": "x",
            "parameters": {"type": "dict", "properties": {}},
        }
    }
    with pytest.raises(RegistryError):
        validate_registry(bad)


def test_validate_registry_rejects_missing_properties_for_object() -> None:
    bad = {
        "x": {
            "name": "x",
            "parameters": {"type": "object"},
        }
    }
    with pytest.raises(RegistryError):
        validate_registry(bad)


def test_validate_registry_rejects_nested_dict_type_leftover() -> None:
    bad = {
        "x": {
            "name": "x",
            "parameters": {
                "type": "object",
                "properties": {"y": {"type": "dict"}},
            },
        }
    }
    with pytest.raises(RegistryError):
        validate_registry(bad)


def test_render_for_anthropic_uses_input_schema() -> None:
    out = render_for_anthropic(_sample_registry())
    assert out == [
        {
            "name": "get_weather",
            "description": "Look up the weather for a city.",
            "input_schema": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        }
    ]


def test_render_for_openai_wraps_in_function_envelope() -> None:
    out = render_for_openai(_sample_registry())
    assert out[0]["type"] == "function"
    assert out[0]["function"]["name"] == "get_weather"
    assert out[0]["function"]["parameters"]["type"] == "object"


def test_render_for_mlx_is_canonical_passthrough() -> None:
    reg = _sample_registry()
    out = render_for_mlx(reg)
    assert out == [reg["get_weather"]]
    # Must be a copy, not the same object — callers may mutate.
    assert out[0] is not reg["get_weather"]
