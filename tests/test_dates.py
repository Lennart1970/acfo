from datetime import date, datetime, timezone

import pytest

from acfo.dates import odata_datetime, parse_exact_datetime, to_mysql_date, to_mysql_datetime


def test_parse_microsoft_date():
    parsed = parse_exact_datetime("/Date(1609459200000)/")
    assert parsed == datetime(2021, 1, 1, tzinfo=timezone.utc)


def test_parse_microsoft_date_with_offset():
    parsed = parse_exact_datetime("/Date(1609459200000+0000)/")
    assert parsed == datetime(2021, 1, 1, tzinfo=timezone.utc)


def test_parse_iso_and_empty():
    assert parse_exact_datetime(None) is None
    assert parse_exact_datetime("") is None
    parsed = parse_exact_datetime("2024-03-15T12:30:00Z")
    assert parsed == datetime(2024, 3, 15, 12, 30, tzinfo=timezone.utc)


def test_mysql_conversions():
    assert to_mysql_date("/Date(1609459200000)/") == date(2021, 1, 1)
    mysql_dt = to_mysql_datetime("2024-03-15T12:30:00+00:00")
    assert mysql_dt == datetime(2024, 3, 15, 12, 30)
    assert mysql_dt.tzinfo is None


def test_odata_datetime():
    assert odata_datetime(date(2024, 1, 31)) == "2024-01-31T00:00:00"
    assert odata_datetime(datetime(2024, 1, 31, 8, 15, 2)) == "2024-01-31T08:15:02"


def test_unsupported_type():
    with pytest.raises(TypeError):
        parse_exact_datetime(["nope"])
