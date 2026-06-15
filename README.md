# AI Podcast

Private-ish podcast feeds hosted by GitHub Pages.

Base URL:

```text
https://alexwangsj.github.io/AI-Podcast/radio-rJ5DwUcy9jXQtZ94ek9A1NZs/
```

Feeds:

```text
https://alexwangsj.github.io/AI-Podcast/radio-rJ5DwUcy9jXQtZ94ek9A1NZs/ai-daily/feed.xml
https://alexwangsj.github.io/AI-Podcast/radio-rJ5DwUcy9jXQtZ94ek9A1NZs/research/feed.xml
```

## Setup

1. Enable GitHub Pages for this repo:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/docs`
   - This avoids needing GitHub Actions `workflow` token scope.

2. Create `.env` locally:

```bash
cp .env.example .env
```

3. Edit `.env` and set `OPENAI_API_KEY`.

4. Generate an episode from prepared Markdown/text:

```bash
python3 scripts/new_episode.py \
  --channel research \
  --title "Example Research" \
  --summary "A short research briefing." \
  --notes-file /path/to/notes.md \
  --script-file /path/to/speech.txt
```

5. Commit and push:

```bash
git add docs
git commit -m "Add podcast episode"
git push
```

## Channels

- `ai-daily`: 20-minute daily AI news briefing.
- `research`: 20-minute ad hoc research briefing.

## Privacy

GitHub Pages is not strict private hosting. This repo uses an unlisted random path:

```text
radio-rJ5DwUcy9jXQtZ94ek9A1NZs
```

Anyone with the URL can access the feed. Do not publish sensitive content here.
