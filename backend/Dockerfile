FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN apt-get -y install git

# RUN --mount=type=cache,target=/root/.cache \

WORKDIR ..

RUN \
  apt-get update && \
  apt-get install -yqq apt-transport-https wget gnupg2

RUN \
    apt-get update -yq && \
    apt install curl -y && \
    curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    npm i -g npm@^8

RUN \
    apt-get install -yqq groff && \
    apt-get install -yqq zip && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

COPY requirements.txt /tmp/requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt

RUN \
    set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/dev-requirements.txt && \
    rm -rf /root/.cache/

COPY package.* /src/
WORKDIR /src/

RUN npm install
RUN chown -R 1001:123 "/root/.npm"

COPY . /src/

RUN npm run build && python manage.py collectstatic

# ------------------------------------------------------------
# Dev/testing layer
# ------------------------------------------------------------

FROM builder AS release

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
