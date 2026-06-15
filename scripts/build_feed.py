from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

from config import CHANNELS, channel_dir, channel_url


def xml(value: str) -> str:
    return escape(value or "", {'"': "&quot;"})


def load_episodes(channel: str) -> list[dict]:
    notes_dir = channel_dir(channel) / "notes"
    episodes = []
    for path in sorted(notes_dir.glob("*.json")):
        episodes.append(json.loads(path.read_text(encoding="utf-8")))
    episodes.sort(key=lambda item: item["pub_date"], reverse=True)
    return episodes


def build_feed(channel: str) -> str:
    meta = CHANNELS[channel]
    base_url = channel_url(channel)
    now = format_datetime(datetime.now(timezone.utc))
    items = []

    for episode in load_episodes(channel):
        audio_path = channel_dir(channel) / "episodes" / episode["audio_file"]
        audio_len = audio_path.stat().st_size if audio_path.exists() else 0
        pub_date = datetime.fromisoformat(episode["pub_date"])
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=timezone.utc)
        items.append(
            f"""    <item>
      <title>{xml(episode["title"])}</title>
      <description>{xml(episode.get("summary", ""))}</description>
      <pubDate>{format_datetime(pub_date)}</pubDate>
      <guid isPermaLink="false">{xml(episode["guid"])}</guid>
      <link>{xml(base_url + "/notes/" + episode["notes_file"])}</link>
      <enclosure url="{xml(base_url + "/episodes/" + episode["audio_file"])}" length="{audio_len}" type="audio/mpeg" />
    </item>"""
        )

    body = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{xml(meta["title"])}</title>
    <link>{xml(base_url + "/feed.xml")}</link>
    <description>{xml(meta["description"])}</description>
    <language>zh-cn</language>
    <lastBuildDate>{now}</lastBuildDate>
    <generator>AI Podcast scripts</generator>
{body}
  </channel>
</rss>
"""


def write_feed(channel: str) -> Path:
    output = channel_dir(channel) / "feed.xml"
    output.write_text(build_feed(channel), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build podcast RSS feed.")
    parser.add_argument("--channel", choices=sorted(CHANNELS), required=True)
    args = parser.parse_args()
    print(write_feed(args.channel))


if __name__ == "__main__":
    main()

