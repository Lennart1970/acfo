# acfo

Project skills for aCFO booking review. `main` previously only had this README; the skills lived on unmerged PR branches and in Drive. This commit puts every skill developed in the project on GitHub.

## Cursor skills (`.cursor/skills/`)

| Skill | What it does |
|---|---|
| [booking-weekoverzicht](.cursor/skills/booking-weekoverzicht/) | Week review of Exact purchase bookings. Excel upload, or `--from-sql` against a ledger replica. Scores Auto / AI Review / Human Review. |
| [pack-skill-zip](.cursor/skills/pack-skill-zip/) | Pack a `SKILL.md` folder into an Agent Skills zip (Copilot Studio or Anthropic). |

## Copilot Studio skills (`acfo/copilot-skills/`)

Unpacked folders plus the zip you upload in Copilot Studio (**Add skill → Upload**).

| Skill | Zip | What it does |
|---|---|---|
| [booking-dagoverzicht](acfo/copilot-skills/booking-dagoverzicht/) | [booking-dagoverzicht.zip](acfo/copilot-skills/booking-dagoverzicht.zip) | One-day purchase list or Booking Confidence. LedgerBotje fetches JSON; sandbox Python writes `.xlsx`. |
| [booking-weekoverzicht-v2](acfo/copilot-skills/booking-weekoverzicht-v2/) | [booking-weekoverzicht-v2.zip](acfo/copilot-skills/booking-weekoverzicht-v2.zip) | Excel-upload week review (Invantive `gmr-eol-transaction-lines`). Asks which ISO week, then scores. Latest revision scores **kostenregels** only (same file as Drive `booking-weekoverzicht-v2-kostenregels.zip`). |

Pattern: **tools = I/O, skill Python = scoring, Excel = result.** The model must not invent GL / VAT / amounts.

## Where these came from

- PR [#1](https://github.com/Lennart1970/acfo/pull/1) — Cursor `booking-weekoverzicht` (Excel + SQL)
- PR [#2](https://github.com/Lennart1970/acfo/pull/2) — Copilot `booking-dagoverzicht`
- PR [#3](https://github.com/Lennart1970/acfo/pull/3) — Copilot `booking-weekoverzicht-v2` + `pack-skill-zip`
- Drive — `booking-dagoverzicht.zip`, `booking-weekoverzicht-v2.zip`, `booking-weekoverzicht-v2-kostenregels.zip`
