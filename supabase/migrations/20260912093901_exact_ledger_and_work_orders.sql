-- Exact Online ledger replica + Microsoft admin work orders.
-- Railway sync uses the service role / database password and bypasses RLS.
-- PostgREST (anon) is denied until a policy matches.

create table public.transaction_lines (
    id uuid primary key,
    division integer not null,
    timestamp bigint not null,
    entry_id uuid,
    entry_number integer,
    line_number integer,
    line_type smallint,
    date date,
    financial_year smallint,
    financial_period smallint,
    journal_code text,
    journal_description text,
    gl_account uuid,
    gl_account_code text,
    gl_account_description text,
    account uuid,
    account_code text,
    account_name text,
    description text,
    amount_dc numeric(19, 4),
    amount_fc numeric(19, 4),
    currency text,
    exchange_rate numeric(19, 6),
    vat_code text,
    vat_code_description text,
    vat_percentage numeric(10, 4),
    vat_type text,
    amount_vat_fc numeric(19, 4),
    amount_vat_base_fc numeric(19, 4),
    type smallint,
    status smallint,
    invoice_number integer,
    order_number integer,
    your_ref text,
    payment_reference text,
    payment_discount_amount numeric(19, 4),
    due_date date,
    cost_center text,
    cost_center_description text,
    cost_unit text,
    cost_unit_description text,
    project uuid,
    project_code text,
    project_description text,
    item uuid,
    item_code text,
    item_description text,
    quantity numeric(19, 4),
    document uuid,
    document_number integer,
    notes text,
    created timestamptz,
    modified timestamptz,
    deleted_at timestamptz,
    synced_at timestamptz not null default now()
);

create index transaction_lines_division_date_idx
    on public.transaction_lines (division, date);
create index transaction_lines_entry_number_idx
    on public.transaction_lines (entry_number);
create index transaction_lines_gl_account_code_idx
    on public.transaction_lines (gl_account_code);
create index transaction_lines_type_idx
    on public.transaction_lines (type);
create index transaction_lines_timestamp_idx
    on public.transaction_lines (timestamp);

create table public.deleted_entities (
    id uuid primary key,
    division integer,
    entity_type text,
    entity_key uuid not null,
    timestamp bigint not null,
    deleted_date timestamptz,
    synced_at timestamptz not null default now()
);

create index deleted_entities_entity_key_idx
    on public.deleted_entities (entity_key);

create table public.sync_state (
    entity text not null,
    division integer not null,
    last_timestamp bigint not null,
    last_sync_at timestamptz not null default now(),
    last_error text,
    primary key (entity, division)
);

create table public.oauth_tokens (
    name text primary key,
    access_token text not null,
    refresh_token text not null,
    expires_at timestamptz not null,
    updated_at timestamptz not null default now()
);

create table public.work_orders (
    id uuid primary key default gen_random_uuid(),
    code text not null unique,
    title text not null,
    audience text not null default 'microsoft_admin',
    status text not null default 'ready',
    sort_order integer not null default 100,
    body text not null,
    created_at timestamptz not null default now()
);

create view public.transaction_lines_incremental
    with (security_invoker = true)
as
select *
from public.transaction_lines
where deleted_at is null;

insert into public.work_orders (code, title, audience, status, sort_order, body)
values
(
    'WO-001',
    'Approve Copilot Studio and Teams hosting',
    'microsoft_admin',
    'ready',
    10,
    $wo$Phase 2 — not required for the Supabase MVP.

Enable Microsoft Copilot Studio in the tenant and allow the finance agent to be published to Teams.

Acceptance:
- Copilot Studio environment exists
- Publishing to Teams is allowed for a named security group (finance)
- Maker account can create an agent$wo$
),
(
    'WO-002',
    'Create a read-only Entra app for the ledger API',
    'microsoft_admin',
    'ready',
    20,
    $wo$Phase 2. The MVP reads Exact via Railway + Supabase. Copilot should not use the official Supabase MCP (that is a developer login).

Create an Entra app (or use Copilot Studio custom connector OAuth) that can call Supabase PostgREST as a read-only role.

Acceptance:
- App registration exists
- Redirect URI for Copilot Studio / Power Platform is registered
- Secret stored in a vault, not in email$wo$
),
(
    'WO-003',
    'Add Copilot Studio tool: PostgREST transaction_lines_incremental',
    'microsoft_admin',
    'ready',
    30,
    $wo$Phase 2. In Copilot Studio, add a custom connector / OpenAPI tool:

GET https://<project-ref>.supabase.co/rest/v1/transaction_lines_incremental
Headers: apikey + Authorization Bearer <publishable or user JWT>
Prefer: count=exact
Query: date=gte.2026-01-01, line_number=gt.0, select=date,journal_code,entry_number,gl_account_code,gl_account_description,account_name,description,amount_dc,type

Do not add execute_sql. Do not use service_role in Copilot.

Acceptance:
- Agent answers "bank bookings last month" from Type = 40
- Agent cannot write or see oauth_tokens$wo$
),
(
    'WO-004',
    'Optional later: replica to Azure SQL for native Copilot knowledge',
    'microsoft_admin',
    'draft',
    40,
    $wo$Only if PostgREST-as-a-tool is not enough. Copy the same Incremental table to Azure SQL and add it as Copilot Studio knowledge.

The source of truth for the MVP stays Supabase.$wo$
);

alter table public.transaction_lines enable row level security;
alter table public.deleted_entities enable row level security;
alter table public.sync_state enable row level security;
alter table public.oauth_tokens enable row level security;
alter table public.work_orders enable row level security;

-- Readers: JWT app_metadata.acfo_role = reader (not user_metadata).
create policy transaction_lines_reader_select
    on public.transaction_lines
    for select
    to authenticated
    using ((auth.jwt() -> 'app_metadata' ->> 'acfo_role') = 'reader');

create policy work_orders_reader_select
    on public.work_orders
    for select
    to authenticated
    using ((auth.jwt() -> 'app_metadata' ->> 'acfo_role') = 'reader');

revoke all on public.transaction_lines from anon, authenticated;
revoke all on public.deleted_entities from anon, authenticated;
revoke all on public.sync_state from anon, authenticated;
revoke all on public.oauth_tokens from anon, authenticated;
revoke all on public.work_orders from anon, authenticated;
revoke all on public.transaction_lines_incremental from anon, authenticated;

grant select on public.transaction_lines to authenticated;
grant select on public.transaction_lines_incremental to authenticated;
grant select on public.work_orders to authenticated;
