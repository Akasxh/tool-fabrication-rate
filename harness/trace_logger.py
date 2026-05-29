"""JSONL trace writer with schema validation and substring redaction.

Implements ``TraceLogger`` per HARNESS_SPEC.md §2 and §3 (16-field schema).

The writer is append-only, flushes after every line so a kill -9 never loses
trailing records, and validates each record against a pydantic model that
mirrors §3 exactly. ``raw_provider_payload`` is dropped on write unless
``persist_raw=True`` was passed at construction time (HARNESS_SPEC §8.3 default).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, IO, Optional

from pydantic import BaseModel, Field, ValidationError


class TraceSchemaError(ValueError):
    """Raised when ``TraceLogger.write`` receives a record violating §3."""


class TraceRecord(BaseModel):
    """Pydantic model mirroring HARNESS_SPEC §3 (16 required fields).

    Field nullability matches the spec table. ``raw_provider_payload`` is an
    optional 17th field tolerated on input and dropped on write unless
    ``persist_raw=True``.
    """

    model_config = {"extra": "allow"}

    task_id: str
    model: str
    benchmark: str
    condition: str
    turn_idx: int
    agent_message: str
    parsed_tool_call: Optional[dict[str, Any]] = None
    tool_call_status: str
    tool_response: Optional[dict[str, Any]] = None
    intervention_event: Optional[dict[str, Any]] = None
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    timestamp: str
    schema_version: str = Field(pattern=r"^1\.0$")


class TraceLogger:
    """Append-only JSONL trace writer.

    Args:
        out_path: Destination JSONL file. Opened lazily in append mode on
            first :meth:`write` (never truncates).
        redact_keys: Substrings to replace with ``"[REDACTED]"`` in
            ``agent_message`` and ``tool_response`` (stringified) prior to
            writing. Useful for stripping user emails / API keys.
        persist_raw: When ``False`` (default per HARNESS_SPEC §8.3), drops
            ``raw_provider_payload`` from every record before write. Set to
            ``True`` only for adapter debugging.
    """

    def __init__(
        self,
        out_path: Path | str,
        redact_keys: list[str] | None = None,
        persist_raw: bool = False,
    ) -> None:
        self._out_path: Path = Path(out_path)
        self._redact_keys: list[str] = list(redact_keys) if redact_keys else []
        self._persist_raw: bool = persist_raw
        self._fh: Optional[IO[str]] = None

    def _ensure_open(self) -> IO[str]:
        if self._fh is None:
            self._out_path.parent.mkdir(parents=True, exist_ok=True)
            self._fh = self._out_path.open("a", encoding="utf-8")
        return self._fh

    def _redact(self, value: Any) -> Any:
        if not self._redact_keys or value is None:
            return value
        if isinstance(value, str):
            out: str = value
            for key in self._redact_keys:
                if key:
                    out = out.replace(key, "[REDACTED]")
            return out
        if isinstance(value, dict):
            return {k: self._redact(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._redact(v) for v in value]
        return value

    def write(self, record: dict) -> None:
        """Validate, redact, and append a single trace record as one JSONL line.

        Raises:
            TraceSchemaError: if the record fails §3 validation. Error message
                includes the offending field name(s).
        """
        try:
            validated: TraceRecord = TraceRecord.model_validate(record)
        except ValidationError as exc:
            field_names: list[str] = [
                ".".join(str(p) for p in err["loc"]) for err in exc.errors()
            ]
            raise TraceSchemaError(
                f"Trace record violates §3 schema; fields: {field_names}"
            ) from exc

        out: dict[str, Any] = validated.model_dump()
        if not self._persist_raw:
            out.pop("raw_provider_payload", None)
        # Redact agent_message + tool_response substrings.
        if self._redact_keys:
            out["agent_message"] = self._redact(out.get("agent_message"))
            out["tool_response"] = self._redact(out.get("tool_response"))

        line: str = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
        fh: IO[str] = self._ensure_open()
        fh.write(line + "\n")
        fh.flush()

    def close(self) -> None:
        """Close the underlying file handle (idempotent)."""
        if self._fh is not None:
            self._fh.close()
            self._fh = None
