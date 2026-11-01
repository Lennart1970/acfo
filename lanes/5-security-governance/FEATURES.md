# Lane 5 — Features (grounded in acfo)

## Already encoded controls

| Control | Where |
| --- | --- |
| Secrets only via env / `.env.example` placeholders | `.env.example`, `.gitignore` (tokens) |
| Ledger API key header; empty key = localhost only | `docs/deployment-plan.md`, swagger securityDefinitions |
| Swagger is GET-only (no write operations) | `powerplatform/acfo-ledger-swagger.json` |
| Copilot must not get Exact / Invantive / `service_role` | `work-orders/WO-005`, `docs/copilot.md`, `work-orders/README.md` |
| Supabase MCP = developer permissions, not end users | `docs/copilot.md`, `.mcp.json` note in intent |
| RLS / security_invoker views on replica | Supabase migration |
| Exact write-back deferred until authz, materiality, audit, reversibility designed | Project context §13 |
| Read-only Entra app for ledger | `work-orders/WO-002` |

## Colony rule (this tree)

No secrets, tenant ids, credentials, or client data in the repository. Agents append STATUS without pasting extracts.

## Development safety (Project context §14)

Small increments inside the aCFO solution; preserve auditability; prefer reversible changes; avoid destructive ops unless explicitly required.
