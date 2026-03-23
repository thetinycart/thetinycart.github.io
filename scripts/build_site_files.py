#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(script_name: str) -> None:
    subprocess.run(["python3", str(SCRIPTS / script_name)], check=True)


def main() -> None:
    run("build_pin_images.py")
    run("build_pinterest_feed.py")
    run("build_sitemap.py")


if __name__ == "__main__":
    main()
