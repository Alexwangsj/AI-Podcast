#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$REPO_DIR/logs"
RUN_DATE="$(date +%F)"
RUN_LOG="$LOG_DIR/daily-ai-podcast-$RUN_DATE.log"
LAST_MESSAGE="$LOG_DIR/daily-ai-podcast-$RUN_DATE.final.txt"
CODEX_BIN="${CODEX_BIN:-codex}"

mkdir -p "$LOG_DIR"

exec > >(tee -a "$RUN_LOG") 2>&1

echo "[$(date '+%F %T %z')] Starting daily AI podcast automation"
cd "$REPO_DIR"

export PATH="$HOME/.local/node/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if ! command -v "$CODEX_BIN" >/dev/null 2>&1; then
  echo "codex CLI not found. Set CODEX_BIN or add codex to PATH."
  exit 1
fi

if [[ ! -x ".venv/bin/python" ]]; then
  echo ".venv is missing. Running scripts/setup_local.sh first."
  ./scripts/setup_local.sh
fi

.venv/bin/python scripts/doctor.py

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean. Refusing to run automated publishing."
  git status --short
  exit 1
fi

git pull --ff-only

"$CODEX_BIN" --search exec \
  --cd "$REPO_DIR" \
  --sandbox danger-full-access \
  --ask-for-approval never \
  --output-last-message "$LAST_MESSAGE" \
  - < prompts/daily_ai_podcast.md

echo "[$(date '+%F %T %z')] Finished daily AI podcast automation"
