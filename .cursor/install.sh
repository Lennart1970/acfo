#!/usr/bin/env bash
# Idempotent development bootstrap for the acfo repo.
# Durable, one-time setup only: system packages, the Python venv, and a local
# Postgres cluster (roles + database) that stands in for the Supabase session
# pooler. Per-boot service startup lives in start.sh.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PG_VERSION=16

echo ">> Installing system packages (python venv + PostgreSQL ${PG_VERSION})"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3-venv postgresql postgresql-contrib

echo ">> Creating Python virtualenv and installing acfo (editable, with dev extras)"
if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -e ".[dev]"

echo ">> Ensuring the Postgres cluster is running for bootstrap"
sudo pg_ctlcluster "$PG_VERSION" main start || true
for _ in $(seq 1 30); do
  if sudo -u postgres pg_isready -q; then break; fi
  sleep 1
done

echo ">> Creating app role, database, and Supabase-compatible roles (idempotent)"
sudo -u postgres psql -v ON_ERROR_STOP=1 <<'SQL'
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'acfo') THEN
    CREATE ROLE acfo LOGIN PASSWORD 'acfo' CREATEDB;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN
    CREATE ROLE anon NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
    CREATE ROLE authenticated NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'service_role') THEN
    CREATE ROLE service_role NOLOGIN BYPASSRLS;
  END IF;
END $$;
SELECT 'CREATE DATABASE acfo OWNER acfo'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'acfo')\gexec
SQL

# Supabase provides these in production; recreate the minimum the migration needs
# (the anon/authenticated roles above plus an auth.jwt() used by RLS policies).
sudo -u postgres psql -d acfo -v ON_ERROR_STOP=1 <<'SQL'
GRANT anon, authenticated, service_role TO acfo;
CREATE SCHEMA IF NOT EXISTS auth AUTHORIZATION acfo;
CREATE OR REPLACE FUNCTION auth.jwt() RETURNS jsonb LANGUAGE sql STABLE AS $fn$
  SELECT coalesce(current_setting('request.jwt.claims', true), '{}')::jsonb;
$fn$;
GRANT USAGE ON SCHEMA auth TO acfo, anon, authenticated, service_role;
ALTER SCHEMA auth OWNER TO acfo;
ALTER FUNCTION auth.jwt() OWNER TO acfo;
SQL

echo ">> Seeding a local .env if one does not already exist"
if [ ! -f .env ]; then
  cp .env.example .env
  # Point at the local cluster. A real DATABASE_URL secret (injected as an env
  # var) still wins because python-dotenv does not override existing env vars.
  {
    echo ""
    echo "# Added by .cursor/install.sh — local Postgres standing in for Supabase."
    echo "DATABASE_URL=postgresql://acfo:acfo@127.0.0.1:5432/acfo"
  } >> .env
  # Placeholder Exact credentials so init-db (DB-only) works out of the box.
  sed -i 's/^EXACT_CLIENT_ID=$/EXACT_CLIENT_ID=demo-client-id/' .env
  sed -i 's/^EXACT_CLIENT_SECRET=$/EXACT_CLIENT_SECRET=demo-client-secret/' .env
fi

echo ">> install.sh complete"
