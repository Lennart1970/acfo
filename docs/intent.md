# Intent: Cursor × Supabase × Railway MVP

## Goal

Pipeline: **Exact Online → Invantive SQL → SQL → web view**.

Exact is the source. Invantive (or `acfo`) is the SQL engine over Sync/Deleted. The web view reads that SQL — Invantive App Online / Bridge Online, or `python -m acfo web` on the Supabase replica.

We are **not** connected to Exact, Invantive, Supabase, or Railway until you add credentials.

## Phases

| Phase | What | Who |
| --- | --- | --- |
| **1 — MVP (now)** | Exact Sync → Railway cron → Supabase Postgres → web view (`acfo web` or Invantive App Online). Work-order rows live in Supabase so MS admins have a queue. | You + Cursor |
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
    │
    ▼
Web view  (`python -m acfo web` or App Online / Bridge Online)
```

## Why this stack

- **Cursor** — build and change the sync + schema here.
- **Supabase** — Postgres + RLS + PostgREST without standing up a DB. Better than MySQL for Invantive *and* for a later HTTP tool.
- **Railway** — one scheduled job, no always-on server. Use the **session pooler** (`pooler.supabase.com:5432`), not transaction mode (prepared statements / session state).

Playbook: [invantive/exact-sql-webview.md](../invantive/exact-sql-webview.md). App Online SQL: [invantive/app-online-ledger.sql](../invantive/app-online-ledger.sql). Local/Railway web view: `python -m acfo web`. Excel is not in this path.

## Out of scope for MVP

- Live Exact calls from Copilot
- Official Supabase MCP in Teams (developer permissions)
- MySQL
- Fabric / Azure SQL (work order WO-004 only)

## Your next inputs

1. Supabase project + database password (Connect → session pooler string).
2. Exact App Center Client ID / Secret / HTTPS redirect.
3. Railway project linked to this repo; env vars from `.env.example`; cron `15 * * * *` (UTC).
