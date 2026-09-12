# WO-002 — Read-only Entra app for the ledger API

**Audience:** Microsoft administrator  
**When:** Before wiring Copilot to Supabase PostgREST

## Ask

Create an Entra app (or Copilot Studio custom-connector OAuth) that can call Supabase PostgREST as a **read-only** caller. The MVP already loads Exact from Railway; Copilot must not use the official Supabase MCP (that runs as a developer).

## Acceptance

- App registration exists
- Redirect URI for Copilot Studio / Power Platform is registered
- Client secret stored in a vault, not email
- No `service_role` in this app
