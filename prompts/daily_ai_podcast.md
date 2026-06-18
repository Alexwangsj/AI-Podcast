# Daily AI Research Podcast Automation

Use the repo skill `ai-research-podcast`.

Create today's AI research daily podcast.

## Requirements

- Time window: focus on the last 2 calendar days relative to the run date.
- Coverage: include both international and China AI developments.
- Editorial focus: prioritize technical changes and upgrades. Spend most of the report on model releases, capability improvements, architecture changes, inference/training efficiency, context length, multimodal systems, agent frameworks, AI infrastructure, developer tools, open-source projects, notable research papers, robotics/embodied AI, and concrete product features driven by new technology.
- Policy/safety/regulatory/business items are secondary. Include them only when they materially affect model access, technical roadmaps, product launches, compute supply, open-source availability, or AI deployment.
- Avoid letting policy or governance dominate the episode unless it is the largest AI story of the day and has clear technical consequences.
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
The speech file is only an input for audio generation. AI daily publishing and local archives keep the news notes only; they must not publish or archive the spoken script.

## Recommended Structure

Use this order unless the day's news makes another order clearly better:

1. 技术主线概览：用 2-3 条主线解释今天 AI 技术在往哪里变。
2. 模型与能力升级：新模型、上下文、多模态、推理、工具使用、评测和限制。
3. 工程与基础设施：训练/推理成本、芯片、云服务、数据、框架、部署方式。
4. 开源与开发者生态：重要 repo、工具链、SDK、agent 框架、社区采用。
5. 应用与产品技术变化：产品里的新能力，说明背后的技术增量。
6. 研究论文与机器人/具身智能：只选有技术启发或产业信号的内容。
7. 政策/商业补充：压缩呈现，只讲和技术路线或可用性相关的影响。

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
Confirm `scripts/new_episode.py` printed an `archive` path under `archive/ai-daily/`; this local archive document is intentionally not committed and must not contain a `播报稿` section.
Confirm generated ai-daily filenames follow `YYYY-MM-DD-ai研究日报.*` without a repeated date suffix.

## Publish

If verification passes:

```bash
git status --short
git add docs scripts README.md AGENTS.md .agents .env.example .gitignore requirements.txt prompts
git commit -m "Add AI daily research podcast <YYYY-MM-DD>"
git push
```

Do not commit `.env`, `.venv`, `tmp/`, `logs/`, `archive/`, or private local notes.

If there are unrelated uncommitted user changes, stop and explain instead of overwriting or staging them.
