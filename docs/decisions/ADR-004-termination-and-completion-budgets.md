# ADR-004: Retain termination reasons and separate call capacity from comparison cost

- **Status:** Accepted
- **Date:** 2026-09-03
- **Owners:** CogTrace contributors
- **Supersedes:** None
- **Superseded by:** None

## Context

`EXP-001` and `EXP-002` failed at the same `checkpoint_loop` step. The retained
`EXP-002` response had empty final content and exactly 2,048 completion tokens,
all represented in the reasoning field. This strongly suggested exhaustion of
the shared reasoning/final-output limit, but the harness did not retain the
provider's `finish_reason` and could not directly distinguish length termination
from other empty-output causes.

The treatments also have intentionally different call topologies: unrestricted
and prompted structured reasoning use one call, post-hoc translation uses two,
and the checkpoint loop uses one call per accepted event. A per-call generation
ceiling and a fair trajectory-level capability or cost comparison are therefore
different concerns.

## Decision

For every successfully returned generation:

- Normalize `choices[0].finish_reason` into `Generation.finish_reason` without
  inferring a missing value.
- Serialize the value as `calls[*].finish_reason`; use `null` when the provider
  does not supply it.
- Retain the generation before parsing or validating its required final output.
- If a checkpoint has `finish_reason="length"` and empty final content, record
  an explicit failed-trial error. Do not silently retry it. Other malformed,
  missing, or truncated outputs remain recorded under their observed failure.
- Aggregate finish-reason counts in the pilot summary so termination patterns
  are visible without opening private reasoning text.

For engineering compatibility experiments, predeclare one `max_tokens` ceiling
and apply it identically to every model call in every treatment and phase. A
change to that ceiling requires a new experiment record and a complete matched
run; selective reruns are not permitted.

Call-count differences remain part of each treatment. Aggregate and report
actual prompt tokens, completion tokens, and latency per trajectory rather than
describing the identical per-call ceiling as equal total compute. The M1
preregistration must separately freeze its capability-loss threshold and any
trajectory-level compute adjustment used for scientific comparison.

## Consequences

- Length exhaustion can be diagnosed from retained provider metadata without
  inspecting or quoting raw chain-of-thought.
- Historical `EXP-001` and `EXP-002` artifacts remain unchanged; their missing
  termination reasons cannot be reconstructed.
- The compatibility smoke can raise the per-call ceiling without favoring a
  treatment at the request-setting level.
- Multi-call treatments can still consume more total compute. Compatibility
  evidence therefore cannot establish matched capability or cost.
- A provider that omits `finish_reason` remains usable, but the value is
  explicitly recorded as unavailable rather than guessed.

## Alternatives considered

- Infer length termination whenever usage equals the requested ceiling. This is
  useful supporting evidence but is not equivalent to retaining the provider's
  stated termination reason.
- Retry empty or length-terminated generations automatically. This could hide a
  treatment-specific failure and bias retained results.
- Impose one hard token total across all treatments during the integration
  smoke. This would truncate the checkpoint treatment because producing its
  typed state intrinsically requires multiple calls, and it would turn a backend
  compatibility test into a different treatment intervention.
- Give checkpoint calls a larger ceiling than other calls. This would make the
  request policy treatment-specific and complicate interpretation.

## Revisit when

Revisit the per-call policy if the serving API exposes a separately enforceable
reasoning budget and final-output reserve. Revisit trajectory-level accounting
before M1 collection, when the capability-loss threshold and primary analysis
are preregistered.
