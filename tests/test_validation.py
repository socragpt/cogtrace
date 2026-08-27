from __future__ import annotations

import unittest

from cogtrace.model import Opcode, TraceEvent
from cogtrace.validation import TraceValidator


def event(
    seq: int,
    opcode: Opcode,
    operands: dict[str, object],
    *,
    event_id: str | None = None,
    parent_id: str | None = None,
    monotonic_ns: int | None = None,
) -> TraceEvent:
    return TraceEvent(
        schema_version=1,
        trace_id="trace",
        event_id=event_id or f"e{seq}",
        seq=seq,
        monotonic_ns=monotonic_ns if monotonic_ns is not None else (seq + 1) * 100,
        source="agent",
        opcode=opcode,
        operands=operands,
        parent_id=parent_id,
    )


class TraceValidatorTest(unittest.TestCase):
    def test_valid_trace(self) -> None:
        trace = [
            event(0, Opcode.OBSERVE, {"subject": "task"}),
            event(
                1,
                Opcode.POLICY_CHECK,
                {"policy": "scope", "result": "allow"},
                parent_id="e0",
            ),
            event(
                2,
                Opcode.CONCLUDE,
                {"result": "continue"},
                parent_id="e1",
            ),
        ]

        self.assertEqual(TraceValidator().validate(trace), [])

    def test_order_parent_and_operand_errors_are_reported(self) -> None:
        trace = [
            event(
                1,
                Opcode.POLICY_CHECK,
                {"policy": "scope", "result": "maybe"},
                event_id="e1",
                parent_id="missing",
                monotonic_ns=200,
            ),
            event(
                0,
                Opcode.EXECUTION_INTENT,
                {"tool": "shell"},
                event_id="e0",
                monotonic_ns=100,
            ),
        ]

        codes = {issue.code for issue in TraceValidator().validate(trace)}

        self.assertIn("invalid_parent", codes)
        self.assertIn("invalid_policy_result", codes)
        self.assertIn("non_monotonic_sequence", codes)
        self.assertIn("non_monotonic_time", codes)
        self.assertIn("missing_operand", codes)

    def test_operand_budget_is_enforced(self) -> None:
        trace = [event(0, Opcode.OBSERVE, {"subject": "x" * 30})]

        codes = {
            issue.code
            for issue in TraceValidator(max_operand_bytes=20).validate(trace)
        }

        self.assertIn("operand_budget_exceeded", codes)


if __name__ == "__main__":
    unittest.main()
