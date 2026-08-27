# Experiment registry

Every experiment gets a record before its first run. The record freezes intent
and acceptance criteria, then retains deviations, results, and interpretation.
Never overwrite an unfavorable run; append a new run or create a new experiment.

## Registry

| ID | Evidence level | Status | Experiment |
| --- | --- | --- | --- |
| [EXP-000](EXP-000-deterministic-fixture-gate.md) | Fixture | Complete | Deterministic end-to-end fixture gate |
| [EXP-001](EXP-001-gpt-oss-live-smoke.md) | Live engineering smoke | Complete; gate failed | GPT-OSS 20B backend smoke |
| [EXP-002](EXP-002-failed-trial-retention-resmoke.md) | Live engineering smoke | Complete; gate failed | Failed-trial retention and GPT-OSS re-smoke |

Use [`EXP-template.md`](EXP-template.md) for the next experiment. Assign the next
number and add it to this table before running it.
