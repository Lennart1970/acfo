# Lane 4 — Features (data plane)

## Responsibilities

| Concern | Guidance |
| --- | --- |
| System of record | Remains in the authoritative business system(s); agents do not redefine it |
| System of work | Dataverse (typical): cases, exceptions, decisions, audit, process events |
| Optional extracts | SQL / replicas for analytics or tool grounding — documented as extracts, not SoR |
| Migrations | Versioned schema changes; no production dumps in git |
| Field ownership | Every attribute named as source-owned, work-plane-owned, or agent-evidence |

## Minimal work-plane patterns

Keep small; extend only when a loop needs it:

- Party / organisation references  
- Work item / case  
- Exception and decision records (agent and human)  
- Process / audit events  
- Pointers to source records (ids/refs), not full payload clones by default  

## Explicit non-features

- No client datasets or production identifiers in docs
- No product-branded solution prefixes required by this lane — publishers stay configurable
