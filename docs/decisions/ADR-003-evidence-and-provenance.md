# ADR-003: Evidence levels and provenance remain separate

- **Status:** Accepted
- **Date:** 2026-08-27
- **Owners:** CogTrace contributors
- **Supersedes:** None
- **Superseded by:** None

## Context

Authored fixtures are useful for pipeline validation but can trivially match the
rules they were designed to exercise. Model-authored fields can also claim that
they are trusted telemetry unless provenance is assigned outside the model.

## Decision

Use three evidence levels:

1. **Fixture evidence:** validates software behavior only.
2. **Live engineering smoke:** validates model/backend integration only.
3. **Frozen collection evidence:** can support preregistered research analysis
   after independent annotation and capability measurement.

The harness assigns trace IDs, event IDs, monotonic timestamps, and trusted
telemetry sources. Model output may supply opcode operands but cannot grant
itself trusted provenance. Preserve all failures and deviations at every level.

## Consequences

- Perfect fixture scores cannot be reported as monitor performance evidence.
- A successful 24-trial live smoke does not answer the research question.
- Tool-spoof detection can compare model intent with independently sourced
  telemetry without trusting a model-authored `source` field.
- Data and result records must state their evidence level.

## Alternatives considered

- Treat any valid structured output as evidence of monitorability. This confuses
  conformance with detection quality.
- Permit model-authored timestamps and provenance. This defeats their evidentiary
  role in incident reconstruction.

## Revisit when

Revisit if a cryptographically authenticated model-side telemetry channel or a
new evidence hierarchy is introduced.
