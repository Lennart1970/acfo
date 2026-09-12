from acfo.webview import DEMO_ROWS, LedgerApp, find_ledger_html


def test_sql_rows_group_into_purchase_bookings():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path("src").resolve()))
    sys.path.insert(0, str(Path(".cursor/skills/booking-weekoverzicht/scripts").resolve()))
    from sql_transactions import row_to_record
    from excel_transactions import apply_scope, bundle_from_records

    records = [row_to_record(dict(row), i) for i, row in enumerate(DEMO_ROWS)]
    # Demo uses journal 20/90/60. Force one purchase journal so scope=auto keeps it.
    records[4]["journalCode"] = "40"
    bundle = apply_scope(bundle_from_records(records, source="demo", source_name="demo"), "auto")
    assert bundle["parse"]["ok"] is True
    assert bundle["parse"]["bookingCount"] >= 1
    numbers = {item["entry"]["entryNumber"] for item in bundle["entries"]}
    assert "20260022" in numbers or 20260022 in {int(n) for n in numbers if str(n).isdigit()}


def test_api_key_still_required_after_vat_columns():
    app = LedgerApp(html_path=find_ledger_html(), demo=True, api_key="k")
    status, _, _ = app.handle("GET", "/api/lines", {}, {"X-Api-Key": "k"})
    assert status == 200
