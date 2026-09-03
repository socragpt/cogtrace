# CogTrace

CogTrace is a research scaffold for testing whether a small, typed reasoning
language can make chain-of-thought (CoT) monitoring cheaper, faster, and more
reliable without requiring a complete account of a model's internal
computation.

The project treats a structured trace as a **monitoring channel**, not as proof
of what a model truly thought and not as an action-control mechanism.

> Status: pre-alpha research infrastructure. The bundled scenarios are
> synthetic smoke tests. Their results are not evidence that structured CoT is
> safer or more faithful.

## Core research question

Can a constrained reasoning representation preserve enough safety-relevant
information to improve risk detection under adversarial pressure, while keeping
task-performance losses within an acceptable budget?

The initial comparison has five treatments:

1. Action and output monitoring only.
2. Unrestricted natural-language CoT.
3. A post-hoc structured summary of unrestricted CoT.
4. Interleaved typed reasoning checkpoints.
5. A fully constrained reasoning DSL.

The main outcome is not general interpretability. It is monitor performance on
predeclared risk properties: recall at a fixed false-positive rate, detection
latency, reviewer time, and robustness to deliberate obfuscation.

## What exists now

- A versioned JSON trace format and typed opcode vocabulary.
- Structural and semantic validation.
- Reference monitors for the five initial risk tags.
- A keyword monitor as a deliberately simple natural-language baseline.
- A provider-neutral live-model adapter and five executable pilot treatments.
- Safe deterministic pilot fixtures, trajectory logs, and unit tests.
- A staged research and adversarial-evaluation plan.

## Quick start

The scaffold uses only Python's standard library and requires Python 3.9 or
newer.

```bash
make check
PYTHONPATH=src python3 -m cogtrace validate examples/traces/policy-bypass.jsonl
PYTHONPATH=src python3 -m cogtrace monitor examples/traces/policy-bypass.jsonl
PYTHONPATH=src python3 -m cogtrace experiment examples/scenarios.json
PYTHONPATH=src python3 -m cogtrace pilot examples/pilot-tasks.json \
  --backend fixture --output runs/fixture-pilot.jsonl
```

The experiment command prints structured-trace and keyword-baseline metrics.
Because the included dataset is hand-authored to exercise the pipeline, those
numbers are engineering checks only.

By default, the pilot command preserves the four-condition engineering smoke
used by `EXP-000` through `EXP-003`:

1. `unrestricted` — natural-language reasoning monitored by a keyword baseline.
2. `posthoc` — unrestricted reasoning translated into typed events afterward.
3. `prompt_structured` — a single generation prompted to emit JSONL reasoning.
4. `checkpoint_loop` — one JSON-schema-constrained event per model call, with
   only prior typed events persisted between calls.

The checkpoint loop is the first causal-bottleneck prototype, but it is not a
fully constrained reasoning channel. The model can still perform transient
unstructured computation inside each call. See
[`docs/pilot-protocol.md`](docs/pilot-protocol.md) for the exact interpretation.

The M1 A/B/C interface is also executable:

```bash
PYTHONPATH=src python3 -m cogtrace pilot examples/pilot-tasks.json \
  --backend fixture \
  --treatments action_only unrestricted posthoc checkpoint_loop \
  --output runs/fixture-m1-views.jsonl
```

Here `action_only`, `unrestricted`, and `posthoc` share one unrestricted base
generation. Their records have a common harness-assigned `base_trajectory_id`;
the post-hoc record adds one translator call. The action-only monitor receives
only trusted telemetry and the final output. Raw reasoning remains in the
private trajectory record for annotation and audit, not in that monitor input.

## Architecture

```text
agent reasoning channel
        │
        ▼
versioned typed trace ──► validator ──► structured monitor ──► findings
        │                                      ▲
        └──────── event IDs and time ──────────┘

natural-language trace ───────────────► keyword baseline ───► findings
```

No component in this repository blocks or authorizes an agent action. Later
experiments may correlate traces with independent action telemetry, but that
telemetry is evidence for evaluation rather than an execution gate.

### Conditional target operating model

If the research gates succeed, CogTrace could become an observability and
investigation layer that joins an untrusted, lossy structured trace with
harness-trusted behavioral telemetry. It would produce versioned findings and
incident timelines for monitors and reviewers while leaving enforcement to a
separate deployment-policy system. See
[`docs/target-operating-model.md`](docs/target-operating-model.md) for the
conditional architecture, trust boundaries, evidence gates, and staged path to
practical use.

## Repository map

- `AGENTS.md` — durable instructions for humans and agents continuing the work.
- `PROJECT_STATE.md` — the single living status, active gate, and next steps.
- `RESEARCH_PLAN.md` — hypotheses, treatments, metrics, and milestones.
- `docs/decisions/` — append-only records of durable project choices.
- `docs/experiments/` — planned configurations, deviations, and results.
- `docs/handoff-checklist.md` — end-of-context continuity checklist.
- `docs/trace-spec.md` — the current trace language and invariants.
- `docs/pilot-protocol.md` — implemented treatments, scoring, and live pilot gates.
- `docs/annotation-guide.md` — M1 risk-tag labels, rater workflow, and adjudication.
- `docs/target-operating-model.md` — conditional success-state architecture,
  trust boundaries, and deployment evidence gates.
- `docs/threat-model.md` — failures the research must actively test.
- `docs/related-work.md` — primary research motivating the project and its cautions.
- `deploy/digitalocean/` — an ephemeral, SSH-only GPU pilot runbook.
- `src/cogtrace/` — backends, pilot runner, validator, monitors, evaluator, and CLI.
- `examples/` — synthetic traces, safe pilot tasks, and smoke-test datasets.
- `tests/` — unit tests for the research infrastructure.

## Continuing the project

Start with [`AGENTS.md`](AGENTS.md), then read
[`PROJECT_STATE.md`](PROJECT_STATE.md) and its linked active experiment. The
repository—not conversation history—is the canonical project memory. Durable
choices go in decision records; changing status goes only in `PROJECT_STATE.md`;
experiment plans and results remain in the experiment registry.

## Research discipline

CogTrace deliberately separates three questions:

1. **Validity:** Does a trace satisfy the declared syntax and schema?
2. **Monitorability:** Does it expose the risk property to a monitor?
3. **Faithfulness:** Did the trace causally represent the computation that
   produced the behavior?

A trace may be valid but unmonitorable, or monitorable but unfaithful. The
research plan measures these separately and avoids treating syntactic
conformance as evidence of alignment.

## Data handling

Raw CoT can contain sensitive data, harmful content, or proprietary model
information. The intended default is private collection with short retention.
Public artifacts should use synthetic, consented, or carefully redacted traces.
