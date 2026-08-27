# EXP-002: Failed-trial retention and GPT-OSS re-smoke

- **Status:** Planned; live run approval required
- **Evidence level:** Live engineering smoke
- **Created:** 2026-08-27
- **Run date:** Not run
- **Owners:** CogTrace contributors
- **Code revision:** `5833c938ee57b104870ce867ec2f5a4c41f75786`
- **Data classification:** Synthetic tasks with private raw model reasoning

## Question

After the harness preserves successful calls that precede a trial error, can a
revision-pinned GPT-OSS 20B endpoint complete the same 24-trial integration
smoke without backend or harness error?

## Non-claims

This re-smoke cannot establish improved monitorability, capability,
faithfulness, investigator performance, or safety. It must not be tuned against
the diagnostic tag scores or trace-validity rates from `EXP-001`.

## Prerequisites and approvals

- An offline failure-injection test proves that every successfully returned
  generation preceding an error remains in the private trial record with its
  model, content, reasoning, token usage, and latency.
- `make check` and CI pass at the exact candidate revision.
- The model revision and immutable server image are pinned.
- The user gives explicit approval immediately before a new billable GPU is
  created. No approval is carried forward from `EXP-001`.

## Frozen configuration

Inherit the tasks, four treatments, prompts, seed 17, temperature 0.0, event
limit 12, token limit 2048, and structured-output setting from `EXP-001`.

- Model: `openai/gpt-oss-20b` revision
  `6cee5e81ee83917806bbde320786a8fb61efebee`.
- Server image:
  `vllm/vllm-openai@sha256:ffb2d59b1c059a5bd8d781320c9f5189de8293693b7d95da54befddaa54abf52`.
- Hardware target: one on-demand NVIDIA H100 80 GB in an available region.
- Expected trials: 24.
- Output: `runs/gpt-oss-20b-resmoke.jsonl` on the local machine.

Any necessary compatibility change to prompts, parser, schema, or treatment
semantics requires a separate decision and must not be folded into this matched
re-smoke.

The frozen remote launch command is:

```bash
git checkout 5833c938ee57b104870ce867ec2f5a4c41f75786
COGTRACE_MODEL_REVISION=6cee5e81ee83917806bbde320786a8fb61efebee \
COGTRACE_VLLM_IMAGE=vllm/vllm-openai@sha256:ffb2d59b1c059a5bd8d781320c9f5189de8293693b7d95da54befddaa54abf52 \
./scripts/serve_gpt_oss.sh
```

The frozen local collection command is:

```bash
PYTHONPATH=src python3 -m cogtrace pilot examples/pilot-tasks.json \
  --backend openai-compatible \
  --base-url http://127.0.0.1:8000/v1 \
  --model openai/gpt-oss-20b \
  --structured-outputs \
  --seed 17 \
  --output runs/gpt-oss-20b-resmoke.jsonl
```

## Procedure

1. Run the failure-injection test and `make check` locally.
2. Update this record with the exact code revision and immutable launch command.
3. Obtain action-point approval and follow `deploy/digitalocean/README.md`.
4. Run the matched 24-trial smoke once and preserve every record.
5. Copy required artifacts locally, destroy the GPU, and verify absence.

## Offline readiness

The candidate harness change adds a failure-injection backend that returns two
valid checkpoints followed by malformed content. The regression test verifies
that the failed record retains all three returned generations, the malformed
content, model identity, raw reasoning, token usage, and latency. Local
`make check` passes with 12 unit tests and the unchanged 24-record fixture gate.
The server launcher accepts an optional `COGTRACE_MODEL_REVISION`, and the
runbook requires an exact checkout plus immutable image digest. Candidate
revision `5833c938ee57b104870ce867ec2f5a4c41f75786` passed local `make check`,
shell syntax validation, and GitHub CI before it was frozen here.

## Acceptance criteria

- Exactly 24 records are retained.
- No backend or harness error occurs.
- Every successfully returned call is retained even if a later operation fails.
- Hardware, model revision, server image, code revision, runtime, deviations,
  artifact checksum, and infrastructure destruction are recorded.
- Invalid traces, malformed outputs, and task failures remain observations and
  are never silently rerun.

Trace validity, task success, token usage, latency, and diagnostic tag scores
remain non-gating engineering measurements.

## Deviations

Not run.

## Results

Not run.

## Interpretation

Pending.

## Artifacts

Pending. Raw reasoning must remain private, access-controlled, and gitignored.

## Next decision

If the integration gate passes, prepare the frozen M1 collection prerequisites.
If it fails, preserve the run and classify the failure from retained evidence
before proposing any compatibility change.
