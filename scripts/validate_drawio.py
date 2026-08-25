#!/usr/bin/env python3
"""Validate structural invariants in compressed or uncompressed Draw.io files."""

from __future__ import annotations

import argparse
import base64
import json
import math
import urllib.parse
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET


def decode_diagram(diagram: ET.Element) -> ET.Element:
    children = list(diagram)
    if children:
        if children[0].tag != "mxGraphModel":
            raise ValueError(f"unexpected diagram child: {children[0].tag}")
        return children[0]

    payload = (diagram.text or "").strip()
    if not payload:
        raise ValueError("diagram page has no XML payload")
    try:
        packed = base64.b64decode(payload)
        encoded = zlib.decompress(packed, -15).decode("utf-8")
        xml = urllib.parse.unquote(encoded)
        return ET.fromstring(xml)
    except Exception as exc:
        raise ValueError(f"cannot decode compressed page: {exc}") from exc


def graph_models(root: ET.Element) -> list[tuple[str, ET.Element]]:
    if root.tag == "mxGraphModel":
        return [("page-1", root)]
    if root.tag != "mxfile":
        raise ValueError(f"root must be mxfile or mxGraphModel, found {root.tag}")

    pages: list[tuple[str, ET.Element]] = []
    for index, diagram in enumerate(root.findall("diagram"), start=1):
        name = diagram.get("name") or f"page-{index}"
        pages.append((name, decode_diagram(diagram)))
    if not pages:
        raise ValueError("mxfile contains no diagram pages")
    return pages


def validate_model(page: str, model: ET.Element) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    graph_root = model.find("root")
    if graph_root is None:
        return [f"{page}: mxGraphModel has no root"], warnings

    cells = graph_root.findall("mxCell")
    ids: dict[str, ET.Element] = {}
    for cell in cells:
        cell_id = cell.get("id")
        if not cell_id:
            errors.append(f"{page}: mxCell without id")
            continue
        if cell_id in ids:
            errors.append(f"{page}: duplicate cell id {cell_id}")
        ids[cell_id] = cell

    for required in ("0", "1"):
        if required not in ids:
            errors.append(f"{page}: missing required cell id {required}")

    for cell_id, cell in ids.items():
        for attr in ("parent", "source", "target"):
            reference = cell.get(attr)
            if reference and reference not in ids:
                errors.append(f"{page}: cell {cell_id} has missing {attr} reference {reference}")

        is_vertex = cell.get("vertex") == "1"
        is_edge = cell.get("edge") == "1"
        geometry = cell.find("mxGeometry")
        if (is_vertex or is_edge) and geometry is None:
            errors.append(f"{page}: cell {cell_id} is missing mxGeometry")
            continue
        if geometry is None:
            continue
        for attr in ("x", "y", "width", "height"):
            value = geometry.get(attr)
            if value is None:
                continue
            try:
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError
            except ValueError:
                errors.append(f"{page}: cell {cell_id} has invalid {attr}={value!r}")
        if is_vertex:
            for attr in ("width", "height"):
                value = geometry.get(attr)
                if value is None:
                    warnings.append(f"{page}: vertex {cell_id} has no {attr}")
                else:
                    try:
                        if float(value) < 0:
                            errors.append(f"{page}: vertex {cell_id} has negative {attr}")
                    except ValueError:
                        pass  # Already reported by the numeric-coordinate check above.
        if is_edge and not (cell.get("source") or cell.get("target")):
            warnings.append(f"{page}: edge {cell_id} has neither source nor target")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("drawio", type=Path, help="Path to a .drawio or XML file")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    try:
        root = ET.parse(args.drawio).getroot()
        pages = graph_models(root)
        errors: list[str] = []
        warnings: list[str] = []
        for page, model in pages:
            page_errors, page_warnings = validate_model(page, model)
            errors.extend(page_errors)
            warnings.extend(page_warnings)
    except (OSError, ET.ParseError, ValueError) as exc:
        pages = []
        errors = [str(exc)]
        warnings = []

    report = {
        "file": str(args.drawio),
        "pages": len(pages),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "VALID" if report["valid"] else "INVALID"
        print(f"{status}: {args.drawio} ({report['pages']} page(s))")
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
