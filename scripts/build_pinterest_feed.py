#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


SITE_URL = "https://tycheventuresllc.com"
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "pinterest_backlog.json"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "feed.xml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Pinterest-friendly RSS feed from the Tiny Cart backlog."
    )
    parser.add_argument(
        "--today",
        default=date.today().isoformat(),
        help="ISO date used to decide which backlog items are included (default: today).",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Path to write the generated RSS feed.",
    )
    return parser.parse_args()


def load_posts() -> list[dict[str, Any]]:
    with DATA_PATH.open() as handle:
        posts = json.load(handle)
    posts.sort(key=lambda post: post["release_date"])
    return posts


def build_feed(posts: list[dict[str, Any]], today: date) -> str:
    eligible_posts = [
        post for post in posts if date.fromisoformat(post["release_date"]) <= today
    ]

    now = datetime.now(timezone.utc)
    item_lines: list[str] = []
    for post in eligible_posts:
        release_dt = datetime.combine(
            date.fromisoformat(post["release_date"]),
            time(15, 0, tzinfo=timezone.utc),
        )
        absolute_link = f"{SITE_URL}{post['path']}"
        absolute_image = f"{SITE_URL}{post['image']}"
        item_lines.extend(
            [
                "    <item>",
                f"      <title>{escape(post['title'])}</title>",
                f"      <link>{absolute_link}</link>",
                f"      <guid isPermaLink=\"true\">{absolute_link}</guid>",
                f"      <pubDate>{format_datetime(release_dt)}</pubDate>",
                f"      <description>{escape(post['description'])}</description>",
                f"      <category>{escape(post['board_hint'])}</category>",
                f"      <enclosure url=\"{absolute_image}\" type=\"image/png\" />",
                f"      <media:content url=\"{absolute_image}\" medium=\"image\" />",
                "    </item>",
            ]
        )

    lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<rss version=\"2.0\" xmlns:media=\"http://search.yahoo.com/mrss/\">",
        "  <channel>",
        "    <title>The Tiny Cart Pinterest Feed</title>",
        f"    <link>{SITE_URL}/blog.html</link>",
        "    <description>Backlog and new-post feed for The Tiny Cart Pinterest auto-publishing.</description>",
        "    <language>en-us</language>",
        f"    <lastBuildDate>{format_datetime(now)}</lastBuildDate>",
        "    <generator>The Tiny Cart feed builder</generator>",
    ]
    lines.extend(item_lines)
    lines.extend(["  </channel>", "</rss>"])
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    today = date.fromisoformat(args.today)
    posts = load_posts()
    output_path.write_text(build_feed(posts, today))


if __name__ == "__main__":
    main()
