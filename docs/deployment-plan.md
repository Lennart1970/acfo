# Deployment plan

```
Exact Online → Invantive Data Hub → Supabase (SQL) → Railway `acfo web` → Power Platform
                                                        └── review-transactions skill
```

Nothing below is connected yet. This environment has no Invantive login, no Railway token, no Exact App Center secret, no `DATABASE_URL`.

## Stage 0 — Inputs you provide

| Item | Where it comes from | Used by |
| --- | --- | --- |
| Exact App Center Client ID + Secret | apps.exactonline.com → private app. Redirect `https://clientredirect.invantive.com` for Invantive | Invantive `@eol` |
| Invantive licence with **Data Hub** | Office Premium or Data Hub subscription. Office for Entrepreneurs / Data Loader alone have no scheduler | Stage 1 |
| Supabase project + database password | Dashboard → Connect. Data Hub: direct host `db.<ref>.supabase.co:5432`. Railway: **session pooler** `…pooler.supabase.com:5432` | Stage 1, 2 |
| Railway project on this repo | railway.com → New project → GitHub repo | Stage 2 |
| `LEDGER_API_KEY` | `openssl rand -hex 32` | Stage 2, 4 |
| Power Platform maker + environment | Microsoft admin | Stage 4 |

## Stage 1 — Extract: Exact → Invantive → Supabase

Machine: any Windows/macOS/Linux box that runs 24/7 (or a small VM). Invantive Cloud cannot run Data Hub for you.

1. Install **Data Hub (.NET 6 build)**. Copy `invantive/settings-distributed.example.xml` to `~/invantive/settings-acfo.xml`; fill `@eol` and uncomment `@pg` with the Supabase **database password** (not the anon key). Allow the machine IP in Supabase → Network restrictions.
2. Apply the schema once: `python -m acfo init-db` with `DATABASE_URL`, or `supabase db push`. This creates RLS, `work_orders`, and the `acfo sync` tables. Invantive writes its own table next to them.
3. First load: run `invantive/copy-to-supabase.sql` in Query Tool. It writes **`transaction_lines_invantive`** (snake_case, same columns the web view reads) plus `gl_accounts_invantive`. Large administrations: first Incremental fill can hit the 5,000 calls/day cap; Invantive resumes next day.
4. Schedule the same script with Data Hub (cron / Task Scheduler), hourly or nightly. After the first run Incremental costs ~2 Exact calls per division.

Check: `select count(*), max(modified) from transaction_lines_invantive;` in the Supabase SQL editor.

Fallback without Invantive: Railway cron `python -m acfo sync` fills `transaction_lines` instead (`docs/railway.md`). Then leave `LEDGER_SOURCE` unset.

## Stage 2 — Serve: Railway web view

One **always-on** Railway service (not cron), Dockerfile build, start command:

```
python -m acfo web --host 0.0.0.0 --port $PORT
```

Variables:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | Supabase **session pooler** URI (port 5432) |
| `LEDGER_SOURCE` | `transaction_lines_invantive` (Invantive path) — omit for `acfo sync` |
| `LEDGER_API_KEY` | random secret; required for `/api/lines` |
| `EXACT_*` | not needed for `web` |

Generate a public domain in Railway → Settings → Networking. Open `https://<domain>/` → the page asks for the key once (stored in the browser session). `/health` is public and shows `source`.

Check: `curl -H "X-Api-Key: $KEY" "https://<domain>/api/lines?type=40&limit=5"`.

## Stage 3 — Review with booking-weekoverzicht

The skill from Drive (`booking-weekoverzicht.zip`) lives at `.cursor/skills/booking-weekoverzicht/`. It scores **inkoopdagboek 40/41** (not Exact Type 40 bank). Python scores; the model does not invent GL/btw/bedrag.

Against the replica (after Stage 2):

```bash
export LEDGER_URL=https://<railway-domain>
export LEDGER_API_KEY=…
python3 .cursor/skills/booking-weekoverzicht/scripts/review_week.py --from-sql --json
# then, after the user picks a week:
python3 .cursor/skills/booking-weekoverzicht/scripts/review_week.py --from-sql --week 2026-W23 --output Weekoverzicht-2026-W23.xlsx --json
```

Without SQL: upload Invantive `gmr-eol-transaction-lines.xlsx` and pass `--input`. Same grouping: Boekingnummer, factuurbedrag = abs(crediteurenregel 1300), kostenregel for GL/btw. Routes: Auto / AI Review / Human Review.

## Stage 4 — Power Platform

Hand `work-orders/WO-005-power-platform-connector.md` to the Microsoft admin:

1. Import `powerplatform/acfo-ledger-swagger.json` as a **custom connector**; set Host to the Railway domain.
2. Security = API Key header `X-Api-Key`; the key lives in the **connection**, not in the file.
3. Build a Power App (gallery on `GetLedgerLines`) or add the connector as a **Copilot Studio tool**.
4. Copilot never gets Exact, Invantive, or Supabase `service_role` credentials. If they later want native Copilot *knowledge*, that is WO-004 (Azure SQL replica), not this connector.

## Order of work

1. Stage 0 inputs → 2. Stage 1 first load → 3. Stage 2 Railway → 4. Stage 3 review → 5. Stage 4 connector.

Stages 1 and 2 are independent once Supabase exists; the web view runs in demo mode until the table has rows.

## Not in this plan

- Excel / `exceltable`
- MySQL
- Live Exact calls from the web view, Power Platform, or Copilot
- Official Supabase MCP for Microsoft users
