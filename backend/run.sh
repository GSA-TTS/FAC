#!/bin/bash

if [[ -n "${ENV}" ]]; then
  echo "Environment set as: ${ENV}"
else
  echo "No environment variable `ENV` is set!"
fi;

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

if [[ "${ENV}" == "LOCAL" ]]; then
    aws --endpoint-url=http://localstack:4566 s3 mb s3://gsa-fac-private-s3
fi;

# Migrate first
python manage.py migrate
# Run the build/watch assets + run server at the same time
npm run dev & python manage.py runserver 0.0.0.0:8000