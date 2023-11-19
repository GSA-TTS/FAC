#!/bin/bash

SOURCE_BUCKET=gsa-fac-private-s3
DEST_BUCKET=daily-sync-gsa-fac-private-s3
MC=/sync/minio-binaries/mc

echo "Running a daily sync from ${SOURCE_BUCKET} to ${DEST_BUCKET}"

if [[ -n "${ENV}" ]]; then
  echo "Environment set as: ${ENV}"
else
  echo "No environment variable ${ENV} is set!"
fi;

if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
    export AWS_PRIVATE_ACCESS_KEY_ID=longtest
    export AWS_PRIVATE_SECRET_ACCESS_KEY=longtest
    export AWS_S3_PRIVATE_ENDPOINT="http://localhost:9000"
    $MC alias set myminio "${AWS_S3_PRIVATE_ENDPOINT}" minioadmin minioadmin
    $MC mb myminio/gsa-fac-private-s3
    $MC mb myminio/fac-census-to-gsafac-s3
    $MC mb myminio/daily-sync-gsa-fac-private-s3
    $MC mb myminio/weekly-sync-gsa-fac-private-s3
fi;

npx s3p sync --bucket gsa-fac-private-s3 daily-sync-gsa-fac-private-s3
