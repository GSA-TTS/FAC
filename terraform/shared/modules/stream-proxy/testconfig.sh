#!/bin/sh

# Copy this file to testconfig.sh, then edit to taste. Don't commit your copy
# to version control!

# user/password are the credentials of a deployer user 
# Instructions for generating them are here:
# https://cloud.gov/docs/services/cloud-gov-service-account/#how-to-create-an-instance

cat << EOF
{ 
  "user": "7e3f116a-8c88-406b-bb15-0fcb0a36c60a",
  "password": "A,o8U0.RY+g4DeMKddP-JvK3VR,I8xdJ",
  "cf_org_name": "sandbox-gsa",
  "cf_space_name": "bret.mogilefsky"
}
EOF
