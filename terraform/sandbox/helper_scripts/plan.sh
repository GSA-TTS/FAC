#!/bin/bash

set -e
dir=$(pwd)
cd ..
cf delete-route app.cloud.gov --hostname fac-sandbox-postgrest -f
cf delete-route app.cloud.gov --hostname fac-sandbox -f
terraform plan \
  -var-file="../shared/config/sandbox.tfvars" \
  -out sandbox.tfplan

cd "$dir"
