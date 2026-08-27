#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="${COGTRACE_MODEL_ID:-openai/gpt-oss-20b}"
VLLM_IMAGE="${COGTRACE_VLLM_IMAGE:-vllm/vllm-openai:v0.26.0}"
MODEL_CACHE="${COGTRACE_MODEL_CACHE:-${PWD}/.cache/huggingface}"

mkdir -p "${MODEL_CACHE}"

docker run --rm --gpus all --ipc=host \
  --publish 127.0.0.1:8000:8000 \
  --volume "${MODEL_CACHE}:/root/.cache/huggingface" \
  "${VLLM_IMAGE}" \
  --model "${MODEL_ID}" \
  --host 0.0.0.0 \
  --port 8000 \
  --reasoning-parser openai_gptoss \
  --generation-config vllm \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.90 \
  --no-enable-prefix-caching
