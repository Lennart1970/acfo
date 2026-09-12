---
name: booking-weekoverzicht
description: >
  Exact-inkoopboekingen van één week uit een geüploade Excel: weekoverzicht
  en Booking Confidence via sandbox-Python. Gebruik bij "review deze Excel",
  "welke week", "weekoverzicht inkoop", "gmr-eol-transaction-lines",
  "Human Review". Gebruiker uploadt Exact-transacties. Python inspecteert
  bladen, vraagt de week, scoort en schrijft .xlsx. Geen LedgerBotje.
  Geen Exact-schrijven. Score draait in scripts/review_week.py, niet in het model.
---

# Booking check v2 — Excel-upload, weekreview

Opvolger van `booking-dagoverzicht`. Geen Exact-API. Geen LedgerBotje.

Patroon: **eerst Excel leesbaar maken, dan week vragen, dan Python-score.**

Het model mag GL/btw/bedrag **niet** zelf verzinnen of nalopen.

## Flow (altijd deze volgorde)

### 1. Wacht op Excel

Vraag om een Exact-export van inkoopboekingen of transactieregels. Zonder bestand: stop en vraag de upload.

Geen Exact-tools, geen `financial_purchase_search`, geen 122-tools-lus.

### 2. Maak de Excel leesbaar (vóór je een week vraagt)

Invantive `gmr-eol-transaction-lines.xlsx` is geen simpele daglijst. Eerste blad is **Parameters** (module + gebruiker), de rijen staan op **TransactionLines** (~70 kolommen, dubbel boekhouden). Zonder onderstaande stappen worden boekstukken `2026-06-01|?|?|12`, leverancier/bedrag leeg, en alles Human Review.

**2a. Inspecteer bladen en mapping**

```bash
python3 scripts/review_week.py --input "$UPLOAD" --inspect --json
```

Controleer:

1. Sla blad **Parameters** over. Data = **TransactionLines** (of Inkoop/Boekingen).
2. `mapped` moet minstens `entryDate`, `entryNumber`, `supplierName`, `amountDC` hebben.
3. `ready` is true. Zo niet: headers van TransactionLines printen, niet scoren.

**Invantive-kolommen (niet raden, dit zijn de namen):**

| Nodig voor | Kolom in Excel | Niet gebruiken |
|---|---|---|
| Datum | `Datum` | `Gemaakt`, `Gewijzigd`, `Vervaldag` |
| Boekstuk | `Boekingnummer` | `Factuurnummer`, `Rij ID`, `Uw Referentie` |
| Leverancier | `Accountnaam` | `Naam Abonnementhouder`, `Administratie Naam` |
| Bedrag | `Bedrag Administratie Munteenheid` | som van alle regels, `Bedrag Vreemde Valuta` |
| Grootboek | `Grootboekrekening Code` | `Grootboekrekening Omschrijving` |
| Btw | `BTW-code` | `BTW-bedrag…` |
| Dagboek | `Dagboekcode` / `Dagboekomschrijving` | — |
| Regel | `Regelnummer` | — |
| Administratie | `Divisie` | — |

**2b. Leesregels (anders is het bestand “gelezen” maar fout)**

- Groepeer op **Boekingnummer**. Elke regel is geen boekstuk (354 regels in week 23 ≠ 32 inkoopboekingen).
- Dubbel boekhouden: debet + credit ≈ 0. **Factuurbedrag = abs(crediteurenregel)** (GB `1300`, soort `22`), niet de som van alle regels.
- Score-GL/btw komt van de **kostenregel** (soort 110/120/…, regel ≥ 1), niet van 1300 of btw-regel `9999` / GB `1450`.
- Standaard alleen inkoopdagboek **40** (Purchases) en **41** (Purchases via MOSS). Dit bestand bevat ook 20/21/23 bank, 30 sales, 90 memoriaal, 91 payroll, 92 assets, 93 deferred sales & costs. Die horen niet in de inkoopreview tenzij de gebruiker `--scope all` vraagt.

**2c. Eerste parse-run, daarna pas week vragen**

```bash
python3 scripts/review_week.py --input "$UPLOAD" --json
```

Exitcode **3**. Lees `parse`:

- `ok: true` en `sample[].entryNumber` lijkt op Exact (`26400387`), met leverancier en bedrag → ga naar stap 3.
- `ok: false`, fallback-sleutels `datum|?|?|index`, of `amountDC` / `supplierName` leeg → headers inspecteren, mapping fixen, **niet scoren**.

### 3. Vraag welke week

Eerst weken tonen. **Niet** zelf een week kiezen, ook niet als er maar één week in het bestand zit.

JSON: `needs_week: true` en `weeks[]` (`week`, `label`, `start`, `end`, `entries`).

Vraag in het Nederlands, bijvoorbeeld:

> Welke week wil je reviewen? In dit bestand staan: week 23 (1–7 juni 2026, 32 inkoopboekingen), week 24 (8–14 juni 2026, 30 boekingen).

Gebruiker mag antwoorden met `2026-W37`, `week 37`, `eerste week`, of een datum in die week.

### 4. Review die week (één Python-run)

Alleen als `parse.ok` true is. Exitcode **4** = mapping onvolledig, stop.

```bash
python3 scripts/review_week.py --input "$UPLOAD" --week 2026-W23 --output Weekoverzicht-2026-W23.xlsx --json
```

`--week` accepteert `2026-W37`, `week 37`, `37-2026`, of `2026-09-12`.

Python daarna:

- filtert de gekozen ISO-week
- per boeking: geschiedenis = **andere inkoopboekingen in hetzelfde bestand** voor dezelfde leverancier (max. 3 recente voor grootboek/btw-regels)
- `accounts_count` = 1 als de leveranciersnaam gevuld is (geen `accounts_search`)
- dezelfde signaalwiskunde als v1 (`confidence_core.py`)

Niet in het model nalopen. Niet Exact of Dataverse schrijven.

### 5. Antwoord (Nederlands)

1. Week, periode, administratie (uit Excel), aantal boekingen in die week, scope (inkoop 40/41).
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

Exact wijzigen, crediteur aanmaken, LedgerBotje/`financial_purchase_*` aanroepen, 122 tools verkennen, GL/btw/bedrag uit het hoofd schatten, scoren terwijl `parse.ok` false is.

## Bestanden in deze zip

Zip-root (zelfde layout als `booking-dagoverzicht`; Copilot weigert een extra map eromheen):

- `SKILL.md` — deze instructie
- `scripts/confidence_core.py` — signaalwiskunde (geen netwerk)
- `scripts/excel_transactions.py` — Exact-Excel lezen, weken, cases
- `scripts/write_weekoverzicht.py` — week-Excel
- `scripts/review_week.py` — CLI (`--inspect`, daarna weken, daarna score)
