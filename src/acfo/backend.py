"""Choose Supabase/Postgres when DATABASE_URL is set, otherwise MySQL."""

from __future__ import annotations

from acfo.config import Settings
from acfo.mysql_store import MySQLStore
from acfo.oauth import ExactOAuth, TokenBackend, TokenStore
from acfo.pg_store import PgTokenStore, PostgresStore


def open_store(settings: Settings):
    if settings.uses_postgres:
        return PostgresStore(settings)
    return MySQLStore(settings)


def open_oauth(settings: Settings, session=None) -> ExactOAuth:
    store: TokenBackend
    if settings.uses_postgres:
        store = PgTokenStore(settings.database_url or "")
    else:
        store = TokenStore(settings.token_file)
    return ExactOAuth(settings, session=session, store=store)
