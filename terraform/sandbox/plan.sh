#!/bin/bash

set -e

terraform plan \
  -var-file="../shared/config/sandbox.tfvars" \
  -out sandbox.tfplan
