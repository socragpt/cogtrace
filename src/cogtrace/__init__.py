"""CogTrace: research infrastructure for structured reasoning traces."""

from .model import Opcode, TraceEvent
from .monitoring import Finding, RiskTag, StructuredTraceMonitor
from .validation import TraceValidator, ValidationIssue

__all__ = [
    "Finding",
    "Opcode",
    "RiskTag",
    "StructuredTraceMonitor",
    "TraceEvent",
    "TraceValidator",
    "ValidationIssue",
]

__version__ = "0.1.0"
