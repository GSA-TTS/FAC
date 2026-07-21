###############################
# FOUNDATION
###############################

FROM python:3.12.13-slim-bookworm AS foundation

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get -yq update && \
    apt install -y \
        build-essential \
        curl \
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
FROM python:3.12.13-slim-bookworm AS final

RUN apt-get -yq update && \
    apt-get install -y \
        ca-certificates \
        chromium \
        curl \
        unzip \
        # Make sure the client version
        # matches the DB version, locally
        # and in production. AWD RDS is v15 in
        # cloud.gov as of August 2025.
        postgresql-client-15 \
        # tools needed for prepare_prod_data_for_local.bash
        gpg \
        jq \
        wget \
        groff \
        zip && \
    wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key \
        | gpg --dearmor -o /usr/share/keyrings/cli.cloudfoundry.org.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cli.cloudfoundry.org.gpg] https://packages.cloudfoundry.org/debian stable main" \
        | tee /etc/apt/sources.list.d/cloudfoundry-cli.list && \
    apt update && \
    apt install cf8-cli && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -f awscliv2.zip && \
    rm -rf aws/

RUN curl -LOf https://github.com/rustfs/cli/releases/download/v0.1.28/rustfs-cli-linux-amd64-v0.1.28.tar.gz && \
 tar -xvf rustfs-cli-linux-amd64-v0.1.28.tar.gz && \
 mv rc /usr/local/bin/rc && \
 chmod +x /usr/local/bin/rc && \
 rm rustfs-cli-linux-amd64-v0.1.28.tar.gz


# Copy from pip stage
COPY --from=pip /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=pip /usr/local/bin /usr/local/bin

# Copy from node stage
COPY --from=node_build /src/static/compiled /src/static/compiled

WORKDIR /src/
COPY . /src/

RUN python manage.py collectstatic
