#!/usr/bin/env python3
"""
Braiins Hashpower MCP Server

Wraps the Braiins Hashpower Spot Market API.
Base URL: https://hashpower.braiins.com/v1
Auth: set BRAIINS_API_KEY env var (apikey header, Kong key-auth)
"""

import logging
import os
import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "https://hashpower.braiins.com/v1"

mcp = FastMCP("braiins-hashpower")


def _headers() -> dict:
    key = os.environ.get("BRAIINS_API_KEY", "")
    return {"apikey": key} if key else {}


def _require_api_key() -> None:
    if not os.environ.get("BRAIINS_API_KEY"):
        raise ValueError("BRAIINS_API_KEY environment variable is not set")


def _handle_http_error(exc: httpx.HTTPStatusError) -> None:
    status = exc.response.status_code
    if status == 401:
        raise ValueError("Authentication failed — check your BRAIINS_API_KEY") from exc
    if status == 403:
        raise ValueError("Access forbidden — your API key lacks permission for this endpoint") from exc
    if status == 404:
        raise ValueError(f"Resource not found: {exc.request.url}") from exc
    if status == 429:
        raise ValueError("Rate limit exceeded — slow down requests") from exc
    if status >= 500:
        raise ValueError(f"Braiins API server error ({status}) — try again later") from exc
    raise ValueError(f"API request failed with status {status}: {exc.response.text}") from exc


def _get(path: str, params: dict = None, auth: bool = False) -> dict:
    if auth:
        _require_api_key()
    headers = _headers() if auth else {}
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{BASE_URL}{path}", headers=headers, params=params or {})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        _handle_http_error(exc)
    except httpx.TimeoutException as exc:
        raise ValueError("Request timed out — the Braiins API did not respond in time") from exc
    except httpx.RequestError as exc:
        raise ValueError(f"Network error reaching Braiins API: {exc}") from exc


def _post(path: str, body: dict = None) -> dict:
    _require_api_key()
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(f"{BASE_URL}{path}", headers=_headers(), json=body or {})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        _handle_http_error(exc)
    except httpx.TimeoutException as exc:
        raise ValueError("Request timed out — the Braiins API did not respond in time") from exc
    except httpx.RequestError as exc:
        raise ValueError(f"Network error reaching Braiins API: {exc}") from exc


def _delete(path: str) -> dict:
    _require_api_key()
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.delete(f"{BASE_URL}{path}", headers=_headers())
            resp.raise_for_status()
            return resp.json() if resp.content else {}
    except httpx.HTTPStatusError as exc:
        _handle_http_error(exc)
    except httpx.TimeoutException as exc:
        raise ValueError("Request timed out — the Braiins API did not respond in time") from exc
    except httpx.RequestError as exc:
        raise ValueError(f"Network error reaching Braiins API: {exc}") from exc


def _put(path: str, body: dict = None) -> dict:
    _require_api_key()
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.put(f"{BASE_URL}{path}", headers=_headers(), json=body or {})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        _handle_http_error(exc)
    except httpx.TimeoutException as exc:
        raise ValueError("Request timed out — the Braiins API did not respond in time") from exc
    except httpx.RequestError as exc:
        raise ValueError(f"Network error reaching Braiins API: {exc}") from exc


# ---------------------------------------------------------------------------
# Public endpoints (no API key required)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_market_stats() -> dict:
    """Get current spot market statistics: best bid/ask prices, 24h volume,
    matched and available hashrate, and market status."""
    return _get("/spot/stats")


@mcp.tool()
def get_orderbook() -> dict:
    """Get the current spot market order book snapshot (bids and asks)."""
    return _get("/spot/orderbook")


@mcp.tool()
def get_recent_trades() -> dict:
    """Get the most recent trades executed on the spot market."""
    return _get("/spot/trades")


@mcp.tool()
def get_market_bars(aggregation_period: str, limit: int = None) -> dict:
    """Get OHLCV (candlestick) bars for the spot market.

    Args:
        aggregation_period: One of PERIOD_1_MINUTE, PERIOD_5_MINUTES,
            PERIOD_15_MINUTES, PERIOD_1_HOUR, PERIOD_1_DAY.
        limit: Maximum number of bars to return (1–1000).
    """
    params = {"aggregation_period": aggregation_period}
    if limit is not None:
        params["limit"] = limit
    return _get("/spot/bars", params=params)


