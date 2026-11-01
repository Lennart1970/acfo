# Lane 4 — Features (grounded in acfo)

## Documented deployment path (`docs/deployment-plan.md`)

| Stage | What |
| --- | --- |
| 0 | Inputs: Exact app, Invantive Data Hub, Supabase, Railway, `LEDGER_API_KEY`, PP environment |
| 1 | Exact → Invantive → Supabase (or `acfo sync` fallback) |
| 2 | Railway always-on `python -m acfo web` + session pooler `DATABASE_URL` |
| 3 | Review via `booking-weekoverzicht` against replica |
| 4 | Power Platform custom connector (WO-005) |

## Repo deploy artifacts

| Artifact | Role |
| --- | --- |
| `Dockerfile` / `docker-compose.yml` | Container build for web/sync |
| `railway.json` | Railway project config |
| `docs/railway.md` | Cron / service runbook |
| `invantive/` | Data Hub settings examples, scheduled SQL |
| `work-orders/` | MS admin queue (phase 2) |

## Power Platform ALM (Project context)

- Single solution: **aCFO Hands-Free Accounting** (`acfo_` prefix).
- Milestone ZIP exports as recovery artifacts; unpacked source under Git when useful.
- Example versions: `aCFO_0.1` core Dataverse → `0.2` booking confidence → …

## Safety

Environment has no Invantive/Railway/Exact/DATABASE_URL until operators supply them. Docs describe shape only.
