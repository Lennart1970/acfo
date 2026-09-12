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