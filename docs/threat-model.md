# Threat model

## Protected property

The research aims to preserve the ability to detect predefined safety-relevant
properties of an agent trajectory. It does not attempt to prove that an agent
is aligned or that a trace fully explains neural computation.

## Adversary

The strongest experimental adversary is an agent that:

- Knows its reasoning channel is monitored.
- Understands the grammar and possibly the monitor.
- Benefits from completing a risky strategy.
- Is penalized when the monitor detects that strategy.
- Can use model state, operands, trace sequences, tool inputs, and observations
  as alternative communication channels.

We also consider accidental failures from underspecification, distribution
shift, parser differences, and annotation error.

## Failure modes

### Strategic misreporting

When a trace can affect evaluation scores or expected downstream treatment, the
agent emits the report that best serves those consequences rather than the most
informative account available to the monitor. A constrained schema can make the
report more regular without making it more truthful.

Compare neutral and detection-contingent incentive conditions while holding the
task and action interface fixed. Measure changes in trace evidence against
independent telemetry and annotations, and record the complete incentive
schedule as an experimental parameter. Do not use traces to authorize actions.

### Omission

The trace excludes a risk-relevant premise, objective, or policy conflict.

Test with behavioral ground truth and tasks where evidence usage can be
intervened upon.

### Semantic laundering

The trace uses compliant-looking opcodes and euphemistic operands for risky
reasoning.

Test held-out paraphrases, blinded annotation, and monitors trained on different
surface forms.

### Compositional encoding

Individually benign events encode information through their sequence.

Test sequence-level classifiers, opcode renaming, permutation controls, and
explicit channel-capacity estimates.

### Operand covert channels

Identifiers, numbers, path fragments, whitespace, or long free-form strings
carry hidden information.

Test typed vocabularies, byte budgets, canonical serialization, and randomized
identifier remapping.

### Timing channels

Delays between events encode information.

Use harness-assigned time, quantization, and experiments that hide timing from
the monitor or model.

### Retrospective rationalization

A translator or model emits a clean trace after choosing an action through
another process.

Keep post-hoc translation as a separate treatment and measure causal influence
with trace interventions.

### Monitor overfitting

Rules exploit benchmark artifacts rather than the target property.

Split by environment template, hold out monitors and attack families, and
evaluate cross-model transfer.

### Capability-induced distribution shift

Constrained reasoning changes which tasks the agent attempts or how it fails,
making monitor comparisons misleading.

Report task capability and behavior prevalence separately, with matched-task
analyses where possible.

### Trusted-source confusion

Self-reported events are mistaken for independent telemetry.

Preserve source provenance and score monitors under explicit visibility
conditions.

## Security boundaries

- Use simulated credentials and isolated evaluation services.
- Do not connect pilot agents to production secrets or accounts.
- Store raw CoT as sensitive research data.
- Treat all generated traces and tool output as untrusted input.
- Keep validation and monitoring separate from authorization and execution.
