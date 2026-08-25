#!/usr/bin/env python3
"""Locate or encode a bundled Material icon without machine-specific paths."""

from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path

ICON_DIR = Path(__file__).resolve().parents[1] / "assets" / "material-icons"
SAFE_NAME = re.compile(r"^[a-z0-9_]+$")


def icon_path(name: str) -> Path:
    if not SAFE_NAME.fullmatch(name):
        raise SystemExit("Icon names may contain only lowercase letters, digits, and underscores.")
    path = ICON_DIR / f"{name}.svg"
    if not path.is_file():
        suggestions = sorted(p.stem for p in ICON_DIR.glob(f"*{name}*.svg"))[:12]
        hint = f" Suggestions: {', '.join(suggestions)}" if suggestions else ""
        raise SystemExit(f"Unknown bundled icon: {name}.{hint}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", nargs="?", help="Material icon name without .svg")
    parser.add_argument("--data-uri", action="store_true", help="Print an embeddable base64 data URI")
    parser.add_argument("--svg", action="store_true", help="Print raw SVG text")
    parser.add_argument("--list", metavar="QUERY", help="List bundled icon names containing QUERY")
    args = parser.parse_args()

    if args.list is not None:
        needle = args.list.casefold()
        for path in sorted(ICON_DIR.glob("*.svg")):
            if needle in path.stem.casefold():
                print(path.stem)
        return 0
    if not args.name:
        parser.error("provide an icon name or --list QUERY")

    path = icon_path(args.name)
    data = path.read_bytes()
    if args.svg:
        print(data.decode("utf-8"))
    elif args.data_uri:
        encoded = base64.b64encode(data).decode("ascii")
        print(f"data:image/svg+xml;base64,{encoded}")
    else:
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