# ---------------------------------------------------------------------------
# Authenticated endpoints (require BRAIINS_API_KEY)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_market_settings() -> dict:
    """Get market settings and trading rules: price/amount limits, tick size,
    grace periods, hr_unit, etc. Requires API key."""
    return _get("/spot/settings", auth=True)


@mcp.tool()
def get_fee_structure() -> dict:
    """Get the spot market fee structure. Requires API key."""
    return _get("/spot/fee", auth=True)


@mcp.tool()
def get_account_balance() -> dict:
    """Get BTC balances for all subaccounts: total, available, blocked,
    lifetime deposits/withdrawals, and spot revenue. Requires API key."""
    return _get("/account/balance", auth=True)


@mcp.tool()
def get_transactions(limit: int = None, offset: int = None) -> dict:
    """List account transactions (deposits, withdrawals, trades).
    Requires API key.

    Args:
        limit: Number of results to return.
        offset: Pagination offset.
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return _get("/account/transaction", params=params, auth=True)


@mcp.tool()
def get_onchain_transactions(limit: int = None, offset: int = None) -> dict:
    """List on-chain Bitcoin transactions for the account. Requires API key.

    Args:
        limit: Number of results to return.
        offset: Pagination offset.
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return _get("/account/transaction/on-chain", params=params, auth=True)


@mcp.tool()
def get_current_bids() -> dict:
    """List all currently active (open) bids for the account. Requires API key."""
    return _get("/spot/bid/current", auth=True)


@mcp.tool()
def get_bids(
    limit: int = None,
    offset: int = None,
    reverse: bool = None,
    created_after: str = None,
    created_before: str = None,
    order_id: str = None,
    bid_status: str = None,
    exclude_active: bool = None,
    upstream_url: str = None,
    upstream_identity: str = None,
) -> dict:
    """List historical and active bids with optional filters. Requires API key.

    Args:
        limit: Number of results (1–1000).
        offset: Pagination offset.
        reverse: If True, return in ascending order (default is descending).
        created_after: Filter bids created on or after this date (YYYY-MM-DD).
        created_before: Filter bids created before this date (YYYY-MM-DD).
        order_id: Filter by a specific order ID (e.g. B123456789).
        bid_status: Filter by status. One of: SPOT_BID_STATUS_ACTIVE,
            SPOT_BID_STATUS_CANCELLED, SPOT_BID_STATUS_COMPLETED,
            SPOT_BID_STATUS_PARTIALLY_FILLED, SPOT_BID_STATUS_EXPIRED.
        exclude_active: If True, exclude currently active orders.
        upstream_url: Filter by mining pool upstream URL.
        upstream_identity: Filter by upstream worker identity.
    """
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if reverse is not None:
        params["reverse"] = reverse
    if created_after is not None:
        params["created_after"] = created_after
    if created_before is not None:
        params["created_before"] = created_before
    if order_id is not None:
        params["order_id"] = order_id
    if bid_status is not None:
        params["bid_status"] = bid_status
    if exclude_active is not None:
        params["exclude_active"] = exclude_active
    if upstream_url is not None:
        params["upstream_url"] = upstream_url
    if upstream_identity is not None:
        params["upstream_identity"] = upstream_identity
    return _get("/spot/bid", params=params, auth=True)


@mcp.tool()
def get_bid_detail(order_id: str) -> dict:
    """Get full details for a specific bid: state, counters, network status,
    and change history. Requires API key.

    Args:
        order_id: Bid order ID in format B123456789.
    """
    return _get(f"/spot/bid/detail/{order_id}", auth=True)


@mcp.tool()
def get_bid_speed_history(
    order_id: str,
    aggregation_period: str = None,
    sliding_window_size: str = None,
    datetime_from: str = None,
    limit: int = None,
) -> dict:
    """Get hashrate speed history time series for a specific bid.
    Requires API key.

    Args:
        order_id: Bid order ID in format B123456789.
        aggregation_period: Resampling period. One of PERIOD_1_MINUTE,
            PERIOD_5_MINUTES, PERIOD_15_MINUTES, PERIOD_1_HOUR, PERIOD_1_DAY.
        sliding_window_size: Speed estimation window. One of
            WINDOW_SIZE_10_MINUTES, WINDOW_SIZE_20_MINUTES, WINDOW_SIZE_30_MINUTES.
        datetime_from: Start of history in RFC 3339 format (e.g. 2025-10-04T12:00:00Z).
        limit: Maximum number of data points to return.
    """
    params = {}
    if aggregation_period is not None:
        params["aggregation_period"] = aggregation_period
    if sliding_window_size is not None:
        params["sliding_window_size"] = sliding_window_size
    if datetime_from is not None:
        params["datetime_from"] = datetime_from
    if limit is not None:
        params["limit"] = limit
    return _get(f"/spot/bid/speed/{order_id}", params=params, auth=True)


