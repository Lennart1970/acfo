"""Read-only ledger queries for the SQL web view."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

LEDGER_COLUMNS: tuple[str, ...] = (
    "date",
    "journal_code",
    "entry_number",
    "line_number",
    "gl_account_code",
    "gl_account_description",
    "account_name",
    "description",
    "amount_dc",
    "type",
    "division",
)

MAX_LIMIT = 500
DEFAULT_LIMIT = 200
DEFAULT_SOURCE = "transaction_lines_incremental"
_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


def ledger_source(name: str | None) -> str:
    """Table/view the web view reads. Invantive Data Hub writes transaction_lines_invantive."""
    source = (name or "").strip() or DEFAULT_SOURCE
    if not _IDENTIFIER.match(source):
        raise ValueError(f"LEDGER_SOURCE must be a plain lowercase identifier, got {source!r}")
    return source


@dataclass(frozen=True)
class LedgerFilter:
    date_from: date | None = None
    date_to: date | None = None
    type: int | None = None
    journal_code: str | None = None
    gl_account_code: str | None = None
    q: str | None = None
    include_headers: bool = False
    limit: int = DEFAULT_LIMIT
    offset: int = 0


def parse_ledger_filter(query: dict[str, str]) -> LedgerFilter:
    def _date(name: str) -> date | None:
        raw = (query.get(name) or "").strip()
        if not raw:
            return None
        return date.fromisoformat(raw)

    def _int(name: str) -> int | None:
        raw = (query.get(name) or "").strip()
        if not raw:
            return None
        return int(raw)

    limit = _int("limit") or DEFAULT_LIMIT
    offset = _int("offset") or 0
    include = (query.get("include_headers") or "").strip().lower() in {"1", "true", "yes"}
    return LedgerFilter(
        date_from=_date("date_from"),
        date_to=_date("date_to"),
        type=_int("type"),
        journal_code=(query.get("journal_code") or "").strip() or None,
        gl_account_code=(query.get("gl_account_code") or "").strip() or None,
        q=(query.get("q") or "").strip() or None,
        include_headers=include,
        limit=min(max(limit, 1), MAX_LIMIT),
        offset=max(offset, 0),
    )


def build_ledger_where(filt: LedgerFilter) -> tuple[str, list[Any]]:
    clauses = ["1=1"]
    params: list[Any] = []
    if not filt.include_headers:
        clauses.append("line_number > 0")
    if filt.date_from is not None:
        clauses.append("date >= %s")
        params.append(filt.date_from)
    if filt.date_to is not None:
        clauses.append("date <= %s")
        params.append(filt.date_to)
    if filt.type is not None:
        clauses.append("type = %s")
        params.append(filt.type)
    if filt.journal_code:
        clauses.append("journal_code = %s")
        params.append(filt.journal_code)
    if filt.gl_account_code:
        clauses.append("gl_account_code = %s")
        params.append(filt.gl_account_code)
    if filt.q:
        clauses.append(
            "(description ilike %s or account_name ilike %s or gl_account_description ilike %s)"
        )
        like = f"%{filt.q}%"
        params.extend([like, like, like])
    return " and ".join(clauses), params


def build_ledger_sql(
    filt: LedgerFilter, *, dialect: str = "postgres", source: str = DEFAULT_SOURCE
) -> tuple[str, list[Any]]:
    where_sql, params = build_ledger_where(filt)
    like_sql = where_sql
    like_params = list(params)
    if dialect == "mysql":
        like_sql = where_sql.replace(" ilike ", " like ")
    columns = ", ".join(LEDGER_COLUMNS)
    sql = (
        f"select {columns} from {ledger_source(source)} "
        f"where {like_sql} "
        f"order by date desc, entry_number desc, line_number "
        f"limit %s offset %s"
    )
    like_params.extend([filt.limit, filt.offset])
    return sql, like_params


def build_ledger_summary_sql(
    filt: LedgerFilter, *, dialect: str = "postgres", source: str = DEFAULT_SOURCE
) -> tuple[str, list[Any]]:
    where_sql, params = build_ledger_where(filt)
    if dialect == "mysql":
        where_sql = where_sql.replace(" ilike ", " like ")
    sql = (
        "select count(*) as n, coalesce(sum(amount_dc), 0) as amount_dc "
        f"from {ledger_source(source)} where {where_sql}"
    )
    return sql, params


def jsonable(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            out[key] = value.isoformat()
        elif isinstance(value, date):
            out[key] = value.isoformat()
        elif isinstance(value, Decimal):
            out[key] = format(value, "f")
        elif isinstance(value, UUID):
            out[key] = str(value)
        else:
            out[key] = value
    return out


def fetch_ledger(
    store: Any,
    filt: LedgerFilter,
    *,
    dialect: str = "postgres",
    source: str = DEFAULT_SOURCE,
) -> dict[str, Any]:
    list_sql, list_params = build_ledger_sql(filt, dialect=dialect, source=source)
    sum_sql, sum_params = build_ledger_summary_sql(filt, dialect=dialect, source=source)
    connection = store.connect()
    with connection.cursor() as cursor:
        cursor.execute(sum_sql, sum_params)
        summary = cursor.fetchone() or {}
        cursor.execute(list_sql, list_params)
        rows = cursor.fetchall() or []
    if not isinstance(summary, dict):
        summary = {"n": summary[0], "amount_dc": summary[1]}
    count = int(summary.get("n") or 0)
    amount = summary.get("amount_dc") or 0
    return {
        "filters": {
            "date_from": filt.date_from.isoformat() if filt.date_from else None,
            "date_to": filt.date_to.isoformat() if filt.date_to else None,
            "type": filt.type,
            "journal_code": filt.journal_code,
            "gl_account_code": filt.gl_account_code,
            "q": filt.q,
            "include_headers": filt.include_headers,
            "limit": filt.limit,
            "offset": filt.offset,
        },
        "count": count,
        "amount_dc": format(Decimal(str(amount)), "f"),
        "rows": [jsonable(dict(row)) for row in rows],
        "source": source,
    }
