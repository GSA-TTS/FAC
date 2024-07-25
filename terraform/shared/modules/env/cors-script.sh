#!/bin/sh

cf t -o "$1" -s "$2"
SERVICE_INSTANCE_NAME=fac-public-s3;
KEY_NAME=fac-public-s3-key;
cf create-service-key "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}";
S3_CREDENTIALS=$(cf service-key "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}" | tail -n +2);
export AWS_ACCESS_KEY_ID="$(echo "${S3_CREDENTIALS}" | jq -r .access_key_id)";
export AWS_SECRET_ACCESS_KEY="$(echo "${S3_CREDENTIALS}" | jq -r .secret_access_key)";
export BUCKET_NAME="$(echo "${S3_CREDENTIALS}" | jq -r .bucket)";
export AWS_DEFAULT_REGION="$(echo "${S3_CREDENTIALS}" | jq -r '.region')";
echo "$BUCKET_NAME";
aws s3api put-bucket-cors --bucket "$BUCKET_NAME" --cors-configuration "$3";
aws s3api get-bucket-cors --bucket "$BUCKET_NAME";
cf delete-service-key "${SERVICE_INSTANCE_NAME}" "${KEY_NAME}";
