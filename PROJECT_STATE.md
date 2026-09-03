# CogTrace project state

This is the single living handoff for the project. Update it only when the
current phase, evidence gate, blocker, or ordered next step changes. Historical
decisions and experiment results belong in their append-only records.

| Field | Current |
| --- | --- |
| Last updated | 2026-09-03 |
| Phase | M1 engineering validation |
| Current gate | Freeze the M1 collection design and acceptance criteria |
| Active experiment | None; [`EXP-003`](docs/experiments/EXP-003-completion-budget-compatibility.md) is complete |
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
- `EXP-001` ran against GPT-OSS 20B on one H100 and retained all 24 top-level
  records. Its integration gate failed because one checkpoint returned no
  parseable event.
- The `EXP-001` error path also discarded the completed calls preceding that
  parse failure. The original artifact is preserved, and the harness now has a
  regression-tested fix that retains successful generations, usage, model, and
  latency on a failed trial.
- The `EXP-001` GPU and its cloud and local experiment SSH keys were destroyed
  and verified absent. No billable experiment resource remains.
- `EXP-002` reproduced the same checkpoint-2 failure with the exact model,
  server image, tasks, prompts, and limits. Its retention fix preserved all 33
  calls and the failed response metadata.
- In the failed call, GPT-OSS returned no final content after using exactly the
  2,048-token completion limit in reasoning. Because the frozen artifact does
  not contain `finish_reason`, budget exhaustion is strongly supported but not
  directly recorded.
- The `EXP-002` GPU and its cloud and local experiment SSH keys were destroyed
  and verified absent. No billable experiment resource remains.
- `ADR-004` defines provider termination-reason retention and separates the
  treatment-neutral per-call ceiling used for compatibility testing from
  trajectory-level capability and cost comparisons.
- The harness now retains `finish_reason` for every returned call, summarizes
  termination reasons by treatment, and explicitly classifies a
  length-terminated checkpoint with empty final content without retrying it.
- `EXP-003` completed the preregistered matched re-smoke with a 4,096-token
  ceiling applied to every model call. All 24 records and 32 returned calls were
  retained, no backend or harness error occurred, every termination reason was
  present, and all 32 calls ended with `finish_reason="stop"`.
- The `EXP-003` compatibility gate passed. Its trace-validity, task-success,
  latency, token, and risk-tag diagnostics are engineering observations from a
  small synthetic run, not research evidence.
- The `EXP-003` GPU and its cloud and local experiment SSH keys were destroyed
  and verified absent. No billable experiment resource remains.

## Evidence status

Current evidence demonstrates that the fixture pipeline works and that three
matched live GPT-OSS runs exercised all four treatment paths. The first two
failed the same integration gate; `EXP-002` localized the likely failure to the
shared reasoning/final-output completion budget. `EXP-003` passed the
compatibility gate at the preregistered 4,096-token per-call ceiling with all
termination reasons retained. This is engineering evidence for one pinned
model/backend/task configuration, not evidence that the higher ceiling caused
the pass or that structured traces improve monitorability, faithfulness,
capability, investigator performance, or safety. The small synthetic diagnostic
scores are not research evidence.

## Ordered next steps

1. Draft and accept the M1 annotation guide, task split, capability-loss budget,
   probabilistic monitoring metrics, raw-reasoning retention policy,
   trajectory-level compute policy, and primary analysis plan.
2. Add an action-only comparator and implement independent annotation and
   adjudication support required by the M1 design.
3. Freeze the M1 tasks, settings, prompts, metrics, analysis code, and acceptance
   criteria in a new preregistered experiment record before collection.
4. Pass local checks and CI on that frozen revision.
5. Only then recheck accelerator price and availability and obtain fresh explicit
   approval at the action point before creating any billable resource.

## Current blockers and approvals

- The M1 capability-loss threshold has not been selected or preregistered.
- Independent annotation procedures have not yet been implemented.
- The M1 probabilistic monitoring metrics, primary analysis, task split,
  retention policy, and trajectory-level compute policy remain unfrozen.
- Any future live run needs a new experiment record and fresh explicit
  billable-resource approval at provisioning time.

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

- 14 unit tests pass.
- The fixture pilot writes 24 JSONL records under `runs/`.
- No pilot record contains a harness error.
- Structured treatments have valid traces.

The authoritative fixture result is recorded in
[`EXP-000`](docs/experiments/EXP-000-deterministic-fixture-gate.md). The failed
live smoke and private artifact metadata are recorded in
[`EXP-001`](docs/experiments/EXP-001-gpt-oss-live-smoke.md) and
[`EXP-002`](docs/experiments/EXP-002-failed-trial-retention-resmoke.md). The
passing compatibility smoke and private artifact metadata are recorded in
[`EXP-003`](docs/experiments/EXP-003-completion-budget-compatibility.md).

## Decisions still open

- Exact M1 capability-loss budget and primary statistical test.
- Annotation rubric, rater count beyond the two-rater minimum, and adjudication.
- Model family and hardware for replication after GPT-OSS engineering validation.
- Raw-CoT retention duration and access controls for live collection.
- Exact M1 trajectory-level compute matching or adjustment policy.
- Design of the action-only and fully constrained treatments.
