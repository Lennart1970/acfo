# Lane 1 — Features (platform map)

## Stack surfaces this lane documents

| Layer | Typical pieces |
| --- | --- |
| Identity | Entra ID apps, delegated vs app-only, environment boundaries |
| Power Platform | Environments, solutions, Dataverse, connectors, Power Automate |
| Agents | Copilot Studio agents, Cursor / Agent SDK hosts, Teams surfaces |
| Tooling | MCP servers (Power Platform and others), custom connectors, HTTP APIs |
| Data plane | Dataverse as system of work; optional SQL / replicas as extracts — not a second SoR by default |
| Hosting | Container or PaaS runtimes for APIs, sync jobs, and agent backends |
| Observability | Logs, traces, and status hooks agents can cite without pasting secrets |

## Architecture artefacts this lane maintains

- Platform overview (components and trust boundaries)
- Environment topology (what is promoted where)
- “How pieces fit” notes: which lane owns which interface on the map
- Non-goals: product roadmaps and client-specific process playbooks live outside this lane

## Explicit non-features

- No product branding, client names, or domain-specific north stars in this lane’s docs
- No live connection strings, tenant ids, or credentials
