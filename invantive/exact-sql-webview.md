# Exact Online → Invantive → SQL → web view

```
Exact Online  →  Invantive  →  SQL  →  web view
```

1. **Exact Online** — source of grootboekmutaties (no dump, no MySQL).
2. **Invantive** — talks Sync + Deleted, hides Timestamp paging.
3. **SQL** — either virtual Invantive SQL (`TransactionLinesIncremental@eol`) or a copy in Supabase / MySQL.
4. **Web view** — App Online HTML, Bridge Online OData in the browser, or `python -m acfo web` on the replica.

Invantive is the engine in the middle. Excel is not in this path.

We are not logged into your Invantive Cloud or Exact from this environment.

## The two shapes

### A — Stay on Invantive Cloud (no replica)

```
Exact Online
    → Invantive SQL  (TransactionLinesIncremental@eol)
    → Bridge Online / App Online / Get My Report
```

SQL is virtual. Nothing is stored in Supabase. The browser (or Power BI) is the web view.

Register a database on [Invantive Cloud](https://cloud.invantive.com) with Exact Online. Same database is then available on three channels ([Cloud structure](https://forums.invantive.com/t/invantive-cloud-structure/229)):

| Channel | URL | What you see |
| --- | --- | --- |
| **Cloud** | `cloud.invantive.com` | Admin UI, databases, monitoring |
| **Bridge Online** | `https://bridge-online.cloud/<database>/odata4` | OData4 “web view”: open the URL, basic-auth, list of tables, then JSON rows. Power BI / Excel use the same URL. |
| **App Online** | `https://app-online.cloud` | Your Invantive SQL as a **hosted HTML app** (low-code web view). |
| **Get My Report** | hosted reports | Ready-made Exact web reports/dashboards on the same SQL. |

Entries (grootboekmutaties):

```
https://bridge-online.cloud/<your-db>/odata4/ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
```

Use Incremental, not `TransactionLines` / Bulk. Allow your IP on the database. Bridge credentials are separate from your Cloud login.

App Online is the actual **webview**: paste [app-online-ledger.sql](app-online-ledger.sql) (or a small PSQL page) and Invantive hosts HTML. Filter `LineNumber > 0`; bank is `Type = 40`.

Office for Entrepreneurs covers Cloud + Bridge + Get My Report. App Online is the web-app channel on the same subscription family.

### B — Invantive SQL into *your* SQL, then *your* web view (MVP)

```
Exact Online
    → Invantive Data Hub  (same Incremental SQL)
    → Supabase Postgres
    → web view = PostgREST / Table Editor / a small app on Railway
```

Use this when Copilot, RLS, or a product you own must sit on the data. The Invantive step is still SQL:

```sql
use all@eol

create or replace table transaction_lines_incremental@pg
as
select *
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
```

Then the web view is Supabase:

- Dashboard table editor
- `GET /rest/v1/transaction_lines_incremental?line_number=gt.0`
- `python -m acfo web` — ledger HTML on that SQL (Railway: second always-on service)
- Later: Copilot tool (WO-003), not live Exact

`acfo` on Railway is the same pipeline with Invantive removed from the middle. The SQL and the web view stay.

## What “SQL” means here

You do **not** get Exact’s own SQL Server. Invantive SQL is a dialect over APIs:

```sql
select date, journal_code, gl_account_code, description, amount_dc, type
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
where  line_number > 0
  and  type = 40
```

Bridge Online rewrites OData `$filter` into that SQL, runs it, streams JSON. App Online runs the same SQL and renders HTML.

## What to pick

| You want | Use |
| --- | --- |
| Open Exact tables in the browser / Power BI this week | **A — Bridge Online** Incremental entity set |
| A branded HTML report for finance | **A — App Online** or Get My Report |
| Data you control + Copilot work orders | **B — Data Hub → Supabase**, then `acfo web` / PostgREST |
| No Invantive license | **B with `acfo` sync + `acfo web`** instead of Data Hub |

Do not point a web view at live Exact APIs. Invantive (or `acfo`) exists so the browser hits SQL/OData, not the 60 calls/minute Exact cap.

Excel (`exceltable`) is only for workbooks that are **not** in Exact. Ignore `excel-to-supabase.md` for this pipeline.
