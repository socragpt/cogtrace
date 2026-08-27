# EXP-000: Deterministic end-to-end fixture gate

- **Status:** Complete
- **Evidence level:** Fixture
- **Created:** 2026-08-27
- **Run date:** 2026-08-27
- **Owners:** CogTrace contributors
- **Code revision:** `1a09bbd` (CI runtime follow-up at `16da75a`)
- **Data classification:** Synthetic

## Question

Can the CogTrace harness execute every implemented treatment, validate structured
events, attach harness-trusted telemetry, score findings, preserve completion
markers, and write complete JSONL records without a live model?

## Non-claims

This experiment cannot establish real-model monitorability, faithfulness,
capability preservation, safety improvement, classifier calibration, or
adversarial robustness.

## Frozen configuration

- Tasks: `examples/pilot-tasks.json`, schema version 1, six synthetic tasks.
- Treatments: all four executable treatments.
- Backend: deterministic fixture backend.
- Repetitions: one for CLI gate, two in the matched-treatment unit test.
- Output: ignored local file under `runs/`.
- Verification: unit tests plus fixture pilot in CI.

## Procedure

```bash
make check
```

## Acceptance criteria

- Eleven unit tests pass.
- The CLI gate emits 24 records with no harness error.
- All structured traces validate.
- All task completion markers are preserved.
- The trusted tool-spoof observation has harness-assigned telemetry provenance.

## Deviations

None.

## Results

- 11 unit tests passed locally and in CI.
- 24 CLI trial records were written.
- Zero harness errors occurred.
- Structured trace validity and task marker checks passed.
- Reference-rule precision, recall, and F1 were 1.0 on the authored fixtures.

## Interpretation

The software integration gate passed. The perfect rule scores are expected by
construction because the fixtures were written to exercise those rules. They
are not scientific evidence.

## Artifacts

- Versioned fixture tasks and tests are in the repository.
- Generated JSONL is reproducible and intentionally ignored by Git.
- CI run for the verified baseline:
  <https://github.com/socragpt/cogtrace/actions/runs/33109681246>

## Next decision

Proceed to `EXP-001` only after explicit approval to create a billable ephemeral
GPU.
