---
name: next-ai-drawio-diagrams
description: Create, edit, export, and review portable Draw.io diagrams with bundled Material icons and searchable native-shape catalogs. Use for architecture diagrams, flowcharts, system or process diagrams, research figures, and editable .drawio deliverables; use the optional Next AI Draw.io MCP only for live editor sessions.
---

# Next AI Draw.io Diagrams

Create readable diagrams whose `.drawio` source remains editable and portable. Prefer direct file generation for normal work; use a live MCP session only when the user asks to interact with Draw.io.

## Portability invariants

- Resolve this skill's directory from the loaded `SKILL.md`; never assume a username, home directory, operating system, drive letter, or working directory.
- Refer to bundled resources relative to the skill directory. Helper scripts locate their resources from `__file__` and can run from any current working directory.
- Never write a path inside the installed skill into a generated diagram. Use Draw.io native shape names or embed a bundled SVG as a data URI.
- Write user deliverables outside the installed skill. Do not modify the bundled catalogs or assets during an ordinary diagram task.
- Use uncompressed Draw.io XML by default so the source is inspectable and version-control friendly.

## Choose a workflow

1. **New diagram or material rebuild:** plan the layers, groups, nodes, and flows, then generate a new `.drawio` file. Full regeneration is safer than a large patch.
2. **Small edit to an existing file:** inspect the current file first and preserve unrelated content. Make only the requested local change.
3. **Live Draw.io interaction:** use MCP only when requested and only if its tools are available. Before starting, read [references/mcp-workflow.md](references/mcp-workflow.md).

For direct generation, start from [assets/templates/starter.drawio](assets/templates/starter.drawio) or create equivalent valid XML. The template is illustrative; replace its example content rather than presenting it as a finished result.

## Find and use icons

Read [references/shape-libraries/index.md](references/shape-libraries/index.md) to select a relevant catalog. Load only the catalog needed for the current diagram.

Search all packaged catalogs without assuming an install path:

```text
python "<skill-directory>/scripts/search_shapes.py" database --limit 20
python "<skill-directory>/scripts/search_shapes.py" pod --library kubernetes
```

Use a native Draw.io shape when the catalog gives an `mxgraph.*` style. Native shapes remain portable because the diagram stores the shape identifier, not a machine-local file.

For Material icons, prefer the 300 bundled SVGs in `assets/material-icons/`. Embed one into XML as a data URI:

```text
python "<skill-directory>/scripts/material_icon.py" analytics --data-uri
```

Place decorative icons at about 40 x 40 px with reduced opacity. Keep them subordinate to labels. The CDN pattern documented in `material_design.md` is an online fallback, not the portable default.

## Build the diagram

- Choose one reading direction, normally left-to-right or top-to-bottom.
- Use large containers only for meaningful grouping and keep child nodes clear of container title areas.
- Give text enough width to wrap naturally; set `whiteSpace=wrap` on text-bearing cells.
- Label every major inter-component arrow with short text and set `labelBackgroundColor=#ffffff`.
- Use dashed lines only for secondary, feedback, or result-returning flows.
- Keep at least 40 px between adjacent nodes so connectors and labels remain visible.
- Use restrained fills, consistent font sizes, and bold text only for titles or module names.
- Do not route edges through readable text.

## Validate and inspect

Validate every final `.drawio` file:

```text
python "<skill-directory>/scripts/validate_drawio.py" <diagram.drawio>
```

Repair malformed XML, duplicate IDs, missing references, missing geometry, or invalid coordinates before handoff. The validator accepts both uncompressed and standard compressed Draw.io pages.

Export to SVG or PNG and visually inspect the actual export. Check wrapping, overlaps, clipping, arrow visibility, label placement, spacing, and scaled-down readability. Prefer a white-background export unless the user requests transparency.

## Final handoff

Show the exported preview when the host supports it, link the editable `.drawio` file, and state what was validated and visually checked. Do not claim success from XML generation alone.
