# acfo

MVP: **Cursor** builds Exact Online sync → **Railway** cron runs it → **Supabase** holds entries and Microsoft **work orders**. Copilot comes later via those work orders.

Intent: [docs/intent.md](docs/intent.md) · Railway: [docs/railway.md](docs/railway.md) · Work orders: [work-orders/](work-orders/README.md)

```bash
export DATABASE_URL='postgresql://postgres.<ref>:<pw>@…pooler.supabase.com:5432/postgres'
python -m acfo init-db
python -m acfo auth
python -m acfo sync
```

Exact Online has no dump. Invantive Data Hub can still load Incremental tables if you prefer that over `acfo`. Copilot should not query Exact live. See [docs/copilot.md](docs/copilot.md).

## Invantive is the better alternative (if you have a license)

Invantive already does this job. `TransactionLinesIncremental` is Exact Sync + Deleted, cached. Data Hub can write that replica straight to MySQL:

```sql
use all@eol

create or replace table transaction_lines_incremental@mysql
as
select *
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
```

That is the path to use if you still have Query Tool / Data Hub / Office Premium. Playbook, `settings-*.xml`, and scheduled SQL are in [`invantive/`](invantive/README.md).

Office for Entrepreneurs (~€59) is enough for Power BI over Exact. An **on-prem MySQL** replica needs **Data Hub** (Office Premium ~€119, or a Data Hub subscription). Data Replicator is only for large warehouses.

This Python CLI is the fallback when you do not want that seat: same Sync/Deleted/Timestamp logic, OAuth operated by you.

## Coming from Invantive (mapping to `acfo`)

The table you likely used:

| Invantive | What it actually is | In this repo |
| --- | --- | --- |
| `ExactOnlineREST.Incremental.TransactionLinesIncremental` | Sync mutations + deletes, cached as a current replica | Supabase view `transaction_lines_incremental` |
| `ExactOnlineREST.Sync.SyncTransactionLines` | Raw `GET …/sync/Financial/TransactionLines` | `python -m acfo sync` upsert into `transaction_lines` |
| `ExactOnlineREST.Sync.SyncDeleted` | Raw `GET …/sync/Deleted` | `deleted_entities` + `deleted_at` on the line |
| `ExactOnlineREST.FinancialTransaction.TransactionLines` / `*Bulk` | Slow 60-row or Bulk 1000-row GET | Only used for a first `--from-date` load if SyncTimestamp is missing |
| `BankEntries` / `BankEntryLines` | Bank journals only; expensive | Filter `type = 40` on the incremental view |

`acfo sync` is the same pattern as the Invantive scripts that **MERGE SyncTransactionLines into SQL Server** (not `CREATE TABLE AS SELECT * FROM TransactionLinesIncremental`). That full rebuild is fast on the API side and slow when millions of rows are rewritten. This tool upserts by `ID`, deletes via `EntityKey` (not the Deleted row’s own `ID`), and stores a `Timestamp` per **division**.

```sql
-- old Invantive
select * from ExactOnlineREST.Incremental.TransactionLinesIncremental

-- MySQL after acfo sync
select * from transaction_lines_incremental
```

Same pitfalls Invantive already documented:

- `LineNumber = 0` is the booking header; the splits are the other lines.
- Do not pull `BankEntryLines` for reporting if `TransactionLines` already has the bank journal.
- After the first run, only rows with a higher `Timestamp` are fetched (typically two Exact calls: lines + deletes).
- Multiple administraties: `python -m acfo sync --all-divisions` loops divisions the way Invantive does.

If you keep Invantive, you do not need `acfo`. If you drop Invantive, put `acfo sync` on cron instead.

## Recommended path

| Step | What | Why |
| --- | --- | --- |
| 1 | Register a **private app** in the [Exact App Center](https://apps.exactonline.com/) | Required for Client ID / Secret. Until Exact reviews a public app, it only works for your own subscription. |
| 2 | OAuth authorization-code flow | Access tokens last **10 minutes**. Refresh tokens last up to **1 year** and **rotate on every refresh** — always persist the new refresh token. |
| 3 | `GET /api/v1/current/Me?$select=CurrentDivision` | Every later URL needs a division (administratie) id. |
| 4 | `GET /api/v1/{division}/sync/Financial/TransactionLines?$filter=Timestamp gt {ts}L` | Official incremental API. **1000 rows/call**. Timestamp is a row version, not a clock. |
| 5 | `GET /api/v1/{division}/sync/Deleted?$filter=Timestamp gt {ts}L` | Sync does **not** return deletions. Keep rows whose `EntityType` is `1` or `TransactionLines`. `EntityKey` is the original line `ID`. |
| 6 | Upsert into MySQL by `id`; soft-delete when Deleted reports the key | Keeps MySQL equal to Exact after corrections. |

Do **not** use the old `/financialtransaction/Transactions` endpoint (deprecated). The 60-row `/financialtransaction/TransactionLines` endpoint is the same data but much slower.

### Optional first load

- **Bulk**: `GET /api/v1/{division}/bulk/Financial/TransactionLines?$filter=Date ge datetime'2024-01-01T00:00:00'` (also 1000 rows/call; `$filter` is mandatory).
- **SyncTimestamp**: Exact can return a starting `Timestamp` for a `Modified` date so a first Sync can skip older history.

### Limits and rules

- **60 calls/minute** and **5,000/day** per app per division (Premium daily cap is higher).
- Calls must be **sequential**. Parallel requests are not allowed.
- Watch `X-RateLimit-Minutely-Remaining` and `X-RateLimit-Remaining`.
- Redirect URI must be **HTTPS** and match the App Center registration. Localhost is not accepted. For this CLI, Exact can 404 on redirect; paste the full redirected URL (it contains `?code=`).
- Country instances are separate: NL `start.exactonline.nl`, BE `.be`, DE `.de`, UK `.co.uk`.

Official index: [REST API resources](https://start.exactonline.nl/docs/HlpRestAPIResources.aspx).

## What this repo does

`python -m acfo` implements that path:

1. `auth` — exchange an OAuth code and store rotating tokens in `.tokens.json`
2. `init-db` — create `transaction_lines`, `deleted_entities`, `sync_state`
3. `sync` — incremental Sync + Deleted → MySQL
4. `divisions` — list administrations the token can access

`transaction_lines` stores the Sync payload as posted in Exact (amounts, VAT, journal, GL account, relation, period, type). Query `transaction_lines_incremental` for the live replica (deleted rows removed). Bank bookings, sales, purchase, and memorial entries are all transaction lines; filter on `type` or `journal_code`. Type `40` is cash flow / bank.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Fill `.env` with the App Center Client ID, Client Secret, HTTPS redirect URI, region, and MySQL settings.

Start MySQL (optional):

```bash
docker compose up -d
```

Or point `.env` at an existing server, then:

```bash
python -m acfo init-db
python -m acfo auth
python -m acfo sync
```

First load from a date (uses SyncTimestamp, or Bulk if that call is unavailable):

```bash
python -m acfo sync --from-date 2024-01-01
```

Full resync:

```bash
python -m acfo sync --full
```

All divisions the token can access (Invantive-style):

```bash
python -m acfo sync --all-divisions
```

Schedule `python -m acfo sync` hourly or daily. After the first run it only fetches new/changed rows.

Example reporting SQL is in `sql/example_queries.sql`.

## Alternatives (no Python)

- **Invantive Data Hub → MySQL** (recommended if licensed): [`invantive/`](invantive/README.md)
- Exact Online → Excel/CSV export (manual, not incremental)
- Hosted ELT (Peliqan, Airbyte-style connectors)

## Tests

```bash
pytest
```
