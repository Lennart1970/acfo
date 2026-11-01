# MS agent-swarm colony — lanes

This tree is an **agent colony** for developing and deploying **swarms of agents in the Microsoft environment** (Azure, Entra ID, Power Platform, Copilot Studio, Dataverse, related MCP/tooling). Product or client work may consume the colony; the lanes themselves stay **general**.

## Colony rules

1. **Lanes are fixed specialisms; agents are not lanes.**  
   An agent picks up work *in* a lane. It does not become the lane. Lane folders and labels stay stable; agents rotate.

2. **Read `STATUS.md` before work.**  
   Before starting a task in a lane, read that lane’s `STATUS.md` (and `INITIATING.md` / `FEATURES.md` as needed). Do not invent prior state.

3. **Write a `STATUS.md` entry after work.**  
   Append an entry with **agent id** and **date** (UTC). Summarize what changed, what is blocked, and what the next agent should know. Do not rewrite history; append.

4. **GitHub issues and PRs with lane labels are the coordination interface.**  
   Use labels matching lane folders (for example `lane:2-agent-design`). Discuss and assign work on issues/PRs — not in private chats that leave no trail.

5. **A PR that touches several lanes updates each affected lane’s `STATUS.md`.**  
   Cross-cutting changes still leave a STATUS trail in every lane whose specialism was exercised.

6. **Only Lennart merges.**  
   Agents open PRs; they do not merge to `main`.

7. **No secrets, tenant ids, credentials, or client/product data in the colony docs.**  
   Use placeholders and public architecture only. Never commit tokens, client secrets, environment URLs that identify a live tenant, or extracts with customer data.

## Lanes

| Lane | Job (one line) |
| --- | --- |
| [1-platform-development](1-platform-development/) | Document and evolve the MS technical platform: stack, architecture, environments, how pieces fit |
| [2-agent-design](2-agent-design/) | Design Copilot Studio / Cursor agent behaviour and swarm operational loops |
| [3-connectors-apis](3-connectors-apis/) | Connectors, HTTP APIs, MCP wiring, and tool contracts into Microsoft and adjacent systems |
| [4-data](4-data/) | Dataverse / SQL schemas, migrations, system-of-record vs system-of-work boundaries |
| [5-alm-deployment](5-alm-deployment/) | Solution packaging, environment promotion, hosting and scheduled runbooks |
| [6-security-governance](6-security-governance/) | AuthZ boundaries, secret hygiene, RLS, approval gates, segregation of duties |
| [7-evaluation](7-evaluation/) | Scoring, KPIs, override learning, evidence that automation is earned |
| [8-training](8-training/) | Training material for people who build and use these agent swarms |

## Lane folder contract

Each lane has exactly:

- `INITIATING.md` — one job, voice, anti-jobs
- `FEATURES.md` — surfaces and capabilities this lane owns *in the general colony*
- `STATUS.md` — append-only current state

## Suggested GitHub labels

Create (once) labels: `lane:1-platform-development`, `lane:2-agent-design`, `lane:3-connectors-apis`, `lane:4-data`, `lane:5-alm-deployment`, `lane:6-security-governance`, `lane:7-evaluation`, `lane:8-training`.
