###############################
# FOUNDATION
###############################

FROM python:3.10-slim AS foundation

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -yq update && \
    apt install -y \
        apt-transport-https \ 
        build-essential \
        ca-certificates \
        chromium \
        curl \
        git \
        gcc \
        gnupg \
        gnupg2 \
        postgresql-client \
        wget 

###############################
# STORAGE
###############################
FROM foundation AS storage
RUN apt-get install -yqq groff && \
    apt-get install -yqq zip && \
    curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" && \
    unzip awscli-bundle.zip && \
    ./awscli-bundle/install -b /usr/local/bin/aws
RUN curl "https://dl.min.io/client/mc/release/linux-amd64/mc" -o "/usr/local/bin/mc" && \
    chmod +x /usr/local/bin/mc

###############################
# PIP
###############################
FROM storage AS pip
COPY requirements.txt /tmp/requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/dev-requirements.txt && \
    rm -rf /root/.cache/

###############################
# NODE
###############################
FROM pip AS node
WORKDIR /src/

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs
COPY package*.json /src/
RUN npm ci && \
    chown -R 1001:123 "/root/.npm"

COPY . /src/

RUN npm run build 

###############################
# DEV
###############################
FROM node AS dev
WORKDIR /src/
RUN python manage.py collectstatic
