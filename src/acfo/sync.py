"""Incremental Exact Online → MySQL sync."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date
from typing import Any

from acfo.exact_client import ExactClient
from acfo.mysql_store import MySQLStore

ENTITY_TRANSACTION_LINES = "transaction_lines"
ENTITY_DELETED = "deleted_transaction_lines"
DEFAULT_BATCH_SIZE = 200


@dataclass
class SyncResult:
    upserted: int = 0
    deleted: int = 0
    last_line_timestamp: int = 0
    last_deleted_timestamp: int = 0


def _chunks(items: Iterable[dict[str, Any]], size: int) -> Iterable[list[dict[str, Any]]]:
    batch: list[dict[str, Any]] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def _max_timestamp(records: list[dict[str, Any]], current: int) -> int:
    timestamps = [int(record["Timestamp"]) for record in records if record.get("Timestamp") is not None]
    return max([current, *timestamps]) if timestamps else current


def sync_transactions(
    client: ExactClient,
    store: MySQLStore,
    *,
    full: bool = False,
    from_date: date | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    progress: Callable[[str], None] | None = None,
) -> SyncResult:
    """Download Exact Online transaction lines into MySQL.

    Incremental sync uses Sync APIs + Timestamp checkpoints. Use ``from_date``
    for a first load of a date range via the Bulk API (no Timestamp), then
    continue incrementally from Sync.
    """
    result = SyncResult()
    division = client.division
    line_ts = 0 if full else store.last_timestamp(ENTITY_TRANSACTION_LINES, division)
    deleted_ts = 0 if full else store.last_timestamp(ENTITY_DELETED, division)

    if from_date is not None and line_ts == 0:
        start_ts = client.sync_timestamp_for_modified(from_date)
        if start_ts is not None:
            line_ts = start_ts
            if progress:
                progress(f"Starting Sync from Timestamp {line_ts} (modified {from_date.isoformat()})")
        else:
            if progress:
                progress(f"SyncTimestamp unavailable; using Bulk API from {from_date.isoformat()}")
            for batch in _chunks(client.bulk_transaction_lines_from(from_date), batch_size):
                result.upserted += store.upsert_transaction_lines(batch)
                result.last_line_timestamp = _max_timestamp(batch, result.last_line_timestamp)
                if progress:
                    progress(f"Bulk upserted {result.upserted} lines")
            if result.last_line_timestamp:
                store.set_timestamp(ENTITY_TRANSACTION_LINES, result.last_line_timestamp, division)

    if progress:
        progress(f"Syncing transaction lines after Timestamp {line_ts}")
    for batch in _chunks(client.sync_transaction_lines(line_ts), batch_size):
        result.upserted += store.upsert_transaction_lines(batch)
        result.last_line_timestamp = _max_timestamp(batch, result.last_line_timestamp)
        store.set_timestamp(ENTITY_TRANSACTION_LINES, result.last_line_timestamp, division)
        if progress:
            progress(f"Upserted {result.upserted} lines (timestamp {result.last_line_timestamp})")

    if result.last_line_timestamp == 0:
        result.last_line_timestamp = line_ts

    if progress:
        progress(f"Syncing deletions after Timestamp {deleted_ts}")
    for batch in _chunks(client.sync_deleted_transaction_lines(deleted_ts), batch_size):
        result.deleted += store.apply_deletions(batch)
        result.last_deleted_timestamp = _max_timestamp(batch, result.last_deleted_timestamp)
        store.set_timestamp(ENTITY_DELETED, result.last_deleted_timestamp, division)
        if progress:
            progress(f"Applied {result.deleted} deletions")

    if result.last_deleted_timestamp == 0:
        result.last_deleted_timestamp = deleted_ts
    return result
