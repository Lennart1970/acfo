# acfo

Finance / CFO tooling around Exact Online, plus **ACFO HQ** — a Basecamp-style board for the parallel workstreams.

## ACFO HQ

A Next.js app in [`hq/`](hq/) to follow projects, post updates, and hand jobs from a plan to Slack + Grok and Cursor Cloud Agents.

```bash
cd hq
npm install
npm run dev
```

Or from the repo root: `npm run dev` (same HQ server). It binds **http://0.0.0.0:3000**.

If you are on a Cloud Agent, the app runs on the remote VM. Open the plug / Ports menu and use the forwarded URL — your laptop’s `localhost:3000` is a different machine, and if that port is already taken Cursor maps HQ to another local port.

See [hq/README.md](hq/README.md) for Slack, Grok, Cursor, and Supabase setup.

The Exact sync pipeline and booking skills live on unmerged PRs. HQ tracks them; it does not replace them.
