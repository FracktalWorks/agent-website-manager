# Agent Data — Index

This folder contains permanent reference data used by the agent at runtime.
Every asset must be listed here.

| Path | Purpose | Usage |
|------|---------|-------|
| `templates/` | Document templates | Referenced by document generation scripts |
| `images/` | Product images and renders | Embedded in outputs |
| `specs/` | Technical specification PDFs | Parsed by research skills |

## Adding Assets

1. Place the file in the appropriate subfolder
2. Add an entry to this index with path, purpose, and usage notes
3. Commit the asset to git

## Rules

- All assets are **read-only** at runtime — never modify them programmatically
- Do NOT place user-provided files here — use `inputs/` instead
- Reference via `AGENT_DIR / "agent-data" / ...` in scripts
