# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                         #
# --------------- Base Image -------------------------    #
#                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
FROM python:3.11-bookworm AS python-base

ARG MY_UID
ARG MY_USERNAME
ARG MY_GID
ARG MY_GROUP

ENV \
    # python in unbuffered mode: to avoid delay in logs or print statements
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # dependencies and virtual environment paths
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend venv to path
ENV PATH="$VENV_PATH/bin:$PATH"

# create a user and group
RUN addgroup --system --gid ${MY_GID} ${MY_GROUP} && \
    adduser --system --uid ${MY_UID} --gid ${MY_GID} --shell /bin/bash --disabled-password ${MY_USERNAME}


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                         #
# --------------- Builder Image ------------------------- #
#                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
FROM python-base AS builder
ENV \
    # pip
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=60 \
    # poetry
    POETRY_VERSION=1.8.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_OPTIONS_NO_PIP=1

ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    curl -sSL https://install.python-poetry.org | python3 -

# Configure Poetry authentication
ARG GITHUB_USERNAME
ARG GITHUB_TOKEN
RUN poetry config repositories.github https://github.com/${GITHUB_USERNAME}/proseva.git
RUN poetry config http-basic.github ${GITHUB_USERNAME} ${GITHUB_TOKEN}

# Set working directory
WORKDIR $PYSETUP_PATH

# Copy only poetry files to install dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                         #
# --------------- Runtime Image ------------------------- #
#                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
FROM python-base as runtime
ARG MY_USERNAME
WORKDIR /opt/proseva/microservices/listing
ENV PYTHONPATH="src:${PYTHONPATH}"

RUN mkdir -p /var/log/listing-microservice
RUN chown -R ${MY_USERNAME}:${MY_GROUP} /var/log/listing-microservice

COPY --from=builder $VENV_PATH $VENV_PATH
COPY . ./
EXPOSE 80
USER ${MY_USERNAME}
CMD ["gunicorn", "-c", "gunicorn_config.py", "listing.app:app"]
