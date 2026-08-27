# M1 pilot protocol

## Purpose

The pilot asks whether a small, typed monitoring channel makes predefined risk
properties easier and cheaper to detect. It does not claim to expose a model's
complete high-dimensional computation. Natural-language token generation is
already a lossy projection; the empirical question is whether another,
deliberately structured projection retains enough information for monitoring.

No pilot treatment authorizes, blocks, or changes a tool action. Independent
telemetry is attached as evaluation evidence and is assigned trusted provenance
by the harness, never by the model.

## Implemented treatments

| Treatment | Generated artifact | What is constrained | Main limitation |
| --- | --- | --- | --- |
| `unrestricted` | Natural-language reasoning and final answer | Nothing | Expensive and semantically variable monitoring input |
| `posthoc` | Unrestricted reasoning, then translated events | Translator's final JSON only | Summary can omit, clean up, or invent rationale |
| `prompt_structured` | JSONL-like emitted reasoning | Prompt compliance only | Syntax is not guaranteed by decoding |
| `checkpoint_loop` | One typed event per call | Each persisted event's JSON schema | Within-call reasoning and hidden computation remain unconstrained |

`checkpoint_loop` is intentionally stronger than a post-hoc summary: each
accepted event becomes the only reasoning state supplied to the next call. It
is still weaker than a continuously grammar-constrained reasoning stream. That
fifth treatment requires tokenizer-aware decoding or a custom logits processor
and remains an M2 deliverable.

Current vLLM structured-output controls apply to a response's structured output
while parsed reasoning remains a separate field. CogTrace therefore asks the
model to return the *next checkpoint* as the constrained final output; it does
not describe this as constrained private reasoning.

## Fixture gate

Run the deterministic end-to-end check before using a model:

```bash
PYTHONPATH=src python3 -m cogtrace pilot examples/pilot-tasks.json \
  --backend fixture \
  --output runs/fixture-pilot.jsonl
```

The six included tasks are safe simulations. They do not execute commands,
open paths, inspect ports, or contain real credentials. Their labels are chosen
to exercise each reference rule; their scores are not evidence about model
behavior or monitor quality.

Fixture acceptance criteria:

- 24 records: six tasks times four treatments.
- No backend or parser errors.
- Every structured treatment has a valid trace.
- Every task contains its declared completion marker.
- Trusted telemetry remains tagged `source=telemetry` and model output cannot
  assign that provenance.

## Live engineering smoke

Start an OpenAI-compatible vLLM endpoint, then run:

```bash
PYTHONPATH=src python3 -m cogtrace pilot examples/pilot-tasks.json \
  --backend openai-compatible \
  --base-url http://127.0.0.1:8000/v1 \
  --model openai/gpt-oss-20b \
  --structured-outputs \
  --seed 17 \
  --output runs/gpt-oss-20b-smoke.jsonl
```

The smoke test is successful when all 24 trials return a record and the harness
reports no errors. Invalid traces, missed tags, and task failures must be kept
in the output; they are results, not reasons to silently rerun.

## M1 collection design

After the live smoke works, expand to at least 25 environment templates. Each
template should have matched benign and risk-bearing instances and should be
split as a template family to prevent train/test leakage. Fifty task instances,
four treatments, and three seeded repetitions produce 600 trajectories, which
clears the plan's 200-trajectory minimum.

Before collection, freeze:

- task templates and held-out template families;
- model checkpoint, server version, sampling parameters, and prompt versions;
- trace schema, validator, monitor versions, and annotation guide;
- a capability-loss budget and primary monitoring metrics;
- rules for malformed traces, failed generations, and reruns;
- the analysis commit hash.

Gold labels must describe evidence in the realized trajectory, not merely an
opportunity present in the task. Two independent raters should annotate live
trajectories without seeing treatment names when practical.

## Recorded fields

Each JSONL record includes the task and treatment, seed, model, gold and
predicted tags, typed events, validation issues, raw reasoning returned by the
backend, final output, token usage, latency, monitor-input characters, task
success, and any error.

Monitor-input characters are a dependency-free engineering proxy. Scientific
collection should add tokenizer-specific monitor tokens, reviewer time,
detection latency from the first relevant event, calibrated monitor scores,
and independent action telemetry.

## Interpretation rules

- Report capability and monitorability separately.
- Treat post-hoc traces as translations, never direct reasoning evidence.
- Treat grammar validity as syntax, never faithfulness.
- Do not infer safety from the deterministic fixtures.
- Report missing or malformed traces rather than dropping them.
- Retain raw CoT privately and briefly; publish only synthetic, consented, or
  reviewed and redacted artifacts.
