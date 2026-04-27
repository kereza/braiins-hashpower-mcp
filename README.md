# Braiins Hashpower MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that wraps the [Braiins Hashpower Spot Market API](https://hashpower.braiins.com), exposing it as tools for Claude and other MCP clients.

## Features

- Query live market data: stats, orderbook, recent trades, OHLCV bars
- Manage bids: create, update, cancel, and inspect active or historical bids
- View account balance and transaction history
- All price values use the API's native unit: **sat/EH/day**

## Prerequisites

- A Braiins Hashpower API key ([get one at market.braiins.com](https://market.braiins.com))
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — provides the `uvx` command used below

## Installation

No manual installation needed. `uvx` fetches and runs the package from PyPI automatically on first use.

If you prefer pip:

```bash
pip install braiins-hashpower-mcp
```

## Connecting to Claude Code (VS Code)

Add to your `.mcp.json` (using `uvx`):

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

Or if using pip, replace `"command": "uvx"` and `"args": ["braiins-hashpower-mcp"]` with `"command": "braiins-hashpower-mcp"` and `"args": []`.

Then reload the VS Code window (`Cmd+Shift+P` → **Developer: Reload Window**).

## Connecting to Claude Code (CLI)

```bash
claude mcp add braiins-hashpower \
  -e BRAIINS_API_KEY=your_api_key_here \
  -- uvx braiins-hashpower-mcp
```

To remove it later:

```bash
claude mcp remove braiins-hashpower
```

## Available Tools

### Public (no API key required)

| Tool | Description |
|------|-------------|
| `get_market_stats` | Best bid/ask prices, 24h volume, matched/available hashrate |
| `get_orderbook` | Current order book snapshot (bids and asks) |
| `get_recent_trades` | Most recently executed trades |
| `get_market_bars` | OHLCV candlestick bars (specify period and optional limit) |

### Authenticated (require API key)

| Tool | Description |
|------|-------------|
| `get_market_settings` | Trading rules: price/speed limits, tick size, hr_unit |
| `get_fee_structure` | Spot market fee structure |
| `get_account_balance` | BTC balances across subaccounts |
| `get_transactions` | Account transactions (deposits, withdrawals, trades) |
| `get_onchain_transactions` | On-chain Bitcoin transactions |
| `get_current_bids` | All currently active bids |
| `get_bids` | Historical and active bids with optional filters |
| `get_bid_detail` | Full details for a specific bid |
| `get_bid_speed_history` | Hashrate time series for a bid |
| `get_bid_delivery_history` | Share delivery history for a bid |
| `create_bid` | Place a new bid |
| `update_bid` | Modify price, amount, or speed of an active bid |
| `cancel_bid` | Cancel an active bid |

## Units

| Field | Unit |
|-------|------|
| Price (`price_sat`) | sat/EH/day |
| Speed (`speed_limit_ph`) | PH/s |
| Amount (`amount_sat`) | satoshis |

> **Note:** The Braiins web UI displays prices in sat/PH/day. To convert: multiply UI price × 1,000 to get the API value (e.g. 48,000 sat/PH/day → 48,000,000 sat/EH/day).

## License

MIT
