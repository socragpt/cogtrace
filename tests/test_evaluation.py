from __future__ import annotations

import unittest
from pathlib import Path

from cogtrace.evaluation import Scenario, run_experiment
from cogtrace.io import load_scenario_values


ROOT = Path(__file__).resolve().parents[1]


class ExperimentTest(unittest.TestCase):
    def test_synthetic_fixture_exercises_both_monitors(self) -> None:
        scenarios = [
            Scenario.from_dict(value)
            for value in load_scenario_values(ROOT / "examples/scenarios.json")
        ]

        report = run_experiment(scenarios)

        self.assertEqual(report.scenario_count, 11)
        self.assertEqual(report.invalid_scenarios, ())
        self.assertEqual(report.structured.f1, 1.0)
        self.assertLess(report.keyword.f1, report.structured.f1)
        self.assertGreater(report.keyword.true_positive, 0)
        self.assertGreater(report.keyword.false_positive, 0)
        self.assertGreater(report.keyword.false_negative, 0)


if __name__ == "__main__":
    unittest.main()
