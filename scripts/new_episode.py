from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

from build_feed import write_feed
from config import (
    ARCHIVE_DIR,
    CHANNELS,
    EDGE_TTS_PITCH,
    EDGE_TTS_RATE,
    EDGE_TTS_VOICE,
    EDGE_TTS_VOLUME,
    OPENAI_TTS_MODEL,
    OPENAI_TTS_VOICE,
    TTS_BACKEND,
    channel_dir,
)


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = value.strip("-")
    return value[:60] or "episode"


def remove_date_from_title(title: str, date_text: str) -> str:
    without_date = title.replace(date_text, "")
    without_date = re.sub(r"\s+", " ", without_date)
    return without_date.strip(" -_") or title


def episode_slug(date_text: str, title: str) -> str:
    return f"{date_text}-{slugify(remove_date_from_title(title, date_text))}"


def synthesize_audio(
    text: str,
    output_path: Path,
    *,
    backend: str,
    model: str,
    openai_voice: str,
    edge_voice: str,
    edge_rate: str,
    edge_pitch: str,
    edge_volume: str,
) -> None:
    if backend == "openai":
        from tts_openai import synthesize as synthesize_openai

        synthesize_openai(text, output_path, model=model, voice=openai_voice)
        return
    if backend == "edge":
        from tts_edge import synthesize as synthesize_edge

        synthesize_edge(
            text,
            output_path,
            voice=edge_voice,
            rate=edge_rate,
            pitch=edge_pitch,
            volume=edge_volume,
        )
        return
    raise ValueError(f"Unknown TTS backend: {backend}")


def build_archive_document(
    *,
    metadata: dict[str, str],
    notes_text: str,
    speech_text: str,
    include_speech: bool,
    tts_backend: str,
    edge_voice: str,
    edge_rate: str,
) -> str:
    lines = [
        f"# {metadata['title']}",
        "",
        "## 播客信息",
        "",
        f"- 频道：`{metadata['channel']}`",
        f"- 发布日期：`{metadata['pub_date']}`",
        f"- 摘要：{metadata['summary'] or '无'}",
        f"- 音频文件：`{metadata['audio_file']}`",
        f"- 公开 notes 文件：`{metadata['notes_file']}`",
        f"- TTS：`{tts_backend}`",
        f"- Edge 声音：`{edge_voice}`",
        f"- Edge 语速：`{edge_rate}`",
        "",
        "## 研究文档",
        "",
        notes_text.rstrip(),
        "",
    ]
    if include_speech:
        lines.extend(
            [
                "## 播报稿",
                "",
                speech_text.rstrip(),
                "",
            ]
        )
    return "\n".join(lines)


def should_publish_script(channel: str) -> bool:
    return channel != "ai-daily"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a podcast episode and rebuild the RSS feed.")
    parser.add_argument("--channel", choices=sorted(CHANNELS), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument("--notes-file", type=Path, required=True)
    parser.add_argument("--script-file", type=Path, required=True)
    parser.add_argument("--date", help="YYYY-MM-DD. Defaults to today UTC.")
    parser.add_argument("--no-tts", action="store_true", help="Create metadata and notes without generating audio.")
    parser.add_argument("--audio-file", type=Path, help="Use an existing MP3 instead of generating one.")
    parser.add_argument("--tts-backend", choices=["edge", "openai"], default=TTS_BACKEND)
    parser.add_argument("--model", default=OPENAI_TTS_MODEL)
    parser.add_argument("--openai-voice", default=OPENAI_TTS_VOICE)
    parser.add_argument("--edge-voice", default=EDGE_TTS_VOICE)
    parser.add_argument("--edge-rate", default=EDGE_TTS_RATE)
    parser.add_argument("--edge-pitch", default=EDGE_TTS_PITCH)
    parser.add_argument("--edge-volume", default=EDGE_TTS_VOLUME)
    args = parser.parse_args()

    date_text = args.date or date.today().isoformat()
    slug = episode_slug(date_text, args.title)
    root = channel_dir(args.channel)
    notes_dir = root / "notes"
    episodes_dir = root / "episodes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    episodes_dir.mkdir(parents=True, exist_ok=True)

    notes_name = f"{slug}.md"
    script_name = f"{slug}.speech.txt"
    audio_name = f"{slug}.mp3"
    metadata_name = f"{slug}.json"

    notes_text = args.notes_file.read_text(encoding="utf-8")
    speech_text = args.script_file.read_text(encoding="utf-8")

    (notes_dir / notes_name).write_text(notes_text, encoding="utf-8")
    publish_script = should_publish_script(args.channel)
    if publish_script:
        (notes_dir / script_name).write_text(speech_text, encoding="utf-8")

    if args.audio_file:
        shutil.copyfile(args.audio_file, episodes_dir / audio_name)
    elif not args.no_tts:
        synthesize_audio(
            speech_text,
            episodes_dir / audio_name,
            backend=args.tts_backend,
            model=args.model,
            openai_voice=args.openai_voice,
            edge_voice=args.edge_voice,
            edge_rate=args.edge_rate,
            edge_pitch=args.edge_pitch,
            edge_volume=args.edge_volume,
        )
    else:
        placeholder = episodes_dir / audio_name
        placeholder.write_bytes(b"")

    pub_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    metadata = {
        "guid": f"{args.channel}-{slug}",
        "channel": args.channel,
        "title": args.title,
        "summary": args.summary,
        "pub_date": pub_date,
        "notes_file": notes_name,
        "audio_file": audio_name,
    }
    if publish_script:
        metadata["script_file"] = script_name
    (notes_dir / metadata_name).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    archive_dir = ARCHIVE_DIR / args.channel
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / notes_name
    archive_path.write_text(
        build_archive_document(
            metadata=metadata,
            notes_text=notes_text,
            speech_text=speech_text,
            include_speech=publish_script,
            tts_backend=args.tts_backend,
            edge_voice=args.edge_voice,
            edge_rate=args.edge_rate,
        ),
        encoding="utf-8",
    )
    feed_path = write_feed(args.channel)

    print(
        json.dumps(
            {"episode": metadata, "feed": str(feed_path), "archive": str(archive_path)},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
