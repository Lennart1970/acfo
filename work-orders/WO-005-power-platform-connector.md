# WO-005 — Power Platform custom connector on the Railway ledger

**Audience:** Microsoft / Power Platform administrator  
**When:** After the Railway web view is live and `LEDGER_API_KEY` is set

## Ask

1. Power Apps / Power Automate → **Custom connectors** → Import an OpenAPI file → `powerplatform/acfo-ledger-swagger.json`.
2. Set **Host** to the Railway public domain of the `acfo web` service.
3. Security: **API Key**, header `X-Api-Key`. The key is created as a **connection**, typed once by the maker. Do not put it in the Swagger file or in a flow variable.
4. Test `GetLedgerLines` with `type=40`, `date_from=<first of last month>`.
5. Share the connector with the finance security group, read-only.
6. Optional: add the connector as a **tool** in Copilot Studio (same connection). Do **not** give Copilot the Supabase `service_role`, the Exact App Center secret, or the Invantive login.

## Acceptance

- A Power App or Copilot Studio agent lists bank lines (type 40) of last month
- The connector cannot write (only GET operations exist)
- Rotating `LEDGER_API_KEY` on Railway invalidates old connections
