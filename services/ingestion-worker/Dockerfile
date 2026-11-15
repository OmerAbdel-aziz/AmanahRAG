FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

COPY pyproject.toml ./
COPY worker ./worker
RUN pip install --upgrade pip && pip install .

RUN useradd --create-home --uid 10001 appuser
USER appuser

CMD ["python", "-m", "worker.main"]
