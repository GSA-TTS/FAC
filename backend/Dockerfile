FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt


# RUN --mount=type=cache,target=/root/.cache \
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/dev-requirements.txt && \
    rm -rf /root/.cache/

# ------------------------------------------------------------
# Dev/testing layer
# ------------------------------------------------------------

FROM builder AS release

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /src/

WORKDIR /src/
