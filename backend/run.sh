#!/bin/bash

if [[ -n "${ENV}" ]]; then
  echo "Environment set as: ${ENV}"
else
  echo "No environment variable ${ENV} is set!"
fi;

export AWS_PRIVATE_ACCESS_KEY_ID=longtest
export AWS_PRIVATE_SECRET_ACCESS_KEY=longtest
export AWS_S3_PRIVATE_ENDPOINT="http://minio:9000"

mc alias set myminio "${AWS_S3_PRIVATE_ENDPOINT}" minioadmin minioadmin
mc mb myminio/gsa-fac-private-s3
mc admin user svcacct add --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" myminio minioadmin

if [[ "${ENV}" == "LOCAL" ]]; then
  aws --endpoint-url=http://minio:9000 s3 mb s3://gsa-fac-private-s3
fi;

# Migrate first
python manage.py migrate
# Run the build/watch assets + run server at the same time
npm run dev & python manage.py runserver 0.0.0.0:8000
