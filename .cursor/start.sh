#!/usr/bin/env bash
# Per-boot startup: bring the local Postgres cluster online and wait until it
# is ready to accept connections. Safe to run repeatedly.
set -euo pipefail

PG_VERSION=16

sudo pg_ctlcluster "$PG_VERSION" main start || true

for _ in $(seq 1 30); do
  if sudo -u postgres pg_isready -q; then
    echo "PostgreSQL ${PG_VERSION} is ready."
    exit 0
  fi
  sleep 1
done

echo "PostgreSQL ${PG_VERSION} did not become ready in time." >&2
exit 1
