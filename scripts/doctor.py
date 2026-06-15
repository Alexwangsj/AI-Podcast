from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from config import (
    EDGE_TTS_RATE,
    EDGE_TTS_VOICE,
    OPENAI_TTS_MODEL,
    PODCAST_BASE_URL,
    PODCAST_PRIVATE_PATH,
    ROOT,
    TTS_BACKEND,
)


PLACEHOLDER_PATH = "replace_with_private_random_path"
PLACEHOLDER_BASE_URL = "https://example.github.io/example-repo"


def status(ok: bool, label: str, detail: str = "") -> bool:
    prefix = "OK" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"[{prefix}] {label}{suffix}")
    return ok


def check_python_package(package: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-c", f"import {package}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def main() -> int:
    checks: list[bool] = []
    env_path = ROOT / ".env"

    checks.append(status(env_path.exists(), ".env exists", str(env_path)))
    checks.append(
        status(
            PODCAST_BASE_URL != PLACEHOLDER_BASE_URL,
            "PODCAST_BASE_URL configured",
            "value is still the public placeholder" if PODCAST_BASE_URL == PLACEHOLDER_BASE_URL else "",
        )
    )
    checks.append(
        status(
            PODCAST_PRIVATE_PATH != PLACEHOLDER_PATH,
            "PODCAST_PRIVATE_PATH configured",
            "value is still the public placeholder" if PODCAST_PRIVATE_PATH == PLACEHOLDER_PATH else "",
        )
    )
    checks.append(status(TTS_BACKEND in {"edge", "openai"}, "TTS_BACKEND valid", TTS_BACKEND))

    if TTS_BACKEND == "edge":
        checks.append(status(check_python_package("edge_tts"), "edge-tts package installed"))
        checks.append(status(bool(EDGE_TTS_VOICE), "EDGE_TTS_VOICE configured", EDGE_TTS_VOICE))
        checks.append(status(bool(EDGE_TTS_RATE), "EDGE_TTS_RATE configured", EDGE_TTS_RATE))
        checks.append(status(shutil.which("ffmpeg") is not None, "ffmpeg available", shutil.which("ffmpeg") or ""))
    elif TTS_BACKEND == "openai":
        checks.append(status(bool(os.environ.get("OPENAI_API_KEY")), "OPENAI_API_KEY configured"))
        checks.append(status(bool(OPENAI_TTS_MODEL), "OPENAI_TTS_MODEL configured", OPENAI_TTS_MODEL))

    for channel in ("ai-daily", "research"):
        feed_paths = list((ROOT / "docs").glob(f"*/{channel}/feed.xml"))
        checks.append(status(bool(feed_paths), f"{channel} feed exists", str(feed_paths[0]) if feed_paths else ""))

    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
