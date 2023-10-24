#!/bin/bash

# Grab AWS cli
curl -X $https_proxy "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install -i ~/usr -b ~/bin
export PATH=/home/vcap/app/usr/v2/2.13.28/bin:$PATH
aws --version

# Get the fac-private-s3 bucket
export S3CREDS="$(echo $VCAP_SERVICES|jq -r '.s3')"
export FACPRIVS3="$(echo $S3CREDS|jq '.[]|select(.name=="fac-private-s3")'|jq '.credentials')"
export AWS_ACCESS_KEY_ID="$(echo "$FACPRIVS3"|jq -r '.access_key_id')"
export AWS_SECRET_ACCESS_KEY="$(echo "$FACPRIVS3"|jq -r '.secret_access_key')"
export BUCKET_NAME="$(echo "$FACPRIVS3"|jq -r '.bucket')"
export URI="$(echo "$FACPRIVS3"|jq -r '.uri')"
export AWS_DEFAULT_REGION='us-gov-west-1'

# Get the backups bucket
export FACBACKUPS="$(echo $S3CREDS|jq '.[]|select(.name=="backups")'|jq '.credentials')"
export AWS_ACCESS_KEY_ID="$(echo "$FACBACKUPS"|jq -r '.access_key_id')"
export AWS_SECRET_ACCESS_KEY="$(echo "$FACBACKUPS"|jq -r '.secret_access_key')"
export BACKUPS_BUCKET_NAME="$(echo "$FACBACKUPS"|jq -r '.bucket')"

# List contents of root bucket
aws s3 ls "s3://${BUCKET_NAME}"

# Sync the buckets
aws s3 sync s3://${BUCKET_NAME} s3://${BACKUPS_BUCKET_NAME} --dryrun

# Grab the s3 tar binary
#curl -X $https_proxy -L "https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-arm64.zip" -o "s3tar-linux-arm64.zip"
#curl -X $https_proxy -L https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-amd64.zip -o "s3tar-linux-amd64.zip"
#unzip s3tar-linux-arm64.zip

# s3tar create a tar
#s3tar --region $REGION -cvf s3://bucket/prefix/archive.tar s3://bucket/files/
# s3tar copy tar to destination
#s3tar --region $REGION -xvf s3://bucket/prefix/archive.tar -C s3://bucket/destination/
