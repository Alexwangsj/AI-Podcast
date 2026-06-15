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
EDGE_TTS_RATE=-15%
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
