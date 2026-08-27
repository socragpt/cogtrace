# EXP-001: GPT-OSS 20B live backend smoke

- **Status:** Planned; approval required
- **Evidence level:** Live engineering smoke
- **Created:** 2026-08-27
- **Run date:** Not run
- **Owners:** CogTrace contributors
- **Code revision:** Record exact commit at run time
- **Data classification:** Synthetic tasks with private raw model reasoning

## Question

Can one live GPT-OSS 20B endpoint complete all four CogTrace treatments and
produce 24 retained trial records without backend or harness failure?

## Non-claims

This smoke cannot establish that structured traces improve monitoring,
faithfulness, capability, investigator performance, or safety. Tag scores are
diagnostic only and must not be used to tune the smoke configuration.

## Prerequisites and approvals

- Explicit user approval immediately before creating a billable GPU Droplet.
- Current GPU availability, size slug, region, and hourly price checked at the
  action point.
- SSH key access and loopback-only inference serving.
- Fixture gate remains green at the exact code revision used for the run.

## Frozen configuration

- Tasks: `examples/pilot-tasks.json`, schema version 1, six synthetic tasks.
- Model: `openai/gpt-oss-20b`; record the resolved model revision at run time.
- Server: `vllm/vllm-openai:v0.26.0`.
- Treatments: `unrestricted`, `posthoc`, `prompt_structured`, `checkpoint_loop`.
- Repetitions: 1.
- Seed: 17.
- Temperature: 0.0.
- Model-event limit: 12.
- Max generated tokens per call: 2048.
- Structured outputs: enabled for post-hoc and checkpoint final outputs.
- Expected trials: 24.
- Output: `runs/gpt-oss-20b-smoke.jsonl` on the local machine.
- Infrastructure procedure: `deploy/digitalocean/README.md`.

## Procedure

Follow the versioned DigitalOcean runbook without exposing port 8000 publicly,
then execute its live pilot command through the SSH tunnel. Destroy the Droplet
after the artifact is safely local.

## Acceptance criteria

- Exactly 24 records are retained.
- No backend or harness error occurs.
- Hardware, model revision, server image, code revision, runtime, and deviations
  are recorded.
- Invalid structured traces and task failures are preserved as observations.
- The GPU is destroyed and absence is verified after collection.

Trace validity, task success, tag scores, latency, and token usage are measured
but are not pass/fail criteria for this integration smoke.

## Deviations

Not run.

## Results

Not run.

## Interpretation

Pending.

## Artifacts

Pending. Raw reasoning must remain private and must not be committed without
review and redaction.

## Next decision

If the integration gate passes, use the retained failures and validity results
to prepare—not interpret—the frozen M1 collection. If it fails, preserve the run
and create a documented follow-up rather than overwriting it.
