from pathlib import Path

import requests

from acfo.config import Settings
from acfo.exact_client import ExactClient, is_transaction_line_deletion, _retry_after
from acfo.oauth import ExactOAuth, TokenSet


class _FakeResponse:
    def __init__(self, payload, status_code=200, headers=None, text=""):
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}
        self.text = text or str(payload)

    def json(self):
        return self._payload


class _FakeSession(requests.Session):
    def __init__(self, responses):
        super().__init__()
        self.responses = list(responses)
        self.calls = []
        self.slept = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": params})
        return self.responses.pop(0)


def _client(tmp_path: Path, session: _FakeSession) -> ExactClient:
    settings = Settings(
        client_id="client",
        client_secret="secret",
        redirect_uri="https://example.com/callback",
        region="nl",
        base_url="https://start.exactonline.nl",
        division=555,
        token_file=tmp_path / "tokens.json",
        database_url=None,
        mysql_host="127.0.0.1",
        mysql_port=3306,
        mysql_user="acfo",
        mysql_password="acfo",
        mysql_database="acfo",
    )
    oauth = ExactOAuth(settings, session=session)
    oauth.store.save(TokenSet("access", "refresh", 9_999_999_999))
    client = ExactClient(settings, oauth, session=session, sleeper=session.slept.append)
    return client


def test_iter_odata_follows_next_and_uses_timestamp_filter(tmp_path):
    session = _FakeSession(
        [
            _FakeResponse(
                {
                    "d": {
                        "results": [{"ID": "1", "Timestamp": 10}],
                        "__next": "https://start.exactonline.nl/api/v1/555/sync/Financial/TransactionLines?$skiptoken=x",
                    }
                }
            ),
            _FakeResponse({"d": {"results": [{"ID": "2", "Timestamp": 20}]}}),
        ]
    )
    client = _client(tmp_path, session)
    rows = list(client.sync_transaction_lines(7))
    assert [row["ID"] for row in rows] == ["1", "2"]
    assert session.calls[0]["params"]["$filter"] == "Timestamp gt 7L"
    assert session.calls[1]["url"].endswith("$skiptoken=x")
    assert session.calls[1]["params"] is None


def test_deleted_filter_is_timestamp_only_then_filtered_locally(tmp_path):
    session = _FakeSession(
        [
            _FakeResponse(
                {
                    "d": {
                        "results": [
                            {"ID": "keep", "EntityType": 1, "Timestamp": 4},
                            {"ID": "skip", "EntityType": 2, "Timestamp": 5},
                            {"ID": "named", "EntityType": "TransactionLines", "Timestamp": 6},
                        ]
                    }
                }
            )
        ]
    )
    client = _client(tmp_path, session)
    rows = list(client.sync_deleted_transaction_lines(3))
    assert session.calls[0]["params"]["$filter"] == "Timestamp gt 3L"
    assert [row["ID"] for row in rows] == ["keep", "named"]


def test_is_transaction_line_deletion():
    assert is_transaction_line_deletion({"EntityType": 1})
    assert is_transaction_line_deletion({"EntityType": "TransactionLines"})
    assert not is_transaction_line_deletion({"EntityType": 2})


def test_retry_after_milliseconds():
    response = _FakeResponse({}, headers={"X-RateLimit-Reset": "5000"})
    assert _retry_after(response, default=60) == 5
