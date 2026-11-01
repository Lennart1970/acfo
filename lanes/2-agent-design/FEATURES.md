# Lane 2 — Features (agent behaviour)

## Patterns this lane owns

| Pattern | Intent |
| --- | --- |
| Role & tool contracts | What each agent may call; grounding rules when tools return empty/partial data |
| Routing | Automate / AI review / human review (or equivalent) with explicit criteria |
| Evidence | Structured capture of inputs, recommendations, overrides, and outcomes |
| Swarm handoffs | Clear ownership when multiple agents collaborate on one case |
| Skill packaging | Cursor / Copilot Studio skill shapes suitable for reuse across domains |

## Design norms

- Prefer **deterministic validators** beside the model for numbers, ids, and policy checks
- Prefer **small closed loops** (observe → decide → act or escalate → record) over open chat
- Prefer **tool-grounded** answers; inventing business facts is a defect
- Prefer **domain-agnostic** templates; product loops instantiate these patterns elsewhere

## Explicit non-features

- Product-specific playbooks and client process maps are out of scope for this lane’s FEATURES
- Live prompts with tenant or customer data must not land in git
