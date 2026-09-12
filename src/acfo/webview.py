"""HTTP front end for the SQL ledger (Exact → Invantive/acfo → SQL → web view)."""

from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from acfo.ledger import DEFAULT_SOURCE, LedgerFilter, fetch_ledger, ledger_source, parse_ledger_filter

DEMO_ROWS: list[dict[str, Any]] = [
    {
        "date": "2026-03-12",
        "journal_code": "20",
        "entry_number": 20260041,
        "line_number": 1,
        "gl_account_code": "1300",
        "gl_account_description": "Debiteuren",
        "account_name": "Bakkerij De Gouden Korrel",
        "description": "Factuur 2026-041",
        "amount_dc": "2420.0000",
        "type": 20,
        "division": 123456,
    },
    {
        "date": "2026-03-12",
        "journal_code": "20",
        "entry_number": 20260041,
        "line_number": 2,
        "gl_account_code": "8000",
        "gl_account_description": "Omzet",
        "account_name": "Bakkerij De Gouden Korrel",
        "description": "Factuur 2026-041",
        "amount_dc": "-2000.0000",
        "type": 20,
        "division": 123456,
    },
    {
        "date": "2026-03-10",
        "journal_code": "90",
        "entry_number": 20260038,
        "line_number": 1,
        "gl_account_code": "1100",
        "gl_account_description": "Bank",
        "account_name": "ING",
        "description": "Ontvangst factuur 2026-033",
        "amount_dc": "1815.0000",
        "type": 40,
        "division": 123456,
    },
    {
        "date": "2026-03-10",
        "journal_code": "90",
        "entry_number": 20260038,
        "line_number": 2,
        "gl_account_code": "1300",
        "gl_account_description": "Debiteuren",
        "account_name": "Bakkerij De Gouden Korrel",
        "description": "Ontvangst factuur 2026-033",
        "amount_dc": "-1815.0000",
        "type": 40,
        "division": 123456,
    },
    {
        "date": "2026-02-28",
        "journal_code": "60",
        "entry_number": 20260022,
        "line_number": 1,
        "gl_account_code": "4000",
        "gl_account_description": "Inkoop goederen",
        "account_name": "Meelhandel Noord",
        "description": "Inkoop meel",
        "amount_dc": "980.5000",
        "type": 30,
        "division": 123456,
    },
]


def find_ledger_html(repo_root: Path | None = None) -> Path:
    here = Path(__file__).resolve()
    candidates = []
    if repo_root is not None:
        candidates.append(repo_root / "web" / "ledger.html")
    candidates.append(here.parents[2] / "web" / "ledger.html")
    candidates.append(Path.cwd() / "web" / "ledger.html")
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError("web/ledger.html not found")


def _demo_payload(filt: LedgerFilter) -> dict[str, Any]:
    rows = list(DEMO_ROWS)
    if not filt.include_headers:
        rows = [row for row in rows if int(row["line_number"] or 0) > 0]
    if filt.date_from:
        rows = [row for row in rows if row["date"] >= filt.date_from.isoformat()]
    if filt.date_to:
        rows = [row for row in rows if row["date"] <= filt.date_to.isoformat()]
    if filt.type is not None:
        rows = [row for row in rows if int(row["type"] or 0) == filt.type]
    if filt.journal_code:
        rows = [row for row in rows if row["journal_code"] == filt.journal_code]
    if filt.gl_account_code:
        rows = [row for row in rows if row["gl_account_code"] == filt.gl_account_code]
    if filt.q:
        needle = filt.q.lower()
        rows = [
            row
            for row in rows
            if needle in str(row.get("description") or "").lower()
            or needle in str(row.get("account_name") or "").lower()
            or needle in str(row.get("gl_account_description") or "").lower()
        ]
    total = sum(float(row["amount_dc"]) for row in rows)
    sliced = rows[filt.offset : filt.offset + filt.limit]
    return {
        "filters": {
            "date_from": filt.date_from.isoformat() if filt.date_from else None,
            "date_to": filt.date_to.isoformat() if filt.date_to else None,
            "type": filt.type,
            "journal_code": filt.journal_code,
            "gl_account_code": filt.gl_account_code,
            "q": filt.q,
            "include_headers": filt.include_headers,
            "limit": filt.limit,
            "offset": filt.offset,
        },
        "count": len(rows),
        "amount_dc": f"{total:.4f}",
        "rows": sliced,
        "demo": True,
    }


