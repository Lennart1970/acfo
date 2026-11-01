# Lane 1 — Features (grounded in acfo)

## Skills (repo / published branches)

| Skill | Path | Role |
| --- | --- | --- |
| `booking-weekoverzicht` | `.cursor/skills/booking-weekoverzicht/` | Week of Exact purchase bookings → week overview + Booking Confidence (sandbox Python; no Exact write) |
| `booking-weekoverzicht-v2` | `acfo/copilot-skills/` (publish branches) | Copilot Studio zip of the week review flow |
| `booking-dagoverzicht` | `acfo/copilot-skills/` (publish branches) | Day overview / Booking Confidence for one date |
| `pack-skill-zip` | `.cursor/skills/` (publish branches) | Package `SKILL.md` folders for Copilot Studio upload |

## Behaviour patterns already documented

- **Booking Confidence routes:** Auto / AI Review / Human Review (skill + Project north star).
- **Score in Python, not the model:** `scripts/review_week.py` — model must not invent GL/btw/bedrag.
- **Sources:** SQL replica (`LEDGER_URL` / `DATABASE_URL`) or Invantive Excel upload (`gmr-eol-transaction-lines`).
- **Journals in scope for inkoop review:** dagboek **40/41** (not Exact Type 40 bank unless asked).
- **Copilot path:** `docs/copilot.md` — agents ground on replica/knowledge/tools, never live Exact exploration.
- **Work orders for MS admins:** `work-orders/WO-001` (Copilot Studio + Teams), `WO-003` (PostgREST tool).

## Product targets (Project context, not yet fully in repo)

- Booking Confidence closed loop: entry → confidence → exception → AI decision → human if needed → recorded outcome.
- AP Inbox Health Agent (observe/classify first).
- Copilot Studio conversational agents where appropriate; Cursor + Power Platform MCP for build orchestration.
