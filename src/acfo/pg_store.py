"""Postgres / Supabase persistence for Exact Online transaction lines."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

from acfo.config import Settings
from acfo.mysql_store import TRANSACTION_COLUMNS, _UPDATABLE, map_deleted_entity, map_transaction_line
from acfo.oauth import TokenSet
from acfo.sqlsplit import split_sql


class PostgresStore:
    def __init__(self, settings: Settings, connection: psycopg.Connection | None = None) -> None:
        self.settings = settings
        self._connection = connection
        self._owns_connection = connection is None

    def connect(self) -> psycopg.Connection:
        if self._connection is None:
            if not self.settings.database_url:
                raise ValueError("DATABASE_URL is required for the Supabase / Postgres store")
            self._connection = psycopg.connect(
                self.settings.database_url,
                sslmode="require",
                row_factory=dict_row,
            )
        return self._connection

    def close(self) -> None:
        if self._owns_connection and self._connection is not None:
            self._connection.close()
            self._connection = None

    def apply_schema(self, schema_sql: str) -> None:
        connection = self.connect()
        with connection.cursor() as cursor:
            for statement in split_sql(schema_sql):
                cursor.execute(statement)
        connection.commit()

    def last_timestamp(self, entity: str, division: int) -> int:
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute(
                "select last_timestamp from sync_state where entity = %s and division = %s",
                (entity, division),
            )
            row = cursor.fetchone()
        return int(row["last_timestamp"]) if row else 0

    def set_timestamp(
        self, entity: str, timestamp: int, division: int, error: str | None = None
    ) -> None:
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into sync_state (entity, division, last_timestamp, last_sync_at, last_error)
                values (%s, %s, %s, now(), %s)
                on conflict (entity, division) do update
                set last_timestamp = excluded.last_timestamp,
                    last_sync_at = excluded.last_sync_at,
                    last_error = excluded.last_error
                """,
                (entity, division, int(timestamp), error),
            )
        connection.commit()

    def upsert_transaction_lines(self, records: Iterable[dict[str, Any]]) -> int:
        rows = [map_transaction_line(record) for record in records]
        if not rows:
            return 0
        columns = TRANSACTION_COLUMNS
        placeholders = ", ".join(["%s"] * len(columns))
        column_sql = ", ".join(columns)
        update_sql = ", ".join(f"{column} = excluded.{column}" for column in _UPDATABLE)
        sql = (
            f"insert into transaction_lines ({column_sql}) values ({placeholders}) "
            f"on conflict (id) do update set {update_sql}"
        )
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.executemany(sql, [tuple(row[column] for column in columns) for row in rows])
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
                insert into deleted_entities
                    (id, division, entity_type, entity_key, timestamp, deleted_date, synced_at)
                values (%s, %s, %s, %s, %s, %s, %s)
                on conflict (id) do update
                set division = excluded.division,
                    entity_type = excluded.entity_type,
                    entity_key = excluded.entity_key,
                    timestamp = excluded.timestamp,
                    deleted_date = excluded.deleted_date,
                    synced_at = excluded.synced_at
                """,
                [
                    (
                        row["id"],
                        row["division"],
                        str(row["entity_type"]) if row["entity_type"] is not None else None,
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
                update transaction_lines
                set deleted_at = coalesce(deleted_at, %s), synced_at = %s
                where id = %s
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


class PgTokenStore:
    """Persist rotating Exact refresh tokens in Supabase (Railway disk is ephemeral)."""

    def __init__(self, database_url: str, name: str = "exact") -> None:
        self.database_url = database_url
        self.name = name

    def load(self) -> TokenSet | None:
        with psycopg.connect(self.database_url, sslmode="require", row_factory=dict_row) as connection:
            row = connection.execute(
                "select access_token, refresh_token, expires_at from oauth_tokens where name = %s",
                (self.name,),
            ).fetchone()
        if row is None:
            return None
        return TokenSet(
            access_token=row["access_token"],
            refresh_token=row["refresh_token"],
            expires_at=row["expires_at"].timestamp(),
        )

    def save(self, tokens: TokenSet) -> None:
        with psycopg.connect(self.database_url, sslmode="require") as connection:
            connection.execute(
                """
                insert into oauth_tokens (name, access_token, refresh_token, expires_at, updated_at)
                values (%s, %s, %s, to_timestamp(%s), now())
                on conflict (name) do update
                set access_token = excluded.access_token,
                    refresh_token = excluded.refresh_token,
                    expires_at = excluded.expires_at,
                    updated_at = excluded.updated_at
                """,
                (self.name, tokens.access_token, tokens.refresh_token, tokens.expires_at),
            )
            connection.commit()


def apply_supabase_migrations(database_url: str, migrations_dir: Path) -> list[str]:
    applied: list[str] = []
    files = sorted(migrations_dir.glob("*.sql"))
    with psycopg.connect(database_url, sslmode="require") as connection:
        for path in files:
            for statement in split_sql(path.read_text(encoding="utf-8")):
                connection.execute(statement)
            applied.append(path.name)
        connection.commit()
    return applied
