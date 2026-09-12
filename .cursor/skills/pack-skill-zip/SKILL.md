---
name: pack-skill-zip
description: >
  Package a SKILL.md folder into an Agent Skills zip (Anthropic spec).
  Use when creating a skill zip, packing SKILL.md, uploading to Copilot
  Studio or Claude.ai, when a skill upload is rejected, or when the user
  mentions Agent Skills, booking-weekoverzicht, or "make a skill zip".
---

# Pack a SKILL.md zip

Meta-task: turn a skill directory into an uploadable zip. Spec: [agentskills.io](https://agentskills.io/specification).

Do **not** guess the zip layout. Ask (or infer from the upload target), then run the packer.

## 1. Author the skill folder

```
skill-name/
├── SKILL.md          # required
├── scripts/          # optional
├── references/       # optional
└── assets/           # optional
```

`SKILL.md` must start with YAML frontmatter. Required fields only for uploads that failed on extra keys:

```yaml
---
name: skill-name
description: >
  What it does. Use when the user says X, Y, or Z.
---
```

Rules (Anthropic / agentskills.io):

- `name`: kebab-case `[a-z0-9]+(-[a-z0-9]+)*`, max 64, no `--`, no leading/trailing `-`
- `name` **equals** the parent folder name
- `name` must not contain `anthropic` or `claude`
- `description`: non-empty, max **1024** chars after YAML fold, what **and** when, trigger phrases
- `description` must not contain `<` or `>` (XML)
- Keep the body under ~500 lines; put detail in `references/`

## 2. Pick the zip target

Read [references/targets.md](references/targets.md). Short version:

| Upload to | Zip contents | Flag |
|---|---|---|
| **Claude.ai / Anthropic Skills API** | `skill-name/SKILL.md` inside the zip | `--target anthropic` (default) |
| **Copilot Studio** | `SKILL.md` at the **zip root** | `--target copilot` |

Copilot Studio **rejects** a nested `skill-name/` folder. That is why `booking-weekoverzicht.zip` failed while `booking-dagoverzicht.zip` (flat root) was accepted. After a rejected name, pack as `skill-name-v2` — Copilot can cache the failed name.

Do not put `.xlsx` fixtures, `__pycache__`, or `.DS_Store` in the zip.

## 3. Pack

From the repo root:

```bash
python3 .cursor/skills/pack-skill-zip/scripts/pack_skill_zip.py \
  --skill acfo/copilot-skills/booking-weekoverzicht-v2 \
  --target copilot \
  --output acfo/copilot-skills/booking-weekoverzicht-v2.zip
```

Anthropic / Claude.ai:

```bash
python3 .cursor/skills/pack-skill-zip/scripts/pack_skill_zip.py \
  --skill path/to/skill-name \
  --target anthropic \
  --output skill-name.zip
```

The script validates frontmatter, checks `name` == folder, writes the zip, then asserts the archive layout.

## 4. Before handing the zip over

1. `unzip -l the.zip` — confirm `SKILL.md` is where the target expects it.
2. Filename = `{name}.zip` (helps humans; Copilot also keys off the skill `name` inside).
3. If the previous upload was rejected under the same name, bump `name`, folder, and zip to `*-v2`.
4. Tell the user which file to upload and which target it is for. Do not upload the Anthropic zip to Copilot or the reverse.

## Worked example (this repo)

Accepted Copilot zips:

- `acfo/copilot-skills/booking-dagoverzicht.zip` — flat root
- `acfo/copilot-skills/booking-weekoverzicht-v2.zip` — flat root, renamed after the nested zip was rejected
