# aCFO

Workspace voor de aCFO Copilot Excel MVP: Exact-inkoopboekingen van één datum als Excel-dagoverzicht, optioneel met Booking Confidence-score.

Dit is de inhoud van de vorige agent-workspace (`lennart-wol/test`, branch `cursor/copilot-excel-mvp-b342`), hierheen gezet omdat dat remote vanaf deze omgeving niet meer bereikbaar was. De skill-zip stond op Drive/Gmail van 11 september 2026.

## Layout

- [`bevindingen dd 11_9.md`](bevindingen%20dd%2011_9.md) — bevindingen van 11-9
- [`acfo/scripts/`](acfo/scripts/) — signaalwiskunde en Excel-writers (geen netwerk)
- [`acfo/copilot-skills/booking-dagoverzicht/`](acfo/copilot-skills/booking-dagoverzicht/) — Copilot Studio skill (GitHub harness)
- [`acfo/copilot-skills/booking-dagoverzicht.zip`](acfo/copilot-skills/booking-dagoverzicht.zip) — uploadbestand voor agent **aCFO Booking Check**

## Lokaal Excel schrijven

```bash
pip install openpyxl
python3 acfo/scripts/write_dagoverzicht.py --date YYYY-MM-DD --admin 3919124 --input search.json --output BookingCheck-YYYY-MM-DD.xlsx
python3 acfo/scripts/score_from_case.py --input cases.json --output BookingCheck-YYYY-MM-DD.xlsx --json
```

Exact-JSON komt van LedgerBotje; deze scripts filteren, scoren en schrijven alleen `.xlsx`.
