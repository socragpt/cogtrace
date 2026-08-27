# ADR-002: Treatment claim boundaries are explicit

- **Status:** Accepted
- **Date:** 2026-08-27
- **Owners:** CogTrace contributors
- **Supersedes:** None
- **Superseded by:** None

## Context

Post-hoc translation, prompted JSON reasoning, interleaved checkpoints, and
token-level constrained decoding impose materially different bottlenecks. Using
the same label for them would make results difficult to interpret and easy to
overclaim.

## Decision

Use the executable treatment names and boundaries below:

- `unrestricted`: natural-language reasoning without structural constraint.
- `posthoc`: unrestricted reasoning translated after generation; this is a
  summary and is not causal evidence.
- `prompt_structured`: a single generation prompted, but not guaranteed by
  decoding, to emit typed JSONL reasoning.
- `checkpoint_loop`: each call returns one JSON-schema-constrained event and only
  prior typed events persist into the next call. Hidden and transient within-call
  computation remain unconstrained.

Reserve “fully constrained reasoning” for a future tokenizer-aware grammar or
logits constraint that applies throughout the emitted reasoning stream. That
treatment is not implemented yet.

## Consequences

- Each result can be tied to the actual information bottleneck imposed.
- The checkpoint loop can test a persistent-state bottleneck without being
  misrepresented as full cognitive bytecode.
- A fifth, continuously constrained treatment remains required for M2.
- Prompt and parser versions are experimental parameters and must be frozen.

## Alternatives considered

- Group every JSON-producing condition as structured CoT. This hides important
  causal differences.
- Treat final-output JSON constraints as constraints on parsed reasoning. Current
  serving semantics do not support that claim.

## Revisit when

Revisit when a backend can constrain the entire emitted reasoning stream or when
trace interventions show that a treatment has a different causal role.
