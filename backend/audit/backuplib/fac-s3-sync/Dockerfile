
FROM python:3.12.0-slim-bullseye
WORKDIR /sync

RUN apt update ; \
    apt install -y \
    curl \
    unzip

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip 
RUN ./aws/install

RUN curl https://dl.min.io/client/mc/release/linux-amd64/mc \
    --create-dirs \
    -o /sync/minio-binaries/mc
RUN chmod +x /sync/minio-binaries/mc

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir boto3

WORKDIR /python
COPY run.py .

ENTRYPOINT [ "python3", "run.py" ]
