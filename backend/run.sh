#!/bin/bash

if [[ -n "${ENV}" ]]; then
  echo "Environment set as: ${ENV}"
else
  echo "No environment variable ${ENV} is set!"
fi;

sleep 10

if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
    export AWS_PRIVATE_ACCESS_KEY_ID=longtest
    export AWS_PRIVATE_SECRET_ACCESS_KEY=longtest
    export AWS_S3_PRIVATE_ENDPOINT="http://minio:9000"
    mc alias set myminio "${AWS_S3_PRIVATE_ENDPOINT}" minioadmin minioadmin
    mc mb myminio/gsa-fac-private-s3
    mc mb myminio/fac-census-to-gsafac-s3
    mc admin user svcacct add --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" myminio minioadmin
fi;

# Migrate first
python manage.py migrate
python manage.py migrate --database census-to-gsafac-db


echo 'Starting API schema deprecation' &&
python manage.py drop_deprecated_api_schema_and_views &&
echo 'Finished API schema deprecation' &&
echo 'Dropping API schema' &&
python manage.py drop_api_schema &&
echo 'Finished dropping API schema' &&
echo 'Starting API schema creation' &&
python manage.py create_api_schema &&
echo 'Finished API schema creation' &&
echo 'Starting API view creation' &&
python manage.py create_api_views &&
echo 'Finished view creation' &&
echo 'Starting seed_cog_baseline' &&
python manage.py seed_cog_baseline &&
echo 'Finished seed_cog_baseline'

npm run dev & python manage.py runserver 0.0.0.0:8000
