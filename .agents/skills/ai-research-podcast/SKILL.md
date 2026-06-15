---
name: ai-research-podcast
description: Create and publish AI Podcast episodes from daily AI news or ad hoc research topics. Use when the user asks to turn research/news into a podcast, audio briefing, RSS episode, AI daily, or 20-minute spoken report in this repository.
---

# AI Research Podcast

Use this skill to produce a publishable podcast episode from this repository.

## Privacy

- Never commit `.env`, API keys, private feed URLs, or the real random podcast path into README or public docs.
- `docs/` is public once pushed to GitHub Pages.
- Use placeholders in committed instructions and read real publishing configuration from local `.env`.

## Setup Check

Before generating an episode on a new machine:

```bash
./scripts/setup_local.sh
.venv/bin/python scripts/doctor.py
```

If `.env` is missing or contains placeholders, ask the user to restore it from their private notes or password manager. Do not ask them to paste secrets into chat.

## Workflow

1. Gather sources.
   - For current news, browse and cite primary or reliable sources.
   - For source-code research, inspect local code first.
   - Keep source URLs in the Markdown notes.

2. Write two local source files under `tmp/`:
   - `tmp/<slug>-notes.md`: complete reading notes or report.
   - `tmp/<slug>-speech.txt`: natural Mandarin spoken script.

3. Generate the episode:

```bash
.venv/bin/python scripts/new_episode.py \
  --channel ai-daily \
  --title "<episode title>" \
  --summary "<one sentence summary>" \
  --notes-file "tmp/<slug>-notes.md" \
  --script-file "tmp/<slug>-speech.txt"
```

Use `--channel research` for ad hoc research topics.

Default TTS backend is free Edge TTS (`TTS_BACKEND=edge`). Use OpenAI only when the user explicitly wants it or `.env` sets `TTS_BACKEND=openai`.

4. Verify:
   - Confirm the command produced an MP3 under `docs/.../<channel>/episodes/`.
   - Confirm the generated MP3 is close to the requested target duration.
   - Confirm `docs/.../<channel>/feed.xml` contains the new item.
   - Run `.venv/bin/python scripts/doctor.py`.
   - If `TTS_BACKEND=openai` and `OPENAI_API_KEY` is missing, stop and ask the user to configure `.env`.

5. Publish:

```bash
git status --short
git add docs scripts README.md AGENTS.md .agents .env.example .gitignore requirements.txt
git commit -m "Add <episode title> podcast episode"
git push
```

Do not commit `.env`, `.venv`, `tmp/`, or private local setup notes.

## Episode Standards

- Target length: about 20 minutes unless the user requests otherwise.
- Spoken script: Mandarin Chinese, calm technical analyst tone, no Markdown tables.
- Notes: Markdown with source links and enough structure for later review.
- Summary: one sentence suitable for RSS clients.
