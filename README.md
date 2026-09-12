# aCFO

Workspace voor aCFO booking-check skills. Beide Copilot-zips hebben `SKILL.md` in de zip-root (geen extra map eromheen).

## v2 — weekoverzicht uit Excel-upload

Skill: [`acfo/copilot-skills/booking-weekoverzicht-v2/`](acfo/copilot-skills/booking-weekoverzicht-v2/). Upload [`booking-weekoverzicht-v2.zip`](acfo/copilot-skills/booking-weekoverzicht-v2.zip) in Copilot Studio.

Flow:

1. Gebruiker uploadt een Exact-export (`.xlsx`).
2. Agent vraagt welke ISO-week.
3. Python scoort die week met dezelfde Booking Confidence als v1 (geschiedenis = andere rijen in het bestand).
4. Output: weekoverzicht + uitkomst per transactie (`Weekoverzicht-YYYY-Www.xlsx`).

```bash
pip install -r acfo/requirements.txt
python3 acfo/scripts/review_week.py --input exact-inkoop.xlsx --inspect --json
python3 acfo/scripts/review_week.py --input exact-inkoop.xlsx --json
python3 acfo/scripts/review_week.py --input exact-inkoop.xlsx --week 2026-W37 --output Weekoverzicht-2026-W37.xlsx --json
```

Zonder `--week` stopt het script met de weken in het bestand (exit 3). Het model mag GL/btw/bedrag niet zelf verzinnen.

## Cursor skill — pack a SKILL.md zip

[`.cursor/skills/pack-skill-zip/`](.cursor/skills/pack-skill-zip/) packages a skill folder for Claude.ai (`--target anthropic`, nested folder) or Copilot Studio (`--target copilot`, `SKILL.md` at the zip root). Invoke `/pack-skill-zip`.

## Tests

```bash
pip install -r requirements-dev.txt
python3 -m pytest
```

## v1 — dagoverzicht via LedgerBotje

Skill: [`acfo/copilot-skills/booking-dagoverzicht/`](acfo/copilot-skills/booking-dagoverzicht/). Upload [`booking-dagoverzicht.zip`](acfo/copilot-skills/booking-dagoverzicht.zip). Haalt JSON via LedgerBotje en filtert op één datum.
