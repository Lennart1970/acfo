---
name: review-transactions
description: Review Exact Online grootboekmutaties (transaction lines) that were loaded through Invantive or acfo into SQL. Use when asked to check, audit, reconcile, or explain bookings, bank lines, VAT, or suspicious entries in the ledger replica.
---

# Review transactions

The data is a replica, never live Exact. Read it through one of:

- SQL on `LEDGER_SOURCE` (`transaction_lines_incremental` from `acfo sync`, or `transaction_lines_invantive` from Invantive Data Hub)
- `GET /api/lines` on the web view (header `X-Api-Key`)
- Supabase PostgREST `transaction_lines_incremental`

Never write to the ledger tables. Never touch `oauth_tokens`, `sync_state`.

## Ground rules (Exact semantics)

- `line_number = 0` is the booking header. Exclude it from amount checks.
- `amount_dc` is in administration currency; `amount_fc` is the foreign amount.
- `type`: 20 sales, 30 purchase, 40 bank/cash, 70 memorial/general journal. Bank review = `type = 40`.
- `status`: 20 open, 50 processed.
- One booking = all lines with the same `entry_number` (and `division`). Debit is positive, credit negative.
- Deletions were already applied (Incremental). A missing line is not an error.

## Checklist

Run these in order and report each with a count and the first examples.

1. **Freshness** — `max(modified)` and, for `acfo sync`, `sync_state.last_sync_at`. Older than one day: say so first.
2. **Unbalanced bookings** — `sum(amount_dc)` per `entry_number` where `line_number > 0` must be 0.
3. **Lines without GL account** — `gl_account_code is null` and `line_number > 0`.
4. **Bank lines without relation** on debtor/creditor accounts (`type = 40`, `gl_account_code in (…13xx, 16xx…)`, `account is null`).
5. **Duplicate descriptions on the same date and amount** — likely double bookings.
6. **VAT sanity** — `vat_percentage` present but `amount_vat_fc = 0` (or the reverse) on sales/purchase.
7. **Period drift** — `date` outside `financial_year`/`financial_period`.
8. **Open items older than 60 days** — `status = 20` and `due_date < today - 60`.

## Output

Short. Table per finding: count, worst example (`date`, `entry_number`, `gl_account_code`, `amount_dc`, `description`). Then one paragraph: what to correct in Exact. Do not propose changing the replica.

## Example SQL

```sql
select entry_number, sum(amount_dc) as diff
from   transaction_lines_incremental
where  line_number > 0
group  by entry_number
having abs(sum(amount_dc)) > 0.005
order  by abs(sum(amount_dc)) desc
limit  20;
```

Web view equivalent for bank lines of a month:

```
GET /api/lines?type=40&date_from=2026-08-01&date_to=2026-08-31&limit=500
```
