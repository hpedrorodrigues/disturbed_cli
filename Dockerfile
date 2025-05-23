FROM python:3.13-alpine AS builder

WORKDIR /app

ENV POETRY_VERSION=1.8.3

COPY pyproject.toml poetry.lock /app/

RUN apk update \
    && apk add --no-cache  \
      gcc \
      musl-dev \
    && rm -rf /var/cache/apk/* \
    && pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-ansi \
    && python -m compileall .

FROM python:3.13-alpine

WORKDIR /app

COPY --from=builder /app/ /app/
COPY disturbed /app/disturbed/
COPY main.py /app/

ENTRYPOINT ["/app/.venv/bin/python"]
CMD ["/app/main.py"]
