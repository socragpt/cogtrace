# CogTrace target operating model

## Status and purpose

This document describes what CogTrace could become if the research program
produces positive, replicated results. It is a conditional target architecture,
not a statement of current capability, a second project roadmap, or evidence
that structured traces improve safety.

Current status, gates, and ordered work remain in
[`PROJECT_STATE.md`](../PROJECT_STATE.md). Research hypotheses and milestones
remain in [`RESEARCH_PLAN.md`](../RESEARCH_PLAN.md). This document explains how
the pieces would work together in practice after the relevant evidence gates are
passed.

The governing principle is:

> CogTrace treats structured reasoning as an untrusted, lossy monitoring signal
> that becomes useful when joined with trusted behavioral telemetry;
> enforcement remains a separate deployment-policy decision.

This operating model applies the boundaries accepted in
[`ADR-001`](decisions/ADR-001-monitoring-projection.md),
[`ADR-002`](decisions/ADR-002-treatment-claim-boundaries.md),
[`ADR-003`](decisions/ADR-003-evidence-and-provenance.md), and
[`ADR-005`](decisions/ADR-005-m1-design-and-data-policy.md).

## Intended outcome

If the experiments succeed, CogTrace becomes an observability and investigation
layer for AI agents. The agent keeps its ordinary task, tool, and action space.
Alongside its actions, it emits a small typed projection of reasoning that is
easier to validate, monitor, compare, and reconstruct than unrestricted prose.

CogTrace correlates that model-authored trace with independently collected
runtime telemetry. It produces versioned findings and evidence bundles for
monitors and investigators. CogTrace itself does not authorize or block an
agent action. A deployment may consume its findings in a separate policy system
only after an additional governance and validation decision.

## End-to-end lifecycle

```text
user task
   |
   v
agent runtime ---------------------> actions, tools, final output
   |                                           |
   | model-authored typed trace                | harness-observed activity
   v                                           v
trace collector                         telemetry collectors
   |                                           |
   +---------------> correlation layer <-------+
                              |
                              v
                 validation and provenance
                              |
                              v
                    versioned monitor scores
                              |
                              v
                 finding and evidence bundle
                         /              \
                        v                v
              investigator view   external policy consumer
                                  (outside CogTrace scope)
```

### 1. Task execution

The user gives an agent a task. The agent uses its normal language, tools, and
action interface. CogTrace does not reduce the vocabulary or permissions of the
action channel.

### 2. Trace emission

The agent emits typed events through the versioned CogTrace schema. The selected
production treatment must be justified by experiment rather than assumed in
advance. It could be an interleaved checkpoint stream, a prompted structured
stream, or a post-hoc translation. Post-hoc output must always remain labeled as
a translation rather than direct reasoning evidence.

Trace emission is deliberately lossy. Its goal is to retain information useful
for predeclared monitoring and investigation tasks, not to encode every hidden
activation or prove what the model truly thought.

### 3. Trusted collection and correlation

The harness assigns trace IDs, event IDs, sequence numbers, monotonic
timestamps, runtime identity, and telemetry provenance. Model output cannot
grant itself trusted provenance.

Collectors observe relevant external behavior, such as tool calls, process
execution, file access, network activity, and final outputs. The correlation
layer joins those observations to the trace without rewriting either source.
Missing, malformed, conflicting, and late evidence remains visible.

### 4. Validation and monitoring

The validator checks schema and semantic invariants. Validation is not an
alignment verdict. A valid trace can be uninformative or deceptive, and an
invalid trace can still accompany important external evidence.

Versioned monitors consume one or more of:

- the model-authored trace;
- trusted action and tool telemetry;
- the final output;
- validation results; and
- trace-to-action discrepancies.

Each probabilistic monitor returns a risk score, monitor version, input
availability, and evidence references. Thresholds are calibrated and frozen for
the applicable deployment population. Missing input is recorded rather than
silently regenerated.

### 5. Findings and evidence bundles

A finding is a reviewable monitoring result, not a statement about model
psychology. It includes:

- the risk tag and calibrated score;
- the monitor and schema versions;
- the trace and telemetry evidence references;
- any missingness or validation condition;
- the relevant time interval; and
- the action taken by the downstream consumer, if any.

Evidence bundles preserve enough versioned material to reproduce the finding
and reconstruct the incident while respecting the applicable retention policy.

### 6. Investigation

An investigator receives a synchronized timeline of model-authored events,
trusted runtime observations, findings, and system responses. The interface
should support filtering by risk tag, following causal or temporal links,
locating the first relevant evidence, and comparing declared intent with
observed behavior.

The intended benefit is operational: reduce the amount of prose a reviewer must
read, shorten timeline reconstruction, make evidence categories consistent, and
surface disagreements between trace and action telemetry.

### 7. Optional policy consumption

A separate deployment-policy system may consume CogTrace findings to log,
escalate, warn, quarantine, or intervene. That system owns its thresholds,
fallbacks, authority, audit, and appeal rules.

No current CogTrace component is an action-control plane. Moving from monitoring
to automated enforcement requires a separately approved scope, evidence base,
threat model, and governance decision. A trace alone must never become an
authorization token.

## Target components

The successful system would likely contain:

1. **Agent integration:** emits versioned typed events without changing the
   agent's external action interface.
2. **Schema registry and validator:** resolves schema versions and preserves all
   validation outcomes.
3. **Telemetry adapters:** collect independently sourced action, tool, process,
   file, network, and output evidence.
