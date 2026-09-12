"""MySQL persistence for Exact Online transaction lines."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from acfo.config import Settings
from acfo.dates import to_mysql_date, to_mysql_datetime

TRANSACTION_COLUMNS: tuple[str, ...] = (
    "id",
    "division",
    "timestamp",
    "entry_id",
    "entry_number",
    "line_number",
    "line_type",
    "date",
    "financial_year",
    "financial_period",
    "journal_code",
    "journal_description",
    "gl_account",
    "gl_account_code",
    "gl_account_description",
    "account",
    "account_code",
    "account_name",
    "description",
    "amount_dc",
    "amount_fc",
    "currency",
    "exchange_rate",
    "vat_code",
    "vat_code_description",
    "vat_percentage",
    "vat_type",
    "amount_vat_fc",
    "amount_vat_base_fc",
    "type",
    "status",
    "invoice_number",
    "order_number",
    "your_ref",
    "payment_reference",
    "payment_discount_amount",
    "due_date",
    "cost_center",
    "cost_center_description",
    "cost_unit",
    "cost_unit_description",
    "project",
    "project_code",
    "project_description",
    "item",
    "item_code",
    "item_description",
    "quantity",
    "document",
    "document_number",
    "notes",
    "created",
    "modified",
    "deleted_at",
    "synced_at",
)

_UPDATABLE = [column for column in TRANSACTION_COLUMNS if column != "id"]


def _guid(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value).strip("{}").lower()


def map_transaction_line(record: dict[str, Any], synced_at: datetime | None = None) -> dict[str, Any]:
    now = synced_at or datetime.now(timezone.utc).replace(tzinfo=None)
    timestamp = record.get("Timestamp")
    if timestamp is None:
        raise ValueError("Transaction line is missing Timestamp")
    line_id = _guid(record.get("ID"))
    if not line_id:
        raise ValueError("Transaction line is missing ID")
    return {
        "id": line_id,
        "division": record.get("Division"),
        "timestamp": int(timestamp),
        "entry_id": _guid(record.get("EntryID")),
        "entry_number": record.get("EntryNumber"),
        "line_number": record.get("LineNumber"),
        "line_type": record.get("LineType"),
        "date": to_mysql_date(record.get("Date")),
        "financial_year": record.get("FinancialYear"),
        "financial_period": record.get("FinancialPeriod"),
        "journal_code": record.get("JournalCode"),
        "journal_description": record.get("JournalDescription"),
        "gl_account": _guid(record.get("GLAccount")),
        "gl_account_code": record.get("GLAccountCode"),
        "gl_account_description": record.get("GLAccountDescription"),
        "account": _guid(record.get("Account")),
        "account_code": record.get("AccountCode"),
        "account_name": record.get("AccountName"),
        "description": record.get("Description"),
        "amount_dc": record.get("AmountDC"),
        "amount_fc": record.get("AmountFC"),
        "currency": record.get("Currency"),
        "exchange_rate": record.get("ExchangeRate"),
        "vat_code": record.get("VATCode"),
        "vat_code_description": record.get("VATCodeDescription"),
        "vat_percentage": record.get("VATPercentage"),
        "vat_type": record.get("VATType"),
        "amount_vat_fc": record.get("AmountVATFC"),
        "amount_vat_base_fc": record.get("AmountVATBaseFC"),
        "type": record.get("Type"),
        "status": record.get("Status"),
        "invoice_number": record.get("InvoiceNumber"),
        "order_number": record.get("OrderNumber"),
        "your_ref": record.get("YourRef"),
        "payment_reference": record.get("PaymentReference"),
        "payment_discount_amount": record.get("PaymentDiscountAmount"),
        "due_date": to_mysql_date(record.get("DueDate")),
        "cost_center": record.get("CostCenter"),
        "cost_center_description": record.get("CostCenterDescription"),
        "cost_unit": record.get("CostUnit"),
        "cost_unit_description": record.get("CostUnitDescription"),
        "project": _guid(record.get("Project")),
        "project_code": record.get("ProjectCode"),
        "project_description": record.get("ProjectDescription"),
        "item": _guid(record.get("Item")),
        "item_code": record.get("ItemCode"),
        "item_description": record.get("ItemDescription"),
        "quantity": record.get("Quantity"),
        "document": _guid(record.get("Document")),
        "document_number": record.get("DocumentNumber"),
        "notes": record.get("Notes"),
        "created": to_mysql_datetime(record.get("Created")),
        "modified": to_mysql_datetime(record.get("Modified")),
        "deleted_at": None,
        "synced_at": now,
    }


def map_deleted_entity(record: dict[str, Any], synced_at: datetime | None = None) -> dict[str, Any]:
    now = synced_at or datetime.now(timezone.utc).replace(tzinfo=None)
    deleted_id = _guid(record.get("ID"))
    entity_key = _guid(record.get("EntityKey"))
    if not deleted_id or not entity_key:
        raise ValueError("Deleted record is missing ID or EntityKey")
    return {
        "id": deleted_id,
        "division": record.get("Division"),
        "entity_type": record.get("EntityType"),
        "entity_key": entity_key,
        "timestamp": int(record["Timestamp"]),
        "deleted_date": to_mysql_datetime(record.get("DeletedDate")),
        "synced_at": now,
    }


class MySQLStore:
    def __init__(self, settings: Settings, connection: Connection | None = None) -> None:
        self.settings = settings
        self._connection = connection
        self._owns_connection = connection is None

    def connect(self) -> Connection:
        if self._connection is None:
            self._connection = pymysql.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                database=self.settings.mysql_database,
                charset="utf8mb4",
                autocommit=False,
                cursorclass=DictCursor,
            )
        return self._connection

    def close(self) -> None:
        if self._owns_connection and self._connection is not None:
            self._connection.close()
            self._connection = None

    def apply_schema(self, schema_sql: str) -> None:
        connection = self.connect()
        statements = [part.strip() for part in schema_sql.split(";") if part.strip()]
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        connection.commit()

    def last_timestamp(self, entity: str) -> int:
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT last_timestamp FROM sync_state WHERE entity = %s",
                (entity,),
            )
            row = cursor.fetchone()
        return int(row["last_timestamp"]) if row else 0

    def set_timestamp(self, entity: str, timestamp: int, error: str | None = None) -> None:
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sync_state (entity, last_timestamp, last_sync_at, last_error)
                VALUES (%s, %s, UTC_TIMESTAMP(), %s)
                ON DUPLICATE KEY UPDATE
                    last_timestamp = VALUES(last_timestamp),
                    last_sync_at = VALUES(last_sync_at),
                    last_error = VALUES(last_error)
                """,
                (entity, int(timestamp), error),
            )
        connection.commit()

    def upsert_transaction_lines(self, records: Iterable[dict[str, Any]]) -> int:
        rows = [map_transaction_line(record) for record in records]
        if not rows:
            return 0
        placeholders = ", ".join(["%s"] * len(TRANSACTION_COLUMNS))
        column_sql = ", ".join(TRANSACTION_COLUMNS)
        update_sql = ", ".join(f"{column} = VALUES({column})" for column in _UPDATABLE)
        sql = (
            f"INSERT INTO transaction_lines ({column_sql}) VALUES ({placeholders}) "
            f"ON DUPLICATE KEY UPDATE {update_sql}"
        )
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.executemany(sql, [tuple(row[column] for column in TRANSACTION_COLUMNS) for row in rows])
        connection.commit()
        return len(rows)

    def apply_deletions(self, records: Iterable[dict[str, Any]]) -> int:
        rows = [map_deleted_entity(record) for record in records]
        if not rows:
            return 0
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO deleted_entities
                    (id, division, entity_type, entity_key, timestamp, deleted_date, synced_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    division = VALUES(division),
                    entity_type = VALUES(entity_type),
                    entity_key = VALUES(entity_key),
                    timestamp = VALUES(timestamp),
                    deleted_date = VALUES(deleted_date),
                    synced_at = VALUES(synced_at)
                """,
                [
                    (
                        row["id"],
                        row["division"],
                        row["entity_type"],
                        row["entity_key"],
                        row["timestamp"],
                        row["deleted_date"],
                        row["synced_at"],
                    )
                    for row in rows
                ],
            )
            cursor.executemany(
                """
                UPDATE transaction_lines
                SET deleted_at = COALESCE(deleted_at, %s), synced_at = %s
                WHERE id = %s
                """,
                [
                    (
                        row["deleted_date"] or row["synced_at"],
                        row["synced_at"],
                        row["entity_key"],
                    )
                    for row in rows
                ],
            )
        connection.commit()
        return len(rows)
