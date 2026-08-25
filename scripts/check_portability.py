#!/usr/bin/env python3
"""Check this skill for machine-specific paths and broken local Markdown links."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

SKILL_DIR = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".drawio", ".svg", ".txt"}
PATH_PATTERNS = {
    "Windows drive path": re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/]"),
    "macOS user path": re.compile(r"/Users/[^/\s]+/"),
    "Linux user path": re.compile(r"/home/[^/\s]+/"),
    "file URI": re.compile(r"(?i)file://"),
}
MARKDOWN_LINK = re.compile(r"\]\(([^)]+)\)")


def text_files() -> list[Path]:
    return [
        path
        for path in SKILL_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
    ]


def main() -> int:
    issues: list[str] = []
    for path in text_files():
        relative = path.relative_to(SKILL_DIR)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if path.resolve() != Path(__file__).resolve():
                for label, pattern in PATH_PATTERNS.items():
                    if pattern.search(line):
                        issues.append(f"{relative}:{line_number}: {label}")
            if path.suffix.lower() != ".md":
                continue
            for match in MARKDOWN_LINK.finditer(line):
                target = match.group(1).strip().strip("<>").split("#", 1)[0]
                if not target or re.match(r"(?i)^(https?://|mailto:)", target):
                    continue
                resolved = (path.parent / unquote(target)).resolve()
                if not resolved.exists():
                    issues.append(f"{relative}:{line_number}: broken local link {target}")

    catalog = SKILL_DIR / "references" / "shape-libraries" / "material_design.md"
    icons = SKILL_DIR / "assets" / "material-icons"
    if catalog.is_file() and icons.is_dir():
        names = {
            match.group(1)
            for line in catalog.read_text(encoding="utf-8").splitlines()
            if (match := re.fullmatch(r"- `([^`]+)`", line.strip()))
        }
        files = {path.stem for path in icons.glob("*.svg")}
        for name in sorted(names - files):
            issues.append(f"assets/material-icons: missing {name}.svg")
        for name in sorted(files - names):
            issues.append(f"assets/material-icons: unindexed {name}.svg")

    if issues:
        print("PORTABILITY CHECK FAILED")
        print("\n".join(issues))
        return 1
    print("PORTABILITY CHECK PASSED")
    print("No machine-specific paths or broken local links found.")
    print("Material icon catalog and bundled SVG set match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
