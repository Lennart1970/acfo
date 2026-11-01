# Lane 7 — Features (evaluation)

## Measurement patterns

| Piece | Role |
| --- | --- |
| Deterministic scorers | Prefer scripts/rules beside the model for reproducible routes |
| Decision records | Capture agent recommendation, human override, and final outcome |
| Threshold policy | Document how Auto / review bands change — with evidence |
| Aggregate KPIs | Rates and counts, not raw customer payloads in git |

## Example KPI families (domain-agnostic)

- Human touches per N cases  
- Automation percentage  

- AI resolution rate  
- Override rate  
- Error / exception rate  
- Human minutes per exception  
- Time-to-resolution  

## Learning loop

Preserve the original recommendation when overridden; use outcomes to move categories only with evidence. Link scoring changes back to lane 2 behaviour specs.
