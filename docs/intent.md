# Intent: Cursor × Supabase × Railway MVP

## Goal

Get Exact Online **entries** (grootboekmutaties) into a store we control, then ask questions and later hand **work orders** to Microsoft administrators for Copilot / Teams.

We are **not** connected to Exact, Supabase, or Railway until you add credentials.

## Phases

| Phase | What | Who |
| --- | --- | --- |
| **1 — MVP (now)** | Exact Sync → Railway cron → Supabase Postgres. Read via PostgREST / SQL. Work-order rows live in Supabase so MS admins have a queue. | You + Cursor |
| **2 — Copilot** | Microsoft admins execute `work_orders` (WO-001…): Copilot Studio tool on PostgREST, not live Exact, not org-wide Supabase MCP. | Microsoft administrators |
| **3 — Optional** | Replica to Azure SQL if they want native Copilot *knowledge* instead of a tool. Supabase stays source of truth for the MVP. | Microsoft administrators |

## Shape

```
Exact Online
    │  OAuth + /sync/Financial/TransactionLines + /sync/Deleted
    ▼
Railway cron  (python -m acfo sync, must exit)
    │  DATABASE_URL = Supabase session pooler (IPv4)
    │  tokens in public.oauth_tokens (ephemeral disk is useless)
    ▼
Supabase
    ├── transaction_lines
    ├── transaction_lines_incremental  (view, security_invoker)
    ├── work_orders                    (queue for MS admins)
    └── oauth_tokens / sync_state      (not exposed to Copilot)
```

## Why this stack

- **Cursor** — build and change the sync + schema here.
- **Supabase** — Postgres + RLS + PostgREST without standing up a DB. Better than MySQL for Invantive *and* for a later HTTP tool.
- **Railway** — one scheduled job, no always-on server. Use the **session pooler** (`pooler.supabase.com:5432`), not transaction mode (prepared statements / session state).

Excel that is **not** in Exact can be loaded with the same Data Hub + `@pg` connection via `exceltable` ([invantive/excel-to-supabase.md](../invantive/excel-to-supabase.md)). That job runs on the PC that sees the .xlsx, not on Railway.

## Out of scope for MVP

- Live Exact calls from Copilot
- Official Supabase MCP in Teams (developer permissions)
- MySQL
- Fabric / Azure SQL (work order WO-004 only)

## Your next inputs

1. Supabase project + database password (Connect → session pooler string).
2. Exact App Center Client ID / Secret / HTTPS redirect.
3. Railway project linked to this repo; env vars from `.env.example`; cron `15 * * * *` (UTC).
