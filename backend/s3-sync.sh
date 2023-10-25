#!/bin/bash

# This requires: cf bind-service gsa-fac fac-private-s3 -c '{"additional_instances": ["backups"]}'

# Grab AWS cli
curl -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && rm awscliv2.zip
./aws/install -i ~/usr -b ~/bin
export PATH=/home/vcap/app/usr/v2/2.13.28/bin:$PATH
aws --version

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
curl -L "https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-amd64.zip" -o "s3tar-linux-amd64.zip"
unzip s3tar-linux-amd64.zip && rm s3tar-linux-amd64.zip

# Create a single tar in the source bucket
./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -cvf s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/archive.tar s3://${FAC_MEDIA_BUCKET} --storage-class INTELLIGENT_TIERING

# List contents of source bucket
aws s3 ls s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/

# Move the tar to the backups bucket
aws s3 sync s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/ s3://${BACKUPS_BUCKET}/mediabackups/$date/ --storage-class INTELLIGENT_TIERING
# Share the Tar to dest and extract (without including the tar)
#./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -cvf s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/archive.tar -C s3://${BACKUPS_BUCKET}/mediabackups/$date/ --storage-class INTELLIGENT_TIERING

# List contents of destination bucket
aws s3 ls s3://${BACKUPS_BUCKET}/mediabackups/$date/

# Cleanup the source bucket so older backups don't get added to the tar
aws s3 rm s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/archive.tar
aws s3 rm s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/

# List contents of source bucket to ensure everything was deleted properly
aws s3 ls s3://${FAC_MEDIA_BUCKET}/mediabackups/$date/
