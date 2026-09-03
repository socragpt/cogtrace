# EXP-003: GPT-OSS completion-budget compatibility smoke

- **Status:** Planned
- **Evidence level:** Live engineering smoke
- **Created:** 2026-09-03
- **Run date:** Not run
- **Owners:** CogTrace contributors
- **Code revision:** `f39ccf8dc836e198f3873b2a26a252367b0056d1`
- **Data classification:** Synthetic tasks with private raw model reasoning

## Question

With provider termination reasons retained and a 4,096-token per-call ceiling,
can the revision-pinned GPT-OSS 20B endpoint complete the same 24-trial matched
smoke without a length termination, backend error, or harness error?

## Non-claims

This smoke cannot establish improved monitorability, faithfulness, capability,
investigator performance, equal total compute, or safety. It must not be tuned
against diagnostic tag scores, trace-validity rates, or task outcomes.

## Prerequisites and approvals

- `ADR-004` remains accepted.
- Offline tests retain and classify a length-terminated response with empty final
  content, and `make check` passes at the exact candidate revision.
- The candidate revision passes CI and is frozen here before collection.
- The model revision and immutable server image remain pinned.
- The user gives fresh explicit approval immediately before a billable GPU is
  created. Approval from an earlier experiment does not carry forward.

## Frozen configuration

Inherit the six synthetic tasks, four treatments, prompts, seed 17, temperature
0.0, event limit 12, and structured-output setting from `EXP-002`. Change only
the instrumentation required by `ADR-004` and the per-call ceiling described
below.

- Model: `openai/gpt-oss-20b` revision
  `6cee5e81ee83917806bbde320786a8fb61efebee`.
- Server image:
  `vllm/vllm-openai@sha256:ffb2d59b1c059a5bd8d781320c9f5189de8293693b7d95da54befddaa54abf52`.
- Hardware target: one on-demand NVIDIA H100 80 GB in an available region.
- Treatments: `unrestricted`, `posthoc`, `prompt_structured`, and
  `checkpoint_loop`.
- Repetitions: 1.
- Max generated tokens per call: 4,096, applied to every treatment and phase.
- Expected trials: 24.
- Output: `runs/gpt-oss-20b-budget-smoke.jsonl` on the local machine.
- Infrastructure procedure: `deploy/digitalocean/README.md`.

The 4,096-token ceiling is one preregistered doubling from the observed
2,048-token truncation boundary. Its purpose is to test backend compatibility,
not optimize task or monitoring scores.

No prompt, parser, schema, model, server, task, seed, temperature, or treatment
change may be folded into this smoke. Any such change requires a deviation
recorded before interpretation or a new experiment.

The frozen remote launch command is:

```bash
git checkout f39ccf8dc836e198f3873b2a26a252367b0056d1
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
  --max-tokens 4096 \
  --output runs/gpt-oss-20b-budget-smoke.jsonl
```

## Procedure

1. Pass the offline instrumentation tests, fixture gate, and CI.
2. Freeze the exact candidate revision and launch command in this record.
3. Obtain action-point approval and follow the DigitalOcean runbook.
4. Run the complete matched 24-trial smoke once. Do not selectively rerun any
   task or treatment.
5. Preserve every record and returned call, including malformed, missing, and
   length-terminated output.
6. Copy the private artifacts locally, destroy the GPU, and verify absence.

## Offline readiness

Candidate revision `f39ccf8dc836e198f3873b2a26a252367b0056d1`
retains provider `finish_reason` values, serializes them for every call, and
summarizes their counts by treatment. Its regression tests cover an omitted
finish reason and a `finish_reason="length"` response with reasoning, full token
usage, and empty final content. The failed checkpoint retains that call and
records an explicit error without retrying it.

Local `make check` passes with 14 unit tests and the unchanged 24-record fixture
gate. GitHub CI passes on Python 3.9, 3.11, and 3.13 for the frozen candidate.
No live endpoint or billable resource was used for offline readiness.

## Acceptance criteria

- Exactly 24 top-level records and every successfully returned call are retained.
- No backend or harness error occurs.
- Every returned call has a non-null serialized `finish_reason`.
- No call records `finish_reason="length"`.
- Hardware, model revision, server image, code revision, runtime, deviations,
  artifact checksum, and infrastructure destruction are recorded.

Trace validity, task success, token usage, latency, call count, and diagnostic
tag scores remain non-gating engineering measurements.

## Deviations

Not run. Record every departure from the frozen configuration here.

## Results

Not run.

## Interpretation

Not run. A passing result would establish only that this model/backend pairing
can exercise all four treatment paths under the preregistered per-call ceiling.

## Artifacts

The planned JSONL contains private raw reasoning and must remain gitignored with
restricted local permissions. Publish only reviewed and redacted material.

## Next decision

If the gate passes, proceed to M1 collection design and freeze its annotation,
capability, retention, metric, and analysis decisions. If it fails, retain the
run unchanged and diagnose the predeclared failure without selective reruns.
