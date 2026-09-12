-- Active (not deleted) Exact Online transaction lines
SELECT
    date,
    journal_code,
    entry_number,
    gl_account_code,
    gl_account_description,
    account_name,
    description,
    amount_dc,
    vat_code,
    type
FROM transaction_lines
WHERE deleted_at IS NULL
ORDER BY date, entry_number, line_number;

-- Bank / cash-flow lines (Exact Type 40)
SELECT *
FROM transaction_lines
WHERE type = 40
  AND deleted_at IS NULL
ORDER BY date, entry_number, line_number;

-- Trial balance by GL account for one year
SELECT
    gl_account_code,
    gl_account_description,
    SUM(amount_dc) AS amount_dc
FROM transaction_lines
WHERE deleted_at IS NULL
  AND financial_year = 2026
GROUP BY gl_account_code, gl_account_description
ORDER BY gl_account_code;
