# EXP-003: GPT-OSS completion-budget compatibility smoke

- **Status:** Complete; gate passed
- **Evidence level:** Live engineering smoke
- **Created:** 2026-09-03
- **Run date:** 2026-09-03
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

No research-configuration deviation was observed. The remote launch was wrapped
in `nohup` for session durability and the loopback-only endpoint was reached
through an SSH tunnel; neither changed the frozen model, image, server
arguments, tasks, prompts, seed, treatment, structured-output setting, or token
ceiling. The complete collection was run once, with no selective reruns.

## Results

The preregistered collection completed on 2026-09-03. It retained exactly 24
top-level records and 32 successfully returned calls. No top-level record had a
backend or harness error. Every call had a non-null termination reason; all 32
were `finish_reason="stop"`, and none were `length` terminated.

The following are non-gating engineering diagnostics. They are recorded to
preserve the observed run, not as evidence of scientific performance.

| Treatment | Records | Calls | Task success | Valid trace | Prompt tokens | Completion tokens | Mean latency (ms) | Diagnostic F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `unrestricted` | 6 | 6 | 4/6 | n/a | 826 | 2,168 | 1,555.4 | 0.889 |
| `posthoc` | 6 | 12 | 4/6 | 4/6 | 4,268 | 6,969 | 4,761.2 | 0.750 |
| `prompt_structured` | 6 | 6 | 2/6 | 1/6 | 1,270 | 4,770 | 2,797.1 | 0.000 |
| `checkpoint_loop` | 6 | 8 | 4/6 | 4/6 | 2,000 | 5,662 | 3,375.0 | 0.000 |
| **Total** | **24** | **32** | **14/24** | — | **8,364** | **19,569** | — | — |

The validator retained 74 issues rather than discarding or regenerating the
affected traces: 66 `missing_operand`, 5 `empty_trace`, 2
`invalid_operand_type`, and 1 `event_budget_exceeded`. Trace validity, task
success, token usage, latency, and diagnostic risk-tag scores were explicitly
non-gating.

The endpoint ran vLLM 0.26.0 from the frozen image on one NVIDIA H100 80GB HBM3
(81,559 MiB, driver 580.173.02). The checked-out remote code revision was
`f39ccf8dc836e198f3873b2a26a252367b0056d1`.

The DigitalOcean resource was Droplet `597569639` in NYC2 at a displayed rate
of $4.41/hour. Provisioning was first observed at approximately
2026-09-03T18:31:23Z, and resource and key absence were verified by
2026-09-03T20:08:27Z. The maximum observed window was about 1.62 hours, giving
an estimated cost of about $7.14 at the displayed rate; the provider invoice is
authoritative. The GPU, temporary cloud SSH key, and corresponding local access
files were deleted and verified absent.

The private JSONL is 197,080 bytes, mode `0600`, with SHA-256
`37aadbfbe83138706880a910271e7cc5d44044197821241ae5ebcbba159a3c3b`.
The private vLLM log is 36,987 bytes, mode `0600`, with SHA-256
`cd0525b0f9297ac70729cb838ee8494d91c77fa902c73366aa6972bd7173c32d`.

## Interpretation

The preregistered compatibility gate passed. This run establishes only that the
pinned GPT-OSS/vLLM pairing exercised all four treatment paths for the frozen
synthetic tasks and seed under a 4,096-token per-call ceiling. It does not show
that the higher ceiling caused the pass, that future runs will pass, that total
compute was matched, or that structured traces improve monitorability,
faithfulness, capability, investigator performance, or safety.

The low structured-trace validity and diagnostic tag scores remain useful
design observations, but this smoke was not powered, sampled, or independently
annotated for interpreting them as research evidence.

## Artifacts

The JSONL and server log remain under gitignored `runs/` paths with mode `0600`.
The JSONL contains private raw reasoning. Publish only reviewed and redacted
material.

## Next decision

Proceed to M1 collection design. Before any M1 collection, freeze the annotation
guide, task split, capability-loss budget, probabilistic monitoring metrics,
retention policy, trajectory-level compute policy, and analysis code in durable
decision and experiment records.
