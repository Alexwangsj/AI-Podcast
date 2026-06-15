# AI Podcast

Podcast publishing workspace.

This repository contains scripts and static podcast artifacts for GitHub Pages publishing.
Private feed URLs, random paths, and personal subscription instructions are intentionally not documented here.

## Setup

1. Run local setup:

```bash
./scripts/setup_local.sh
```

2. Restore local publishing config in `.env`.

If `.env` was just created from the public example, replace the placeholders:

```bash
PODCAST_BASE_URL=https://example.github.io/example-repo
PODCAST_PRIVATE_PATH=replace_with_private_random_path
```

Use your private GitHub Pages base URL and random podcast path. Do not commit `.env`.

If setup needs to be run manually:

```bash
python3 -m venv .venv
HTTPS_PROXY=http://proxy.nioint.com:8080 HTTP_PROXY=http://proxy.nioint.com:8080 \
  .venv/bin/python -m pip install -r requirements.txt
```

If your network does not need a proxy, omit the `HTTPS_PROXY` and `HTTP_PROXY` prefix.

3. Choose a TTS backend in `.env`.

Free Edge TTS:

```bash
TTS_BACKEND=edge
EDGE_TTS_VOICE=zh-CN-YunjianNeural
EDGE_TTS_RATE=-15%
```

OpenAI TTS:

```bash
TTS_BACKEND=openai
OPENAI_API_KEY=replace_me
```

4. Check the local environment:

```bash
.venv/bin/python scripts/doctor.py
```

5. Generate an episode from prepared notes and speech text:

```bash
.venv/bin/python scripts/new_episode.py \
  --channel research \
  --title "Example Research" \
  --summary "A short research briefing." \
  --notes-file /path/to/notes.md \
  --script-file /path/to/speech.txt
```

6. Commit and push:

```bash
git add docs scripts README.md requirements.txt .env.example
git commit -m "Add podcast episode"
git push
```

## Channels

- `ai-daily`: daily AI news briefing.
- `research`: ad hoc research briefing.

## Codex Usage

This repo includes:

- `AGENTS.md`: repo guidance for Codex.
- `.agents/skills/ai-research-podcast/SKILL.md`: repo-scoped podcast workflow skill.
- `scripts/setup_local.sh`: new-machine setup.
- `scripts/doctor.py`: local readiness check.
- `prompts/daily_ai_podcast.md`: daily AI research podcast automation prompt.
- `scripts/run_daily_ai_podcast.sh`: daily automation runner.

After cloning on a new computer, open this repository in Codex and ask it to use the `ai-research-podcast` skill.

## Daily Automation

Install the macOS daily job:

```bash
./scripts/install_daily_launchd.sh
```

It runs every day at 07:30 local time and asks Codex CLI to create an `ai-daily` episode covering the last two days of AI news and research.

Logs are written to `logs/`, which is intentionally ignored by git.

Uninstall:

```bash
./scripts/uninstall_daily_launchd.sh
```

## Privacy

This repository is public. Do not place private feed URLs, random paths, credentials, or sensitive research material in this README.
