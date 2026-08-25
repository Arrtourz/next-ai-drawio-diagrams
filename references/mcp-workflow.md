# Optional Next AI Draw.io MCP workflow

Use MCP only for a user-requested live Draw.io session, in-app inspection, or preservation of manual editor changes. Direct `.drawio` generation does not require MCP.

## Portable server configuration

The tested server package is pinned to `@next-ai-drawio/mcp-server@0.2.3` and requires Node.js with `npx` available on `PATH`.

```json
{
  "mcpServers": {
    "drawio": {
      "command": "npx",
      "args": ["-y", "@next-ai-drawio/mcp-server@0.2.3"]
    }
  }
}
```

Add this configuration through the host application's supported MCP settings. Do not copy a machine-specific Node path into the skill or project. The package is not auto-started by this skill because launching it can open Draw.io and may download npm dependencies.

## Session rules

- New live diagram: `start_session` -> `create_new_diagram` -> `export_diagram`.
- Existing live diagram: `start_session` -> `load_diagram` -> `get_diagram` -> `edit_diagram` -> `export_diagram`.
- After loading an existing diagram, call `get_diagram` before the first edit.
- Preserve manual changes and existing pages. Use page-specific operations for adding, renaming, or deleting pages.
- Use `edit_diagram` only for a genuinely local change while the original session remains alive. Regenerate for bulk or layout-wide changes.
- If the MCP tools are unavailable, continue with direct file generation and the bundled validator; do not block an ordinary diagram request.

