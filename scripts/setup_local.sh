#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-python3}"
PIP_PROXY_PREFIX=()

if [[ ! -d ".venv" ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

if [[ -n "${HTTPS_PROXY:-}" ]]; then
  PIP_PROXY_PREFIX+=("HTTPS_PROXY=$HTTPS_PROXY")
fi
if [[ -n "${HTTP_PROXY:-}" ]]; then
  PIP_PROXY_PREFIX+=("HTTP_PROXY=$HTTP_PROXY")
fi

if [[ ${#PIP_PROXY_PREFIX[@]} -gt 0 ]]; then
  env "${PIP_PROXY_PREFIX[@]}" .venv/bin/python -m pip install -r requirements.txt
else
  .venv/bin/python -m pip install -r requirements.txt
fi

if [[ ! -f ".env" ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Fill in PODCAST_BASE_URL and PODCAST_PRIVATE_PATH before publishing."
fi

.venv/bin/python scripts/doctor.py || true
