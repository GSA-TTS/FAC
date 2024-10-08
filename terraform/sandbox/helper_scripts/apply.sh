#!/bin/bash

set -e
dir=$(pwd)
cd ..
terraform apply \
  sandbox.tfplan
cd "$dir"
