---
name: booking-weekoverzicht
description: >
  Exact-inkoopboekingen reviewen vanuit een geüpload Excel-bestand (v2).
  Gebruiker uploadt Exact-transacties. Agent vraagt welke week. Python scoort
  met Booking Confidence en schrijft weekoverzicht + uitkomst per transactie.
  Gebruik bij "review deze Excel", "welke week", "weekoverzicht inkoop",
  "check week 37", "Human Review". Geen LedgerBotje. Geen Exact-schrijven.
  Score draait in scripts/review_week.py, niet in het model.
---

# Booking check v2 — Excel-upload, weekreview

Opvolger van `booking-dagoverzicht`. Geen Exact-API. Geen LedgerBotje.

Patroon: **gebruiker levert Excel, skill-Python = logica, Excel = resultaat.**

1. Gebruiker uploadt een Exact-inkoopexport (`.xlsx`).
2. Agent vraagt **welke week** (ISO, ma–zo).
3. Python filtert die week, scoort elke boeking tegen de rest van het bestand, schrijft `.xlsx`.
4. Agent geeft weekoverzicht + uitkomst per transactie. Cijfers komen uit Python, niet uit het model.

Het model mag GL/btw/bedrag **niet** zelf verzinnen of nalopen.

## Flow (altijd deze volgorde)

### 1. Wacht op Excel

Vraag om een Exact-export van inkoopboekingen of transactieregels. Zonder bestand: stop en vraag de upload.

Geen Exact-tools, geen `financial_purchase_search`, geen 122-tools-lus.

### 2. Vraag welke week

Eerst weken tonen. **Niet** zelf een week kiezen, ook niet als er maar één week in het bestand zit.

```bash
python3 scripts/review_week.py --input "$UPLOAD" --json
```

Exitcode **3** + JSON met `needs_week: true` en `weeks[]` (`week`, `label`, `start`, `end`, `entries`).

Vraag in het Nederlands, bijvoorbeeld:

> Welke week wil je reviewen? In dit bestand staan: week 36 (1–7 september 2026, 8 boekingen), week 37 (8–14 september 2026, 12 boekingen).

Gebruiker mag antwoorden met `2026-W37`, `week 37`, of een datum in die week (`12 september`).

### 3. Review die week (één Python-run)

```bash
python3 scripts/review_week.py --input "$UPLOAD" --week 2026-W37 --output Weekoverzicht-2026-W37.xlsx --json
```

`--week` accepteert `2026-W37`, `week 37`, `37-2026`, of `2026-09-12`.

Python doet intern:

- parse Exact-kolommen (NL/EN én Invantive TransactionLines: Datum, Boekingnummer, Accountnaam, Bedrag Administratie Munteenheid, Grootboekrekening Code, BTW-code, …)
- groepeert regels tot boekstukken (`Boekingnummer`); bij dubbel boekhouden is het factuurbedrag de crediteurenregel, niet de som van alle regels
- standaard alleen inkoopdagboeken **40 / 41** (Purchases) als die in het bestand zitten (`--scope auto`)
- filtert de gekozen ISO-week
- per boeking: geschiedenis = **andere rijen in hetzelfde bestand** voor dezelfde leverancier (max. 3 recente voor grootboek/btw-regels)
- `accounts_count` = 1 als de leveranciersnaam gevuld is (Excel-v2, geen `accounts_search`)
- dezelfde signaalwiskunde als v1 (`confidence_core.py`)

Niet in het model nalopen. Niet Exact of Dataverse schrijven.

### 4. Antwoord (Nederlands)

1. Week, periode, administratie (uit Excel), aantal boekingen in die week.
2. Counts **Auto / AI Review / Human Review**.
3. **Uitkomst per transactie:** boekstuk, leverancier, bedrag, route, confidence, afwijkende signalen.
4. Het `.xlsx` (bladen Overzicht, Boekingen, Uitkomsten).
5. Exact is niet geraadpleegd en niet gewijzigd.

## Routes (ongewijzigd t.o.v. v1)

- **Auto** — confidence ≥ 0.9 én bekende leverancier én signalen eens (≥ 75%)
- **AI Review** — 0.6–0.9 onder dezelfde voorwaarden
- **Human Review** — anders (geen leverancier, te weinig agreement, of lage score)

Signalen: bekende leverancier, eerder geboekt, grootboek, btw, bedragband, cadence, omschrijving, valuta/betaling, geen bijzondere afwijking.

Eerste boeking van een leverancier in het bestand heeft geen geschiedenis → meestal Human Review.

## Weigeren

Exact wijzigen, crediteur aanmaken, LedgerBotje/`financial_purchase_*` aanroepen, 122 tools verkennen, GL/btw/bedrag uit het hoofd schatten.

## Bestanden in deze zip

- `SKILL.md` — deze instructie
- `scripts/confidence_core.py` — signaalwiskunde (geen netwerk)
- `scripts/excel_transactions.py` — Exact-Excel lezen, weken, cases
- `scripts/write_weekoverzicht.py` — week-Excel
- `scripts/review_week.py` — CLI (eerst weken, daarna score)
