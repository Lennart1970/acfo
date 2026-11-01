# Lane 2 — Features (grounded in acfo)

## Exact Online (system of record access)

- CLI OAuth + rotating refresh tokens: `python -m acfo auth` (tokens → `.tokens.json` locally or `oauth_tokens` on Railway — never commit).
- Incremental Sync + Deleted: `python -m acfo sync` (`/sync/Financial/TransactionLines`, `/sync/Deleted`).
- Divisions listing: `python -m acfo divisions`.
- Env contract: `.env.example` (`EXACT_CLIENT_ID/SECRET`, redirect, region, division).
- Invantive alternative path: `invantive/` playbooks for Incremental → SQL without the Python sync.

## Ledger HTTP (Railway web view)

- `python -m acfo web` — ledger UI + `/api/lines` protected by `LEDGER_API_KEY` (`X-Api-Key`).
- OpenAPI for Power Platform: `powerplatform/acfo-ledger-swagger.json` (read-only GET; host placeholder).
- Work order: `work-orders/WO-005-power-platform-connector.md`.

## MCP / Cursor

- Repo `.mcp.json`: Supabase MCP URL (developer use; not for end-user Copilot).
- Project skill `powerplatform-mcp-connect` (Context + open PRs): Azure CLI auth → `powerplatform-mcp-server` stdio for Power Platform / Dataverse / Automate from Cursor.
- LedgerBotje MCP (Project architecture): controlled Exact access for agent/dev workflows — prefer read/analyse/recommend before any write-back.

## Copilot-facing tools (planned via work orders)

| WO | Surface |
| --- | --- |
| WO-002 | Read-only Entra app for ledger API |
| WO-003 | Copilot tool on PostgREST / `transaction_lines_incremental` |
| WO-005 | Custom connector on Railway ledger |

## Explicit non-features

- No live Exact MCP for Teams agents (`docs/copilot.md`).
- No Supabase `service_role` or official Supabase MCP for end users.
