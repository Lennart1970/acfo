-- Typical CFO replica: ledger + relations + journals.
-- Incremental tables first; Bulk only where Exact has no Incremental.

local on error continue

use all@eol

set use-http-memory-cache@eol false

create or replace table transaction_lines_incremental@mysql
as
select *
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol

create or replace table gl_accounts_incremental@mysql
as
select *
from   ExactOnlineREST.Incremental.GLAccountsIncremental@eol

create or replace table accounts_incremental@mysql
as
select *
from   ExactOnlineREST.Incremental.AccountsIncremental@eol

create or replace table journals@mysql
as
select *
from   ExactOnlineREST.Financial.Journals@eol
