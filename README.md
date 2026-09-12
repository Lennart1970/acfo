# acfo

Download **Exact Online** financial transactions (grootboekmutaties) into **MySQL**.

Exact Online does not expose a MySQL dump. The supported way to get an exact copy of posted transactions is the REST API: OAuth 2.0, then the **Sync** `TransactionLines` endpoint, then upsert into your own database.

## Recommended path

| Step | What | Why |
| --- | --- | --- |
| 1 | Register a **private app** in the [Exact App Center](https://apps.exactonline.com/) | Required for Client ID / Secret. Until Exact reviews a public app, it only works for your own subscription. |
| 2 | OAuth authorization-code flow | Access tokens last **10 minutes**. Refresh tokens last up to **1 year** and **rotate on every refresh** — always persist the new refresh token. |
| 3 | `GET /api/v1/current/Me?$select=CurrentDivision` | Every later URL needs a division (administratie) id. |
| 4 | `GET /api/v1/{division}/sync/Financial/TransactionLines?$filter=Timestamp gt {ts}L` | Official incremental API. **1000 rows/call**. Timestamp is a row version, not a clock. |
| 5 | `GET /api/v1/{division}/sync/Deleted?$filter=Timestamp gt {ts}L` | Sync does **not** return deletions. Keep rows whose `EntityType` is `1` or `TransactionLines`. `EntityKey` is the original line `ID`. |
| 6 | Upsert into MySQL by `id`; soft-delete when Deleted reports the key | Keeps MySQL equal to Exact after corrections. |

Do **not** use the old `/financialtransaction/Transactions` endpoint (deprecated). The 60-row `/financialtransaction/TransactionLines` endpoint is the same data but much slower.

### Optional first load

- **Bulk**: `GET /api/v1/{division}/bulk/Financial/TransactionLines?$filter=Date ge datetime'2024-01-01T00:00:00'` (also 1000 rows/call; `$filter` is mandatory).
- **SyncTimestamp**: Exact can return a starting `Timestamp` for a `Modified` date so a first Sync can skip older history.

### Limits and rules

- **60 calls/minute** and **5,000/day** per app per division (Premium daily cap is higher).
- Calls must be **sequential**. Parallel requests are not allowed.
- Watch `X-RateLimit-Minutely-Remaining` and `X-RateLimit-Remaining`.
- Redirect URI must be **HTTPS** and match the App Center registration. Localhost is not accepted. For this CLI, Exact can 404 on redirect; paste the full redirected URL (it contains `?code=`).
- Country instances are separate: NL `start.exactonline.nl`, BE `.be`, DE `.de`, UK `.co.uk`.

Official index: [REST API resources](https://start.exactonline.nl/docs/HlpRestAPIResources.aspx).

## What this repo does

`python -m acfo` implements that path:

1. `auth` — exchange an OAuth code and store rotating tokens in `.tokens.json`
2. `init-db` — create `transaction_lines`, `deleted_entities`, `sync_state`
3. `sync` — incremental Sync + Deleted → MySQL
4. `divisions` — list administrations the token can access

`transaction_lines` stores the Sync payload as posted in Exact (amounts, VAT, journal, GL account, relation, period, type). Bank bookings, sales, purchase, and memorial entries are all transaction lines; filter on `type` or `journal_code`. Type `40` is cash flow / bank.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Fill `.env` with the App Center Client ID, Client Secret, HTTPS redirect URI, region, and MySQL settings.

Start MySQL (optional):

```bash
docker compose up -d
```

Or point `.env` at an existing server, then:

```bash
python -m acfo init-db
python -m acfo auth
python -m acfo sync
```

First load from a date (uses SyncTimestamp, or Bulk if that call is unavailable):

```bash
python -m acfo sync --from-date 2024-01-01
```

Full resync:

```bash
python -m acfo sync --full
```

Schedule `python -m acfo sync` hourly or daily. After the first run it only fetches new/changed rows.

Example reporting SQL is in `sql/example_queries.sql`.

## Alternatives (no code)

If you only need a warehouse and not this repo:

- Exact Online → Excel/CSV export (manual, not incremental)
- [Invantive Cloud / Data Hub](https://forums.invantive.com/) SQL over Exact
- Hosted ELT (Peliqan, Airbyte-style connectors)

Those still use the same APIs underneath. This project is the self-hosted MySQL version.

## Tests

```bash
pytest
```
