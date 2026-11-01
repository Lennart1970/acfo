# Lane 3 — Features (connectors & APIs)

## Surfaces this lane owns

| Surface | Role |
| --- | --- |
| Custom connectors | Power Platform connectors over documented OpenAPI; prefer read-first |
| HTTP APIs | Backend APIs agents and flows call; documented auth (API key / Entra) |
| MCP wiring | Stdio/HTTP MCP servers for Cursor and other hosts; tool lists and scopes |
| Auth contracts | Headers, OAuth shapes, and which principals may call which operations |
| Non-goals for agents | High-privilege admin APIs and system-of-record write paths until gated |

## Design norms

- Contracts are versioned and testable; placeholders for hosts and secrets
- End-user Copilot / Teams agents get **scoped** tools, not developer MCP or `service_role`-class keys
- Write operations are explicit and reviewed with lane 6 before exposure

## Explicit non-features

- No live credentials, tenant URLs, or customer payloads in repo artefacts
- No domain-product CLI brands as the definition of this lane — keep contracts generic
