FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY zscaler_cert.pem /tmp/zscaler.crt
COPY requirements.txt /tmp/requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt

RUN if [ "$ENV" = "LOCAL" ] ; then cp /tmp/zscaler.crt /usr/local/share/ca-certificates/zscaler.crt ; update-ca-certificates ; fi

RUN apt-get -y update
RUN apt-get -y install git

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive \
    apt-get install --no-install-recommends --assume-yes \
      postgresql-client

WORKDIR ..

# Dependencies
RUN \
    apt-get update -yq && \
    apt-get install -yqq \
        apt-transport-https \
        wget \
        gnupg2 \
        build-essential \
        curl \
        gcc \
        ca-certificates \
        gnupg \
        groff \
        zip \
    ; \
    # Install zscaler cert for local builds
    if [ "$ENV" = "LOCAL" ] ; then cp /tmp/zscaler.crt /usr/local/share/ca-certificates/zscaler.crt ; update-ca-certificates ; fi \
    # Updated nodesource install via: https://github.com/nodesource/distributions#ubuntu-versions
    && mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    NODE_MAJOR=18 && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install nodejs -y \
    ; \
    # Pip install
    set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/dev-requirements.txt && \
    rm -rf /root/.cache/ \
    ; \
    # AWS CLI install
    curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" && \
    unzip awscli-bundle.zip && \
    ./awscli-bundle/install -b /usr/local/bin/aws \
    ; \
    # Minio install
    curl "https://dl.min.io/client/mc/release/linux-amd64/mc" -o "/usr/local/bin/mc" && \
    chmod +x /usr/local/bin/mc

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
