"""Load the same booking bundle from the SQL replica / Railway web view."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from excel_transactions import bundle_from_records

FIELD_MAP = {
    "date": "entryDate",
    "entry_number": "entryNumber",
    "account_name": "supplierName",
    "amount_dc": "amountDC",
    "currency": "currency",
    "vat_code": "vatCode",
    "gl_account_code": "glAccountCode",
    "journal_code": "journalCode",
    "journal_description": "journalDescription",
    "description": "description",
    "division": "division",
    "line_number": "lineNumber",
    "line_type": "glAccountType",
}


def row_to_record(row: dict[str, Any], index: int) -> dict:
    rec: dict[str, Any] = {field: None for field in FIELD_MAP.values()}
    for src, dest in FIELD_MAP.items():
        if src in row and row[src] not in (None, ""):
            rec[dest] = row[src]
    day = rec.get("entryDate")
    if hasattr(day, "isoformat"):
        rec["entryDate"] = day.isoformat()
    elif day:
        rec["entryDate"] = str(day)[:10]
    if rec.get("amountDC") is not None:
        rec["amountDC"] = float(rec["amountDC"])
    rec["entryNumber"] = str(rec.get("entryNumber") or "").strip()
    rec["supplierName"] = str(rec.get("supplierName") or "").strip()
    rec["journalCode"] = str(rec.get("journalCode") or "").strip()
    rec["glAccountCode"] = str(rec.get("glAccountCode") or "").strip()
    rec["vatCode"] = str(rec.get("vatCode") or "").strip()
    rec["division"] = str(rec.get("division") or "").strip()
    rec["_index"] = index
    return rec


def load_from_api(base_url: str, api_key: str | None = None, *, limit: int = 500) -> dict:
    base = base_url.rstrip("/")
    headers = {}
    if api_key:
        headers["X-Api-Key"] = api_key
    rows: list[dict] = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {"include_headers": "true", "limit": limit, "offset": offset}
        )
        req = urllib.request.Request(f"{base}/api/lines?{query}", headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        batch = payload.get("rows") or []
        rows.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    records = [row_to_record(row, i) for i, row in enumerate(rows)]
    return bundle_from_records(
        records,
        source=base,
        source_name="sql-replica",
        sheet="TransactionLines",
        mapped_fields=list(FIELD_MAP.values()),
        mapped_headers={v: k for k, v in FIELD_MAP.items()},
    )


def load_from_database(database_url: str, source: str = "transaction_lines_invantive") -> dict:
    import psycopg
    from psycopg.rows import dict_row

    if source not in {
        "transaction_lines_invantive",
        "transaction_lines_incremental",
        "transaction_lines",
    }:
        raise ValueError(f"refusing unknown LEDGER_SOURCE {source!r}")
    sql = (
        f"select date, entry_number, account_name, amount_dc, currency, vat_code, "
        f"gl_account_code, journal_code, journal_description, description, "
        f"division, line_number, line_type "
        f"from {source} order by date, entry_number, line_number"
    )
    with psycopg.connect(database_url, sslmode="require", row_factory=dict_row) as conn:
        rows = list(conn.execute(sql))
    records = [row_to_record(dict(row), i) for i, row in enumerate(rows)]
    return bundle_from_records(
        records,
        source=source,
        source_name="sql-replica",
        sheet="TransactionLines",
        mapped_fields=list(FIELD_MAP.values()),
        mapped_headers={v: k for k, v in FIELD_MAP.items()},
    )


def load_replica() -> dict:
    api = os.environ.get("LEDGER_URL", "").strip()
    if api:
        return load_from_api(api, os.environ.get("LEDGER_API_KEY"))
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url:
        return load_from_database(
            database_url,
            os.environ.get("LEDGER_SOURCE", "transaction_lines_invantive") or "transaction_lines_invantive",
        )
    raise SystemExit("set LEDGER_URL or DATABASE_URL, or pass --input Excel")
