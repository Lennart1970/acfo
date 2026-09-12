# Recommendation: Exact entries → Microsoft Copilot agents

Do **not** land this in MySQL if Copilot is the consumer. Copilot Studio can ground on **Azure SQL**, **Dataverse**, and **Fabric / Power BI semantic models**. MySQL is only reachable as a custom action, not as structured knowledge.

Do **not** let the agent query Exact Online live. Copilot will explore with many queries; Exact allows 60 calls/minute and 5,000/day. Put a replica in a Microsoft store, then point the agent at that.

## Recommended path

**Invantive Data Hub → Azure SQL → Copilot Studio knowledge → Teams**

1. Keep Invantive. Copy `TransactionLinesIncremental` (and `GLAccountsIncremental`) into **Azure SQL**, not MySQL. Same SQL as `invantive/copy-recommended-tables.sql`, alias `@sqlserver` instead of `@mysql`.
2. In Copilot Studio, add **Azure SQL tables as knowledge**: `transaction_lines_incremental`, `gl_accounts_incremental`. Use clear column names and a short glossary (`AmountDC` = bedrag in administratievaluta, `Type 40` = bank/cash, `LineNumber 0` = kopregel).
3. Publish the agent to Teams. Authenticate with Microsoft so the SQL connection uses the maker/user path Copilot Studio documents.

That matches how you already used Invantive, and it matches how Copilot Studio reads tabular finance data today.

[Azure SQL as Copilot Studio knowledge](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/knowledge-add-azure-sql-tables)

## If you already pay for Fabric / Power BI Premium

Same Azure SQL (or a Fabric Warehouse) → Power BI semantic model with measures (omzet, kosten, banksaldo) → **Fabric data agent** → add that agent as a **tool** in Copilot Studio (Fabric IQ / connected agent).

Better for “what was gross margin last quarter?” because measures live in the model. Needs Fabric F2+ or P1. Heavier than Azure SQL knowledge.

## Can you use Supabase instead?

Yes. Supabase is Postgres. Invantive already has a PostgreSQL driver, so Data Hub can load Exact Incremental tables there the same way it would load SQL Server:

```sql
create or replace table transaction_lines_incremental@pg
as
select *
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
```

Connection is the Supabase **database** URI (`db.<project>.supabase.co`, port 5432, SSL, database `postgres`), not the anon REST key. Use a dedicated loader role (or the database password). Do not load through the `anon` key. Allow the Data Hub machine’s IP in Supabase network restrictions.

For Copilot:

- Copilot Studio has **no** native “Supabase knowledge” picker. Azure SQL still wins if you want one-click grounding.
- You *can* add [Supabase MCP](https://supabase.com/docs/guides/getting-started/mcp) (`https://mcp.supabase.com/mcp`) as a Copilot Studio MCP tool. Supabase themselves say **do not give that MCP to end users**: it runs with *your* developer permissions, not the agent user’s. Fine for you in Cursor; wrong for a Teams agent.
- The safe Copilot path on Supabase is **PostgREST as a tool**: expose a read-only view (`line_number > 0`), enable RLS, and add `https://<project>.supabase.co/rest/v1` as an OpenAPI / custom connector (or a small PostgREST MCP). The agent queries filtered ledger rows; it does not get `execute_sql` on the whole project.

Use Supabase if you already live there (auth, apps, RLS). Use Azure SQL if the only consumer is Copilot Studio.

## What to skip

| Approach | Why not |
| --- | --- |
| MySQL + `acfo` | Wrong store for Copilot. Extra OAuth you must run. |
| Live Exact MCP (CData, Exact AI Connect, etc.) | Fine for one lookup. Dies on “all bookings this year” (API limits). Vendor in the middle. |
| Exact Online Premium Power BI connector | Needs Exact Premium + gateway + IP allow list. Invantive Incremental is simpler if you already have it. |
| Dumping entries into SharePoint PDFs | RAG over documents, not a ledger. Totals will be wrong. |

## What the agent can answer well

After the replica exists, ground it on **lines with `LineNumber > 0`** (skip headers) and teach it:

- Trial balance / P&L: `sum(AmountDC)` by `GLAccountCode` and `FinancialYear`
- Bank: `Type = 40`
- Open vs processed: `Status` 20 / 50
- Filter by `Date`, `JournalCode`, `AccountName`

Do not expose raw GUIDs as the only keys; keep `GLAccountCode`, `JournalCode`, `EntryNumber` in the knowledge tables.