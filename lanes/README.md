# aCFO agent colony — lanes

This repository is an **agent colony** for developing and deploying swarms of agents in the Microsoft environment (Power Platform, Copilot Studio, Azure) around Exact Online as the financial system of record.

North star (Project context): **Exact = System of Record**, **Dataverse = System of Work**, progressive hands-free accounting — Observe → Measure → Assist → Automate → Learn → Expand.

## Colony rules

1. **Lanes are fixed specialisms; agents are not lanes.**  
   An agent picks up work *in* a lane. It does not become the lane. Lane folders and labels stay stable; agents rotate.

2. **Read `STATUS.md` before work.**  
   Before starting a task in a lane, read that lane’s `STATUS.md` (and `INITIATING.md` / `FEATURES.md` as needed). Do not invent prior state.

3. **Write a `STATUS.md` entry after work.**  
   Append an entry with **agent id** and **date** (UTC). Summarize what changed, what is blocked, and what the next agent should know. Do not rewrite history; append.

4. **GitHub issues and PRs with lane labels are the coordination interface.**  
   Use labels matching lane folders (for example `lane:1-agent-design`). Discuss and assign work on issues/PRs — not in private chats that leave no trail.

5. **A PR that touches several lanes updates each affected lane’s `STATUS.md`.**  
   Cross-cutting changes still leave a STATUS trail in every lane whose specialism was exercised.

6. **Only Lennart merges.**  
   Agents open PRs; they do not merge to `main`.

7. **No secrets, tenant ids, credentials, or client data in the repo.**  
   Use `.env.example` / connection placeholders only. Never commit tokens, Exact secrets, Supabase keys, Railway keys, Entra client secrets, ledger API keys, division/tenant identifiers that identify a live client, or accounting extracts with client data.

## Lanes

| Lane | Job (one line) |
| --- | --- |
| [1-agent-design](1-agent-design/) | Design Copilot Studio / Cursor agent behaviour and closed operational loops |
| [2-connectors-apis](2-connectors-apis/) | Exact, LedgerBotje MCP, ledger HTTP, Power Platform connectors and MCP wiring |
| [3-data](3-data/) | Exact SoR, Supabase replica, Dataverse SoW schema and migrations |
| [4-alm-deployment](4-alm-deployment/) | Railway, Invantive/sync deploy, solution packaging and environment promotion |
| [5-security-governance](5-security-governance/) | AuthZ boundaries, RLS, read-only paths, secret hygiene, segregation of duties |
| [6-evaluation](6-evaluation/) | Booking confidence, metrics, override learning, human-touch measures |

## Lane folder contract

Each lane has exactly:

- `INITIATING.md` — one job, voice, anti-jobs
- `FEATURES.md` — tools, skills, connectors, and what this lane can do *today* in acfo
- `STATUS.md` — append-only current state

## Suggested GitHub labels

Create (once) labels: `lane:1-agent-design`, `lane:2-connectors-apis`, `lane:3-data`, `lane:4-alm-deployment`, `lane:5-security-governance`, `lane:6-evaluation`.
