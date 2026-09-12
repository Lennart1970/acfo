-- Invantive Data Hub: Exact Online → Supabase (Postgres) for the acfo web view.
--
-- Writes transaction_lines_invantive@pg with the snake_case columns that
-- `python -m acfo web` reads (LEDGER_SOURCE=transaction_lines_invantive).
-- Use Incremental: after the first run it costs ~2 Exact API calls per division.
-- LineNumber 0 is the booking header; the web view hides it, keep it here.
--
-- @pg alias: see settings-distributed.example.xml (database password, SSL, NOT the anon key).

local on error continue

use all@eol

set use-http-memory-cache@eol false

create or replace table transaction_lines_invantive@pg
as
select ID                          id
,      Division                    division
,      Timestamp                   timestamp
,      EntryID                     entry_id
,      EntryNumber                 entry_number
,      LineNumber                  line_number
,      LineType                    line_type
,      Date                        date
,      FinancialYear               financial_year
,      FinancialPeriod             financial_period
,      JournalCode                 journal_code
,      JournalDescription          journal_description
,      GLAccount                   gl_account
,      GLAccountCode               gl_account_code
,      GLAccountDescription        gl_account_description
,      Account                     account
,      AccountCode                 account_code
,      AccountName                 account_name
,      Description                 description
,      AmountDC                    amount_dc
,      AmountFC                    amount_fc
,      Currency                    currency
,      ExchangeRate                exchange_rate
,      VATCode                     vat_code
,      VATCodeDescription          vat_code_description
,      VATPercentage               vat_percentage
,      VATType                     vat_type
,      AmountVATFC                 amount_vat_fc
,      AmountVATBaseFC             amount_vat_base_fc
,      Type                        type
,      Status                      status
,      InvoiceNumber               invoice_number
,      OrderNumber                 order_number
,      YourRef                     your_ref
,      PaymentReference            payment_reference
,      DueDate                     due_date
,      CostCenter                  cost_center
,      CostCenterDescription       cost_center_description
,      CostUnit                    cost_unit
,      CostUnitDescription         cost_unit_description
,      Project                     project
,      ProjectCode                 project_code
,      ProjectDescription          project_description
,      Item                        item
,      ItemCode                    item_code
,      ItemDescription             item_description
,      Quantity                    quantity
,      Document                    document
,      DocumentNumber              document_number
,      Notes                       notes
,      Created                     created
,      Modified                    modified
,      sysdateutc                  synced_at
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol

-- Optional lookups for the review skill.
create or replace table gl_accounts_invantive@pg
as
select ID id, Division division, Code code, Description description, Type type, BalanceSide balance_side
from   ExactOnlineREST.Incremental.GLAccountsIncremental@eol
