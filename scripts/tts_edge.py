from __future__ import annotations

import argparse
import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path

import edge_tts

from config import EDGE_TTS_PITCH, EDGE_TTS_RATE, EDGE_TTS_VOICE, EDGE_TTS_VOLUME
from tts_openai import split_text


async def synthesize_chunk(
    text: str,
    output_path: Path,
    *,
    voice: str,
    rate: str,
    pitch: str,
    volume: str,
) -> None:
    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    await communicate.save(str(output_path))


def merge_mp3_files(part_paths: list[Path], output_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        with output_path.open("wb") as merged:
            for part_path in part_paths:
                merged.write(part_path.read_bytes())
        return

    concat_file = output_path.with_suffix(".concat.txt")
    concat_file.write_text(
        "\n".join(f"file '{part_path}'" for part_path in part_paths),
        encoding="utf-8",
    )
    try:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(output_path),
            ],
            check=True,
        )
    finally:
        concat_file.unlink(missing_ok=True)


async def synthesize_async(
    text: str,
    output_path: Path,
    *,
    voice: str,
    rate: str,
    pitch: str,
    volume: str,
) -> None:
    chunks = split_text(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if len(chunks) == 1:
        await synthesize_chunk(
            chunks[0],
            output_path,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        part_paths: list[Path] = []
        for idx, chunk in enumerate(chunks, start=1):
            part_path = Path(tmpdir) / f"part-{idx:03d}.mp3"
            await synthesize_chunk(
                chunk,
                part_path,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume=volume,
            )
            part_paths.append(part_path)
        merge_mp3_files(part_paths, output_path)


def synthesize(
    text: str,
    output_path: Path,
    *,
    voice: str,
    rate: str,
    pitch: str,
    volume: str,
) -> None:
    asyncio.run(
        synthesize_async(
            text,
            output_path,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MP3 speech from text using Edge TTS.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--voice", default=EDGE_TTS_VOICE)
    parser.add_argument("--rate", default=EDGE_TTS_RATE)
    parser.add_argument("--pitch", default=EDGE_TTS_PITCH)
    parser.add_argument("--volume", default=EDGE_TTS_VOLUME)
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Input text is empty.")
    synthesize(
        text,
        args.output,
        voice=args.voice,
        rate=args.rate,
        pitch=args.pitch,
        volume=args.volume,
    )
    print(args.output)


if __name__ == "__main__":
    main()
