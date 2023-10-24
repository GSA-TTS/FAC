#!/bin/bash

# Grab AWS cli
curl -X $https_proxy "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install -i ~/usr -b ~/bin
export PATH=/home/vcap/app/usr/v2/2.13.28/bin:$PATH
aws --version

# Get the s3 from $VCAP_SERVICES
export S3CREDS="$(echo $VCAP_SERVICES|jq -r '.s3')"

# Get the fac-private-s3 bucket
export FACPRIVS3="$(echo $S3CREDS|jq '.[]|select(.name=="fac-private-s3")'|jq '.credentials')"
export AWS_ACCESS_KEY_ID="$(echo "$FACPRIVS3"|jq -r '.access_key_id')"
export AWS_SECRET_ACCESS_KEY="$(echo "$FACPRIVS3"|jq -r '.secret_access_key')"
export BUCKET_NAME="$(echo "$FACPRIVS3"|jq -r '.bucket')"
export URI="$(echo "$FACPRIVS3"|jq -r '.uri')"
export AWS_DEFAULT_REGION='us-gov-west-1'

# Get the backups bucket
# export FACBACKUPS="$(echo $S3CREDS|jq '.[]|select(.name=="backups")'|jq '.credentials')"
# export AWS_ACCESS_KEY_ID="$(echo "$FACBACKUPS"|jq -r '.access_key_id')"
# export AWS_SECRET_ACCESS_KEY="$(echo "$FACBACKUPS"|jq -r '.secret_access_key')"
# export BACKUPS_BUCKET_NAME="$(echo "$FACBACKUPS"|jq -r '.bucket')"

# List contents of root bucket
aws s3 ls "s3://${BUCKET_NAME}"

# Sync the buckets
#aws s3 sync s3://${BUCKET_NAME} s3://${BACKUPS_BUCKET_NAME} --dryrun

##########
# s3 tar #
##########

# Grab the s3 tar binary
curl -L "https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-amd64.zip" -o "s3tar-linux-amd64.zip"
unzip s3tar-linux-arm64.zip
# Create a tar in the source bucket
./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -cvf s3://${BUCKET_NAME}/prefix/archive.tar s3://${BUCKET_NAME}

# This gets us the following:
# ./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -cvf s3://${BUCKET_NAME}/prefix/archive.tar s3://${BUCKET_NAME}
# estimated tar size: 637238272
# processing 263 Amazon S3 Objects
# final size 0GB (without tar headers + padding)
# estimated final size: 637334517 bytes (with headers + padding)
# multipart part-size: 5242880 bytes
# Final Object: s3://${BUCKET_NAME}/prefix/archive.tar
# deleting all intermediate objects
# Time elapsed: 39.093430244s
# vcap@630ee638-71b3-4821-7a74-b60e:~$ aws s3 ls "s3://${BUCKET_NAME}/prefix/"
# 2023-10-24 13:43:52  637268480 archive.tar

# List contents of backups bucket
aws s3 ls "s3://${BACKUPS_BUCKET_NAME}"

# Share the Tar to dest
./s3tar-linux-amd64 --region $AWS_DEFAULT_REGION -xvf s3://${BUCKET_NAME}/prefix/archive.tar -C s3://${BACKUPS_BUCKET_NAME}/mediabackups/
