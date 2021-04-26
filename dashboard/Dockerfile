FROM python:3.8 as build

ARG FLASK_ENV='production'
ARG FLASK_DEBUG=0

#ARG FLASK_ENV='development'
#ARG FLASK_DEBUG=1

ENV FLASK_ENV=${FLASK_ENV} \
  FLASK_DEBUG=${FLASK_DEBUG} \
  FLASK_APP=dashboard/__init__.py \
  # build:
  BUILD_ONLY_PACKAGES='wget' \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.1.6 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="$PATH:/root/.poetry/bin"

# System deps:
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    # Defining build-time-only dependencies:
    $BUILD_ONLY_PACKAGES \
  # Installing `poetry` package manager:
  # https://github.com/python-poetry/poetry
  && curl -sSL 'https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py' | python \
  && poetry --version \
  # Removing build-time-only dependencies:
  && apt-get remove -y $BUILD_ONLY_PACKAGES \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Setting up proper permissions:
RUN groupadd -r web && useradd -d /app -r -g web web \
  && chown web:web -R /app

# Copy only requirements, to cache them in docker layer
COPY --chown=web:web ./poetry.lock ./pyproject.toml /app/

# Project initialization:
RUN poetry install \
    $(if [ "$FLASK_ENV" = 'production' ]; then echo '--no-dev'; fi) \
    --no-interaction --no-ansi \
  # Cleaning poetry installation's cache for production:
  && if [ "$FLASK_ENV" = 'production' ]; then rm -rf "$POETRY_CACHE_DIR"; fi

# Running as non-root user:
USER web

EXPOSE 443
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "443", "--cert", "adhoc"]

# The following stage is only for Prod:
FROM build AS production
COPY --chown=web:web . /app