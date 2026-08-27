"""File readers for trace and scenario artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import TraceEvent


def load_trace_jsonl(path: str | Path) -> list[TraceEvent]:
    """Load one trace from newline-delimited JSON."""

    events: list[TraceEvent] = []
    trace_path = Path(path)
    for line_number, raw_line in enumerate(
        trace_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{trace_path}:{line_number}: invalid JSON: {error.msg}"
            ) from error
        if not isinstance(value, dict):
            raise ValueError(f"{trace_path}:{line_number}: event must be an object")
        try:
            events.append(TraceEvent.from_dict(value))
        except ValueError as error:
            raise ValueError(f"{trace_path}:{line_number}: {error}") from error
    return events


def load_scenario_values(path: str | Path) -> list[dict[str, Any]]:
    """Load the versioned synthetic experiment fixture."""

    scenario_path = Path(path)
    value = json.loads(scenario_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("scenario file must be a schema_version 1 object")
    scenarios = value.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError("scenario file must contain a scenarios array")
    if not all(isinstance(item, dict) for item in scenarios):
        raise ValueError("every scenario must be an object")
    return scenarios
