# Zip layouts by upload target

Learned while packing `booking-dagoverzicht` (accepted) and `booking-weekoverzicht` (rejected, then accepted as `-v2`).

## Anthropic / Claude.ai / Skills API (spec)

Claude Help Center: zip the **skill folder**. The archive root is the folder, not the files.

```
skill-name.zip
└── skill-name/
    ├── SKILL.md
    └── scripts/
```

Incorrect for this target: `SKILL.md` loose at the zip root.

`--target anthropic`

## Copilot Studio

Microsoft / Copilot Skill Creator: `SKILL.md` must be at the **archive root**.

```
skill-name.zip
├── SKILL.md
└── scripts/
    └── review_week.py
```

Incorrect for this target (this is what got `booking-weekoverzicht` rejected):

```
booking-weekoverzicht.zip
└── booking-weekoverzicht/
    ├── SKILL.md
    ├── fixtures/sample.xlsx
    └── scripts/
```

`--target copilot`

Also omit Excel fixtures. Copilot does not need them; they bloat the package and are not part of the working dagoverzicht zip.

## If Copilot still rejects a valid flat zip

1. Confirm `unzip -l` shows `SKILL.md` not `name/SKILL.md`.
2. Confirm frontmatter is only `name` + `description`, description ≤ 1024, no `<>`.
3. Rename the skill (`name`, folder, zip) to `*-v2`. The failed name can stay cached.
4. Do not re-upload the old filename from Downloads.
