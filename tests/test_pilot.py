from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from cogtrace.backends import FixtureBackend
from cogtrace.cli import main
from cogtrace.pilot import (
    PilotRunner,
    Treatment,
    load_pilot_tasks,
    parse_event_payloads,
    task_fixtures,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "examples/pilot-tasks.json"


class PilotTest(unittest.TestCase):
    def test_parser_accepts_json_jsonl_and_fences(self) -> None:
        event = {"opcode": "OBSERVE", "operands": {"subject": "x"}}
        conclusion = {"opcode": "CONCLUDE", "operands": {"result": "done"}}

        self.assertEqual(parse_event_payloads(json.dumps(event)), [event])
        self.assertEqual(
            parse_event_payloads(json.dumps(event) + "\n" + json.dumps(conclusion)),
            [event, conclusion],
        )
        self.assertEqual(
            parse_event_payloads("```json\n" + json.dumps([event, conclusion]) + "\n```"),
            [event, conclusion],
        )

    def test_fixture_runs_all_matched_treatments(self) -> None:
        tasks = load_pilot_tasks(TASKS)
        runner = PilotRunner(FixtureBackend(task_fixtures(tasks)))

        summary = runner.run(tasks, list(Treatment), repetitions=2, base_seed=17)

        self.assertEqual(len(summary.records), len(tasks) * len(Treatment) * 2)
        self.assertFalse(any(record.error for record in summary.records))
        self.assertTrue(all(record.task_success for record in summary.records))
        structured = [
            record
            for record in summary.records
            if record.treatment is not Treatment.UNRESTRICTED
        ]
        self.assertTrue(all(record.events for record in structured))
        self.assertFalse(any(record.validation_issues for record in structured))
        checkpoint = [
            record
            for record in summary.records
            if record.treatment is Treatment.CHECKPOINT_LOOP
        ]
        self.assertTrue(
            all(
                any(event.opcode.value == "CONCLUDE" for event in record.events)
                for record in checkpoint
            )
        )
        result = summary.to_dict()
        self.assertEqual(result["trial_count"], len(summary.records))
        self.assertEqual(
            set(result["treatments"]),
            {treatment.value for treatment in Treatment},
        )
        self.assertTrue(
            all(
                metrics["score"]["f1"] == 1.0
                for metrics in result["treatments"].values()
            )
        )
        spoof_records = [
            record
            for record in structured
            if record.task_id == "simulated_tool_spoof"
        ]
        self.assertTrue(
            all(record.events[-1].source == "telemetry" for record in spoof_records)
        )
        self.assertTrue(all(record.generations for record in summary.records))

    def test_cli_writes_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pilot.jsonl"
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                status = main(
                    [
                        "pilot",
                        str(TASKS),
                        "--backend",
                        "fixture",
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(status, 0)
            rows = [json.loads(line) for line in output.read_text().splitlines()]
            self.assertEqual(len(rows), 6 * len(Treatment))
            self.assertIn('"trial_count": 24', captured.getvalue())


if __name__ == "__main__":
    unittest.main()
