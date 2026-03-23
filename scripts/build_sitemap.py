#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


SITE_URL = "https://tycheventuresllc.com"
ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = ROOT / "sitemap.xml"
ROBOTS_PATH = ROOT / "robots.txt"


def iter_site_files() -> list[Path]:
    top_level = sorted(ROOT.glob("*.html"))
    nested_pages = []
    for content_dir in ["printables", "cartkind", "homekeeper", "kids-meal-planner", "little-routines"]:
        for page in sorted((ROOT / content_dir).glob("*.html")):
            if content_dir != "printables" and page.name == "index.html":
                continue
            nested_pages.append(page)
    return top_level + nested_pages


def to_url_path(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel == Path("index.html"):
        return "/"
    if rel.name == "index.html":
        return f"/{rel.parent.as_posix()}/"
    return f"/{rel.as_posix()}"


def priority_for(path: str) -> str:
    if path == "/":
        return "1.0"
    if path == "/blog.html":
        return "0.9"
    if path == "/printables/":
        return "0.9"
    if path.startswith("/printables/"):
        return "0.8"
    if path.startswith("/best-") or path in {
        "/easy-lunch-ideas-for-picky-eaters.html",
        "/how-to-meal-plan-for-kids.html",
    }:
        return "0.9"
    if path.endswith(".html") and path.count("/") == 1:
        return "0.8"
    return "0.5"


def changefreq_for(path: str) -> str:
    if path == "/" or path == "/blog.html":
        return "weekly"
    if path == "/printables/":
        return "weekly"
    if path.startswith("/printables/"):
        return "monthly"
    if path.startswith("/best-") or path in {
        "/easy-lunch-ideas-for-picky-eaters.html",
        "/how-to-meal-plan-for-kids.html",
    }:
        return "monthly"
    return "yearly"


def build_sitemap() -> str:
    lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
    ]

    for page in iter_site_files():
        url_path = to_url_path(page)
        lastmod = datetime.fromtimestamp(page.stat().st_mtime, tz=timezone.utc).date()
        lines.extend(
            [
                "  <url>",
                f"    <loc>{escape(f'{SITE_URL}{url_path}')}</loc>",
                f"    <lastmod>{lastmod.isoformat()}</lastmod>",
                f"    <changefreq>{changefreq_for(url_path)}</changefreq>",
                f"    <priority>{priority_for(url_path)}</priority>",
                "  </url>",
            ]
        )

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots() -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "",
            f"Sitemap: {SITE_URL}/sitemap.xml",
        ]
    ) + "\n"


def main() -> None:
    SITEMAP_PATH.write_text(build_sitemap())
    ROBOTS_PATH.write_text(build_robots())


if __name__ == "__main__":
    main()
