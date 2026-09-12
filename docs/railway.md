# Railway deploy (MVP cron)

Railway starts this service, runs `python -m acfo sync`, and the process **must exit**. If it stays running, the next cron is skipped.

## Create the service

1. New Railway project → deploy this repo.
2. Settings → **Cron Schedule**: `15 * * * *` (hourly at minute 15, UTC). Minimum interval is 5 minutes.
3. Builder: Dockerfile (see `railway.json`).
4. Variables (from `.env.example`):

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | Supabase **session pooler** (`…pooler.supabase.com:5432`, user `postgres.<project-ref>`). Not transaction port 6543. |
| `EXACT_CLIENT_ID` / `EXACT_CLIENT_SECRET` / `EXACT_REDIRECT_URI` / `EXACT_REGION` | App Center |
| `EXACT_DIVISION` | Optional |

Do **not** rely on `.tokens.json` on Railway. Tokens go in `public.oauth_tokens`.

## First run

On your laptop (so you can paste the Exact redirect URL):

```bash
export DATABASE_URL='postgresql://postgres.<ref>:<password>@aws-0-….pooler.supabase.com:5432/postgres'
python -m acfo init-db
python -m acfo auth
python -m acfo sync --from-date 2024-01-01
```

Then Railway cron continues incrementally.

Alternatively apply schema with `supabase db push` against the linked project, then `auth` + `sync` locally once.
