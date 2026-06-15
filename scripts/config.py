from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

DEFAULT_PRIVATE_PATH = "radio-rJ5DwUcy9jXQtZ94ek9A1NZs"
DEFAULT_BASE_URL = "https://alexwangsj.github.io/AI-Podcast"


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or (ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv()

PODCAST_BASE_URL = os.environ.get("PODCAST_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
PODCAST_PRIVATE_PATH = os.environ.get("PODCAST_PRIVATE_PATH", DEFAULT_PRIVATE_PATH).strip("/")
OPENAI_TTS_MODEL = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = os.environ.get("OPENAI_TTS_VOICE", "coral")

CHANNELS = {
    "ai-daily": {
        "title": "AI Podcast - Daily",
        "description": "A 20-minute Chinese AI news briefing.",
        "author": "Niello",
    },
    "research": {
        "title": "AI Podcast - Research",
        "description": "A 20-minute Chinese research briefing on demand.",
        "author": "Niello",
    },
}


def channel_dir(channel: str) -> Path:
    if channel not in CHANNELS:
        raise ValueError(f"Unknown channel: {channel}")
    return DOCS_DIR / PODCAST_PRIVATE_PATH / channel


def channel_url(channel: str) -> str:
    if channel not in CHANNELS:
        raise ValueError(f"Unknown channel: {channel}")
    return f"{PODCAST_BASE_URL}/{PODCAST_PRIVATE_PATH}/{channel}"

