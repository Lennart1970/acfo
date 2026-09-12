import json
from pathlib import Path

import requests

from acfo.config import Settings
from acfo.oauth import ExactOAuth, TokenStore


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        client_id="client",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        region="nl",
        base_url="https://start.exactonline.nl",
        division=123,
        token_file=tmp_path / "tokens.json",
        mysql_host="127.0.0.1",
        mysql_port=3306,
        mysql_user="acfo",
        mysql_password="acfo",
        mysql_database="acfo",
    )


def test_authorization_url_and_extract_code(tmp_path):
    oauth = ExactOAuth(_settings(tmp_path))
    url = oauth.authorization_url()
    assert "client_id=client" in url
    assert "response_type=code" in url
    code = oauth.extract_code("https://example.com/callback?code=abc123&state=x")
    assert code == "abc123"


def test_token_store_roundtrip_and_permissions(tmp_path):
    path = tmp_path / "tokens.json"
    store = TokenStore(path)
    from acfo.oauth import TokenSet

    store.save(TokenSet("a", "r", 100.0))
    loaded = store.load()
    assert loaded is not None
    assert loaded.access_token == "a"
    assert path.stat().st_mode & 0o777 == 0o600


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


class _FakeSession(requests.Session):
    def __init__(self, payload):
        super().__init__()
        self.payload = payload
        self.last_request = None

    def post(self, url, headers=None, data=None, timeout=None):
        self.last_request = {"url": url, "headers": headers, "data": data}
        return _FakeResponse(self.payload)


def test_refresh_rotates_and_persists_new_refresh_token(tmp_path):
    session = _FakeSession(
        {"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 600}
    )
    oauth = ExactOAuth(_settings(tmp_path), session=session)
    tokens = oauth.refresh("old-refresh")
    assert tokens.access_token == "new-access"
    assert tokens.refresh_token == "new-refresh"
    assert session.last_request["data"]["grant_type"] == "refresh_token"
    persisted = json.loads((tmp_path / "tokens.json").read_text())
    assert persisted["refresh_token"] == "new-refresh"
