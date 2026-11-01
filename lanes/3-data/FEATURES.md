# Lane 3 — Features (grounded in acfo)

## Exact → SQL replica (SoR extract, not SoR itself)

| Artifact | Role |
| --- | --- |
| `supabase/migrations/20260912093901_exact_ledger_and_work_orders.sql` | Tables/views for sync path, RLS, `work_orders` |
| `transaction_lines` / `transaction_lines_incremental` | Sync upsert + soft-delete replica (acfo sync) |
| `transaction_lines_invantive` | Invantive Data Hub path (`LEDGER_SOURCE`) |
| `deleted_entities`, `sync_state`, `oauth_tokens` | Sync bookkeeping; tokens not for Copilot |
| `python -m acfo init-db` | Apply schema locally / against `DATABASE_URL` |
| `invantive/copy-to-supabase.sql` (and related) | Incremental copy playbooks |

## MVP intent (`docs/intent.md`)

Pipeline: Exact → Invantive or `acfo sync` → Supabase Postgres → web view. Copilot consumes replica/tool, not live Exact.

## Dataverse SoW (Project context — target model)

Keep small; extend only when a loop needs it:

- Client, Company/Administration  
- Transaction Reference (pointers, not full ledger clone)  
- Accounting Exception, Agent Decision, Human Decision  
- AP Conversation, Process Event  

Publisher/prefix preference: `acfo_` inside solution **aCFO Hands-Free Accounting**.

## Optional MS path

- WO-004: Azure SQL knowledge replica for Copilot Studio (optional; Supabase remains MVP SoT for the sync).
