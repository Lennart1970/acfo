---
name: booking-dagoverzicht
description: >
  Exact-inkoopboekingen van één datum: Excel-dagoverzicht, of Booking Confidence
  via sandbox-Python. Gebruik bij "check 9 september", "boekingen in Excel",
  "score deze dag", "Human Review", "dagoverzicht Whiffle". LedgerBotje haalt
  JSON op. Python in de sandbox filtert, scoort en schrijft .xlsx. Geen Exact-schrijven.
  Geen 122-tools-lus. Score draait in scripts/score_from_case.py, niet in het model.
---

# Booking check — skill + sandbox Python

Ontwikkelpatroon: **tools = I/O (Exact lezen), skill-Python = logica, Excel = resultaat.**

De Copilot-sandbox heeft geen netwerk. `requests` komt er niet uit. Daarom:

1. LedgerBotje-**tool** haalt boekings-JSON op.
2. Packaged Python (`scripts/`) runt op die JSON.
3. `.xlsx` gaat terug in de chat.

Zelfde signaalwiskunde als Cursor: `confidence_core.py` (meegezipped vanuit `acfo/scripts/confidence_core.py`). Het model mag GL/btw/bedrag **niet** zelf verzinnen.

## Wanneer lijst, wanneer score

| Gebruiker vraagt | Modus | Script |
|---|---|---|
| overzicht, Excel, wat stond er | **lijst** | `write_dagoverzicht.py` |
| check, score, confidence, Human Review, Auto | **score** | `score_from_case.py` (na bounded fetch) |

Administraties: Whiffle B.V. `3919124`, Whiffle Holding B.V. `4011167`.

Weigeren: Exact wijzigen, crediteur aanmaken, 122 tools verkennen.

## Modus lijst (max 3 LedgerBotje-calls)

1. Optioneel `admin_list` / `admin_current`
2. Optioneel `admin_switch` (`administrationCode` als string)
3. **Eén** `financial_purchase_search`:

```json
{"query": "*","sortBy": "entryDate","sortDirection": "desc","limit": 50,"context": "aCFO dagoverzicht inkoop"}
```

JSON naar `search.json`. `entryNumber` als string. Datumfilter in Python.

```bash
python3 scripts/write_dagoverzicht.py --date YYYY-MM-DD --admin 3919124 --input search.json --output BookingCheck-YYYY-MM-DD.xlsx
```

## Modus score (bounded fetch, daarna één Python-run)

Eerst de lijst-stap (boven), filter op datum. Cap **5** matched entries (LedgerBotje 60/min).

Per matched boekstuk, **niet** per signaal, deze calls (entryNumber altijd string):

1. `financial_purchase_get` {entryNumber}
2. `accounts_search` {query: supplierName, type: "supplier"}
3. `financial_purchase_search` {query: supplierName, limit: 20, sortBy: "entryDate", sortDirection: "desc"}
4. Voor de **3** nieuwste history-hits (huidig boekstuk eruit): `financial_purchase_get`

Zet alles in `cases.json`:

```json
{
  "date": "YYYY-MM-DD",
  "administrationCode": "3919124",
  "searched": 50,
  "cases": [
    {
      "entry": {},
      "lines": [],
      "accounts_count": 1,
      "history": [],
      "history_lines": []
    }
  ]
}
```

`history` = search-results minus huidig entryNumber. `history_lines` = `lines` van die max-3 gets. `accounts_count` uit accounts_search.

**Eén** keer:

```bash
python3 scripts/score_from_case.py --input cases.json --output BookingCheck-YYYY-MM-DD.xlsx --json
```

Niet in het model nalopen. Niet Dataverse schrijven (Default heeft de aCFO-tabellen niet).

## Antwoord (Nederlands)

1. Datum, administratie, aantal op datum.
2. Bij score: counts Auto / AI Review / Human Review + Human Review-regels.
3. Het `.xlsx`.
4. Exact is niet gewijzigd.

## Bestanden in deze zip

- `SKILL.md` — deze instructie
- `scripts/confidence_core.py` — signaalwiskunde (geen netwerk)
- `scripts/score_from_case.py` — score + Excel
- `scripts/write_dagoverzicht.py` — lijst + Excel
