#!/bin/bash
# The content of this file is managed by Terraform. If you modify it, it may
# be reverted the next time Terraform runs. If you want to make changes, do it
# in ../meta/bootstrap-env/templates.

set -e

# Force the user of the script into the sanbox environment.
# This way, we don't accidentally operate on something else.
cf t -s sandbox

dir=$(pwd)
cd ..
basename=$(basename "$(pwd)")
terraform init \
  --backend-config=../shared/config/backend.tfvars \
  --backend-config=key=terraform.tfstate."$basename"

cd "$dir"
