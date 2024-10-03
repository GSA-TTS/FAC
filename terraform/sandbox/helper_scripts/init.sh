#!/bin/bash
# The content of this file is managed by Terraform. If you modify it, it may
# be reverted the next time Terraform runs. If you want to make changes, do it
# in ../meta/bootstrap-env/templates.

set -e
dir=$(pwd)
cd ..
terraform init \
  --backend-config=../shared/config/sandbox.tfvars \
  --backend-config=key=terraform.tfstate.$(basename "$(pwd)")

cd "$dir"
