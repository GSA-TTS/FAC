#!/bin/bash

set -e
dir=$(pwd)
cd ..
cf delete-route app.cloud.gov --hostname fac-sandbox-postgrest -f
cf delete-route app.cloud.gov --hostname fac-sandbox -f
cf delete-route apps.internal --hostname fac-file-scanner-fs -f
terraform plan \
  -var-file="../shared/config/sandbox.tfvars" \
  -out sandbox.tfplan

cd "$dir"
