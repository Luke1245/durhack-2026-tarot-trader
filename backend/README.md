# Tarot Trader — Backend

FastAPI + SQLAlchemy (async). All routes are mounted under `/api`; the OpenAPI
spec at `/openapi.json` drives the frontend's `npm run gen:api` codegen.

## Layout

- `app/main.py` — app factory, CORS, `/api` mount, lifespan (create tables on startup)
- `app/config.py` — pydantic-settings, reads `APP_*` vars from `.env`
- `app/db.py` — async engine + `get_session` dependency
- `app/models/` — SQLAlchemy ORM (storage): `users`, `sessions`, `tarot_cards` (78-card reference data), `readings` + `reading_cards` (3-card spread), `assets`, `positions` (paper-trading ledger)
- `app/schemas/` — Pydantic request/response models (the API contract)
- `app/routers/` — thin HTTP layer, one module per resource
- `app/services/` — business logic
- `alembic/versions/0001_initial_schema.py` — initial schema (hand-written; `alembic check` verifies model parity)
- `scripts/import_cards.py` — idempotent upsert of the Zenodo tarot dataset into `tarot_cards`:

```bash
uv run python scripts/import_cards.py <dataset.json>
```

- `scripts/import_card_images.py` — convert card scans to WebP + backfill `image_path`:

```bash
uv run python scripts/import_card_images.py <scan_dir>
```

- `scripts/seed_assets.py` — idempotent upsert of the 15 tradeable stocks:

```bash
uv run python scripts/seed_assets.py
```

Prices come from Finnhub (free tier, 60 req/min); the 60-second cache in
`app/services/prices.py` keeps us under that. Set `APP_FINNHUB_API_KEY` in `.env`.
Portfolio value history is snapshot-based (ADR-0001 amendment): lazy-write on
read if stale >5 min, plus an in-process 5-minute loop in `app/main.py`.

## Run

```bash
cp .env.example .env   # fill in your TigerData DATABASE_URL
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

For local dev without a database: `APP_DATABASE_URL="sqlite+aiosqlite:///./dev.db" uv run uvicorn app.main:app --reload`

## Test

```bash
uv run pytest
```

Tests run against SQLite in-memory via `tests/conftest.py` — no external DB needed.

## Migrations

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

## Frontend contract

```bash
# from frontend/, with the backend running:
npm run gen:api   # → src/api/schema.d.ts
```
