#!/bin/bash

echo "Environment set as: ${ENV}"

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
if [[ "${ENV}" == "LOCAL" ]]; then
    aws --endpoint-url=http://localstack:4566 s3 mb s3://gsa-fac-public-s3
    aws --endpoint-url=http://localstack:4566 s3 mb s3://gsa-fac-private-s3
fi;

python manage.py migrate
npm run dev & python manage.py runserver 0.0.0.0:8000