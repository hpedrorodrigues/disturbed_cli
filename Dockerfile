FROM python:3.15-alpine AS builder

WORKDIR /app

ENV POETRY_VERSION=1.8.3

COPY pyproject.toml poetry.lock /app/

RUN apk update \
    && apk add --no-cache  \
      gcc \
      musl-dev \
      yaml-dev \
    && rm -rf /var/cache/apk/* \
    && pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-ansi \
    && python -m compileall .

FROM python:3.15-alpine

WORKDIR /app

RUN apk update \
    && apk add --no-cache yaml \
    && rm -rf /var/cache/apk/*

COPY --from=builder /app/ /app/
COPY disturbed /app/disturbed/
COPY main.py /app/

ENTRYPOINT ["/app/.venv/bin/python"]
CMD ["/app/main.py"]
