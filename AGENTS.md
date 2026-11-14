# Rules
## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in this repo (`gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles, label strings equal to their names (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at the repo root, consumed lazily. See `docs/agents/domain.md`.

- Frontend: React function components + hooks, TypeScript strict, no `any`
- API types come from src/api/schema.d.ts. Never hand-write them; run `npm run gen:api`
- Fetch data with TanStack Query + the openapi-fetch client
- UI: Tailwind + shadcn/ui components before custom CSS
- A task isn't done until `npm run typecheck` and `npm run lint` pass
- Backend: all routes under /api, Pydantic models for every request/response. FastAPI lives in backend/: `uv run uvicorn app.main:app --reload --port 8000` to serve, `uv run pytest` to test, `uv run alembic upgrade head` for migrations. `APP_DATABASE_URL` in backend/.env points at TigerData (Postgres/asyncpg)
- TypeScript is pinned to ~6.0.x. Never add `baseUrl` to tsconfig (deprecated in TS 6, hard error); `"paths"` works without it under `moduleResolution: "bundler"`
- openapi-typescript is NOT installed: latest v7 peers typescript@^5.x which conflicts with TS 6. Run it ad hoc via `npx openapi-typescript <spec> -o src/api/schema.d.ts`
- Tailwind is v4 wired via `@tailwindcss/vite` (vite.config.ts) + `@import "tailwindcss"` in src/index.css. No tailwind.config.js — v4 is CSS-first; theme tokens live in src/index.css
- shadcn/ui is initialized with the Base UI component library (Nova preset); `@/*` path alias is set up in tsconfig.app.json paths + vite.config.ts resolve.alias — keep both in sync
