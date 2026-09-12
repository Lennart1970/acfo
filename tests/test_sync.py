from datetime import date

from acfo.sync import SyncResult, sync_transactions


class FakeClient:
    def __init__(self, lines=None, deleted=None, bulk=None, start_ts=None):
        self.lines = lines or []
        self.deleted = deleted or []
        self.bulk = bulk or []
        self.start_ts = start_ts
        self.sync_calls = []
        self.bulk_calls = []

    def sync_transaction_lines(self, timestamp):
        self.sync_calls.append(timestamp)
        return [row for row in self.lines if row["Timestamp"] > timestamp]

    def sync_deleted_transaction_lines(self, timestamp):
        return [row for row in self.deleted if row["Timestamp"] > timestamp]

    def bulk_transaction_lines_from(self, from_date):
        self.bulk_calls.append(from_date)
        return list(self.bulk)

    def sync_timestamp_for_modified(self, modified):
        return self.start_ts


class FakeStore:
    def __init__(self):
        self.timestamps = {}
        self.upserted = []
        self.deletions = []

    def last_timestamp(self, entity):
        return self.timestamps.get(entity, 0)

    def set_timestamp(self, entity, timestamp, error=None):
        self.timestamps[entity] = timestamp

    def upsert_transaction_lines(self, records):
        rows = list(records)
        self.upserted.extend(rows)
        return len(rows)

    def apply_deletions(self, records):
        rows = list(records)
        self.deletions.extend(rows)
        return len(rows)


def test_incremental_sync_upserts_and_soft_deletes():
    client = FakeClient(
        lines=[
            {"ID": "a", "Timestamp": 10},
            {"ID": "b", "Timestamp": 20},
        ],
        deleted=[{"ID": "del", "EntityKey": "a", "Timestamp": 15, "EntityType": 1}],
    )
    store = FakeStore()
    store.timestamps["transaction_lines"] = 5
    result = sync_transactions(client, store, batch_size=1)
    assert isinstance(result, SyncResult)
    assert result.upserted == 2
    assert result.deleted == 1
    assert store.timestamps["transaction_lines"] == 20
    assert store.deletions[0]["EntityKey"] == "a"
    assert client.sync_calls == [5]


def test_from_date_uses_sync_timestamp_when_available():
    client = FakeClient(
        lines=[{"ID": "a", "Timestamp": 500}],
        start_ts=400,
    )
    store = FakeStore()
    sync_transactions(client, store, from_date=date(2024, 1, 1))
    assert client.sync_calls == [400]
    assert client.bulk_calls == []


def test_from_date_falls_back_to_bulk():
    client = FakeClient(
        lines=[],
        bulk=[{"ID": "bulk", "Timestamp": 9}],
        start_ts=None,
    )
    store = FakeStore()
    result = sync_transactions(client, store, from_date=date(2024, 1, 1))
    assert result.upserted == 1
    assert client.bulk_calls == [date(2024, 1, 1)]
    assert store.timestamps["transaction_lines"] == 9
