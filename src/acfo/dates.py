"""Parse Exact Online OData date values."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

_MS_DATE = re.compile(r"^/Date\((-?\d+)([+-]\d{4})?\)/$")


def parse_exact_datetime(value: object) -> datetime | None:
    """Convert Exact JSON dates to timezone-aware UTC datetimes."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    if isinstance(value, str):
        match = _MS_DATE.match(value)
        if match:
            millis = int(match.group(1))
            return datetime.fromtimestamp(millis / 1000, tz=timezone.utc)
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    raise TypeError(f"Unsupported Exact date value: {value!r}")


def to_mysql_datetime(value: object) -> datetime | None:
    """Return a naive UTC datetime for MySQL DATETIME columns."""
    parsed = parse_exact_datetime(value)
    if parsed is None:
        return None
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


def to_mysql_date(value: object) -> date | None:
    parsed = parse_exact_datetime(value)
    if parsed is None:
        return None
    return parsed.date()


def odata_datetime(value: date | datetime) -> str:
    """Format a date for Exact OData filters."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    return f"{value.isoformat()}T00:00:00"
