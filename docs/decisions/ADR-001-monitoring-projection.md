# ADR-001: Structured traces are monitoring projections

- **Status:** Accepted
- **Date:** 2026-08-27
- **Owners:** CogTrace contributors
- **Supersedes:** None
- **Superseded by:** None

## Context

Autoregressive text is already a lossy projection of model computation. CogTrace
does not need a complete description of hidden-state computation to test whether
a smaller, typed projection is useful for predefined monitoring tasks. At the
same time, syntactic structure can be mistaken for faithful explanation or an
authorization signal.

## Decision

Treat a CogTrace event stream as a monitoring and investigation artifact. Do not
describe it as the model's full thought process, proof of causal faithfulness, or
an action-control plane. Evaluate validity, monitorability, faithfulness, and
task capability as separate properties.

No component in the research harness may authorize or block an agent action on
the basis of the trace unless a later, separately approved project explicitly
changes scope.

## Consequences

- The project can pursue a useful narrower claim without solving mechanistic
  interpretability.
- Results must be phrased in terms of risk-property detection and investigation,
  not general transparency or alignment.
- Faithfulness requires separate intervention evidence.
- Independent action telemetry remains evaluation evidence rather than an
  execution gate.

## Alternatives considered

- Require the trace to represent all internal computation. This is not currently
  operationally testable and is unnecessary for the monitoring hypothesis.
- Use structured traces as policy enforcement. This changes the research target
  and creates additional safety and governance requirements.

## Revisit when

Revisit only if the project deliberately expands from monitoring research into
action control or obtains a validated causal interface to model computation.
