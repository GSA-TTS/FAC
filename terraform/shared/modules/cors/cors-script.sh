#!/bin/sh

# Modifying this file will cause terraform to update it in the system and re-apply the cors headers,
# since the md5 will be changing.

curl -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip && rm awscliv2.zip
./aws/install -i ~/usr -b ~/bin
/github/home/bin/aws --version

cf t -o "$1" -s "$2"
SERVICE_INSTANCE_NAME=fac-public-s3;
KEY_NAME=fac-public-s3-key;
cf create-service-key "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}";
echo "Sleeping for CF API"
sleep 10
S3_CREDENTIALS=$(cf service-key "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}" | tail -n +2);
export AWS_ACCESS_KEY_ID="$(echo "$S3_CREDENTIALS" | jq -r .credentials.access_key_id)";
export AWS_SECRET_ACCESS_KEY="$(echo "$S3_CREDENTIALS" | jq -r .credentials.secret_access_key)";
export BUCKET_NAME="$(echo "$S3_CREDENTIALS" | jq -r .credentials.bucket)";
export AWS_DEFAULT_REGION="$(echo "$S3_CREDENTIALS" | jq -r .credentials.region)";
echo "Bucket: $BUCKET_NAME";
echo "INFO: Putting CORS config in bucket..."
/github/home/bin/aws s3api put-bucket-cors --bucket "$BUCKET_NAME" --cors-configuration file://"$3";
echo "INFO: aws s3api get-bucket-cors output..."
/github/home/bin/aws s3api get-bucket-cors --bucket "$BUCKET_NAME";
cf delete-service-key -f "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}";
