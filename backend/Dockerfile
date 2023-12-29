FROM python:3.10-slim AS foundation

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -yq update && \
    apt install -y \
        apt-transport-https \ 
        build-essential \
        ca-certificates \
        curl \
        git \
        gcc \
        gnupg \
        gnupg2 \
        postgresql-client \
        wget 

FROM foundation AS node

ENV NODE_MAJOR 18 
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

# We have to update after adding to the apt sources lists.
RUN apt-get update
RUN apt-get install -y nodejs npm 

COPY package.* /src/
WORKDIR /src/

# RUN npm install
RUN npm i -g npm@latest --force
RUN npm i -g npm-run-all
RUN chown -R 1001:123 "/root/.npm"

FROM node AS pip

COPY requirements.txt /tmp/requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/dev-requirements.txt && \
    rm -rf /root/.cache/

FROM pip AS storage

RUN apt-get install -yqq groff && \
    apt-get install -yqq zip && \
    curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" && \
    unzip awscli-bundle.zip && \
    ./awscli-bundle/install -b /usr/local/bin/aws

RUN curl "https://dl.min.io/client/mc/release/linux-amd64/mc" -o "/usr/local/bin/mc" && \
    chmod +x /usr/local/bin/mc

COPY . /src/

FROM storage AS dev

RUN npm run build && python manage.py collectstatic
