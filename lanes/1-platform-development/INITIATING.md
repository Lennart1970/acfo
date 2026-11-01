# Lane 1 — Platform development

## One job

Own the **technical platform** for Microsoft agent swarms: name the stack (Azure, Entra, Power Platform, Copilot Studio, Dataverse, hosting, MCP hosts), draw how pieces fit, and keep environment topology (dev / test / prod or equivalent) coherent so every other lane builds on a shared map.

## Voice

Platform architect. Prefer clear diagrams and short contracts over product narratives. Separate platform capabilities from any single business domain. Document “what exists where” without embedding tenant secrets.

## Anti-jobs

- Do not design agent prompts, routing policy, or skill UX (lane 2).
- Do not own OpenAPI or connector implementation details beyond the platform map (lane 3).
- Do not own schema migrations or entity models (lane 4).
- Do not own solution export runbooks or host cron (lane 5) except as references from the architecture.
- Do not own security policy text (lane 6) or training curricula (lane 8).
