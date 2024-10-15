#!/bin/bash

set -e

# Force the user of the script into the sanbox environment.
# This way, we don't accidentally operate on something else.
cf t -s sandbox

dir=$(pwd)
cd ..
DestroyPublicS3() {
  PUBLIC_S3=fac-public-s3;
  PUBLIC_KEY_NAME=fac-public-s3-key;
  cf create-service-key "${PUBLIC_S3}" "${PUBLIC_KEY_NAME}";
  echo "Sleeping for CF API"
  sleep 10
  S3_CREDENTIALS=$(cf service-key "${PUBLIC_S3}" "${PUBLIC_KEY_NAME}" | tail -n +2);
  export AWS_ACCESS_KEY_ID="$(echo "$S3_CREDENTIALS" | jq -r .credentials.access_key_id)";
  export AWS_SECRET_ACCESS_KEY="$(echo "$S3_CREDENTIALS" | jq -r .credentials.secret_access_key)";
  export BUCKET="$(echo "$S3_CREDENTIALS" | jq -r .credentials.bucket)";
  export AWS_DEFAULT_REGION="$(echo "$S3_CREDENTIALS" | jq -r .credentials.region)";
  aws s3 rm s3://$BUCKET/ --recursive
  cf delete-service-key -f "${PUBLIC_S3}" "${PUBLIC_KEY_NAME}";
  echo "Sleeping for CF API"
  sleep 10
}

DestroyPrivateS3() {
  PRIVATE_S3=fac-private-s3;
  PRIVATE_KEY_NAME=fac-private-s3-key;
  cf create-service-key "${PRIVATE_S3}" "${PRIVATE_KEY_NAME}";
  echo "Sleeping for CF API"
  sleep 10
  S3_CREDENTIALS=$(cf service-key "${PRIVATE_S3}" "${PRIVATE_KEY_NAME}" | tail -n +2);
  export AWS_ACCESS_KEY_ID="$(echo "$S3_CREDENTIALS" | jq -r .credentials.access_key_id)";
  export AWS_SECRET_ACCESS_KEY="$(echo "$S3_CREDENTIALS" | jq -r .credentials.secret_access_key)";
  export BUCKET="$(echo "$S3_CREDENTIALS" | jq -r .credentials.bucket)";
  export AWS_DEFAULT_REGION="$(echo "$S3_CREDENTIALS" | jq -r .credentials.region)";
  aws s3 rm s3://$BUCKET/ --recursive
  cf delete-service-key -f "${PRIVATE_S3}" "${PRIVATE_KEY_NAME}";
  echo "Sleeping for CF API"
  sleep 10
}

TerraformDestroy() {
  terraform plan \
    -var-file="../shared/config/sandbox.tfvars" \
    -out sandbox-destroy.tfplan \
    -destroy

  terraform apply sandbox-destroy.tfplan
}

echo "Deleting contents of fac-public-s3"
DestroyPublicS3
echo "Deleting contents of fac-private-s3"
DestroyPrivateS3
echo "Performing Terraform Destroy"
TerraformDestroy

cd "$dir"
