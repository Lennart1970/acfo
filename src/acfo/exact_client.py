"""Sequential Exact Online REST/OData client with rate-limit handling."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import requests

from acfo.config import Settings
from acfo.dates import odata_datetime
from acfo.oauth import ExactOAuth, TokenSet
from acfo.types import DELETED_ENTITY_TYPE_TRANSACTION_LINES

TRANSACTION_LINE_SELECT = ",".join(
    [
        "Timestamp",
        "ID",
        "Account",
        "AccountCode",
        "AccountName",
        "AmountDC",
        "AmountFC",
        "AmountVATBaseFC",
        "AmountVATFC",
        "CostCenter",
        "CostCenterDescription",
        "CostUnit",
        "CostUnitDescription",
        "Created",
        "Currency",
        "Date",
        "Description",
        "Division",
        "Document",
        "DocumentNumber",
        "DueDate",
        "EntryID",
        "EntryNumber",
        "ExchangeRate",
        "FinancialPeriod",
        "FinancialYear",
        "GLAccount",
        "GLAccountCode",
        "GLAccountDescription",
        "InvoiceNumber",
        "Item",
        "ItemCode",
        "ItemDescription",
        "JournalCode",
        "JournalDescription",
        "LineNumber",
        "LineType",
        "Modified",
        "Notes",
        "OrderNumber",
        "PaymentDiscountAmount",
        "PaymentReference",
        "Project",
        "ProjectCode",
        "ProjectDescription",
        "Quantity",
        "Status",
        "Type",
        "VATCode",
        "VATCodeDescription",
        "VATPercentage",
        "VATType",
        "YourRef",
    ]
)


class ExactAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ExactClient:
    def __init__(
        self,
        settings: Settings,
        oauth: ExactOAuth,
        session: requests.Session | None = None,
        sleeper: Any = time.sleep,
    ) -> None:
        self.settings = settings
        self.oauth = oauth
        self.session = session or requests.Session()
        self.sleeper = sleeper
        self._tokens: TokenSet | None = None
        self._division: int | None = settings.division

    @property
    def division(self) -> int:
        if self._division is None:
            self._division = self.current_division()
        return self._division

    def current_division(self) -> int:
        payload = self.get("/api/v1/current/Me", params={"$select": "CurrentDivision"})
        return int(payload["d"]["results"][0]["CurrentDivision"])

    def divisions(self) -> list[dict[str, Any]]:
        path = f"/api/v1/{self.division}/system/Divisions"
        return list(self.iter_odata(path, {"$select": "Code,Description,HID,Status"}))

    def sync_transaction_lines(self, timestamp: int) -> Iterator[dict[str, Any]]:
        path = f"/api/v1/{self.division}/sync/Financial/TransactionLines"
        params = {
            "$select": TRANSACTION_LINE_SELECT,
            "$filter": f"Timestamp gt {int(timestamp)}L",
        }
        yield from self.iter_odata(path, params)

    def sync_deleted_transaction_lines(self, timestamp: int) -> Iterator[dict[str, Any]]:
        path = f"/api/v1/{self.division}/sync/Deleted"
        params = {
            "$filter": (
                f"Timestamp gt {int(timestamp)}L and "
                f"EntityType eq {DELETED_ENTITY_TYPE_TRANSACTION_LINES}"
            )
        }
        yield from self.iter_odata(path, params)

    def bulk_transaction_lines_from(self, from_date: Any) -> Iterator[dict[str, Any]]:
        path = f"/api/v1/{self.division}/bulk/Financial/TransactionLines"
        params = {
            "$select": TRANSACTION_LINE_SELECT,
            "$filter": f"Date ge datetime'{odata_datetime(from_date)}'",
        }
        yield from self.iter_odata(path, params)

    def sync_timestamp_for_modified(self, modified) -> int | None:
        """Best-effort starting Timestamp for a Modified date. Returns None if unsupported."""
        path = f"/api/v1/{self.division}/sync/SyncTimestamp"
        try:
            payload = self.get(
                path,
                params={"modified": f"datetime'{odata_datetime(modified)}'"},
            )
        except ExactAPIError:
            return None
        data = payload.get("d", payload)
        if isinstance(data, dict) and "results" in data and data["results"]:
            data = data["results"][0]
        if isinstance(data, dict) and "Timestamp" in data:
            return int(data["Timestamp"])
        return None

    def iter_odata(self, path: str, params: dict[str, str] | None = None) -> Iterator[dict[str, Any]]:
        url: str | None = path
        query = params
        while url:
            payload = self.get(url, params=query)
            query = None
            block = payload.get("d", payload)
            results = block["results"] if isinstance(block, dict) and "results" in block else block
            if not isinstance(results, list):
                raise ExactAPIError(f"Unexpected OData payload: {payload!r}")
            yield from results
            url = block.get("__next") if isinstance(block, dict) else None

    def get(self, path_or_url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        url = path_or_url if path_or_url.startswith("http") else f"{self.settings.base_url}{path_or_url}"
        last_error: ExactAPIError | None = None
        for attempt in range(4):
            tokens = self._access_tokens()
            response = self.session.get(
                url,
                params=params if not path_or_url.startswith("http") else None,
                headers={
                    "Authorization": f"Bearer {tokens.access_token}",
                    "Accept": "application/json",
                    "User-Agent": "acfo/0.1",
                },
                timeout=60,
            )
            self._maybe_throttle(response)
            if response.status_code == 401 and attempt == 0:
                self._tokens = None
                self.oauth.store.load()
                refreshed = self.oauth.refresh(tokens.refresh_token)
                self._tokens = refreshed
                continue
            if response.status_code == 429:
                wait_s = _retry_after(response, default=60)
                self.sleeper(wait_s)
                last_error = ExactAPIError(
                    f"Rate limited: {response.text}", status_code=429
                )
                continue
            if response.status_code >= 400:
                raise ExactAPIError(
                    f"GET {url} failed ({response.status_code}): {response.text}",
                    status_code=response.status_code,
                )
            return response.json()
        raise last_error or ExactAPIError(f"GET {url} failed after retries")

    def _access_tokens(self) -> TokenSet:
        if self._tokens is None or self._tokens.expired:
            self._tokens = self.oauth.load_or_error()
        return self._tokens

    def _maybe_throttle(self, response: requests.Response) -> None:
        remaining = response.headers.get("X-RateLimit-Minutely-Remaining")
        if remaining is None:
            return
        try:
            if int(remaining) <= 2:
                self.sleeper(2)
        except ValueError:
            return


def _retry_after(response: requests.Response, default: int) -> int:
    raw = response.headers.get("Retry-After") or response.headers.get("X-RateLimit-Reset")
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    # X-RateLimit-Reset is remaining milliseconds in some Exact responses.
    if value > 120:
        return max(1, value // 1000)
    return max(1, value)
