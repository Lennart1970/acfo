from datetime import date

from acfo.ledger import LedgerFilter, build_ledger_sql, build_ledger_where, parse_ledger_filter
from acfo.webview import LedgerApp, _demo_payload, find_ledger_html


def test_parse_ledger_filter_defaults():
    filt = parse_ledger_filter({})
    assert filt.include_headers is False
    assert filt.limit == 200
    assert filt.offset == 0


def test_parse_ledger_filter_values():
    filt = parse_ledger_filter(
        {
            "date_from": "2026-01-01",
            "type": "40",
            "journal_code": "90",
            "q": "ing",
            "include_headers": "true",
            "limit": "9999",
        }
    )
    assert filt.date_from == date(2026, 1, 1)
    assert filt.type == 40
    assert filt.journal_code == "90"
    assert filt.q == "ing"
    assert filt.include_headers is True
    assert filt.limit == 500


def test_where_skips_header_and_parameterizes():
    sql, params = build_ledger_where(
        LedgerFilter(date_from=date(2026, 1, 1), type=40, q="meel")
    )
    assert "line_number > 0" in sql
    assert "type = %s" in sql
    assert "ilike" in sql
    assert params[0] == date(2026, 1, 1)
    assert params[1] == 40
    assert params[2] == "%meel%"


def test_mysql_dialect_uses_like():
    sql, _params = build_ledger_sql(LedgerFilter(q="bank"), dialect="mysql")
    assert " like " in sql
    assert "ilike" not in sql
    assert "from transaction_lines_incremental" in sql


def test_demo_payload_filters_bank():
    payload = _demo_payload(LedgerFilter(type=40))
    assert payload["demo"] is True
    assert payload["count"] == 2
    assert all(row["type"] == 40 for row in payload["rows"])


class _FakeCursor:
    def __init__(self, summary, rows):
        self._summary = summary
        self._rows = rows
        self.calls: list[tuple[str, list]] = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params):
        self.calls.append((sql, list(params)))

    def fetchone(self):
        return self._summary

    def fetchall(self):
        return self._rows


class _FakeStore:
    def __init__(self, summary, rows):
        self._cursor = _FakeCursor(summary, rows)

    def connect(self):
        return self

    def cursor(self):
        return self._cursor


def test_fetch_ledger_uses_parameterized_sql():
    from acfo.ledger import fetch_ledger

    store = _FakeStore(
        {"n": 1, "amount_dc": "10.0000"},
        [{"date": date(2026, 3, 10), "amount_dc": "10.0000", "type": 40}],
    )
    payload = fetch_ledger(store, LedgerFilter(type=40, q="ing"))
    assert payload["count"] == 1
    assert payload["rows"][0]["date"] == "2026-03-10"
    assert "type = %s" in store._cursor.calls[0][0]
    assert 40 in store._cursor.calls[0][1]


def test_app_serves_html_and_lines(tmp_path):
    html = find_ledger_html()
    app = LedgerApp(html_path=html, demo=True)
    status, content_type, body = app.handle("GET", "/", {})
    assert status == 200
    assert "text/html" in content_type
    assert b"Grootboekmutaties" in body

    status, content_type, body = app.handle("GET", "/api/lines", {"type": "40"})
    assert status == 200
    assert "application/json" in content_type
    assert b'"type": 40' in body

    status, _, _ = app.handle("GET", "/missing", {})
    assert status == 404
