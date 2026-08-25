# Next AI Draw.io Diagrams skill

A portable Codex skill for creating, editing, validating, and visually reviewing editable Draw.io diagrams. It bundles searchable native-shape catalogs, 300 offline Material SVG icons, an uncompressed Draw.io starter template, and dependency-free Python helpers.

## Install

Clone this repository, then place the repository folder in your Codex skills directory under the name `next-ai-drawio-diagrams`. If `CODEX_HOME` is configured, the destination is `$CODEX_HOME/skills/next-ai-drawio-diagrams`; otherwise use the skills directory documented by your Codex host.

Restart or reload the host after installation, then invoke `$next-ai-drawio-diagrams` or make a Draw.io diagram request that matches the skill description.

## Requirements

- Python 3 for catalog search, icon embedding, validation, and portability checks.
- diagrams.net or Draw.io Desktop to open and export `.drawio` files.
- Node.js and `npx` only for the optional live MCP workflow.

The core direct-file workflow does not require MCP or network access. The optional MCP package is pinned in [references/mcp-workflow.md](references/mcp-workflow.md).

## Verify

Run from any current directory, replacing `<skill-directory>` with the cloned or installed skill path:

```text
python "<skill-directory>/scripts/check_portability.py"
python "<skill-directory>/scripts/validate_drawio.py" "<skill-directory>/assets/templates/starter.drawio"
python "<skill-directory>/scripts/search_shapes.py" database --limit 10
python "<skill-directory>/scripts/material_icon.py" analytics --data-uri
```

On systems where the Python 3 launcher is named `python3` or `py`, use that command instead.

## License

Apache License 2.0. See [NOTICE](NOTICE) and [references/attribution.md](references/attribution.md) for third-party attribution. This is an unofficial community skill.

