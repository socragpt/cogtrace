"""Trace validation independent of risk monitoring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from .model import Opcode, TraceEvent


REQUIRED_OPERANDS: dict[Opcode, dict[str, type]] = {
    Opcode.OBSERVE: {"subject": str},
    Opcode.RETRIEVE: {"query": str, "source": str},
    Opcode.HYPOTHESIZE: {"claim": str},
    Opcode.EVALUATE: {"claim": str, "result": str},
    Opcode.POLICY_CHECK: {"policy": str, "result": str},
    Opcode.PLAN: {"goal": str},
    Opcode.EXECUTION_INTENT: {"tool": str, "operation": str},
    Opcode.UPDATE: {"belief": str},
    Opcode.CONCLUDE: {"result": str},
}

KNOWN_SOURCES = {"agent", "translator", "harness", "telemetry"}
POLICY_RESULTS = {"allow", "deny", "unknown"}


@dataclass(frozen=True)
class ValidationIssue:
    """One machine-readable trace validity issue."""

    code: str
    message: str
    event_id: str | None = None
    seq: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "event_id": self.event_id,
            "seq": self.seq,
        }


class TraceValidator:
    """Validate envelope ordering, provenance, and opcode operands."""

    def __init__(
        self,
        *,
        supported_schema_version: int = 1,
        max_events: int = 512,
        max_operand_bytes: int = 4096,
    ) -> None:
        self.supported_schema_version = supported_schema_version
        self.max_events = max_events
        self.max_operand_bytes = max_operand_bytes

    def validate(self, events: Iterable[TraceEvent]) -> list[ValidationIssue]:
        trace = list(events)
        issues: list[ValidationIssue] = []

        if not trace:
            return [ValidationIssue("empty_trace", "trace contains no events")]
        if len(trace) > self.max_events:
            issues.append(
                ValidationIssue(
                    "event_budget_exceeded",
                    f"trace has {len(trace)} events; limit is {self.max_events}",
                )
            )

        expected_trace_id = trace[0].trace_id
        seen_ids: dict[str, TraceEvent] = {}
        previous_seq: int | None = None
        previous_time: int | None = None

        for event in trace:
            context = {"event_id": event.event_id, "seq": event.seq}

            if event.schema_version != self.supported_schema_version:
                issues.append(
                    ValidationIssue(
                        "unsupported_schema",
                        f"schema version {event.schema_version} is not supported",
                        **context,
                    )
                )
            if event.trace_id != expected_trace_id:
                issues.append(
                    ValidationIssue(
                        "mixed_trace_ids",
                        f"expected trace_id {expected_trace_id!r}",
                        **context,
                    )
                )
            if event.event_id in seen_ids:
                issues.append(
                    ValidationIssue(
                        "duplicate_event_id",
                        f"event_id {event.event_id!r} is repeated",
                        **context,
                    )
                )
            if previous_seq is not None and event.seq <= previous_seq:
                issues.append(
                    ValidationIssue(
                        "non_monotonic_sequence",
                        f"sequence {event.seq} does not follow {previous_seq}",
                        **context,
                    )
                )
            if previous_time is not None and event.monotonic_ns <= previous_time:
                issues.append(
                    ValidationIssue(
                        "non_monotonic_time",
                        "monotonic_ns must strictly increase",
                        **context,
                    )
                )
            if event.parent_id is not None and event.parent_id not in seen_ids:
                issues.append(
                    ValidationIssue(
                        "invalid_parent",
                        f"parent {event.parent_id!r} is not an earlier event",
                        **context,
                    )
                )
            if event.source not in KNOWN_SOURCES:
                issues.append(
                    ValidationIssue(
                        "unknown_source",
                        f"source {event.source!r} is not declared by schema v1",
                        **context,
                    )
                )

            self._validate_operands(event, issues)
            seen_ids[event.event_id] = event
            previous_seq = event.seq
            previous_time = event.monotonic_ns

        return issues

    def _validate_operands(
        self, event: TraceEvent, issues: list[ValidationIssue]
    ) -> None:
        context = {"event_id": event.event_id, "seq": event.seq}
        required = REQUIRED_OPERANDS[event.opcode]
        for name, expected_type in required.items():
            if name not in event.operands:
                issues.append(
                    ValidationIssue(
                        "missing_operand",
                        f"{event.opcode.value} requires operand {name!r}",
                        **context,
                    )
                )
            elif not isinstance(event.operands[name], expected_type):
                issues.append(
                    ValidationIssue(
                        "invalid_operand_type",
                        f"operand {name!r} must be {expected_type.__name__}",
                        **context,
                    )
                )

        if (
            event.opcode is Opcode.POLICY_CHECK
            and event.operands.get("result") not in POLICY_RESULTS
        ):
            issues.append(
                ValidationIssue(
                    "invalid_policy_result",
                    "POLICY_CHECK result must be allow, deny, or unknown",
                    **context,
                )
            )

        try:
            serialized = json.dumps(event.operands, separators=(",", ":"))
        except (TypeError, ValueError):
            issues.append(
                ValidationIssue(
                    "non_json_operands",
                    "operands must contain only JSON-compatible values",
                    **context,
                )
            )
            return
        operand_bytes = len(serialized.encode("utf-8"))
        if operand_bytes > self.max_operand_bytes:
            issues.append(
                ValidationIssue(
                    "operand_budget_exceeded",
                    f"operands use {operand_bytes} bytes; limit is {self.max_operand_bytes}",
                    **context,
                )
            )
