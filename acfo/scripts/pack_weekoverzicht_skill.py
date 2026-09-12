#!/usr/bin/env python3
"""Package booking-weekoverzicht in Anthropic Agent Skills zip layout."""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(__file__).resolve().parent
SKILL = ROOT / "acfo" / "copilot-skills" / "booking-weekoverzicht"
ZIP_PATH = ROOT / "acfo" / "copilot-skills" / "booking-weekoverzicht.zip"
SKILL_PATH = ROOT / "acfo" / "copilot-skills" / "booking-weekoverzicht.skill"
FILES = (
    "confidence_core.py",
    "excel_transactions.py",
    "write_weekoverzicht.py",
    "review_week.py",
)
EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_FILES = {".DS_Store"}


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
    body = match.group(1)
    desc_match = re.search(r"description:\s*>\s*(.*)$", body, re.DOTALL)
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
    fixture = SKILL / "fixtures" / "exact-inkoop-sample.xlsx"
    import sys

    sys.path.insert(0, str(ROOT / "tests"))
    from exact_fixtures import write_nl_export

    write_nl_export(fixture)
    validate_skill(SKILL)
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SKILL.rglob("*")):
            if not path.is_file():
                continue
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name in EXCLUDE_FILES or path.name.endswith(".pyc"):
                continue
            # Anthropic layout: skill-name/SKILL.md inside the archive
            zf.write(path, path.relative_to(SKILL.parent))
    shutil.copy2(ZIP_PATH, SKILL_PATH)
    print(f"packed {ZIP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
