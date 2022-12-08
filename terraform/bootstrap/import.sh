#!/usr/bin/env bash

read -p "Are you sure you want to import terraform state (y/n)? " verify

if [[ $verify == "y" ]]; then
  echo "Importing bootstrap state"
  ./run.sh import module.s3.cloudfoundry_service_instance.bucket 2f8babdc-0bd4-4281-b9ab-584a634566b1
  ./run.sh import cloudfoundry_service_key.bucket_creds 3da2a5d0-2fd7-4e3a-a0c2-5773a885b082
  ./run.sh plan
else
  echo "Not importing bootstrap state"
fi
