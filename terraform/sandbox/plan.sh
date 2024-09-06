#!/bin/bash

set -e
terraform plan \
  -out sandbox.tfplan
