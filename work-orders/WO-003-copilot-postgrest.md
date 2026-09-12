# WO-003 — Copilot Studio tool on PostgREST

**Audience:** Microsoft administrator  
**When:** After WO-001 and WO-002

## Ask

Add a custom connector / OpenAPI tool:

`GET https://<project-ref>.supabase.co/rest/v1/transaction_lines_incremental`

Query examples:

- `line_number=gt.0`
- `type=eq.40` (bank / cash flow)
- `date=gte.2026-01-01`

Headers: `apikey` + user JWT. Never `service_role`. Never `execute_sql`.

Teach the agent: `LineNumber 0` is a header; `AmountDC` is admin currency; `Type 40` is bank.

## Acceptance

- “Bank bookings last month” returns Type 40 lines
- Agent cannot read `oauth_tokens` or write ledger rows
