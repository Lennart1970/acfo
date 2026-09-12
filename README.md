# aCFO

Workspace voor aCFO booking-check skills. **v2** reviewt Exact-inkoopboekingen vanuit een geüpload Excel-bestand (geen Exact-API).

## v2 — weekoverzicht uit Excel-upload

Skill: [`acfo/copilot-skills/booking-weekoverzicht/`](acfo/copilot-skills/booking-weekoverzicht/) (`name: booking-weekoverzicht-v2`). Upload [`booking-weekoverzicht-v2.zip`](acfo/copilot-skills/booking-weekoverzicht-v2.zip) in Copilot Studio (zelfde layout als `booking-dagoverzicht.zip`: `SKILL.md` in de zip-root). Gebruik dit nieuwe bestand; de oude `booking-weekoverzicht.zip` kan in cache blijven hangen.

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

## Tests

```bash
pip install -r requirements-dev.txt
python3 -m pytest
```

## v1 (referentie)

v1 (`booking-dagoverzicht`) haalt JSON via LedgerBotje en filtert op één datum. Die skill staat op branch `cursor/copilot-excel-mvp-bc25`.
