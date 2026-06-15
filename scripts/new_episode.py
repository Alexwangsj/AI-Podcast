from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from build_feed import write_feed
from config import (
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

    date_text = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    slug = f"{date_text}-{slugify(args.title)}"
    root = channel_dir(args.channel)
    notes_dir = root / "notes"
    episodes_dir = root / "episodes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    episodes_dir.mkdir(parents=True, exist_ok=True)

    notes_name = f"{slug}.md"
    script_name = f"{slug}.speech.txt"
    audio_name = f"{slug}.mp3"
    metadata_name = f"{slug}.json"

    shutil.copyfile(args.notes_file, notes_dir / notes_name)
    shutil.copyfile(args.script_file, notes_dir / script_name)

    if args.audio_file:
        shutil.copyfile(args.audio_file, episodes_dir / audio_name)
    elif not args.no_tts:
        speech_text = args.script_file.read_text(encoding="utf-8")
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
        "script_file": script_name,
        "audio_file": audio_name,
    }
    (notes_dir / metadata_name).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    feed_path = write_feed(args.channel)

    print(json.dumps({"episode": metadata, "feed": str(feed_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
