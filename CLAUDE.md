# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python MCP (Model Context Protocol) server that wraps the [Braiins Hashpower Spot Market API](https://hashpower.braiins.com/v1), exposing it as tools for Claude and other MCP clients. The entire server is implemented in a single file: [server.py](server.py).

## Setup & Running

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key (required for authenticated endpoints)
export BRAIINS_API_KEY=<your_key>

# Run the MCP server
venv/bin/python3 server.py
```

## Connecting to Claude Code (VS Code)

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "braiins-hashpower": {
      "command": "uvx",
      "args": ["braiins-hashpower-mcp"],
      "env": {
        "BRAIINS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Reload the VS Code window to pick up the server.

## Connecting to Claude Code (CLI)

```bash
claude mcp add braiins-hashpower \
  -e BRAIINS_API_KEY=your_api_key_here \
  -- uvx braiins-hashpower-mcp
```

## Architecture

**Single-file MCP server** using FastMCP from the `mcp` SDK.

```
Claude/MCP Client → FastMCP tool dispatch → _get/_post/_put/_delete helpers → httpx → Braiins API
```

Key elements in [server.py](server.py):
- `BASE_URL` — `https://hashpower.braiins.com/v1`
- `_headers()` — reads `BRAIINS_API_KEY` from env, returns `{"apikey": ...}` header dict
- `_require_api_key()` — raises a clear `ValueError` if `BRAIINS_API_KEY` is not set; called before every authenticated request
- `_handle_http_error()` — maps HTTP status codes (401, 403, 404, 429, 5xx) to descriptive error messages
- `_get/_post/_put/_delete` — HTTP helpers used by all tools; handle errors, timeouts, and network failures
- 19 `@mcp.tool()` functions, split into public (no auth) and authenticated sections
- `mcp.run()` at module bottom starts the server

**Authentication:** Kong key-auth via `apikey` header. The `auth` parameter on `_get()` controls whether the header is included — public endpoints pass `auth=False`, authenticated endpoints pass `auth=True`.

**Logging:** Structured via Python `logging`. Level is configurable via the `LOG_LEVEL` env var (default: `INFO`). Mutating operations (`create_bid`, `update_bid`, `cancel_bid`) log both intent and result.

## Adding a New Tool

1. Add a function decorated with `@mcp.tool()` in [server.py](server.py)
2. Call `_get(path, params={...}, auth=True/False)` and return the result
3. Include a docstring — FastMCP exposes it as the tool description to clients
4. Use `if param is not None:` (not `if param:`) when building optional query params

Refer to existing tools for the pattern; they are consistent throughout the file.

## Releases

Releases are fully automated via [python-semantic-release](https://python-semantic-release.readthedocs.io). Every push to `main` is evaluated — if it contains a releasable commit, the version is bumped, a GitHub release is created, and the package is published to PyPI automatically.

Commit message format:
- `fix: ...` → patch release (1.0.0 → 1.0.1)
- `feat: ...` → minor release (1.0.0 → 1.1.0)
- `feat!: ...` or `BREAKING CHANGE:` in body → major release (1.0.0 → 2.0.0)
- `chore:`, `docs:`, etc. → no release triggered
