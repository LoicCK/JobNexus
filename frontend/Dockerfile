FROM python:3.14-slim AS builder

WORKDIR /usr/src/app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install poetry poetry-plugin-export

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install -r requirements.txt

FROM python:3.14-slim

LABEL authors="LoicCK"

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

RUN adduser --disabled-password --gecos '' myuser

COPY --chown=myuser:myuser . .

USER myuser

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
