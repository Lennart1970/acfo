-- ACFO HQ tables. Named hq_* so they do not collide with ledger / work_orders.

create table if not exists public.hq_projects (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    slug text not null unique,
    summary text not null default '',
    github_pr_url text,
    default_ref text not null default 'main',
    slack_channel_id text,
    slack_channel_name text,
    grok_invited boolean not null default false,
    created_at timestamptz not null default now()
);

create table if not exists public.hq_messages (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references public.hq_projects(id) on delete cascade,
    author text not null,
    title text not null,
    body text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.hq_message_comments (
    id uuid primary key default gen_random_uuid(),
    message_id uuid not null references public.hq_messages(id) on delete cascade,
    author text not null,
    body text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.hq_plans (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    raw_markdown text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.hq_todos (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references public.hq_projects(id) on delete cascade,
    title text not null,
    body text not null default '',
    status text not null default 'open'
        check (status in ('open', 'handed_over', 'in_progress', 'done')),
    source_plan_id uuid references public.hq_plans(id) on delete set null,
    created_at timestamptz not null default now()
);

create table if not exists public.hq_handovers (
    id uuid primary key default gen_random_uuid(),
    todo_id uuid not null references public.hq_todos(id) on delete cascade,
    slack_channel_id text,
    slack_thread_ts text,
    slack_permalink text,
    cursor_agent_id text,
    cursor_agent_url text,
    cursor_status text,
    notes text,
    created_at timestamptz not null default now()
);

create table if not exists public.hq_slack_installations (
    id uuid primary key default gen_random_uuid(),
    team_id text not null unique,
    team_name text not null,
    bot_token text not null,
    created_at timestamptz not null default now()
);

alter table public.hq_projects enable row level security;
alter table public.hq_messages enable row level security;
alter table public.hq_message_comments enable row level security;
alter table public.hq_plans enable row level security;
alter table public.hq_todos enable row level security;
alter table public.hq_handovers enable row level security;
alter table public.hq_slack_installations enable row level security;

create policy hq_projects_authenticated on public.hq_projects
    for all to authenticated using (true) with check (true);

create policy hq_messages_authenticated on public.hq_messages
    for all to authenticated using (true) with check (true);

create policy hq_message_comments_authenticated on public.hq_message_comments
    for all to authenticated using (true) with check (true);

create policy hq_plans_authenticated on public.hq_plans
    for all to authenticated using (true) with check (true);

create policy hq_todos_authenticated on public.hq_todos
    for all to authenticated using (true) with check (true);

create policy hq_handovers_authenticated on public.hq_handovers
    for all to authenticated using (true) with check (true);

-- Slack bot tokens are server-only (service role). No authenticated policies.

insert into public.hq_projects (name, slug, summary, github_pr_url, default_ref)
values
    (
        'Exact sync → SQL → web',
        'exact-sync',
        'Exact Online → Railway cron → Supabase → web view. The main aCFO pipeline (PR #1).',
        'https://github.com/Lennart1970/acfo/pull/1',
        'cursor/exact-online-mysql-sync-4963'
    ),
    (
        'Copilot Excel / dagoverzicht',
        'excel-mvp',
        'v1 daily booking skill: Excel dagoverzicht and Copilot scoring (PR #2).',
        'https://github.com/Lennart1970/acfo/pull/2',
        'cursor/copilot-excel-mvp-bc25'
    ),
    (
        'Booking weekoverzicht v2',
        'weekoverzicht',
        'Weekly Excel upload → ISO week → Auto / AI / Human review routes (PR #3).',
        'https://github.com/Lennart1970/acfo/pull/3',
        'cursor/booking-weekoverzicht-v2-b1a5'
    ),
    (
        'Cloud Agent env setup',
        'env-setup',
        'Cursor Cloud Agent environment: local Postgres, install/start scripts (PR #4).',
        'https://github.com/Lennart1970/acfo/pull/4',
        'cursor/dev-environment-setup-20b3'
    ),
    (
        'MS admin work orders',
        'ms-work-orders',
        'Phase 2 queue for Microsoft admins: Copilot Studio, Entra, PostgREST, Power Platform (WO-001–005).',
        'https://github.com/Lennart1970/acfo/pull/1',
        'cursor/exact-online-mysql-sync-4963'
    )
on conflict (slug) do nothing;
