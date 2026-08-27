"""Shared evaluation pipeline for structured and text monitors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .model import TraceEvent
from .monitoring import KeywordTextMonitor, RiskTag, StructuredTraceMonitor
from .validation import TraceValidator


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    labels: frozenset[RiskTag]
    events: tuple[TraceEvent, ...]
    free_text: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Scenario":
        try:
            scenario_id = value["id"]
            labels = frozenset(RiskTag(label) for label in value.get("labels", []))
            events = tuple(TraceEvent.from_dict(item) for item in value["events"])
            free_text = value.get("free_text", "")
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"invalid scenario: {value.get('id', '<unknown>')}: {error}") from error
        if not isinstance(scenario_id, str) or not scenario_id:
            raise ValueError("scenario id must be a non-empty string")
        if not isinstance(free_text, str):
            raise ValueError(f"scenario {scenario_id}: free_text must be a string")
        return cls(scenario_id, labels, events, free_text)


@dataclass(frozen=True)
class Score:
    true_positive: int
    false_positive: int
    false_negative: int

    @property
    def precision(self) -> float:
        denominator = self.true_positive + self.false_positive
        return self.true_positive / denominator if denominator else 0.0

    @property
    def recall(self) -> float:
        denominator = self.true_positive + self.false_negative
        return self.true_positive / denominator if denominator else 0.0

    @property
    def f1(self) -> float:
        denominator = self.precision + self.recall
        return 2 * self.precision * self.recall / denominator if denominator else 0.0

    def to_dict(self) -> dict[str, float | int]:
        return {
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "false_negative": self.false_negative,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


@dataclass(frozen=True)
class ExperimentReport:
    structured: Score
    keyword: Score
    scenario_count: int
    invalid_scenarios: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_count": self.scenario_count,
            "invalid_scenarios": list(self.invalid_scenarios),
            "structured": self.structured.to_dict(),
            "keyword": self.keyword.to_dict(),
            "warning": "Synthetic smoke-test metrics are not scientific evidence.",
        }


def _score(
    labels_and_predictions: Iterable[tuple[set[RiskTag], set[RiskTag]]],
) -> Score:
    true_positive = 0
    false_positive = 0
    false_negative = 0
    for labels, predictions in labels_and_predictions:
        true_positive += len(labels & predictions)
        false_positive += len(predictions - labels)
        false_negative += len(labels - predictions)
    return Score(true_positive, false_positive, false_negative)


def run_experiment(scenarios: Iterable[Scenario]) -> ExperimentReport:
    scenario_list = list(scenarios)
    validator = TraceValidator()
    structured_monitor = StructuredTraceMonitor()
    keyword_monitor = KeywordTextMonitor()
    invalid: list[str] = []
    structured_pairs: list[tuple[set[RiskTag], set[RiskTag]]] = []
    keyword_pairs: list[tuple[set[RiskTag], set[RiskTag]]] = []

    for scenario in scenario_list:
        labels = set(scenario.labels)
        issues = validator.validate(scenario.events)
        if issues:
            invalid.append(scenario.scenario_id)
            structured_predictions: set[RiskTag] = set()
        else:
            structured_predictions = {
                finding.tag for finding in structured_monitor.analyze(scenario.events)
            }
        keyword_predictions = {
            finding.tag for finding in keyword_monitor.analyze(scenario.free_text)
        }
        structured_pairs.append((labels, structured_predictions))
        keyword_pairs.append((labels, keyword_predictions))

    return ExperimentReport(
        structured=_score(structured_pairs),
        keyword=_score(keyword_pairs),
        scenario_count=len(scenario_list),
        invalid_scenarios=tuple(invalid),
    )
