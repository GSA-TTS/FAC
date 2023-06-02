#!/bin/bash

export AWS_PRIVATE_ACCESS_KEY_ID=longtest
export AWS_PRIVATE_SECRET_ACCESS_KEY=longtest
export AWS_S3_PRIVATE_ENDPOINT="http://minio:9000"

mc alias set myminio "${AWS_S3_PRIVATE_ENDPOINT}" minioadmin minioadmin
mc mb myminio/gsa-fac-private-s3
mc admin user svcacct add --access-key="${AWS_PRIVATE_ACCESS_KEY_ID}" --secret-key="${AWS_PRIVATE_SECRET_ACCESS_KEY}" myminio minioadmin