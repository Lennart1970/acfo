"""Environment configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REGIONS: dict[str, str] = {
    "nl": "https://start.exactonline.nl",
    "be": "https://start.exactonline.be",
    "de": "https://start.exactonline.de",
    "uk": "https://start.exactonline.co.uk",
    "fr": "https://start.exactonline.fr",
    "es": "https://start.exactonline.es",
    "com": "https://start.exactonline.com",
}


@dataclass(frozen=True)
class Settings:
    client_id: str
    client_secret: str
    redirect_uri: str
    region: str
    base_url: str
    division: int | None
    token_file: Path
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str


def load_settings(env_file: str | Path | None = None) -> Settings:
    load_dotenv(env_file)
    region = os.getenv("EXACT_REGION", "nl").lower()
    if region not in REGIONS:
        known = ", ".join(sorted(REGIONS))
        raise ValueError(f"Unknown EXACT_REGION={region!r}. Use one of: {known}")
    division_raw = os.getenv("EXACT_DIVISION", "").strip()
    return Settings(
        client_id=_required("EXACT_CLIENT_ID"),
        client_secret=_required("EXACT_CLIENT_SECRET"),
        redirect_uri=_required("EXACT_REDIRECT_URI"),
        region=region,
        base_url=REGIONS[region],
        division=int(division_raw) if division_raw else None,
        token_file=Path(os.getenv("EXACT_TOKEN_FILE", ".tokens.json")),
        mysql_host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        mysql_port=int(os.getenv("MYSQL_PORT", "3306")),
        mysql_user=os.getenv("MYSQL_USER", "acfo"),
        mysql_password=os.getenv("MYSQL_PASSWORD", "acfo"),
        mysql_database=os.getenv("MYSQL_DATABASE", "acfo"),
    )


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value
