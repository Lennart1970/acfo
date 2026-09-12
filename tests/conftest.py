from __future__ import annotations

import sys
from pathlib import Path

import pytest

from exact_fixtures import (
    write_dutch_amounts_export,
    write_en_lines_export,
    write_invantive_purchases,
    write_nl_export,
    write_remote_europe_gl_trap,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "acfo" / "scripts"))


@pytest.fixture
def nl_export(tmp_path: Path) -> Path:
    return write_nl_export(tmp_path / "exact-inkoop.xlsx")


@pytest.fixture
def en_lines_export(tmp_path: Path) -> Path:
    return write_en_lines_export(tmp_path / "exact-lines.xlsx")


@pytest.fixture
def dutch_amounts_export(tmp_path: Path) -> Path:
    return write_dutch_amounts_export(tmp_path / "bedragen.xlsx")


@pytest.fixture
def invantive_export(tmp_path: Path) -> Path:
    return write_invantive_purchases(tmp_path / "gmr-eol-transaction-lines.xlsx")


@pytest.fixture
def remote_europe_export(tmp_path: Path) -> Path:
    return write_remote_europe_gl_trap(tmp_path / "gmr-eol-remote-europe.xlsx")
