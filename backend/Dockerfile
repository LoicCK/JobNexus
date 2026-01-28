# multi-stage build
# first, we build the builder

FROM python:3.14-slim AS builder

WORKDIR /usr/src/app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# we use poetry to get the dependancies, but we will not need it later
RUN pip install poetry poetry-plugin-export

COPY pyproject.toml poetry.lock ./

# we export the dependancies
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

# we use a non-root user for improved security
RUN adduser --disabled-password --gecos '' myuser

# we copy the file as the user
COPY --chown=myuser:myuser . .

USER myuser

# finally, we run the app as the user
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
