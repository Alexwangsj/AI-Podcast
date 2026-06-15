# Daily AI Research Podcast Automation

Use the repo skill `ai-research-podcast`.

Create today's AI research daily podcast.

## Requirements

- Time window: focus on the last 2 calendar days relative to the run date.
- Coverage: include both international and China AI developments.
- Topics: major AI company news, model releases, product launches, AI infrastructure, notable research papers, open-source projects, policy/safety/regulatory changes, and important business moves.
- Prioritize primary and reliable sources. Use web search for current information.
- Write Mandarin Chinese output.
- Podcast target duration: about 20 minutes.
- TTS backend: use the repository default, normally Edge TTS.
- Channel: `ai-daily`.

## Output Files

Create:

- `tmp/<YYYY-MM-DD>-ai-daily-research-notes.md`
- `tmp/<YYYY-MM-DD>-ai-daily-research-speech.txt`

The notes file must include source links. The speech file should be natural spoken Mandarin, not a Markdown article.

## Episode Command

After writing notes and speech, generate the episode with:

```bash
.venv/bin/python scripts/new_episode.py \
  --channel ai-daily \
  --title "AI研究日报 <YYYY-MM-DD>" \
  --summary "过去两天国内外AI大事件、技术进展、研究与产业动态的20分钟中文播报。" \
  --notes-file "tmp/<YYYY-MM-DD>-ai-daily-research-notes.md" \
  --script-file "tmp/<YYYY-MM-DD>-ai-daily-research-speech.txt"
```

## Verification

Run:

```bash
.venv/bin/python scripts/doctor.py
ffprobe -v error -show_entries format=duration,size -of default=nw=1 <generated-mp3>
```

Confirm the generated MP3 is roughly 18 to 23 minutes. If the duration is too short, expand the speech script before publishing.

## Publish

If verification passes:

```bash
git status --short
git add docs scripts README.md AGENTS.md .agents .env.example .gitignore requirements.txt prompts
git commit -m "Add AI daily research podcast <YYYY-MM-DD>"
git push
```

Do not commit `.env`, `.venv`, `tmp/`, `logs/`, or private local notes.

If there are unrelated uncommitted user changes, stop and explain instead of overwriting or staging them.
