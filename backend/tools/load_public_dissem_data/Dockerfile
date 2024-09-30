FROM debian:bookworm

RUN apt-get update && \
    apt-get -y upgrade
RUN apt-get install -y \
    postgresql-client \
    curl \
    unzip

WORKDIR /layered
COPY data/sling.yaml .
COPY data/config.json .

# Curl in `sling`
RUN curl -LO 'https://github.com/slingdata-io/sling-cli/releases/latest/download/sling_linux_amd64.tar.gz' \
  && tar xf sling_linux_amd64.tar.gz \
  && rm -f sling_linux_amd64.tar.gz \
  && chmod +x sling \
  && mv sling /bin/sling

RUN curl -L -O https://github.com/GSA-TTS/fac-backup-utility/releases/download/v0.1.8/gov.gsa.fac.cgov-util-v0.1.8-linux-amd64.tar.gz \
    && tar xvzf gov.gsa.fac.cgov-util-v0.1.8-linux-amd64.tar.gz gov.gsa.fac.cgov-util \
    && chmod 755 gov.gsa.fac.cgov-util \ 
    && mv gov.gsa.fac.cgov-util /layered/cgov-util

# This grabs a config file from the repo
# that is intended for local devleopment. Therefore, it has all the right values
# for talking to our stack.
WORKDIR /root/.fac
RUN curl -L -O https://raw.githubusercontent.com/GSA-TTS/fac-backup-utility/refs/heads/main/config.json 

WORKDIR /app
ENTRYPOINT [ "./load_public_data_locally.sh" ]
