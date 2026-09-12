#!/usr/bin/env python3
"""Package booking-weekoverzicht as a Copilot Studio skill zip.

Copilot accepts the same layout as booking-dagoverzicht.zip:
SKILL.md and scripts/ at the archive root. A nested
booking-weekoverzicht/ folder makes the upload fail validation
(SKILL.md is not found at the zip root). Do not include fixtures.
"""
from __future__ import annotations

import re
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


def validate_skill(skill_path: Path) -> None:
    text = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    name = fields.get("name") or ""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"invalid skill name: {name!r}")
    if len(name) > 64:
        raise ValueError("name longer than 64 characters")
    extra = set(fields) - {"name", "description"}
    if extra:
        raise ValueError(f"unsupported frontmatter keys: {sorted(extra)}")
    body = match.group(1)
    desc_match = re.search(r"description:\s*>-?\s*(.*)$", body, re.DOTALL)
    description = " ".join(desc_match.group(1).split()) if desc_match else fields.get("description", "")
    if not description:
        raise ValueError("missing description")
    if "<" in description or ">" in description:
        raise ValueError("description cannot contain angle brackets")
    if len(description) > 1024:
        raise ValueError(f"description too long ({len(description)} chars)")


def main() -> int:
    dest = SKILL / "scripts"
    dest.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copy2(SCRIPTS / name, dest / name)
    validate_skill(SKILL)
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    include = [SKILL / "SKILL.md"]
    include.extend(dest / name for name in FILES)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in include:
            zf.write(path, path.relative_to(SKILL).as_posix())
    names = zipfile.ZipFile(ZIP_PATH).namelist()
    if names[0] != "SKILL.md" and "SKILL.md" not in names:
        raise ValueError("zip must have SKILL.md at archive root (Copilot Studio)")
    if "SKILL.md" not in names:
        raise ValueError("zip must have SKILL.md at archive root (Copilot Studio)")
    if any(name == "booking-weekoverzicht/SKILL.md" or name.startswith("booking-weekoverzicht/") for name in names):
        raise ValueError("do not nest files under booking-weekoverzicht/")
    if any(name.endswith(".xlsx") for name in names):
        raise ValueError("do not pack Excel fixtures into the skill zip")
    print(f"packed {ZIP_PATH} ({', '.join(names)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
