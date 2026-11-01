# Lane 5 — Features (ALM & deployment)

## Promotion model

| Stage | Intent |
| --- | --- |
| Build | Maker / agent work in a non-prod environment |
| Test | Validated solution or package in a controlled environment |
| Publish / Export | Versioned artefact (solution ZIP or equivalent) as recovery point |
| Promote | Move only what is versioned; never “prod is the repo” |

## Surfaces this lane owns

| Surface | Role |
| --- | --- |
| Power Platform solutions | Naming, versioning, export/import, unmanaged vs managed policy |
| Hosting runbooks | Container/PaaS services for APIs and jobs — shape only, no live secrets |
| Schedules | Documented cron/Data Hub/job triggers with placeholder credentials |
| Environment map | Links to lane 1 topology; this lane owns *how* promotion happens |

## Safety

Environments have no production credentials until operators supply them. Docs describe shape only. Destructive ops require explicit human approval (lane 6).
