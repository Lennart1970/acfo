#!/usr/bin/env python3
"""Copy v2 scripts into the Copilot skill folder and refresh the zip."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent
SKILL = ROOT / "acfo" / "copilot-skills" / "booking-weekoverzicht"
ZIP_PATH = ROOT / "acfo" / "copilot-skills" / "booking-weekoverzicht.zip"
FILES = (
    "confidence_core.py",
    "excel_transactions.py",
    "write_weekoverzicht.py",
    "review_week.py",
)


def main() -> int:
    dest = SKILL / "scripts"
    dest.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copy2(SCRIPTS / name, dest / name)
    fixture = SKILL / "fixtures" / "exact-inkoop-sample.xlsx"
    import sys

    sys.path.insert(0, str(ROOT / "tests"))
    from exact_fixtures import write_nl_export

    write_nl_export(fixture)
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SKILL.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(SKILL))
    print(f"packed {ZIP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
