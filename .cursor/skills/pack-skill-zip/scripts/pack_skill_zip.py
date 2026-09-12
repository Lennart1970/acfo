#!/usr/bin/env python3
"""Pack a SKILL.md folder into an Agent Skills zip.

Targets:
  anthropic — skill-name/SKILL.md inside the archive (Claude.ai / spec)
  copilot   — SKILL.md at the archive root (Copilot Studio)
"""
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

SKIP_DIRS = {"__pycache__", ".git", "node_modules"}
SKIP_FILES = {".DS_Store"}
SKIP_SUFFIXES = {".pyc", ".xlsx"}
RESERVED = ("anthropic", "claude")


def parse_frontmatter(skill_dir: Path) -> tuple[str, str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise ValueError(f"missing {skill_md}")
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter")
    raw = match.group(1)
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    name = fields.get("name") or ""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"invalid skill name: {name!r}")
    if len(name) > 64:
        raise ValueError("name longer than 64 characters")
    if name != skill_dir.name:
        raise ValueError(f"name {name!r} must match folder {skill_dir.name!r}")
    if any(word in name for word in RESERVED):
        raise ValueError(f"name cannot contain reserved words: {RESERVED}")
    extra = set(fields) - {"name", "description"}
    if extra:
        raise ValueError(f"keep upload frontmatter to name+description; extra keys: {sorted(extra)}")
    desc_match = re.search(r"description:\s*>-?\s*(.*)$", raw, re.DOTALL)
    description = " ".join(desc_match.group(1).split()) if desc_match else fields.get("description", "")
    if not description:
        raise ValueError("missing description")
    if "<" in description or ">" in description:
        raise ValueError("description cannot contain angle brackets")
    if len(description) > 1024:
        raise ValueError(f"description too long ({len(description)} chars)")
    return name, description


def iter_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES or path.suffix in SKIP_SUFFIXES:
            continue
        files.append(path)
    if not any(p.name == "SKILL.md" for p in files):
        raise ValueError("nothing to pack: SKILL.md missing after filters")
    return files


def pack(skill_dir: Path, output: Path, target: str) -> list[str]:
    name, _ = parse_frontmatter(skill_dir)
    files = iter_files(skill_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            relative = path.relative_to(skill_dir).as_posix()
            arcname = f"{name}/{relative}" if target == "anthropic" else relative
            zf.write(path, arcname)
    names = zipfile.ZipFile(output).namelist()
    if target == "anthropic":
        if f"{name}/SKILL.md" not in names:
            raise ValueError("anthropic zip must contain skill-name/SKILL.md")
        if "SKILL.md" in names:
            raise ValueError("anthropic zip must not have SKILL.md at the root")
    else:
        if "SKILL.md" not in names:
            raise ValueError("copilot zip must have SKILL.md at the archive root")
        if any(item.endswith("/SKILL.md") for item in names):
            raise ValueError("copilot zip must not nest SKILL.md under a folder")
    if any(item.endswith(".xlsx") for item in names):
        raise ValueError("do not pack Excel fixtures")
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True, type=Path, help="folder that contains SKILL.md")
    parser.add_argument("--output", required=True, type=Path, help="destination .zip")
    parser.add_argument(
        "--target",
        choices=("anthropic", "copilot"),
        default="anthropic",
        help="anthropic = nested folder (spec); copilot = SKILL.md at zip root",
    )
    args = parser.parse_args()
    skill_dir = args.skill.expanduser().resolve()
    names = pack(skill_dir, args.output.expanduser().resolve(), args.target)
    print(f"packed {args.output} target={args.target} ({', '.join(names)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