4. **Correlation service:** joins traces and telemetry using harness-trusted
   identifiers and monotonic time.
5. **Monitor service:** runs versioned deterministic or probabilistic monitors
   and records calibration and missingness.
6. **Evidence store:** retains private, reviewable incident bundles under an
   explicit access and deletion policy.
7. **Investigator viewer:** presents synchronized timelines, risk findings, and
   supporting evidence.
8. **Policy adapter:** exports findings to an external policy system without
   giving CogTrace authority over the action channel.
9. **Evaluation and drift suite:** continuously measures capability,
   monitorability, calibration, missingness, adversarial robustness, reviewer
   time, and distribution shift.

## Trust model

CogTrace distinguishes four evidence classes:

| Evidence | Trust and interpretation |
| --- | --- |
| Model-authored trace | Untrusted claim and monitoring signal; never self-authenticating |
| Harness telemetry | Trusted provenance assignment for an observed sensor event; sensors can still be incomplete or wrong |
| Monitor finding | Versioned inference with uncertainty and evidence references; not ground truth |
| Human annotation or adjudication | Research label created under a recorded procedure; not proof of hidden intent |

Trace validity, monitorability, faithfulness, and task capability remain
separate properties throughout the system. No conversion from one property to
another is implied.

## Failure handling

The operating model assumes that traces and monitors will fail. The system must
retain and surface at least these conditions:

- missing or malformed traces;
- event-budget or generation-limit exhaustion;
- trace-to-action disagreement;
- unsupported or ambiguous operands;
- post-hoc translation errors;
- telemetry gaps or collector failure;
- monitor calibration drift;
- semantic laundering or covert coding;
- distribution shift; and
- correlated model, translator, and monitor errors.

Failures are observations, not records to delete or automatically rerun. A
fallback may rely on action telemetry alone, but the fallback and its reduced
evidence must be explicit.

## Evidence required before use

The target architecture is justified in stages. A later stage does not inherit
evidence that was collected only for an earlier claim.

| Stage | Required evidence | Permitted use |
| --- | --- | --- |
| Engineering validation | End-to-end retention, provenance, failure, and reproducibility gates pass | Offline development only |
| M1 monitorability | Frozen, independently annotated collection shows useful monitoring at an acceptable capability cost | Research conclusions and shadow evaluation |
| M2 causal testing | Trace interventions and stronger constraints characterize causal participation and failure modes | Narrow causal claims supported by those interventions |
| M3 adversarial evaluation | Benefits persist against held-out monitor-aware pressure and covert-channel tests | Adversarially informed shadow deployment |
| M4 investigator study | Blinded reviewers reconstruct incidents faster or more accurately | Investigator-assistance pilot |
| Operational validation | Population-specific calibration, privacy, security, reliability, and drift controls pass | Limited production monitoring |
| Enforcement decision | Separate safety case, governance approval, rollback, and audit controls exist | External policy integration only |

Positive M1 results alone would not authorize automated intervention. They would
justify further research and, at most, a carefully scoped shadow-monitoring
deployment.

## Deployment sequence

If the evidence gates pass, deployment should proceed in this order:

1. **Offline replay:** run CogTrace against retained or synthetic trajectories
   without affecting agents or users.
2. **Shadow monitoring:** collect findings while existing operations remain
   unchanged; measure calibration, missingness, latency, and drift.
3. **Investigator assistance:** show findings and timelines to trained reviewers,
   but keep decisions human-owned and record disagreement and override rates.
4. **Limited policy integration:** only under a separate approved project, allow
   narrowly scoped external policy responses with rollback and audit.
5. **Broader operation:** expand only after replicated performance and ongoing
   monitoring show that benefits survive the deployment distribution.

Every stage needs a rollback condition. A lower trace-validity rate, higher
capability loss, calibration drift, excessive reviewer burden, privacy failure,
or successful evasion can stop progression even if earlier experiments passed.

## Data handling

Raw reasoning, prompts, tool output, telemetry, and incident bundles can contain
sensitive or proprietary information. Research collections follow the private
storage, access, and deletion rules frozen in their experiment and decision
records. For M1, [`ADR-005`](decisions/ADR-005-m1-design-and-data-policy.md) sets
a 30-day maximum for unredacted trajectory bundles.

A production deployment requires its own privacy review and retention schedule.
Longer retention of compact structured traces is not automatically safe merely
because they are smaller than raw CoT. Public artifacts remain synthetic,
consented, or reviewed and redacted.

## Success criteria for the project direction

The practical direction remains viable only if replicated evidence shows that a
typed trace, when joined with independent telemetry:

- improves a preregistered monitoring or investigation outcome;
- stays within a declared capability and reliability budget;
- remains useful under meaningful adversarial pressure;
- provides value beyond action-only telemetry;
- does not depend on treating syntax as faithfulness; and
- can be operated with acceptable privacy, cost, calibration, and reviewer
  burden.

If those conditions do not hold, the correct outcome is to narrow or stop the
deployment claim while retaining the negative result. The architecture is a
hypothesis made concrete, not a predetermined product conclusion.

## Non-claims and out of scope

Even if all planned experiments succeed, CogTrace does not by itself establish:

- complete access to hidden model computation;
- proof that an emitted trace caused the behavior;
- general alignment or safety;
- immunity to deception or covert channels;
- correctness of external telemetry;
- equal compute across treatments with different call topologies; or
- authority to permit or deny agent actions.

These limits are part of the target operating model, not temporary disclaimers.
