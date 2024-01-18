#!/bin/bash

# This requires: cf bind-service gsa-fac fac-private-s3 -c '{"additional_instances": ["backups"]}'

# Grab AWS cli
# awscli.amazonaws.com needs to be added to the proxy allow list
curl -x $https_proxy -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && rm awscliv2.zip
./aws/install -i ~/usr -b ~/bin
/home/vcap/app/bin/aws --version

# Get the fac-private-s3 bucket
export S3CREDS="$(echo $VCAP_SERVICES|jq -r '.s3')"
export FACPRIVS3="$(echo $S3CREDS|jq '.[]|select(.name=="fac-private-s3")'|jq '.credentials')"
export AWS_ACCESS_KEY_ID="$(echo "$FACPRIVS3"|jq -r '.access_key_id')"
export AWS_SECRET_ACCESS_KEY="$(echo "$FACPRIVS3"|jq -r '.secret_access_key')"
export FAC_MEDIA_BUCKET="$(echo "$FACPRIVS3"|jq -r '.bucket')"
export AWS_DEFAULT_REGION='us-gov-west-1'

# Get the backups bucket
export FACBACKUPS="$(echo $S3CREDS|jq '.[]|select(.name=="backups")'|jq '.credentials')"
export BACKUPS_BUCKET="$(echo "$FACBACKUPS"|jq -r '.bucket')"

date=$(date +%Y%m%d%H%M)

# Grab the s3 tar binary
# objects.githubusercontent.com needs to be added to the proxy allow list
curl -x $https_proxy -L "https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-amd64.zip" -o "s3tar-linux-amd64.zip"
unzip s3tar-linux-amd64.zip && rm s3tar-linux-amd64.zip

# Unset the proxy so that s3tar-tool and aws-cli can function. Without doing this, none of the subsequent commands will work
unset https_proxy

# Create a single tar in the backups bucket
./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -cvf s3://${BACKUPS_BUCKET}/mediabackups/$date/archive.tar s3://${FAC_MEDIA_BUCKET} --storage-class INTELLIGENT_TIERING
# List out the contents
./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -tvf s3://${BACKUPS_BUCKET}/mediabackups/$date/archive.tar
