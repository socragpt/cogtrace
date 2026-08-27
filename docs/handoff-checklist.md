# Context handoff checklist

Use this checklist before ending a substantial work session or handing the
project to a fresh context.

## Preserve the work

- [ ] Inspect the working tree and separate project changes from unrelated work.
- [ ] Run `make check` plus any focused verification required by the change.
- [ ] Retain failed runs, malformed traces, deviations, and negative results.
- [ ] Confirm no credential, raw private CoT, or unreviewed sensitive artifact is
      staged for commit.

## Preserve the reasoning

- [ ] If a durable assumption changed, add an accepted or proposed record under
      `docs/decisions/` and update its index.
- [ ] If an experiment was planned or run, update its record and the experiment
      registry before interpreting the result.
- [ ] Separate observed results from interpretation and future hypotheses.
- [ ] Record exact model, server, hardware, prompt/configuration, seed, code
      revision, and deviations for a live run.

## Prepare the next context

- [ ] Update `PROJECT_STATE.md` if the phase, gate, blocker, evidence status, or
      ordered next step changed.
- [ ] Ensure `PROJECT_STATE.md` links to the active experiment.
- [ ] Make the first next step executable and identify any required approval.
- [ ] Keep completed history in decision and experiment records rather than
      expanding the living state indefinitely.
- [ ] Commit related code, tests, documentation, and state together.

## Fresh-context recovery test

A new collaborator should be able to answer these questions using only the
repository:

1. What narrow claim is CogTrace testing?
2. What evidence exists, and what does it not establish?
3. Which experiment is active and what is frozen?
4. What action comes next, and does it require approval or money?
5. Which command verifies the current software baseline?

If any answer is unclear, the handoff is incomplete.
