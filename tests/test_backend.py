from pathlib import Path

from acfo.backend import open_store
from acfo.config import Settings
from acfo.mysql_store import MySQLStore
from acfo.pg_store import PostgresStore


def _settings(tmp_path: Path, database_url: str | None) -> Settings:
    return Settings(
        client_id="client",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        region="nl",
        base_url="https://start.exactonline.nl",
        division=1,
        token_file=tmp_path / "tokens.json",
        database_url=database_url,
        mysql_host="127.0.0.1",
        mysql_port=3306,
        mysql_user="acfo",
        mysql_password="acfo",
        mysql_database="acfo",
    )


def test_open_store_uses_postgres_when_database_url(tmp_path):
    store = open_store(_settings(tmp_path, "postgresql://postgres@localhost/postgres"))
    assert isinstance(store, PostgresStore)


def test_open_store_defaults_to_mysql(tmp_path):
    store = open_store(_settings(tmp_path, None))
    assert isinstance(store, MySQLStore)
