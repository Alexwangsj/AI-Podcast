# AI Podcast Agent Guide

This repository publishes static podcast RSS feeds and MP3 episodes through GitHub Pages.

## Privacy

- Do not commit `.env`, API keys, access tokens, private feed URLs, or the real random podcast path into documentation.
- Public docs may mention placeholders only, such as `replace_with_private_random_path`.
- Generated files under `docs/` are public once pushed.

## Local Setup

Run the local setup script after cloning on a new machine:

```bash
./scripts/setup_local.sh
```

Then create or restore `.env` from a private source:

```bash
cp .env.example .env
```

Required `.env` values:

```bash
PODCAST_BASE_URL=<real GitHub Pages base URL>
PODCAST_PRIVATE_PATH=<real random path>
TTS_BACKEND=edge
EDGE_TTS_VOICE=zh-CN-YunjianNeural
EDGE_TTS_RATE=+50%
```

If the machine needs a proxy for GitHub or OpenAI API access, `.env` may also include:

```bash
HTTP_PROXY=http://proxy.nioint.com:8080
HTTPS_PROXY=http://proxy.nioint.com:8080
```

## Validation

Before generating or publishing an episode, run:

```bash
.venv/bin/python scripts/doctor.py
```

Before committing script changes, run:

```bash
.venv/bin/python -m py_compile scripts/*.py
```

## Episode Workflow

Use the repo skill at `.agents/skills/ai-research-podcast/SKILL.md` for daily AI news and ad hoc research podcast episodes.

The usual command shape is:

```bash
.venv/bin/python scripts/new_episode.py \
  --channel ai-daily \
  --title "<episode title>" \
  --summary "<one sentence summary>" \
  --notes-file "tmp/<slug>-notes.md" \
  --script-file "tmp/<slug>-speech.txt"
```

Use `--channel research` for ad hoc research topics.

## Daily Automation

The daily automation prompt lives at `prompts/daily_ai_podcast.md`.

To install the macOS schedule:

```bash
./scripts/install_daily_launchd.sh
```

The launchd job runs `scripts/run_daily_ai_podcast.sh` every day at 07:30 local time.
