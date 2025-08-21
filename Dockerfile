FROM python:3.11-slim AS base

ENV POETRY_VERSION=1.8.3 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app


COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --without dev --no-interaction --no-ansi


FROM base AS development
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM base AS production
COPY . .

CMD ["sh", "-c", "until pg_isready -h ${DB_HOST:-db} -p 5432 > /dev/null; do sleep 1; done; alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
