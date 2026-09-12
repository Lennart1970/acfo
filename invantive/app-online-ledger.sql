-- Invantive App Online / Query Tool / Bridge Online
-- Exact Online → Invantive SQL → this result set is the web view.
--
-- Use Incremental, not TransactionLines / TransactionLinesBulk.
-- LineNumber 0 is the booking header; hide it in a finance web view.

select Date
,      JournalCode
,      EntryNumber
,      LineNumber
,      GLAccountCode
,      GLAccountDescription
,      AccountName
,      Description
,      AmountDC
,      Type
,      Division
from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
where  LineNumber > 0
order
by     Date desc
,      EntryNumber desc
,      LineNumber

-- Bank / kas only (Exact Type 40), same Incremental table:
--
-- select *
-- from   ExactOnlineREST.Incremental.TransactionLinesIncremental@eol
-- where  LineNumber > 0
-- and    Type = 40
