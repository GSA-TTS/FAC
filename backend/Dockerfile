FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt

RUN apt-get -y update
RUN apt-get -y install git

# RUN --mount=type=cache,target=/root/.cache \

WORKDIR ..

RUN \
  apt-get update && \
  apt-get install -yqq apt-transport-https wget gnupg2  && \
  apt-get install wget && \
  wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | apt-key add - && \
  echo "deb https://packages.cloudfoundry.org/debian stable main" | tee /etc/apt/sources.list.d/cloudfoundry-cli.list && \
  apt-get update && \
  apt-get install cf7-cli

RUN \
    apt-get update -yq && \
    echo "deb https://deb.nodesource.com/node_14.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
    wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    apt-get -y install nodejs && \
    apt-get install nodejs npm -yqq && \
    npm i -g npm@^8


RUN \
    set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/dev-requirements.txt && \
    rm -rf /root/.cache/

COPY . /src/

WORKDIR /src/

RUN npm install
RUN chown -R 1001:123 "/root/.npm"
RUN npm run build && python manage.py shell --command="import environs; env = environs.Env(); print(env.str('ENV', 'UNDEFINED').upper())" && python manage.py collectstatic


# ------------------------------------------------------------
# Dev/testing layer
# ------------------------------------------------------------

FROM builder AS release

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
