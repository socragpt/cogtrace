"""Typed data model for CogTrace events."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class Opcode(str, Enum):
    """Version 0.1 reasoning instruction vocabulary."""

    OBSERVE = "OBSERVE"
    RETRIEVE = "RETRIEVE"
    HYPOTHESIZE = "HYPOTHESIZE"
    EVALUATE = "EVALUATE"
    POLICY_CHECK = "POLICY_CHECK"
    PLAN = "PLAN"
    EXECUTION_INTENT = "EXECUTION_INTENT"
    UPDATE = "UPDATE"
    CONCLUDE = "CONCLUDE"


@dataclass(frozen=True)
class TraceEvent:
    """One versioned event in a structured reasoning trace.

    Sequence numbers, timestamps, and event IDs are expected to be assigned by
    the experiment harness in a real collection system.
    """

    schema_version: int
    trace_id: str
    event_id: str
    seq: int
    monotonic_ns: int
    source: str
    opcode: Opcode
    operands: Mapping[str, Any]
    parent_id: str | None = None

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TraceEvent":
        """Parse an event envelope and reject malformed field types early."""

        required = {
            "schema_version",
            "trace_id",
            "event_id",
            "seq",
            "monotonic_ns",
            "source",
            "opcode",
            "operands",
        }
        missing = sorted(required - value.keys())
        if missing:
            raise ValueError(f"missing event fields: {', '.join(missing)}")

        if not isinstance(value["schema_version"], int):
            raise ValueError("schema_version must be an integer")
        if not isinstance(value["trace_id"], str) or not value["trace_id"]:
            raise ValueError("trace_id must be a non-empty string")
        if not isinstance(value["event_id"], str) or not value["event_id"]:
            raise ValueError("event_id must be a non-empty string")
        if not isinstance(value["seq"], int):
            raise ValueError("seq must be an integer")
        if not isinstance(value["monotonic_ns"], int):
            raise ValueError("monotonic_ns must be an integer")
        if not isinstance(value["source"], str) or not value["source"]:
            raise ValueError("source must be a non-empty string")
        if not isinstance(value["operands"], Mapping):
            raise ValueError("operands must be an object")

        parent_id = value.get("parent_id")
        if parent_id is not None and not isinstance(parent_id, str):
            raise ValueError("parent_id must be a string or null")

        try:
            opcode = Opcode(value["opcode"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"unknown opcode: {value['opcode']!r}") from error

        return cls(
            schema_version=value["schema_version"],
            trace_id=value["trace_id"],
            event_id=value["event_id"],
            seq=value["seq"],
            monotonic_ns=value["monotonic_ns"],
            source=value["source"],
            opcode=opcode,
            operands=dict(value["operands"]),
            parent_id=parent_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable event envelope."""

        return {
            "schema_version": self.schema_version,
            "trace_id": self.trace_id,
            "event_id": self.event_id,
            "seq": self.seq,
            "monotonic_ns": self.monotonic_ns,
            "source": self.source,
            "opcode": self.opcode.value,
            "operands": dict(self.operands),
            "parent_id": self.parent_id,
        }
