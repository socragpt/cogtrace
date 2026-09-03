from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from cogtrace.backends import ChatRequest, FixtureBackend, Generation
from cogtrace.cli import main
from cogtrace.pilot import (
    ENGINEERING_SMOKE_TREATMENTS,
    PilotRunner,
    Treatment,
    load_pilot_tasks,
    parse_event_payloads,
    task_fixtures,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "examples/pilot-tasks.json"


class MalformedCheckpointBackend:
    name = "malformed-checkpoint"
    supports_structured_outputs = True

    def generate(self, request: ChatRequest) -> Generation:
        step = int(request.metadata.get("step") or 0)
        contents = (
            '{"opcode":"OBSERVE","operands":{"subject":"simulation"}}',
            '{"opcode":"PLAN","operands":{"goal":"finish"}}',
            "not a JSON event",
        )
        return Generation(
            content=contents[step],
            reasoning=f"checkpoint reasoning {step}",
            prompt_tokens=10 + step,
            completion_tokens=20 + step,
            latency_ms=1.5 + step,
            model="malformed-model",
        )


class LengthTerminatedCheckpointBackend:
    name = "length-terminated-checkpoint"
    supports_structured_outputs = True

    def generate(self, request: ChatRequest) -> Generation:
        return Generation(
            content="",
            reasoning="unfinished checkpoint reasoning",
            prompt_tokens=10,
            completion_tokens=request.max_tokens,
            latency_ms=2.5,
            model="length-model",
            finish_reason="length",
        )


class RecordingFixtureBackend(FixtureBackend):
    def __init__(self, fixtures: dict[str, object]) -> None:
        super().__init__(fixtures)
        self.requests: list[ChatRequest] = []

    def generate(self, request: ChatRequest) -> Generation:
        self.requests.append(request)
        return super().generate(request)


class FailingBaseBackend:
    name = "failing-base"
    supports_structured_outputs = True

    def __init__(self) -> None:
        self.requests: list[ChatRequest] = []

    def generate(self, request: ChatRequest) -> Generation:
        self.requests.append(request)
        raise RuntimeError("base generation failed")


class RecordingTextMonitor:
    def __init__(self) -> None:
        self.inputs: list[str] = []

    def analyze(self, text: str) -> list[object]:
        self.inputs.append(text)
        return []


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
            if record.treatment
            in {
                Treatment.POSTHOC,
                Treatment.PROMPT_STRUCTURED,
                Treatment.CHECKPOINT_LOOP,
            }
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
                result["treatments"][treatment.value]["score"]["f1"] == 1.0
                for treatment in ENGINEERING_SMOKE_TREATMENTS
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
        self.assertEqual(
            result["treatments"][Treatment.ACTION_ONLY.value]["finish_reasons"],
            {"stop": len(tasks) * 2},
        )
        self.assertIsNone(
            result["treatments"][Treatment.ACTION_ONLY.value]["valid_trace_rate"]
        )
        self.assertEqual(
            result["treatments"][Treatment.UNRESTRICTED.value]["finish_reasons"],
            {"stop": len(tasks) * 2},
        )
        self.assertEqual(
            result["treatments"][Treatment.POSTHOC.value]["finish_reasons"],
            {"stop": len(tasks) * 4},
        )
        self.assertEqual(
            result["treatments"][Treatment.PROMPT_STRUCTURED.value][
                "finish_reasons"
            ],
            {"stop": len(tasks) * 2},
        )
        self.assertGreaterEqual(
            result["treatments"][Treatment.CHECKPOINT_LOOP.value][
                "finish_reasons"
            ]["stop"],
            len(tasks) * 2,
        )

    def test_m1_views_share_one_base_generation_and_hide_reasoning_from_a(self) -> None:
        task = next(
            task
            for task in load_pilot_tasks(TASKS)
            if task.task_id == "simulated_tool_spoof"
        )
        backend = RecordingFixtureBackend(task_fixtures([task]))
        text_monitor = RecordingTextMonitor()
        runner = PilotRunner(backend)
        runner.keyword_monitor = text_monitor

        summary = runner.run(
            [task],
            [
                Treatment.ACTION_ONLY,
                Treatment.UNRESTRICTED,
                Treatment.POSTHOC,
            ],
            base_seed=29,
        )

        self.assertEqual(
            [request.metadata["phase"] for request in backend.requests],
            ["unrestricted", "translate"],
        )
        records = {record.treatment: record for record in summary.records}
        action = records[Treatment.ACTION_ONLY]
        unrestricted = records[Treatment.UNRESTRICTED]
        posthoc = records[Treatment.POSTHOC]
        self.assertEqual(
            {record.base_trajectory_id for record in summary.records},
            {action.base_trajectory_id},
        )
        self.assertEqual(len({record.record_id for record in summary.records}), 3)
        self.assertEqual(action.call_ids, unrestricted.call_ids)
        self.assertEqual(posthoc.call_ids[0], action.call_ids[0])
        self.assertEqual(len(posthoc.call_ids), 2)
        self.assertEqual(
            {record.final_output for record in summary.records},
            {action.final_output},
        )
        self.assertEqual(
            {record.raw_reasoning for record in summary.records},
            {action.raw_reasoning},
        )
        self.assertNotIn(action.raw_reasoning, text_monitor.inputs[0])
        self.assertIn(action.raw_reasoning, text_monitor.inputs[1])
        self.assertIn(action.final_output, text_monitor.inputs[0])
        self.assertIn("TRUSTED_TELEMETRY", text_monitor.inputs[0])
        self.assertTrue(action.events)
        self.assertTrue(all(event.source == "telemetry" for event in action.events))
        self.assertEqual(action.events, unrestricted.events)
        self.assertEqual(summary.to_dict()["base_trajectory_count"], 1)
        self.assertEqual(summary.to_dict()["unique_call_count"], 2)

    def test_failed_shared_base_is_recorded_once_for_every_requested_view(self) -> None:
        task = load_pilot_tasks(TASKS)[0]
        backend = FailingBaseBackend()
        runner = PilotRunner(backend)

        summary = runner.run(
            [task],
            [
                Treatment.ACTION_ONLY,
                Treatment.UNRESTRICTED,
                Treatment.POSTHOC,
            ],
            base_seed=43,
        )

        self.assertEqual(len(backend.requests), 1)
        self.assertEqual(len(summary.records), 3)
        self.assertTrue(all(record.error for record in summary.records))
        self.assertTrue(all(not record.generations for record in summary.records))
        self.assertEqual(
            len({record.base_trajectory_id for record in summary.records}), 1
        )
        self.assertEqual(summary.to_dict()["unique_call_count"], 0)

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
            self.assertEqual(len(rows), 6 * len(ENGINEERING_SMOKE_TREATMENTS))
            self.assertNotIn(
                Treatment.ACTION_ONLY.value,
                {row["treatment"] for row in rows},
            )
            self.assertIn('"trial_count": 24', captured.getvalue())

    def test_failed_checkpoint_retains_successful_generations(self) -> None:
        task = load_pilot_tasks(TASKS)[0]
        runner = PilotRunner(MalformedCheckpointBackend())

        record = runner.run_trial(
            task,
            Treatment.CHECKPOINT_LOOP,
            repetition=0,
            seed=17,
        )

        self.assertEqual(
            record.error,
            "ValueError: checkpoint 2 returned 0 valid events; expected one",
        )
        self.assertEqual(len(record.generations), 3)
        self.assertEqual(record.generations[-1].content, "not a JSON event")
        self.assertEqual(record.model, "malformed-model")
        self.assertEqual(record.prompt_tokens, 33)
        self.assertEqual(record.completion_tokens, 63)
        self.assertEqual(record.latency_ms, 7.5)
        self.assertIn("checkpoint reasoning 2", record.raw_reasoning)
        self.assertEqual(len(record.to_dict()["calls"]), 3)

    def test_length_terminated_checkpoint_is_retained_and_classified(self) -> None:
        task = load_pilot_tasks(TASKS)[0]
        runner = PilotRunner(LengthTerminatedCheckpointBackend(), max_tokens=2048)

        record = runner.run_trial(
            task,
            Treatment.CHECKPOINT_LOOP,
            repetition=0,
            seed=17,
        )

        self.assertEqual(
            record.error,
            "ValueError: checkpoint 0 length-terminated before final content; "
            "expected one event",
        )
        self.assertEqual(len(record.generations), 1)
        self.assertEqual(record.generations[0].finish_reason, "length")
        self.assertEqual(record.completion_tokens, 2048)
        self.assertEqual(record.final_output, "")
        self.assertEqual(record.to_dict()["calls"][0]["finish_reason"], "length")


if __name__ == "__main__":
    unittest.main()
