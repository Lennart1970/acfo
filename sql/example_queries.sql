-- Invantive used TransactionLinesIncremental: current replica, deletes already applied.
SELECT
    date,
    journal_code,
    entry_number,
    line_number,
    gl_account_code,
    gl_account_description,
    account_name,
    description,
    amount_dc,
    vat_code,
    type
FROM transaction_lines_incremental
ORDER BY date, entry_number, line_number;

-- Bank / cash-flow (Exact Type 40). Invantive often derived this from TransactionLines
-- instead of BankEntryLines to stay within API limits.
SELECT *
FROM transaction_lines_incremental
WHERE type = 40
ORDER BY date, entry_number, line_number;

-- Skip header lines (LineNumber 0 is the booking header, same as in Exact/Invantive).
SELECT *
FROM transaction_lines_incremental
WHERE line_number > 0
ORDER BY date, entry_number, line_number;

-- Trial balance by GL account for one year
SELECT
    gl_account_code,
    gl_account_description,
    SUM(amount_dc) AS amount_dc
FROM transaction_lines_incremental
WHERE financial_year = 2026
GROUP BY gl_account_code, gl_account_description
ORDER BY gl_account_code;
