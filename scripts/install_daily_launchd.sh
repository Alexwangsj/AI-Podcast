#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.ai-podcast.daily.plist"
CODEX_BIN="${CODEX_BIN:-$(command -v codex || true)}"

if [[ -z "$CODEX_BIN" ]]; then
  echo "codex CLI not found. Install/login Codex first, or run with CODEX_BIN=/path/to/codex."
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$REPO_DIR/logs"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.ai-podcast.daily</string>

  <key>ProgramArguments</key>
  <array>
    <string>$REPO_DIR/scripts/run_daily_ai_podcast.sh</string>
  </array>

  <key>WorkingDirectory</key>
  <string>$REPO_DIR</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>CODEX_BIN</key>
    <string>$CODEX_BIN</string>
    <key>PATH</key>
    <string>$HOME/.local/node/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>

  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>7</integer>
    <key>Minute</key>
    <integer>30</integer>
  </dict>

  <key>StandardOutPath</key>
  <string>$REPO_DIR/logs/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>$REPO_DIR/logs/launchd.err.log</string>

  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/com.ai-podcast.daily"

echo "Installed daily AI Podcast launchd job:"
echo "$PLIST"
echo "Schedule: every day at 07:30 local time"
echo "Logs: $REPO_DIR/logs/"
