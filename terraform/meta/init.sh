#!/bin/bash

set -e
terraform init \
  --backend-config=../shared/config/backend.tfvars \
  --backend-config=key=terraform.tfstate.$(basename $(pwd))