@mcp.tool()
def get_bid_delivery_history(
    order_id: str,
    aggregation_period: str = None,
    datetime_from: str = None,
    limit: int = None,
) -> dict:
    """Get share delivery history for a specific bid: shares purchased,
    accepted, and rejected over time. Requires API key.

    Args:
        order_id: Bid order ID in format B123456789.
        aggregation_period: Resampling period. One of PERIOD_1_MINUTE,
            PERIOD_5_MINUTES, PERIOD_15_MINUTES, PERIOD_1_HOUR, PERIOD_1_DAY.
        datetime_from: Start of history in RFC 3339 format (e.g. 2025-10-04T12:00:00Z).
        limit: Maximum number of data points to return.
    """
    params = {}
    if aggregation_period is not None:
        params["aggregation_period"] = aggregation_period
    if datetime_from is not None:
        params["datetime_from"] = datetime_from
    if limit is not None:
        params["limit"] = limit
    return _get(f"/spot/bid/delivery/{order_id}", params=params, auth=True)


@mcp.tool()
def create_bid(
    upstream_url: str,
    speed_limit_ph: float,
    amount_sat: int,
    price_sat: int,
    upstream_identity: str = None,
    cl_order_id: str = None,
    memo: str = None,
) -> dict:
    """Place a new bid on the spot market. Requires API key.

    Args:
        upstream_url: Mining pool upstream URL (e.g. stratum+tcp://pool.net:7770).
        speed_limit_ph: Maximum hashrate to deliver in PH/s.
        amount_sat: Budget for this bid in satoshis.
        price_sat: Price in satoshis per EH/day.
        upstream_identity: Worker identity string for the upstream pool.
        cl_order_id: Optional client-assigned order ID for idempotency.
        memo: Optional note for this bid.
    """
    body: dict = {
        "dest_upstream": {"url": upstream_url},
        "speed_limit_ph": speed_limit_ph,
        "amount_sat": amount_sat,
        "price_sat": price_sat,
    }
    if upstream_identity is not None:
        body["dest_upstream"]["identity"] = upstream_identity
    if cl_order_id is not None:
        body["cl_order_id"] = cl_order_id
    if memo is not None:
        body["memo"] = memo
    log.info("create_bid upstream=%s speed_limit_ph=%s amount_sat=%s price_sat=%s", upstream_url, speed_limit_ph, amount_sat, price_sat)
    result = _post("/spot/bid", body)
    log.info("create_bid result=%s", result)
    return result


@mcp.tool()
def update_bid(
    bid_id: str,
    cl_order_id: str = None,
    new_amount_sat: int = None,
    new_price_sat: int = None,
    new_speed_limit_ph: float = None,
    memo: str = None,
) -> dict:
    """Update an existing active bid. Requires API key.

    Args:
        bid_id: The bid ID to update.
        cl_order_id: Optional client-assigned order ID.
        new_amount_sat: New budget in satoshis.
        new_price_sat: New price in satoshis per EH/day.
        new_speed_limit_ph: New maximum hashrate in PH/s.
        memo: Updated note for this bid.
    """
    body: dict = {"bid_id": bid_id}
    if cl_order_id is not None:
        body["cl_order_id"] = cl_order_id
    if new_amount_sat is not None:
        body["new_amount_sat"] = new_amount_sat
    if new_price_sat is not None:
        body["new_price_sat"] = new_price_sat
    if new_speed_limit_ph is not None:
        body["new_speed_limit_ph"] = {"value": new_speed_limit_ph}
    if memo is not None:
        body["memo"] = memo
    log.info("update_bid bid_id=%s updates=%s", bid_id, {k: v for k, v in body.items() if k != "bid_id"})
    result = _put("/spot/bid", body)
    log.info("update_bid result=%s", result)
    return result


@mcp.tool()
def cancel_bid(order_id: str) -> dict:
    """Cancel an active bid. Requires API key.

    Args:
        order_id: Bid order ID in format B123456789.
    """
    log.info("cancel_bid order_id=%s", order_id)
    result = _delete(f"/spot/bid/{order_id}")
    log.info("cancel_bid confirmed order_id=%s", order_id)
    return result


def main():
    mcp.run()


if __name__ == "__main__":
    main()
