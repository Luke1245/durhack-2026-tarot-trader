# ADR-0001: Paper-trading ledger with read-time PnL

## Status
Accepted, 2026-11-14

## Context
Tarot Trader lets users open positions (long/short) on assets motivated by tarot readings. The project needed a trading backend, with two fundamentally different options:

- **Broker/exchange integration**: positions backed by a real account (Alpaca, broker APIs). Per-user API keys, webhook handling, onboarding friction, and far beyond hackathon scope.
- **Internal paper-trading ledger**: the app records positions and entry/exit prices itself, fetching prices from a market-data API (Finnhub free tier). No money moves; PnL is computed.

Within the ledger option, PnL could be computed **at read time** (fetch current price on each positions request) or **snapshotted** (background job writes `current_price`/`pnl` columns).

## Decision
Paper-trading ledger, **no broker integration**, with **read-time PnL**:

- Positions store `side`, `quantity`, `entry_price`, `status`, `closed_at`, `exit_price` only. No `current_price`/`pnl` columns.
- Unrealized PnL is computed when positions are read, using a ~60-second in-memory price cache in `services/prices.py` to respect Finnhub rate limits.
- Closing a position (`POST /positions/{id}/close`) fetches the current price once and records it as `exit_price`.
- Price-provider access is isolated in one service module so swapping providers is a local change.

## Amendment (2026-11-14): portfolio value history
The MVP requires a graph of portfolio value over time, which read-time PnL cannot provide (no historical data exists). Addition, scoped to keep read-time PnL for positions:
- A `portfolio_snapshots` table (user_id, value, taken_at).
- Snapshots are written two ways, combined:
  - **Lazy**: whenever portfolio data is read and the latest snapshot is older than ~5 minutes, the server computes and stores one inline.
  - **Scheduled**: an in-process task snapshots every 5 minutes, so the graph fills even when nobody is watching.
  - (Single-worker dev/demo deployment; a real deployment would move the scheduled part to a cron job.)
- Position-level PnL remains read-time per the original decision; only the portfolio aggregate is snapshotted.

## Consequences
- **Hard to reverse once positions accumulate**: switching to a real broker later invalidates the existing position data (it references no external account or order ids). Treat the ledger as permanent product data, not a prototype artifact.
- Closed positions give exact PnL from recorded prices; open positions give approximate, cached valuations — acceptable for a demo, and must be stated if numbers are ever shown to users as precise.
- No background jobs, no extra state, one rate-limit surface (the cache) to reason about.
