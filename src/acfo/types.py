"""Exact Online transaction Type codes from the Sync TransactionLines docs."""

TRANSACTION_TYPES: dict[int, str] = {
    10: "Opening balance",
    20: "Sales entry",
    21: "Sales credit note",
    30: "Purchase entry",
    31: "Purchase credit note",
    40: "Cash flow",
    50: "VAT return",
    70: "Asset - Depreciation",
    71: "Asset - Investment",
    72: "Asset - Revaluation",
    73: "Asset - Transfer",
    74: "Asset - Split",
    75: "Asset - Discontinue",
    76: "Asset - Sales",
    80: "Revaluation",
    82: "Exchange rate difference",
    83: "Payment difference",
    84: "Deferred revenue",
    85: "Tracking number: Revaluation",
    86: "Deferred cost",
    87: "VAT on prepayment",
    90: "Other",
    95: "Accrued revenue",
    96: "Accrued costs",
    120: "Delivery",
    121: "Sales return",
    130: "Receipt",
    131: "Purchase return",
    140: "Shop order stock receipt",
    141: "Shop order stock reversal",
    142: "Issue to parent",
    145: "Shop order time entry",
    146: "Shop order time entry reversal",
    147: "Shop order by-product receipt",
    148: "Shop order by-product reversal",
    150: "Requirement issue",
    151: "Requirement reversal",
    152: "Returned from parent",
    155: "Subcontract issue",
    156: "Subcontract reversal",
    158: "Shop order completed",
    162: "Finish assembly",
    170: "Payroll",
    180: "Stock revaluation",
    181: "Financial revaluation",
    195: "Stock count",
    200: "Trade-in",
    201: "Trade-in (Purchase)",
    290: "Correction entry",
    310: "Period closing",
    320: "Year end reflection",
    321: "Year end costing",
    322: "Year end profits to gross profit",
    323: "Year end costs to gross profit",
    324: "Year end tax",
    325: "Year end gross profit to net p/l",
    326: "Year end net p/l to balance sheet",
    327: "Year end closing balance",
    328: "Year start opening balance",
    3000: "Budget",
}

# Sync/Deleted EntityType for financial transaction lines.
# Exact documents this as integer 1; some payloads use the entity name.
DELETED_ENTITY_TYPE_TRANSACTION_LINES = 1
DELETED_TRANSACTION_LINE_TYPES: frozenset[object] = frozenset(
    {1, "1", "TransactionLines"}
)

STATUS_OPEN = 20
STATUS_PROCESSED = 50
