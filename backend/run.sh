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

# Migrate historic data first
echo 'Starting migration of historic tables' &&
python manage.py migrate --database census-to-gsafac-db &&
echo 'Finished migration of historic tables' &&
# API has to be deprecated/removed before migration, because
# of tight coupling between schema/views and the dissemination tables
echo 'Starting API schema deprecation' &&
python manage.py drop_deprecated_api_schema_and_views &&
echo 'Finished API schema deprecation' &&
echo 'Dropping API schema' &&
python manage.py drop_api_schema &&
echo 'Finished dropping API schema' &&
# Migrate the internal models
echo 'Starting migrate' &&
python manage.py migrate &&
echo 'Finished migrate' &&
# First create non-managed tables
echo 'Starting create_access_tables' &&
python manage.py create_access_tables &&
echo 'Finished create_access_tables' &&
# Bring the API back, possibly installing a new API
echo 'Starting API schema creation' &&
python manage.py create_api_schema &&
echo 'Finished API schema creation' &&
echo 'Starting API view creation' &&
python manage.py create_api_views &&
echo 'Finished view creation' &&
# Update the cog/baseline table
echo 'Starting seed_cog_baseline' &&
python manage.py seed_cog_baseline &&
echo 'Finished seed_cog_baseline'

npm run dev & python manage.py runserver 0.0.0.0:8000
