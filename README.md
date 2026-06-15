# AI Podcast

Podcast publishing workspace.

This repository contains scripts and static podcast artifacts for GitHub Pages publishing.
Private feed URLs, random paths, and personal subscription instructions are intentionally not documented here.

## Setup

1. Create `.env` locally:

```bash
cp .env.example .env
```

2. Install dependencies:

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

4. Generate an episode from prepared notes and speech text:

```bash
.venv/bin/python scripts/new_episode.py \
  --channel research \
  --title "Example Research" \
  --summary "A short research briefing." \
  --notes-file /path/to/notes.md \
  --script-file /path/to/speech.txt
```

5. Commit and push:

```bash
git add docs scripts README.md requirements.txt .env.example
git commit -m "Add podcast episode"
git push
```

## Channels

- `ai-daily`: daily AI news briefing.
- `research`: ad hoc research briefing.

## Privacy

This repository is public. Do not place private feed URLs, random paths, credentials, or sensitive research material in this README.
