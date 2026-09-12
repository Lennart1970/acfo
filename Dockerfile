FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY supabase ./supabase
COPY sql ./sql

RUN pip install --no-cache-dir .

# Railway cron: run once and exit. Session-pooler DATABASE_URL required.
CMD ["python", "-m", "acfo", "sync"]
