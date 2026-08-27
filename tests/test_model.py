from __future__ import annotations

import unittest

from cogtrace.model import Opcode, TraceEvent


class TraceEventTest(unittest.TestCase):
    def test_round_trip(self) -> None:
        value = {
            "schema_version": 1,
            "trace_id": "trace-1",
            "event_id": "e0",
            "seq": 0,
            "monotonic_ns": 100,
            "source": "agent",
            "opcode": "OBSERVE",
            "operands": {"subject": "input"},
            "parent_id": None,
        }

        event = TraceEvent.from_dict(value)

        self.assertEqual(event.opcode, Opcode.OBSERVE)
        self.assertEqual(event.to_dict(), value)

    def test_unknown_opcode_is_rejected(self) -> None:
        value = {
            "schema_version": 1,
            "trace_id": "trace-1",
            "event_id": "e0",
            "seq": 0,
            "monotonic_ns": 100,
            "source": "agent",
            "opcode": "THINK_HARDER",
            "operands": {},
        }

        with self.assertRaisesRegex(ValueError, "unknown opcode"):
            TraceEvent.from_dict(value)


if __name__ == "__main__":
    unittest.main()
