"""Tool registry helpers + provider-shape renderers.

Canonical in-memory registry shape (per HARNESS_SPEC §2):
    Registry = dict[tool_name, ToolSchema]
where ToolSchema follows the OpenAI ``{"name", "description", "parameters"}``
convention. The BFCL loader applies :func:`_normalize_bfcl_schema` to rewrite
``"type": "dict"`` → ``"type": "object"`` (BFCL's idiosyncratic JSON-Schema
dialect), since all three target adapters reject the ``"dict"`` form.

Public surface:
    - ``Registry``          type alias
    - ``RegistryError``     raised by ``validate_registry``
    - ``_normalize_bfcl_schema(d)``   recursive, idempotent normalizer
    - ``validate_registry(reg)``      structural sanity check
    - ``render_for_anthropic(reg)``   → Anthropic ``tools=`` shape
    - ``render_for_openai(reg)``      → OpenAI ``tools=`` shape
    - ``render_for_mlx(reg)``         → passthrough (Qwen3 chat template)
"""
from __future__ import annotations

from typing import Any

# Canonical OpenAI-shape tool schema: {"name": str, "description": str,
# "parameters": <JSON-Schema object>}. Kept as a plain dict alias to avoid
# tying the registry to a TypedDict the adapters would have to import.
ToolSchema = dict[str, Any]
Registry = dict[str, ToolSchema]


class RegistryError(ValueError):
    """Raised when a tool registry is structurally malformed."""


# Map Python-style type names used in BFCL to canonical JSON Schema 2020-12 types.
# Found in BFCL multi-turn data via empirical scan: only "dict" and "float" appear
# as non-standard values; "int", "tuple", "any" never surfaced in 200-task sample
# but are mapped defensively in case the long tail uses them.
_BFCL_TYPE_REMAP: dict[str, str] = {
    "dict": "object",
    "float": "number",
    "int": "integer",
    "tuple": "array",
    "any": "string",   # JSON Schema has no untyped "any"; "string" is the safest fallback
                       # since no production tool actually uses it (sentinel only).
}


def _normalize_bfcl_schema(d: Any) -> Any:
    """Recursively rewrite Python-style JSON-Schema types to JSON Schema 2020-12.

    BFCL multi-turn task definitions use Python-style type names like
    ``"type": "dict"`` and ``"type": "float"`` in their JSON-Schema parameter
    blocks; Anthropic ``input_schema``, OpenAI ``tools[*].function.parameters``,
    and the Qwen3 chat template all reject these. The normalizer rewrites every
    ``type`` field to the canonical equivalent (see :data:`_BFCL_TYPE_REMAP`).
    It is **idempotent**: running it twice yields the same result.

    Args:
        d: Any nested combination of dicts, lists, and scalars. Non-container
            inputs are returned unchanged.

    Returns:
        A structurally identical object with every non-canonical ``"type"``
        value rewritten at any nesting depth.
    """
    if isinstance(d, dict):
        return {
            k: (_BFCL_TYPE_REMAP.get(v, v)
                if k == "type" and isinstance(v, str)
                else _normalize_bfcl_schema(v))
            for k, v in d.items()
        }
    if isinstance(d, list):
        return [_normalize_bfcl_schema(x) for x in d]
    return d


def validate_registry(registry: Registry) -> None:
    """Sanity-check a registry; raise :class:`RegistryError` on the first defect.

    Checks:
        * Top-level mapping shape.
        * Each value has ``name`` and ``parameters``.
        * ``parameters`` is a dict with a ``type`` field (post-normalization).
        * If ``type == "object"``, ``properties`` is present (may be empty
          dict — JSON Schema permits it but we want it explicit).
        * No leftover ``"type": "dict"`` survives anywhere in the schema tree.
    """
    if not isinstance(registry, dict):
        raise RegistryError(f"registry must be a dict, got {type(registry).__name__}")

    for tool_name, schema in registry.items():
        if not isinstance(schema, dict):
            raise RegistryError(f"tool {tool_name!r}: schema must be a dict")
        if "name" not in schema:
            raise RegistryError(f"tool {tool_name!r}: missing 'name' field")
        if "parameters" not in schema:
            raise RegistryError(f"tool {tool_name!r}: missing 'parameters' field")
        params = schema["parameters"]
        if not isinstance(params, dict):
            raise RegistryError(f"tool {tool_name!r}: 'parameters' must be a dict")
        if "type" not in params:
            raise RegistryError(
                f"tool {tool_name!r}: 'parameters' missing required 'type' field"
            )
        if params["type"] == "dict":
            raise RegistryError(
                f"tool {tool_name!r}: 'parameters.type' is 'dict'; "
                "run _normalize_bfcl_schema before validation"
            )
        if params["type"] == "object" and "properties" not in params:
            raise RegistryError(
                f"tool {tool_name!r}: object-typed parameters require 'properties'"
            )
        if _has_dict_type(params):
            raise RegistryError(
                f"tool {tool_name!r}: nested 'type': 'dict' survived; "
                "loader did not normalize"
            )


def _has_dict_type(d: Any) -> bool:
    """Return True iff any nested ``"type": "dict"`` survives in ``d``."""
    if isinstance(d, dict):
        if d.get("type") == "dict":
            return True
        return any(_has_dict_type(v) for v in d.values())
    if isinstance(d, list):
        return any(_has_dict_type(x) for x in d)
    return False


def render_for_anthropic(registry: Registry) -> list[dict]:
    """Convert canonical registry to Anthropic ``tools=[...]`` shape.

    Anthropic expects ``[{"name", "description", "input_schema"}]``; ``input
    _schema`` carries the JSON-Schema parameters block.
    """
    out: list[dict] = []
    for schema in registry.values():
        out.append(
            {
                "name": schema["name"],
                "description": schema.get("description", ""),
                "input_schema": schema["parameters"],
            }
        )
    return out


def render_for_openai(registry: Registry) -> list[dict]:
    """Convert canonical registry to OpenAI ``tools=[...]`` shape.

    OpenAI expects ``[{"type": "function", "function": {"name", "description",
    "parameters"}}]``. Same shape works for xAI via ``base_url``.
    """
    out: list[dict] = []
    for schema in registry.values():
        out.append(
            {
                "type": "function",
                "function": {
                    "name": schema["name"],
                    "description": schema.get("description", ""),
                    "parameters": schema["parameters"],
                },
            }
        )
    return out


def render_for_mlx(registry: Registry) -> list[dict]:
    """Passthrough for MLX/Qwen3.

    The Qwen3 chat template accepts the canonical OpenAI shape directly via
    ``tokenizer.apply_chat_template(messages, tools=[...], ...)``.
    """
    return [dict(schema) for schema in registry.values()]
