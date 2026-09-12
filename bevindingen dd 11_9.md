# Bevindingen dd 11-9

Bron: Copilot Excel MVP-workspace van de vorige agent (`lennart-wol/test`, branch `cursor/copilot-excel-mvp-b342`). Het oude remote was vanaf deze omgeving niet meer leesbaar (404 / geen token-scope). Deze notitie volgt uit de skill-zip die die agent op 11 september 2026 naar Drive/Gmail zette (`acfo/copilot-skills/booking-dagoverzicht.zip`).

## Wat er staat

De booking-check is geen chat-redenering over Exact-cijfers. Tools lezen, Python scoort, Excel is het resultaat.

- LedgerBotje haalt inkoopboekingen op (Exact **lezen**).
- De Copilot Studio-sandbox heeft **geen netwerk**; `requests` werkt daar niet.
- Score-logica zit in `acfo/scripts/confidence_core.py` (meegezipped in de skill).
- Output is `BookingCheck-YYYY-MM-DD.xlsx` (overzicht + boekingen).
- Exact wordt niet geschreven. Geen crediteur aanmaken. Geen 122-tools-verkenningslus.

## Twee modi

| Vraag | Modus | Script |
|---|---|---|
| overzicht / Excel / wat stond er | lijst | `write_dagoverzicht.py` |
| check / score / Human Review / Auto | score | `score_from_case.py` |

Lijst: max 3 LedgerBotje-calls, daarna datumfilter in Python op de search-JSON.

Score: eerst dezelfde lijst, dan per matched boekstuk een bounded fetch (cap 5 entries vanwege 60 calls/min). Daarna **één** Python-run. Het model mag GL/btw/bedrag niet zelf verzinnen of nalopen.

## Administraties (pilot)

- Whiffle B.V. `3919124`
- Whiffle Holding B.V. `4011167`

`entryNumber` altijd als string. `administrationCode` bij switch ook als string.

## Booking Confidence

Signalen (gewogen tot confidence 0–1): bekende leverancier, eerder geboekt, grootboek, btw, bedragband, cadence, omschrijving, valuta/betalingsconditie, geen bijzondere afwijking.

Routes:

- **Auto** — confidence ≥ 0.9 én bekende leverancier én signalen eens (≥ 75%)
- **AI Review** — 0.6–0.9 onder dezelfde voorwaarden
- **Human Review** — anders (onbekende leverancier, te weinig agreement, of lage score)

## Wat niet

- Dataverse schrijven: de Default-omgeving heeft de aCFO-tabellen niet.
- Exact wijzigen vanuit de skill.
- Score in het LLM in plaats van in `score_from_case.py`.

## Skill-upload

Zip voor Copilot Studio agent **aCFO Booking Check**:

`acfo/copilot-skills/booking-dagoverzicht.zip`

Add skill → Upload. Inhoud: `SKILL.md` + `scripts/confidence_core.py`, `score_from_case.py`, `write_dagoverzicht.py`.
