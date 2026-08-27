# CogTrace project state

This is the single living handoff for the project. Update it only when the
current phase, evidence gate, blocker, or ordered next step changes. Historical
decisions and experiment results belong in their append-only records.

| Field | Current |
| --- | --- |
| Last updated | 2026-08-27 |
| Phase | M1 engineering validation |
| Current gate | Checkpoint completion-budget compatibility decision |
| Active experiment | [`EXP-002 — complete; integration gate failed`](docs/experiments/EXP-002-failed-trial-retention-resmoke.md) |
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
  2,048-token completion limit in reasoning. Because `finish_reason` is not yet
  retained, budget exhaustion is strongly supported but not directly recorded.
- The `EXP-002` GPU and its cloud and local experiment SSH keys were destroyed
  and verified absent. No billable experiment resource remains.
- CI passes on Python 3.9, 3.11, and 3.13.

## Evidence status

Current evidence demonstrates that the fixture pipeline works and that two
matched live GPT-OSS runs exercised all four treatment paths. Both live runs
failed the same zero-error integration gate; `EXP-002` localizes the likely
failure to the shared reasoning/final-output completion budget. Their small
diagnostic scores are not research evidence. Nothing yet shows that structured
traces improve real-model monitorability, faithfulness, capability, or safety.
The fixture's perfect rule matches remain expected by construction.

## Ordered next steps

1. Create a proposed decision record for provider `finish_reason` retention and
   a treatment-neutral completion-budget policy. Do not change the frozen
   `EXP-002` result.
2. Implement and test the accepted instrumentation offline, including length-
   terminated responses with empty final content.
3. Preregister `EXP-003` before any compatibility change or third live run.
4. Obtain fresh explicit approval at the action point before creating any new
   billable GPU; prior approvals do not carry forward.
5. Before M1 collection, freeze the annotation guide, task split, capability-loss
   budget, probabilistic monitoring metrics, retention policy, and analysis code.

## Current blockers and approvals

- The live checkpoint treatment can consume the entire shared completion budget
  in reasoning before producing its required final JSON event.
- Provider termination reasons are not retained in `Generation` or trial calls.
- Any future live run needs a new experiment record and explicit billable-GPU
  approval at provisioning time.
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

- 12 unit tests pass.
- The fixture pilot writes 24 JSONL records under `runs/`.
- No pilot record contains a harness error.
- Structured treatments have valid traces.

The authoritative fixture result is recorded in
[`EXP-000`](docs/experiments/EXP-000-deterministic-fixture-gate.md). The failed
live smoke and private artifact metadata are recorded in
[`EXP-001`](docs/experiments/EXP-001-gpt-oss-live-smoke.md) and
[`EXP-002`](docs/experiments/EXP-002-failed-trial-retention-resmoke.md).

## Decisions still open

- Exact M1 capability-loss budget and primary statistical test.
- Annotation rubric, rater count beyond the two-rater minimum, and adjudication.
- Model family and hardware for replication after GPT-OSS engineering validation.
- Raw-CoT retention duration and access controls for live collection.
- Provider termination-reason fields and treatment-neutral completion-budget
  semantics for checkpoint generation.
- Design of the action-only and fully constrained treatments.
