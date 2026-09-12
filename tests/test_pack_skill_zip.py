from __future__ import annotations

import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".cursor" / "skills" / "pack-skill-zip" / "scripts"))

from pack_skill_zip import pack, parse_frontmatter  # noqa: E402


def _write_skill(folder: Path, name: str) -> Path:
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: >\n  Test skill for zip packing. Use when testing.\n---\n\n# Test\n",
        encoding="utf-8",
    )
    (folder / "scripts").mkdir()
    (folder / "scripts" / "hello.py").write_text("print('ok')\n", encoding="utf-8")
    (folder / "fixtures").mkdir()
    (folder / "fixtures" / "sample.xlsx").write_bytes(b"not-a-real-xlsx")
    return folder


def test_anthropic_zip_nests_folder(tmp_path: Path):
    skill = _write_skill(tmp_path / "demo-skill", "demo-skill")
    out = tmp_path / "demo-skill.zip"
    names = pack(skill, out, "anthropic")
    assert "demo-skill/SKILL.md" in names
    assert "demo-skill/scripts/hello.py" in names
    assert "SKILL.md" not in names
    assert not any(name.endswith(".xlsx") for name in names)


def test_copilot_zip_is_flat(tmp_path: Path):
    skill = _write_skill(tmp_path / "demo-skill", "demo-skill")
    out = tmp_path / "demo-skill.zip"
    names = pack(skill, out, "copilot")
    assert "SKILL.md" in names
    assert "scripts/hello.py" in names
    assert "demo-skill/SKILL.md" not in names
    assert not any(name.endswith(".xlsx") for name in names)


def test_this_cursor_skill_is_valid():
    skill = ROOT / ".cursor" / "skills" / "pack-skill-zip"
    name, description = parse_frontmatter(skill)
    assert name == "pack-skill-zip"
    assert "zip" in description.lower()
    assert len(description) <= 1024


def test_weekoverzicht_copilot_layout_still_flat():
    skill = ROOT / "acfo" / "copilot-skills" / "booking-weekoverzicht-v2"
    names = ZipFile(skill.parent / "booking-weekoverzicht-v2.zip").namelist()
    assert "SKILL.md" in names
    assert "booking-weekoverzicht-v2/SKILL.md" not in names
    parse_frontmatter(skill)
