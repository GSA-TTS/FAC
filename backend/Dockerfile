###############################
# FOUNDATION
###############################

FROM python:3.14.3-slim-bookworm AS foundation

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get -yq update && \
    apt install -y \
        build-essential \
        curl \
        jq \
        groff \
        zip && \
        rm -rf /var/lib/apt/lists/*

###############################
# PIP
###############################
FROM foundation AS pip
COPY requirements.txt /tmp/requirements.txt
COPY dev-requirements.txt /tmp/dev-requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/dev-requirements.txt && \
    rm -rf /root/.cache/ && \
    rm -rf /tmp/requirements.txt /tmp/dev-requirements.txt

###############################
# NODE
###############################
FROM pip AS node_build
WORKDIR /src/

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs
COPY package*.json /src/
RUN npm ci 
COPY . /src/

RUN npm run build

###############################
# FINAL
###############################
FROM python:3.12.11-slim-bookworm AS final

RUN apt-get -yq update && \
    apt-get install -y \
        ca-certificates \
        chromium \
        curl \
        # Make sure the client version
        # matches the DB version, locally
        # and in production. AWD RDS is v15 in 
        # cloud.gov as of August 2025.
        postgresql-client-15 && \
    rm -rf /var/lib/apt/lists/*

RUN curl "https://dl.min.io/client/mc/release/linux-amd64/mc" -o "/usr/local/bin/mc" && \
    chmod +x /usr/local/bin/mc

# Copy from pip stage
COPY --from=pip /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=pip /usr/local/bin /usr/local/bin

# Copy from node stage
COPY --from=node_build /src/static/compiled /src/static/compiled

WORKDIR /src/
COPY . /src/

RUN python manage.py collectstatic
