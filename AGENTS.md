# CogTrace repository instructions

These instructions apply to the entire repository. They exist so a new human or
agent context can recover the project's intent from versioned files instead of
conversation history.

## Mission

CogTrace tests whether a small, typed projection of emitted model reasoning can
improve safety monitoring and incident investigation at an acceptable capability
cost. A structured trace is a monitoring artifact. It is not a complete account
of hidden computation, proof of faithfulness, or an action-control mechanism.

## Start every work session here

1. Read this file.
2. Read `PROJECT_STATE.md` for the current phase, gate, and ordered next steps.
3. Read the active experiment record linked from `PROJECT_STATE.md`.
4. Read relevant accepted records under `docs/decisions/` before changing a
   research assumption, treatment, schema, metric, or safety boundary.
5. Check the working tree and recent commits. Treat uncommitted work as belonging
   to the user unless the current task clearly says otherwise.
6. Run `make check` before relying on the fixture pipeline. If the task is
   documentation-only, a proportionate check is acceptable.

Conversation history can explain a request, but the repository is the canonical
project memory. Verify stale status claims against code, tests, and artifacts.

## Canonical sources

Each concern has one primary home:

- `README.md`: public project overview and entry points.
- `RESEARCH_PLAN.md`: hypotheses, treatments, metrics, phases, and gates.
- `PROJECT_STATE.md`: current status, active experiment, blockers, and next steps.
- `docs/decisions/`: durable decisions and their consequences.
- `docs/experiments/`: preregistered experiment configurations and results.
- `docs/trace-spec.md`: trace schema and invariants.
- `docs/pilot-protocol.md`: current pilot treatment semantics and collection rules.

Do not create a second roadmap or status file. Link to the canonical source and
update it in the same commit as the change that makes it stale.

## Non-negotiable research boundaries

- Keep validity, monitorability, faithfulness, and capability as separate claims.
- Never present synthetic fixture performance as scientific evidence.
- Label post-hoc traces as translations, not direct reasoning evidence.
- Describe `checkpoint_loop` precisely: it constrains persistent external state,
  not hidden activations or transient within-call reasoning.
- Assign trusted IDs, timestamps, and telemetry provenance in the harness, never
  from model-authored fields.
- Record failed, malformed, and missing traces; do not silently discard or rerun
  them to improve results.
- Freeze tasks, model/server settings, prompts, metrics, and analysis rules before
  interpreting an M1 collection.
- Keep raw chain-of-thought private with short retention. Commit only synthetic,
  consented, or reviewed and redacted material.
- Use simulated, isolated resources for risky scenarios. Never use production
  credentials or systems.
- Do not create a billable cloud resource without explicit user approval at the
  action point. Power-off is not teardown for a billed GPU; verify destruction.

## Change workflow

For an ordinary implementation:

1. Identify the active milestone and acceptance gate in `PROJECT_STATE.md`.
2. Add or update tests before treating the work as complete.
3. Run `make check` and any focused tests needed for the change.
4. Add a decision record when the change alters a durable assumption, treatment
   semantics, metric, schema contract, data policy, or infrastructure choice.
5. Add or update an experiment record when parameters are frozen, a run occurs,
   a deviation is discovered, or results are interpreted.
6. Update `PROJECT_STATE.md` when the phase, active gate, blocker, or ordered next
   step changes. Do not edit it for trivial refactors.
7. Keep code, tests, documentation, state, and experiment metadata in the same
   commit when they describe one logical change.

## Definition of done

Work is not complete until:

- behavior and claim boundaries are documented;
- relevant tests and `make check` pass;
- failures and limitations are retained rather than hidden;
- the active experiment or decision record is updated when applicable;
- `PROJECT_STATE.md` gives the next context an accurate starting point;
- the working tree contains no accidental run output or sensitive data.

Use `docs/handoff-checklist.md` before ending a substantial work session.
