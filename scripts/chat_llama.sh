#!/usr/bin/env bash
# ==============================================================================
# chat_llama.sh
# Interactive terminal chat with Qwen3.8-4B on CPU using llama-cli.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

MODEL_PATH="${MODEL_PATH:-${PROJECT_ROOT}/models/gguf/Qwen3.8-4B-Q4_K_M.gguf}"
THREADS="${THREADS:-16}"
CTX_SIZE="${CTX_SIZE:-4096}"

LLAMA_CLI="$(which llama-cli 2>/dev/null || echo "${HOME}/.local/bin/llama-cli")"

if [ ! -f "${LLAMA_CLI}" ]; then
    if [ -f "${HOME}/Documents/git/llama.cpp/build/bin/llama-cli" ]; then
        LLAMA_CLI="${HOME}/Documents/git/llama.cpp/build/bin/llama-cli"
    else
        echo "Error: llama-cli binary not found."
        exit 1
    fi
fi

if [ ! -f "${MODEL_PATH}" ]; then
    echo "Error: Model file not found at: ${MODEL_PATH}"
    exit 1
fi

exec "${LLAMA_CLI}" \
    --model "${MODEL_PATH}" \
    --threads "${THREADS}" \
    --ctx-size "${CTX_SIZE}" \
    --n-gpu-layers 0 \
    --temp 0.3 \
    "$@"
