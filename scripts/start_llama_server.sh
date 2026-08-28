#!/usr/bin/env bash
# ==============================================================================
# start_llama_server.sh
# Starts the llama.cpp OpenAI-compatible HTTP server running Qwen3.8-4B-Q4_K_M on CPU.
# Optimized for AMD Ryzen 9 7950X / multi-core CPUs without consuming GPU compute.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Configuration defaults (overrideable via environment variables)
MODEL_PATH="${MODEL_PATH:-${PROJECT_ROOT}/models/gguf/Qwen3.8-4B-Q4_K_M.gguf}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8081}"
THREADS="${THREADS:-16}"
CTX_SIZE="${CTX_SIZE:-4096}"
MODEL_ALIAS="${MODEL_ALIAS:-qwen3.8-4b,llama3.2}"

# Ensure binary is in PATH or resolve local build
LLAMA_SERVER="$(which llama-server 2>/dev/null || echo "${HOME}/.local/bin/llama-server")"

if [ ! -f "${LLAMA_SERVER}" ]; then
    if [ -f "${HOME}/Documents/git/llama.cpp/build/bin/llama-server" ]; then
        LLAMA_SERVER="${HOME}/Documents/git/llama.cpp/build/bin/llama-server"
    else
        echo "Error: llama-server binary not found in PATH or ~/.local/bin."
        exit 1
    fi
fi

if [ ! -f "${MODEL_PATH}" ]; then
    echo "Error: Model file not found at: ${MODEL_PATH}"
    echo "Please download it first using:"
    echo "  hf download empero-ai/Qwen3.8-4B-Distill-GGUF Qwen3.8-4B-Q4_K_M.gguf --local-dir ${PROJECT_ROOT}/models/gguf"
    exit 1
fi

echo "=============================================================================="
echo " Starting llama.cpp Server (CPU Mode)"
echo "=============================================================================="
echo " Model:    ${MODEL_PATH}"
echo " Endpoint: http://${HOST}:${PORT}/v1"
echo " Threads:  ${THREADS}"
echo " Context:  ${CTX_SIZE} tokens"
echo " Aliases:  ${MODEL_ALIAS}"
echo "=============================================================================="

exec "${LLAMA_SERVER}" \
    --model "${MODEL_PATH}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --threads "${THREADS}" \
    --ctx-size "${CTX_SIZE}" \
    --alias "${MODEL_ALIAS}" \
    --n-gpu-layers 0 \
    "$@"
