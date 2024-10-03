#!/bin/bash

set -e
dir=$(pwd)
cd ..

terraform plan \
  -var-file="../shared/config/sandbox.tfvars" \
  -out sandbox.tfplan

cd "$dir"
