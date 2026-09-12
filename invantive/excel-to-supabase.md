# Invantive: Excel → Supabase

Invantive does **not** need an “Excel database provider” for this. Excel is a **file**. Invantive SQL reads it with `exceltable`, then `create or replace table …@pg` writes **PostgreSQL**. Supabase is that Postgres.

We are not connected to Invantive or your Supabase from this environment. You still need Data Hub (or Query Tool) on a machine that can **see the .xlsx**.

## Which Invantive product

| Product | Excel → Supabase? |
| --- | --- |
| **Query Tool** | Yes, interactively. Test the `exceltable` mapping here first. |
| **Data Hub** | Yes, scheduled. This is the one for a drop folder of workbooks. |
| **Data Loader** | Yes, GUI one-shot. Same SQL underneath. |
| **Cloud / App Online** | Only if the file is **uploaded** (blob) or lives somewhere Cloud can HTTP-get. Cloud cannot read `C:\Users\…\sheet.xlsx` on your laptop. |
| **Control for Excel** | Wrong direction: SQL **into** a workbook, not extract. |

`exceltable` is documented in [Invantive UniversalSQL](https://documentation.invantive.com) and the forum notes on [exceltable ranges](https://forums.invantive.com/t/improved-selection-capabilities-of-exceltable-table/3704) and [Excel + Exact actuals](https://forums.invantive.com/t/combining-excel-based-sales-estimate-with-exact-online-actuals/930).

## How it works

```
.xlsx on disk (or Dropbox/OneDrive sync folder)
        │
        │  exceltable (positional columns, skip header)
        ▼
Invantive Data Hub / Query Tool
        │
        │  create or replace table …@pg
        ▼
Supabase Postgres  (database password, SSL, session pooler if IPv4)
```

Column mapping is **positional** from the top-left of a named range, table, or sheet — not Excel header names. `position 1` is the first column; `position next` walks right. `skip first 1 rows` drops the header row.

## Connection

Only **PostgreSQL** must be in `settings-*.xml` (`provider="PostgreSql"`, alias `pg`). See the `@pg` block in `settings-distributed.example.xml`.

Use the Supabase **database password**, not the anon key.

- Persistent / IPv6: `Host=db.<ref>.supabase.co;Port=5432;Username=postgres;SSL Mode=Require`
- IPv4-only Data Hub PC: **session pooler** from Dashboard → Connect (`Username=postgres.<ref>`, host `…pooler.supabase.com`, port **5432**)

Allow the Data Hub machine’s public IP under Supabase Network Restrictions. The `postgres` role **bypasses RLS**; that is what you want for the loader. Do not put `service_role` in Invantive.

## One sheet → one table

```sql
create or replace table excel_sales_estimates@pg
as
select xlsx.*
from   exceltable
       ( name 'salesdata'
         passing file 'C:\data\sales.xlsx'
         skip first 1 rows
         skip empty rows
         columns region       varchar2 position 1
         ,       item_code    varchar2 position next
         ,       sales_period number   position next
         ,       revenue      number   position next
       ) xlsx
```

Without a named range, use the first sheet:

```sql
from exceltable
     ( worksheet 1
       passing file 'C:\data\sales.xlsx'
       skip first 1 rows
       ...
     )
```

Full script: `excel-to-supabase.sql`.

## Folder of workbooks

Invantive OS provider (always there, no extra settings):

```sql
create or replace table excel_sales_estimates@pg
as
select fle.file_path
,      xlsx.*
from   files('C:\data\drop', '*.xlsx', false)@os fle
join   exceltable
       ( worksheet 1
         passing file fle.file_path
         skip first 1 rows
         skip empty rows
         columns region    varchar2 position 1
         ,       item_code varchar2 position next
         ,       revenue   number   position next
       ) xlsx
```

Schedule that in Data Hub (Task Scheduler / cron) like the Exact Incremental job.

## Cloud upload (no local path)

Invantive App Online: `cloud_http.get_request_form_file_contents('p_file')` returns a blob; `exceltable ( … passing l_payload … )` parses it, then insert into `@pg` if Cloud can reach Supabase (public pooler + IP allow).

## Limits and pitfalls

- **Header row:** always `skip first 1 rows` unless you use a named range that starts on data.
- **Types:** Excel numbers as `number`/`double`; dates often arrive as Excel serials — `to_date` / convert in the SELECT.
- **`create or replace`:** rebuilds the whole Supabase table. Fine for small sheets. For large or append-only drops, `insert into existing@pg select …` or merge on a business key.
- **Merged cells / multiple header rows:** Invantive will mis-align. Clean the sheet or name a data-only range.
- **Password-protected / XLS (old binary):** prefer `.xlsx`.
- **Railway:** Invantive Data Hub is not what we deploy on Railway. Railway runs `acfo` for Exact. Excel loads stay on the PC/server that has Data Hub and the files.
- **Do not** mix this with Exact Incremental in one `create or replace` unless you intend to overwrite.

## After the load

Query in Supabase:

```sql
select * from excel_sales_estimates;
```

Add RLS if the table is in `public` and you expose PostgREST. The loader uses `postgres` and ignores RLS.

If the sheet is actually an Exact export, prefer `TransactionLinesIncremental` over Excel. Use Excel only for data that does **not** live in Exact (budgets, forecasts, lists, work-order intakes).
