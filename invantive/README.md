# Invantive as the Exact Online → MySQL path

Invantive is the stronger alternative if you still have (or want) a license. It already speaks Exact’s Sync APIs, hides the Timestamp/Deleted pitfalls, and can write MySQL. The Python `acfo` CLI in this repo is the self-hosted fallback when you do not want that subscription.

We are **not** connected to Invantive or Exact from this environment. This folder is the playbook.

## What Invantive actually is

Invantive SQL is a virtual database over Exact Online (and ~100 other platforms). You write SQL; Invantive translates it to Exact REST calls, respects rate limits, and pages Sync/Bulk for you.

| Product | Role | Use for MySQL? |
| --- | --- | --- |
| **Query Tool** | Desktop SQL against Exact | Explore `TransactionLinesIncremental`. Not a scheduler. |
| **Cloud / Office for Entrepreneurs** (~€59/mo) | OData for Power BI, Excel, Get My Report | Can push to a **publicly reachable** MySQL. Cannot see a laptop/on-prem MySQL behind NAT. Does **not** include Data Hub. |
| **Data Hub** (Office Premium ~€119/mo, or its own sub) | Headless Invantive SQL on Windows/macOS/Linux, cron or Task Scheduler | **This is the product that copies Exact → your MySQL.** |
| **Data Replicator** | Warehouse engine: versioning, partitions, trickle load | Only if you have many companies or tens of GB+. Invantive themselves say Data Hub is enough for smaller volumes. |

Exact Online on-prem Data Hub now needs the **.NET 6 multi-platform** build. The old .NET Framework Data Hub breaks on One Exact Identity.

Downloads: [download.invantive.com](https://download.invantive.com). Data model: [TransactionLinesIncremental](https://datamodels.invantive.com/Exact+Online+Data+Model/Tables/ExactOnlineREST-Incremental-TransactionLinesIncremental).

## The table you want

```sql
select *
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
```

That is **not** a live Exact table. Invantive builds it from:

1. `GET /sync/Financial/TransactionLines` (new/changed rows, 1000/call)
2. `GET /sync/Deleted` (soft-delete by `EntityKey`)
3. a local cache of the current replica

After the first fill it typically costs **two Exact API calls**, regardless of how many lines you already have. That is why Invantive tells you to stop using `TransactionLines` / `TransactionLinesBulk` for this.

`LineNumber = 0` is the booking header. Bank journals are in the same table (`Type = 40`); do not also download `BankEntryLines` unless you need bank-statement fields.

## How to land it in MySQL

### 1. Distributed database

Data Hub talks to one platform per connection unless you bundle them. Put `settings-distributed.example.xml` (renamed) in `%USERPROFILE%\invantive` (Windows) or `~/invantive` (Linux/macOS).

- `@eol` = Exact Online (`ExactOnlineAll`)
- `@mysql` = your MySQL (`MySql`; install [Invantive’s MySQL driver](https://support.invantive.com/download-driver-mysql))
- `@pg` = PostgreSQL / **Supabase** (`PostgreSql`; host `db.<project>.supabase.co`, SSL, database password — not the anon key)

You still need an Exact **App Center** Client ID. Invantive can use their redirect `https://clientredirect.invantive.com`. Add `client-secret=...` and a TOTP secret if Exact requires 2FA.

### 2. First copy (small/medium administrations)

```sql
use all@eol

create or replace table transaction_lines_incremental@mysql
as
select *
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
```

That is the official one-liner. Invantive creates the MySQL table and (re)loads all current rows.

**Caveat:** MySQL has no bulk loader. Invantive inserts **row by row**. Fine for tens/hundreds of thousands of lines. Painful for millions — the Incremental download is fast, the MySQL rewrite is not.

### 3. Daily job (recommended)

Schedule `copy-transaction-lines.sql` with Data Hub + cron/Task Scheduler. For a typical CFO set, also copy GL accounts and relations (`copy-recommended-tables.sql`).

For millions of rows, do **not** `create or replace` every night. Use the Incremental cache once, then MERGE only `SyncTransactionLines` / `SyncDeleted` where `Timestamp` is new — the pattern on the [Invantive SQL Server sync scripts](https://forums.invantive.com/t/updated-synchronization-script-between-eol-and-sql-server/6335). `acfo sync` is that same MERGE, written in Python.

### 4. Query MySQL afterwards

```sql
select date, journal_code, gl_account_code, description, amount_dc, type
from   transaction_lines_incremental
where  line_number > 0
order by date, entry_number, line_number;
```

Column names stay close to Exact/Invantive (`AmountDC`, `GLAccountCode`, …) if you `select *`. The Python path snake_cases them (`amount_dc`).

## When to use Invantive vs `acfo`

Use **Invantive Data Hub** when you want Exact’s full catalog (1,200+ tables), multi-division `use all@eol`, rate-limit handling, and SQL you already know.

Use **`acfo`** when you do not want a paid Invantive seat, only need transaction lines (plus deletes) in MySQL, and will operate OAuth yourself.

Office for Entrepreneurs alone is enough for Power BI over Exact. It is **not** enough for an on-prem MySQL replica; that needs Data Hub (or a Cloud job that can reach the MySQL host).
