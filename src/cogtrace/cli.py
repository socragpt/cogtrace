"""Command-line interface for validation, monitoring, and smoke experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .evaluation import Scenario, run_experiment
from .io import load_scenario_values, load_trace_jsonl
from .monitoring import StructuredTraceMonitor
from .validation import TraceValidator


def _validate(path: Path) -> int:
    events = load_trace_jsonl(path)
    issues = TraceValidator().validate(events)
    if issues:
        print(json.dumps([issue.to_dict() for issue in issues], indent=2))
        return 1
    print(f"valid trace: {len(events)} events")
    return 0


def _monitor(path: Path) -> int:
    events = load_trace_jsonl(path)
    issues = TraceValidator().validate(events)
    if issues:
        print(json.dumps({"validation_issues": [issue.to_dict() for issue in issues]}, indent=2))
        return 1
    findings = StructuredTraceMonitor().analyze(events)
    print(json.dumps([finding.to_dict() for finding in findings], indent=2))
    return 0


def _experiment(path: Path, as_json: bool) -> int:
    scenarios = [Scenario.from_dict(value) for value in load_scenario_values(path)]
    report = run_experiment(scenarios)
    if as_json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0

    print("Synthetic pipeline smoke test — not a scientific result")
    print(f"Scenarios: {report.scenario_count}")
    print()
    print(f"{'Monitor':<18} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print(f"{'Structured':<18} {report.structured.precision:>10.3f} {report.structured.recall:>10.3f} {report.structured.f1:>10.3f}")
    print(f"{'Keyword':<18} {report.keyword.precision:>10.3f} {report.keyword.recall:>10.3f} {report.keyword.f1:>10.3f}")
    if report.invalid_scenarios:
        print()
        print("Invalid scenarios: " + ", ".join(report.invalid_scenarios))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cogtrace",
        description="Structured reasoning trace research tools",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a JSONL trace")
    validate.add_argument("trace", type=Path)

    monitor = subparsers.add_parser("monitor", help="run reference rules on a JSONL trace")
    monitor.add_argument("trace", type=Path)

    experiment = subparsers.add_parser("experiment", help="run a synthetic comparison fixture")
    experiment.add_argument("scenarios", type=Path)
    experiment.add_argument("--json", action="store_true", help="emit machine-readable output")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate(args.trace)
    if args.command == "monitor":
        return _monitor(args.trace)
    if args.command == "experiment":
        return _experiment(args.scenarios, args.json)
    parser.error(f"unknown command {args.command!r}")
    return 2
