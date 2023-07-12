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
    mc admin user svcacct add --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" myminio minioadmin
fi;

API_VERSIONS=(api_v1_0_0_beta)

create_views() {
    for version in "${API_VERSIONS[@]}"
    do
        echo "🚨"
        echo $version
        python manage.py create_views --api_version $version
    done
}

# Migrate first
python manage.py migrate && create_views
# Run the build/watch assets + run server at the same time
npm run dev & python manage.py runserver 0.0.0.0:8000
