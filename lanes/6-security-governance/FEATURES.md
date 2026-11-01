# Lane 6 — Features (security & governance)

## Control catalogue (colony defaults)

| Control | Intent |
| --- | --- |
| Secrets via env / placeholders | Never commit tokens or client secrets |
| Least-privilege connectors | Prefer GET/read; writes gated and audited |
| Agent credential split | End-user agents ≠ developer MCP / admin principals |
| RLS / row filters | Replica and work-plane data scoped by role |
| Write-back gates | System-of-record writes need authZ, materiality, audit, reversibility |
| No client data in STATUS | Append operational status without extracts |

## Development safety

Small increments; preserve auditability; prefer reversible changes; avoid destructive ops unless explicitly required and approved.
