# ACFO HQ

Basecamp-style command center for the aCFO workstreams. Follow the open PRs, post updates, and hand jobs from a plan to Slack (with Grok) and a Cursor Cloud Agent.

This app lives on `main` and **does not merge** the Exact sync or booking-skill PRs. It only tracks them.

## Run locally (demo mode)

No secrets required. Demo login stores data in `.data/hq.json`.

```bash
cd hq
cp .env.example .env.local   # optional
npm install
npm run dev
```

Open http://localhost:3000, continue in demo mode, then:

1. Open each seeded project
2. Post a message and add a to-do
3. Paste a plan on **Hand over a plan** (headings, `- [ ]` checkboxes, or numbered lists)
4. Slack / Cursor stay skipped until you add keys

```bash
npm test
```

## Seeded projects

| Project | Source |
| --- | --- |
| Exact sync → SQL → web | [PR #1](https://github.com/Lennart1970/acfo/pull/1) |
| Copilot Excel / dagoverzicht | [PR #2](https://github.com/Lennart1970/acfo/pull/2) |
| Booking weekoverzicht v2 | [PR #3](https://github.com/Lennart1970/acfo/pull/3) |
| Cloud Agent env setup | [PR #4](https://github.com/Lennart1970/acfo/pull/4) |
| MS admin work orders | WO-001–005 on PR #1 |

## Hand over a plan

Paste markdown. HQ splits it into jobs, creates to-do cards, then optionally:

1. Posts a Slack thread in the project channel and @mentions Grok
2. Launches a Cursor Cloud Agent (`POST https://api.cursor.com/v1/agents`) on `https://github.com/Lennart1970/acfo` with `autoCreatePR: true`

If Slack or `CURSOR_API_KEY` is missing, the job card is still created and the skip reason is stored on the handover.

## Slack + Grok

1. Create a Slack app from [`slack-manifest.json`](slack-manifest.json) (or copy the bot scopes: `channels:manage`, `channels:read`, `chat:write`, `users:read`)
2. Set `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_REDIRECT_URI`
3. Install [Grok for Slack](https://slack.hooks.x.ai/) in the same workspace
4. Set `SLACK_GROK_USER_ID` to Grok’s Slack user id (`U…`), or leave it empty to look up a user named Grok
5. In HQ: **Add ACFO HQ to Slack** → **Create #acfo-&lt;slug&gt;** → **Invite Grok**

## Cursor

Create an API key at Cursor Dashboard → API Keys. Set `CURSOR_API_KEY`. Agents start from the project’s `default_ref` (the open PR branch) and open a new `cursor/*` branch.

## Supabase (optional)

Apply [`../supabase/migrations/20260912120000_hq_tables.sql`](../supabase/migrations/20260912120000_hq_tables.sql). Set `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`. HQ then uses Postgres instead of the JSON file.

`hq_slack_installations.bot_token` is service-role only. Do not expose it to the browser.

## Environment

See [`.env.example`](.env.example).