class LedgerApp:
    """API key: `X-Api-Key` header or `Authorization: Bearer`. Empty key = open (local only)."""

    def __init__(
        self,
        store: Any | None = None,
        *,
        html_path: Path,
        dialect: str = "postgres",
        demo: bool = False,
        source: str = DEFAULT_SOURCE,
        api_key: str | None = None,
    ) -> None:
        self.store = store
        self.html_path = html_path
        self.dialect = dialect
        self.demo = demo or store is None
        self.source = ledger_source(source)
        self.api_key = (api_key or "").strip() or None

    def _authorized(self, headers: dict[str, str] | None, query: dict[str, str]) -> bool:
        if self.api_key is None:
            return True
        headers = {key.lower(): value for key, value in (headers or {}).items()}
        presented = headers.get("x-api-key", "")
        auth = headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            presented = presented or auth[7:].strip()
        presented = presented or query.get("api_key", "")
        return hmac.compare_digest(presented, self.api_key)

    def handle(
        self,
        method: str,
        path: str,
        query: dict[str, str],
        headers: dict[str, str] | None = None,
    ) -> tuple[int, str, bytes]:
        if method != "GET":
            return 405, "text/plain; charset=utf-8", b"method not allowed\n"
        if path in {"/", "/ledger", "/ledger.html"}:
            return 200, "text/html; charset=utf-8", self.html_path.read_bytes()
        if path == "/health":
            body = json.dumps({"ok": True, "demo": self.demo, "source": self.source}).encode("utf-8")
            return 200, "application/json; charset=utf-8", body
        if path == "/api/lines":
            if not self._authorized(headers, query):
                return (
                    401,
                    "application/json; charset=utf-8",
                    json.dumps({"error": "api key required"}).encode("utf-8"),
                )
            try:
                filt = parse_ledger_filter(query)
                if self.demo:
                    payload = _demo_payload(filt)
                else:
                    payload = fetch_ledger(
                        self.store, filt, dialect=self.dialect, source=self.source
                    )
            except ValueError as exc:
                return (
                    400,
                    "application/json; charset=utf-8",
                    json.dumps({"error": str(exc)}).encode("utf-8"),
                )
            return 200, "application/json; charset=utf-8", json.dumps(payload).encode("utf-8")
        return 404, "text/plain; charset=utf-8", b"not found\n"


def _first(values: list[str] | None) -> str:
    return values[0] if values else ""


def make_handler(app: LedgerApp):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            query = {key: _first(vals) for key, vals in parse_qs(parsed.query).items()}
            headers = {key: value for key, value in self.headers.items()}
            status, content_type, body = app.handle(self.command, parsed.path, query, headers)
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args: object) -> None:
            print(f"{self.address_string()} {fmt % args}")

    return Handler


def serve(
    app: LedgerApp,
    *,
    host: str = "127.0.0.1",
    port: int = 8080,
) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), make_handler(app))
    return server


def run_server(app: LedgerApp, *, host: str, port: int) -> None:
    server = serve(app, host=host, port=port)
    mode = "demo" if app.demo else "sql"
    print(f"Ledger web view ({mode}) http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        server.server_close()


def port_from_env(default: int = 8080) -> int:
    raw = os.environ.get("PORT")
    if not raw:
        return default
    return int(raw)


def source_from_env() -> str:
    return ledger_source(os.environ.get("LEDGER_SOURCE"))


def api_key_from_env() -> str | None:
    return os.environ.get("LEDGER_API_KEY", "").strip() or None
