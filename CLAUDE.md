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

There are no tests, no build step, and no linting configuration.

## Connecting to Claude Code (VS Code)

Copy `.mcp.json.example` to `.mcp.json` and fill in your absolute paths and API key:

```bash
cp .mcp.json.example .mcp.json
```

Then edit `.mcp.json` with the correct paths and your `BRAIINS_API_KEY`. Reload the VS Code window to pick up the server.

## Connecting to Claude Code (CLI)

```bashge
claude mcp add braiins-hashpower \
  -e BRAIINS_API_KEY=your_key \
  -- /absolute/path/to/venv/bin/python3 \
     /absolute/path/to/server.py
```

## Architecture

**Single-file MCP server** using FastMCP from the `mcp` SDK.

```
Claude/MCP Client → FastMCP tool dispatch → _get() helper → httpx → Braiins API
```

Key elements in [server.py](server.py):
- `BASE_URL` — `https://hashpower.braiins.com/v1`
- `_headers()` — reads `BRAIINS_API_KEY` from env, returns `{"apikey": ...}` header dict
- `_get(path, params, auth)` — single HTTP GET helper used by all tools; calls `.raise_for_status()` and returns parsed JSON
- 19 `@mcp.tool()` functions, split into public (no auth) and authenticated sections
- `mcp.run()` at module bottom starts the server

**Authentication:** Kong key-auth via `apikey` header. The `auth` parameter on `_get()` controls whether the header is included — public endpoints pass `auth=False`, authenticated endpoints pass `auth=True`.

## Adding a New Tool

1. Add a function decorated with `@mcp.tool()` in [server.py](server.py)
2. Call `_get(path, params={...}, auth=True/False)` and return the result
3. Include a docstring — FastMCP exposes it as the tool description to clients

Refer to existing tools for the pattern; they are consistent throughout the file.
