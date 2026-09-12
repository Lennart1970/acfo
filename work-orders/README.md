# Work orders for Microsoft administrators

These are **phase 2**. The MVP does not need them. The same text is seeded in Supabase `public.work_orders` so you can track status in the dashboard (`ready` → `done`).

| Code | Title |
| --- | --- |
| [WO-001](WO-001-copilot-studio.md) | Approve Copilot Studio and Teams hosting |
| [WO-002](WO-002-entra-readonly.md) | Read-only Entra app for the ledger API |
| [WO-003](WO-003-copilot-postgrest.md) | Copilot tool on `transaction_lines_incremental` |
| [WO-004](WO-004-optional-azure-sql.md) | Optional Azure SQL knowledge replica |

Do not give admins the Supabase `service_role` key or the official Supabase MCP URL. Those are developer credentials.
