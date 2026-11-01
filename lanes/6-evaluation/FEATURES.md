# Lane 6 — Features (grounded in acfo)

## Booking Confidence scoring (exists)

| Piece | Role |
| --- | --- |
| `.cursor/skills/booking-weekoverzicht/scripts/review_week.py` | Deterministic week score; routes Auto / AI Review / Human Review |
| Excel or SQL inputs | Invantive `gmr-eol-transaction-lines` or ledger replica via `LEDGER_URL` / `DATABASE_URL` |
| Grouping rules | Boekingnummer; factuurbedrag = abs(crediteurenregel); kostenregel for GL/btw |
| Scope default | Inkoopdagboek 40/41 |

Related: `booking-dagoverzicht` / `booking-weekoverzicht-v2` on publish branches for Copilot packaging.

## Conceptual signals (Project context §6)

Known supplier, historical GL/VAT, amount range, timing/frequency, description similarity, currency/payment normality, multi-signal agreement — History → Pattern → Confidence → Anomaly → Investigation → Intervention.

## Target measures (Project context §16)

- Human touches per 1,000 transactions  
- Hands-free percentage  
- AI resolution rate  
- Override rate  
- Error rate / exception rate  
- Human minutes per exception  
- Client response burden  
- AP workload and response time  

## Learning loop (Project context §7)

Structured Agent Decision / Human Decision records: preserve original recommendation when overridden; use outcomes to move categories only with evidence.
