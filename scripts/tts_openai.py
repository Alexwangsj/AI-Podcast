from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from config import OPENAI_TTS_MODEL, OPENAI_TTS_VOICE


def split_text(text: str, max_chars: int = 3500) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs or [text.strip()]:
        extra = len(paragraph) + 2
        if current and current_len + extra > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        if len(paragraph) > max_chars:
            for i in range(0, len(paragraph), max_chars):
                part = paragraph[i : i + max_chars]
                if current:
                    chunks.append("\n\n".join(current))
                    current = []
                    current_len = 0
                chunks.append(part)
        else:
            current.append(paragraph)
            current_len += extra

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def synthesize_chunk(text: str, output_path: Path, *, model: str, voice: str) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and fill it in.")

    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "instructions": "Speak natural Mandarin Chinese like a calm senior technology analyst. Keep pacing suitable for a 20-minute briefing.",
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            output_path.write_bytes(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI TTS failed: HTTP {error.code}: {detail}") from error


def synthesize(text: str, output_path: Path, *, model: str, voice: str) -> None:
    chunks = split_text(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if len(chunks) == 1:
        synthesize_chunk(chunks[0], output_path, model=model, voice=voice)
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        part_paths = []
        for idx, chunk in enumerate(chunks, start=1):
            part_path = Path(tmpdir) / f"part-{idx:03d}.mp3"
            synthesize_chunk(chunk, part_path, model=model, voice=voice)
            part_paths.append(part_path)
        with output_path.open("wb") as merged:
            for part_path in part_paths:
                merged.write(part_path.read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MP3 speech from text using OpenAI TTS.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", default=OPENAI_TTS_MODEL)
    parser.add_argument("--voice", default=OPENAI_TTS_VOICE)
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Input text is empty.")
    synthesize(text, args.output, model=args.model, voice=args.voice)
    print(args.output)


if __name__ == "__main__":
    main()

