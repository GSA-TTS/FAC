#!/bin/bash

if [[ -n "${ENV}" ]]; then
  echo "Environment set as: ${ENV}"
else
  echo "No environment variable ${ENV} is set!"
fi;

export AWS_PRIVATE_ACCESS_KEY_ID=longtest
export AWS_PRIVATE_SECRET_ACCESS_KEY=longtest
export AWS_S3_PRIVATE_ENDPOINT="http://minio:9001"

mc alias set myminio "${AWS_S3_PRIVATE_ENDPOINT}" minioadmin minioadmin
mc mb myminio/gsa-fac-private-s3
mc admin user svcacct add --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" myminio minioadmin

if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
  aws --endpoint-url=${AWS_S3_PRIVATE_ENDPOINT} s3 mb s3://gsa-fac-private-s3
fi;

# Migrate first
python manage.py migrate

# Run the build/watch assets + run server at the same time
if [[ "${VSCODE_DEBUG}" == 1 ]]; then 
  echo "RUNNING WITH VSCODE DEBUGGING"
  # FIXME MCJ 20230614 - Add this to the container build.
  pip install debugpy -t /tmp
  npm run dev & python /tmp/debugpy --wait-for-client --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000
else
  echo "RUNNING WITHOUT DEBUGGER"
  npm run dev & python manage.py runserver 0.0.0.0:8000
fi;