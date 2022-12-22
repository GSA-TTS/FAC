#!/usr/bin/env bash

if [[ ! -f "secrets.auto.tfvars" ]]; then
  out=$(../../bin/ops/create_service_account.sh -s production -u config-bootstrap-deployer)
  if [[ $? -gt 0 ]]; then
    echo "Error creating service account. Not running terraform"
    exit 1
  else
    echo "$out" > secrets.auto.tfvars
  fi
fi

terraform $@