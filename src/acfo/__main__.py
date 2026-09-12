"""CLI: python -m acfo auth|sync|divisions|init-db"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from acfo.backend import open_oauth, open_store
from acfo.config import Settings, load_settings
from acfo.exact_client import ExactClient
from acfo.oauth import ExactOAuth, OAuthError
from acfo.pg_store import apply_supabase_migrations
from acfo.sync import sync_transactions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download Exact Online financial transactions into Supabase or MySQL."
    )
    parser.add_argument("--env-file", default=None, help="Optional .env path")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth", help="Authorize the Exact Online app and store tokens")
    auth.add_argument("--force-login", action="store_true")
    auth.add_argument("--code", help="Authorization code if you already have it")
    auth.add_argument("--redirected-url", help="Full URL Exact redirected to after login")

    sync = sub.add_parser("sync", help="Download transaction lines into MySQL")
    sync.add_argument("--full", action="store_true", help="Ignore stored timestamps and resync")
    sync.add_argument("--from-date", help="First load from this date (YYYY-MM-DD)")
    sync.add_argument("--batch-size", type=int, default=200)
    sync.add_argument(
        "--all-divisions",
        action="store_true",
        help="Sync every division the token can access (Invantive-style loop)",
    )

    sub.add_parser("divisions", help="List Exact Online divisions the token can access")
    sub.add_parser("init-db", help="Create MySQL tables from sql/schema.sql")

    args = parser.parse_args(argv)
    settings = load_settings(args.env_file)
    oauth = open_oauth(settings)

    if args.command == "auth":
        return _auth(oauth, args)
    if args.command == "init-db":
        return _init_db(settings)
    client = ExactClient(settings, oauth)
    if args.command == "divisions":
        return _divisions(client)
    if args.command == "sync":
        from_date = date.fromisoformat(args.from_date) if args.from_date else None
        store = open_store(settings)
        try:
            divisions = _sync_divisions(client, args.all_divisions)
            totals = []
            for division in divisions:
                client.use_division(division)
                print(f"=== division {division} ===")
                totals.append(
                    sync_transactions(
                        client,
                        store,
                        full=args.full,
                        from_date=from_date,
                        batch_size=args.batch_size,
                        progress=print,
                    )
                )
        finally:
            store.close()
        upserted = sum(item.upserted for item in totals)
        deleted = sum(item.deleted for item in totals)
        print(f"Done. divisions={len(totals)} upserted={upserted} deleted={deleted}")
        return 0
    raise AssertionError(args.command)


def _auth(oauth: ExactOAuth, args: argparse.Namespace) -> int:
    try:
        if args.code:
            oauth.exchange_code(args.code)
        elif args.redirected_url:
            oauth.exchange_code(oauth.extract_code(args.redirected_url))
        else:
            url = oauth.authorization_url(force_login=args.force_login)
            print("Open this URL, sign in to Exact Online, and approve the app:")
            print(url)
            print()
            print(
                "Exact will redirect to your registered HTTPS URI. "
                "Paste that full redirected URL here (it contains ?code=...)."
            )
            redirected = input("Redirected URL: ").strip()
            oauth.exchange_code(oauth.extract_code(redirected))
    except (OAuthError, EOFError) as exc:
        print(f"Authorization failed: {exc}", file=sys.stderr)
        return 1
    print(f"Tokens saved to {oauth.settings.token_file}")
    return 0


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "supabase" / "migrations").exists() or (parent / "sql" / "schema.sql").exists():
            return parent
    return Path.cwd()


def _init_db(settings: Settings) -> int:
    root = _repo_root()
    if settings.uses_postgres:
        applied = apply_supabase_migrations(settings.database_url or "", root / "supabase" / "migrations")
        print("Applied " + ", ".join(applied))
        return 0
    schema_path = root / "sql" / "schema.sql"
    store = open_store(settings)
    try:
        store.apply_schema(schema_path.read_text(encoding="utf-8"))
    finally:
        store.close()
    print(f"Applied {schema_path}")
    return 0


def _sync_divisions(client: ExactClient, all_divisions: bool) -> list[int]:
    if not all_divisions:
        return [client.division]
    rows = client.divisions()
    codes = [int(row["Code"]) for row in rows if row.get("Code") is not None]
    return codes or [client.division]


def _divisions(client: ExactClient) -> int:
    current = client.current_division()
    print(f"Current division: {current}")
    for row in client.divisions():
        print(f"{row.get('Code')}\t{row.get('HID')}\t{row.get('Description')}\tstatus={row.get('Status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
