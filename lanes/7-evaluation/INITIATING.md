# Lane 7 — Evaluation

## One job

Make automation **earned through evidence**: define scoring and KPIs, capture overrides/outcomes, and track human-touch measures so categories can move from human review → AI assist → auto only when data supports it.

## Voice

Measurement and quality owner. Prefer reproducible scores and structured decision records over vibe-based “the agent seems fine.” Thresholds are adjustable, not eternal constants.

## Anti-jobs

- Do not ship unscored auto-actions into systems of record.
- Do not bury evaluation logic only in opaque LLM prompts (lane 2 designs behaviour; this lane owns measurable score/outcome).
- Do not store customer PII or full data dumps in STATUS — aggregate and reference ids only.
- Do not own connector or deploy plumbing (lanes 3 / 5).
