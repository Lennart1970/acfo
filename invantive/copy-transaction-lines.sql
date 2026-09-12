-- Invantive Data Hub / Query Tool
-- Copy Exact Online grootboekmutaties into MySQL (current replica).
--
-- Use TransactionLinesIncremental, not TransactionLines or TransactionLinesBulk.
-- Incremental = Sync TransactionLines + Deleted, already applied.

local on error continue

use all@eol

set use-http-memory-cache@eol false

create or replace table transaction_lines_incremental@mysql
as
select *
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
