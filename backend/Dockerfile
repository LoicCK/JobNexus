FROM python:3.14-slim

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --no-dev

RUN adduser --disabled-password --gecos '' myuser

COPY --chown=myuser:myuser . .

USER myuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
