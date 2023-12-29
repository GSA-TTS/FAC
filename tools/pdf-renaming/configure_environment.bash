# Source this file into your shell before 
# running any operations in the scripts.

cf target -s preview

PREVIEW_SERVICE_INSTANCE_NAME=fac-private-s3
PREVIEW_KEY_NAME=jadud-fac-private-s3

cf create-service-key "${PREVIEW_SERVICE_INSTANCE_NAME}" "${PREVIEW_KEY_NAME}"
PREVIEW_S3_CREDENTIALS=$(cf service-key "${PREVIEW_SERVICE_INSTANCE_NAME}" "${PREVIEW_KEY_NAME}" | tail -n +2)

export PREVIEW_AWS_ACCESS_KEY_ID=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.access_key_id')
export PREVIEW_AWS_SECRET_ACCESS_KEY=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.secret_access_key')
export PREVIEW_BUCKET_NAME=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.bucket')
export PREVIEW_URI=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.uri')
export PREVIEW_AWS_DEFAULT_REGION=$(echo "${PREVIEW_S3_CREDENTIALS}" | jq -r '.region')

# The bucket is in the production environment.
# We have to switch there to grab the credentials.
cf target -s production

CENSUS_SERVICE_INSTANCE_NAME=Census-data-transfer
CENSUS_KEY_NAME=jadud-s3-key

cf create-service-key "${CENSUS_SERVICE_INSTANCE_NAME}" "${CENSUS_KEY_NAME}"
CENSUS_S3_CREDENTIALS=$(cf service-key "${CENSUS_SERVICE_INSTANCE_NAME}" "${CENSUS_KEY_NAME}" | tail -n +2)

export CENSUS_AWS_ACCESS_KEY_ID=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.access_key_id')
export CENSUS_AWS_SECRET_ACCESS_KEY=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.secret_access_key')
export CENSUS_BUCKET_NAME=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.bucket')
export CENSUS_URI=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.uri')
export CENSUS_AWS_DEFAULT_REGION=$(echo "${CENSUS_S3_CREDENTIALS}" | jq -r '.region')

# Don't leave us in the production environment.
cf target -s preview

# Set the LOCAL_TEMP_PATH manually.
