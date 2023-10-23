#!/bin/bash

# Grab AWS cli
# Need to add *.amazonaws.com:443 to https proxy
curl -X $https_proxy "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Grab the s3 tar binary
curl -X $https_proxy -L "https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-arm64.zip" -o "s3tar-linux-arm64.zip"
#curl -X $https_proxy -L https://github.com/awslabs/amazon-s3-tar-tool/releases/download/v1.0.14/s3tar-linux-amd64.zip -o "s3tar-linux-amd64.zip"
unzip s3tar-linux-arm64.zip

# s3tar create a tar
s3tar --region $REGION -cvf s3://bucket/prefix/archive.tar s3://bucket/files/
# s3tar copy tar to destination
s3tar --region $REGION -xvf s3://bucket/prefix/archive.tar -C s3://bucket/destination/
