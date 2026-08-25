#!/usr/bin/env python3
"""Search bundled Draw.io shape and Material icon catalogs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CATALOG_DIR = Path(__file__).resolve().parents[1] / "references" / "shape-libraries"
ITEM_RE = re.compile(r"`([^`]+)`")


def parse_catalog(path: Path) -> list[dict[str, str]]:
    library = path.stem
    section = ""
    locator = ""
    results: list[dict[str, str]] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("### "):
            section = re.sub(r"\s*\(\d+\)\s*$", "", line[4:]).strip()
        elif line.startswith("## ") and line not in {"## Usage", "## Shapes", "## Categories"}:
            section = re.sub(r"\s*\(\d+\)\s*$", "", line[3:]).strip()
        elif line.startswith(("**Prefix:**", "**Path:**", "**URL Pattern:**")):
            values = ITEM_RE.findall(line)
            if values:
                locator = ", ".join(values)

        if not line.startswith("-"):
            continue
        for item in ITEM_RE.findall(line):
            results.append(
                {
                    "library": library,
                    "item": item,
                    "section": section,
                    "locator": locator,
                    "source": path.name,
                }
            )
    return results


def load_entries(library: str | None) -> list[dict[str, str]]:
    paths = sorted(CATALOG_DIR.glob("*.md"))
    paths = [path for path in paths if path.name != "index.md"]
    if library:
        paths = [path for path in paths if path.stem.casefold() == library.casefold()]
        if not paths:
            choices = ", ".join(
                path.stem
                for path in sorted(CATALOG_DIR.glob("*.md"))
                if path.name != "index.md"
            )
            raise SystemExit(f"Unknown library: {library}. Available: {choices}")
    return [entry for path in paths for entry in parse_catalog(path)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="", help="Case-insensitive text to match")
    parser.add_argument("--library", help="Restrict search to one catalog filename without .md")
    parser.add_argument("--limit", type=int, default=50, help="Maximum results (default: 50)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    entries = load_entries(args.library)
    needle = args.query.casefold()
    if needle:
        entries = [
            entry
            for entry in entries
            if needle in " ".join(entry.values()).casefold()
        ]
    entries = entries[: args.limit]

    if args.json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
    elif not entries:
        print("No matching catalog entries.")
    else:
        for entry in entries:
            context = f" [{entry['section']}]" if entry["section"] else ""
            locator = f" | {entry['locator']}" if entry["locator"] else ""
            print(f"{entry['library']}:{entry['item']}{context}{locator}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

