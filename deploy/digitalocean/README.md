# Ephemeral DigitalOcean GPU runbook

This runbook prepares the first live CogTrace engineering smoke. It does not
create a billable resource automatically. Provisioning the GPU is a separate,
explicitly approved step.

## Recommended first machine

Use one NVIDIA H100 GPU Droplet for the least ambiguous first run of
`openai/gpt-oss-20b`. The model itself is small enough for less memory, but the
current [vLLM GPT-OSS recipe](https://github.com/vllm-project/recipes/blob/main/OpenAI/GPT-OSS.md)
explicitly validates Hopper while describing Ada support as an active
compatibility area. A cheaper L40S or RTX 6000 Ada run is a worthwhile
follow-up after the harness is known to work.

Check the live catalog immediately before creation:

```bash
doctl compute size list --format Slug,Description,Memory,VCPUs,PriceHourly \
  | grep -E 'H100|L40S|RTX'
doctl compute region list
```

DigitalOcean starts GPU billing when a Droplet is created and stops it only
when the Droplet is destroyed, not when it is powered off. See the
[GPU pricing page](https://www.digitalocean.com/pricing/gpu-droplets) and
[Droplet billing documentation](https://docs.digitalocean.com/products/droplets/details/pricing/).

## Security boundary

- Use DigitalOcean's NVIDIA AI/ML-ready image and SSH-key authentication.
- Keep the inference port bound to `127.0.0.1`; reach it only through an SSH
  tunnel. Do not expose port 8000 publicly.
- Do not enable a model tool server, shell executor, browser, or production
  credential.
- Use only the synthetic tasks in `examples/pilot-tasks.json` for the first run.
- Download result JSONL before destroying the Droplet, then verify destruction.

DigitalOcean documents the current NVIDIA image slug and included drivers in
its [recommended GPU setup](https://docs.digitalocean.com/products/droplets/getting-started/recommended-gpu-setup/).

## Server setup

After creating the Droplet in the control panel and connecting over SSH:

```bash
git clone https://github.com/socragpt/cogtrace.git
cd cogtrace
./scripts/serve_gpt_oss.sh
```

The script pins vLLM, disables tool use, turns off prefix caching for cleaner
synthetic measurements, and publishes the API only on the server's loopback
interface. The initial model download may take several minutes.

For a revision-pinned run, also pin the checkout, model, and immutable image:

```bash
git checkout COGTRACE_COMMIT
COGTRACE_MODEL_REVISION=MODEL_COMMIT \
COGTRACE_VLLM_IMAGE=VLLM_IMAGE_DIGEST \
./scripts/serve_gpt_oss.sh
```

Replace all three placeholders with values frozen in the active experiment
record. Do not rely on a moving branch, model alias, or container tag for a
recorded live collection.

From the local machine, create the tunnel in a separate terminal:

```bash
ssh -N -L 8000:127.0.0.1:8000 root@DROPLET_IP
```

Verify the endpoint locally:

```bash
curl http://127.0.0.1:8000/v1/models
```

## Run the pilot

From a local CogTrace checkout while the tunnel is active:

```bash
PYTHONPATH=src python3 -m cogtrace pilot examples/pilot-tasks.json \
  --backend openai-compatible \
  --base-url http://127.0.0.1:8000/v1 \
  --model openai/gpt-oss-20b \
  --structured-outputs \
  --seed 17 \
  --output runs/gpt-oss-20b-smoke.jsonl
```

Keep the complete JSONL even if some trials fail. Record the Droplet GPU type,
vLLM image tag, model revision, command, and CogTrace commit with the run.

## Teardown checklist

1. Stop vLLM and close the SSH tunnel.
2. Confirm the result JSONL is on the local machine.
3. Destroy the GPU Droplet in the control panel or with `doctl`.
4. List Droplets again and verify the resource is absent.
5. Record the observed runtime and billed duration in the run notes.

Powering the machine off is not teardown. Destroying it is the cost boundary.
