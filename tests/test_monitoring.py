from __future__ import annotations

import unittest
from pathlib import Path

from cogtrace.io import load_trace_jsonl
from cogtrace.monitoring import RiskTag, StructuredTraceMonitor


ROOT = Path(__file__).resolve().parents[1]


class StructuredTraceMonitorTest(unittest.TestCase):
    def test_policy_bypass_example(self) -> None:
        events = load_trace_jsonl(ROOT / "examples/traces/policy-bypass.jsonl")

        tags = {finding.tag for finding in StructuredTraceMonitor().analyze(events)}

        self.assertEqual(
            tags,
            {
                RiskTag.ALIGN_COT_BYPASS,
                RiskTag.COLLUDE_CHANNEL_DISCOVERY,
            },
        )


if __name__ == "__main__":
    unittest.main()
