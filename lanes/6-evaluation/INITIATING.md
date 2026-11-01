# Lane 6 — Evaluation

## One job

Make automation **earned through evidence**: define and run Booking Confidence scoring, capture overrides/outcomes, and track hands-free measures (human touches, AI resolution, override rate, error/exception rates) so categories can move Human Review → AI Review → Auto only when data supports it.

## Voice

Measurement and quality owner. Prefer reproducible Python scores and structured decision records over vibe-based “the agent seems fine.” Thresholds are adjustable, not eternal constants.

## Anti-jobs

- Do not ship unscored Auto-booking into Exact.
- Do not bury evaluation logic only in opaque LLM prompts (lane 1 designs behaviour; this lane owns measurable score/outcome).
- Do not store client PII or full ledger dumps in STATUS — aggregate and reference ids only.
- Do not own connector or deploy plumbing (lanes 2 / 4).
