from pathlib import Path

import pytest

from acfo.config import load_settings


def test_load_settings_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("EXACT_CLIENT_ID", "id")
    monkeypatch.setenv("EXACT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("EXACT_REDIRECT_URI", "https://example.com/cb")
    monkeypatch.setenv("EXACT_REGION", "be")
    monkeypatch.setenv("EXACT_DIVISION", "42")
    monkeypatch.setenv("EXACT_TOKEN_FILE", str(tmp_path / "t.json"))
    monkeypatch.setenv("MYSQL_HOST", "db.internal")
    settings = load_settings(env_file=Path("/nonexistent.env"))
    assert settings.base_url == "https://start.exactonline.be"
    assert settings.division == 42
    assert settings.mysql_host == "db.internal"


def test_unknown_region(monkeypatch):
    monkeypatch.setenv("EXACT_CLIENT_ID", "id")
    monkeypatch.setenv("EXACT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("EXACT_REDIRECT_URI", "https://example.com/cb")
    monkeypatch.setenv("EXACT_REGION", "xx")
    with pytest.raises(ValueError, match="EXACT_REGION"):
        load_settings(env_file=Path("/nonexistent.env"))
