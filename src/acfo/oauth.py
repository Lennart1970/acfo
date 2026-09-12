"""Exact Online OAuth 2.0 authorization-code flow."""

from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from acfo.config import Settings


class OAuthError(RuntimeError):
    pass


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str
    expires_at: float

    @property
    def expired(self) -> bool:
        return time.time() >= self.expires_at - 30


class TokenBackend(Protocol):
    def load(self) -> TokenSet | None: ...
    def save(self, tokens: TokenSet) -> None: ...


class TokenStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> TokenSet | None:
        if not self.path.exists():
            return None
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return TokenSet(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=float(data["expires_at"]),
        )

    def save(self, tokens: TokenSet) -> None:
        payload = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_at": tokens.expires_at,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.path.chmod(0o600)


class ExactOAuth:
    def __init__(
        self,
        settings: Settings,
        session: requests.Session | None = None,
        store: TokenBackend | None = None,
    ) -> None:
        self.settings = settings
        self.session = session or requests.Session()
        self.store = store or TokenStore(settings.token_file)

    def authorization_url(self, force_login: bool = False) -> str:
        params = {
            "client_id": self.settings.client_id,
            "redirect_uri": self.settings.redirect_uri,
            "response_type": "code",
            "force_login": "1" if force_login else "0",
        }
        return f"{self.settings.base_url}/api/oauth2/auth?{urlencode(params)}"

    def extract_code(self, redirected_url: str) -> str:
        parsed = urlparse(redirected_url.strip())
        query = parse_qs(parsed.query)
        if "code" in query:
            return query["code"][0]
        if "error" in query:
            description = query.get("error_description", [""])[0]
            raise OAuthError(f"Exact denied authorization: {query['error'][0]} {description}")
        raise OAuthError("No authorization code found in the redirected URL.")

    def exchange_code(self, code: str) -> TokenSet:
        return self._token_request(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.settings.redirect_uri,
            }
        )

    def refresh(self, refresh_token: str) -> TokenSet:
        """Exchange a refresh token. Exact rotates refresh tokens; persist the result."""
        return self._token_request(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

    def load_or_error(self) -> TokenSet:
        tokens = self.store.load()
        if tokens is None:
            raise OAuthError("No tokens found. Run: python -m acfo auth")
        if tokens.expired:
            tokens = self.refresh(tokens.refresh_token)
            self.store.save(tokens)
        return tokens

    def _token_request(self, data: dict[str, str]) -> TokenSet:
        credentials = base64.b64encode(
            f"{self.settings.client_id}:{self.settings.client_secret}".encode()
        ).decode()
        response = self.session.post(
            f"{self.settings.base_url}/api/oauth2/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            data=data,
            timeout=30,
        )
        if response.status_code != 200:
            raise OAuthError(f"Token request failed ({response.status_code}): {response.text}")
        payload: dict[str, Any] = response.json()
        expires_in = int(payload.get("expires_in", 600))
        tokens = TokenSet(
            access_token=payload["access_token"],
            refresh_token=payload["refresh_token"],
            expires_at=time.time() + expires_in,
        )
        self.store.save(tokens)
        return tokens
