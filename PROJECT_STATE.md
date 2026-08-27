# CogTrace project state

This is the single living handoff for the project. Update it only when the
current phase, evidence gate, blocker, or ordered next step changes. Historical
decisions and experiment results belong in their append-only records.

| Field | Current |
| --- | --- |
| Last updated | 2026-08-27 |
| Phase | M1 engineering validation |
| Current gate | Live-model smoke test |
| Active experiment | [`EXP-001 — GPT-OSS live smoke`](docs/experiments/EXP-001-gpt-oss-live-smoke.md) |
| Repository | <https://github.com/socragpt/cogtrace> |

## North star

Determine whether a small, typed reasoning projection improves monitoring of
predeclared risk properties under matched capability and adversarial pressure.
The project does not need full access to high-dimensional neural computation to
answer that narrower empirical question.

## Established facts

- M0 infrastructure is implemented: trace model, validator, reference monitors,
  evaluation pipeline, CLI, examples, and tests.
- The live harness supports `unrestricted`, `posthoc`, `prompt_structured`, and
  `checkpoint_loop` treatments behind a provider-neutral interface.
- Model-authored events and harness-trusted telemetry have separate provenance.
- The six-task deterministic fixture covers all five initial risk tags.
- `checkpoint_loop` persists only typed events between calls but does not
  constrain transient within-call reasoning or hidden computation.
- The deterministic fixture gate passed: 24 trial records, no harness errors,
  valid structured traces, and preserved completion markers.
- CI passes on Python 3.9, 3.11, and 3.13.
- No live model run has occurred. No GPU has been provisioned.

## Evidence status

Current evidence demonstrates that the software pipeline works on authored
fixtures. It does **not** show that structured traces improve real-model
monitorability, faithfulness, capability, or safety. The fixture's perfect rule
matches are expected by construction.

## Ordered next steps

1. Obtain explicit approval for a billable ephemeral GPU.
2. Follow `deploy/digitalocean/README.md` to start an SSH-only GPT-OSS endpoint.
3. Execute the frozen 24-trial live smoke in `EXP-001` and retain every record.
4. Update `EXP-001` with hardware, model revision, runtime, deviations, and raw
   artifact locations; then update this file with the gate result.
5. Fix harness failures only after preserving the original run and documenting
   deviations. Do not tune against tag scores during the smoke gate.
6. Before M1 collection, freeze the annotation guide, task split, capability-loss
   budget, probabilistic monitoring metrics, retention policy, and analysis code.

## Current blockers and approvals

- The next experiment needs a billable GPU and therefore explicit approval at
  provisioning time.
- Live GPU availability, region, size slug, and price must be checked immediately
  before creation.
- The M1 capability-loss threshold has not been selected or preregistered.
- Independent annotation procedures have not yet been implemented.

## Known limitations

- There is no action-only treatment in the executable pilot runner yet.
- There is no continuously grammar-constrained reasoning stream; that is M2.
- Current monitors are transparent reference rules, not calibrated classifiers.
- Monitor input characters are only an engineering proxy for tokenizer-specific
  monitor cost.
- The task suite is small, synthetic, and tailored to exercise the rules.
- Detection latency, reviewer time, and causal trace interventions are not yet
  implemented.

## Last verified baseline

Run:

```bash
make check
```

Expected baseline:

- 11 unit tests pass.
- The fixture pilot writes 24 JSONL records under `runs/`.
- No pilot record contains a harness error.
- Structured treatments have valid traces.

The authoritative historical result is recorded in
[`EXP-000`](docs/experiments/EXP-000-deterministic-fixture-gate.md).

## Decisions still open

- Exact M1 capability-loss budget and primary statistical test.
- Annotation rubric, rater count beyond the two-rater minimum, and adjudication.
- Model family and hardware for replication after GPT-OSS engineering validation.
- Raw-CoT retention duration and access controls for live collection.
- Design of the action-only and fully constrained treatments.
