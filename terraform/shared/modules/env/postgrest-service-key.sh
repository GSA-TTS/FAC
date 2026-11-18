#!/bin/bash

set -e

INPUT=$(cat)
ORG_NAME=$(jq -r '.org_name' <<< $INPUT)
SPACE=$(jq -r '.space' <<< $INPUT)

cf target -o $ORG_NAME -s $SPACE > /dev/null
cf create-service-key fac-db postgrest > /dev/null # this will do nothing if service key already exists

SERVICE_KEY_ID=$(cf service-key fac-db postgrest --guid)

cf curl /v3/service_credential_bindings/$SERVICE_KEY_ID/details | jq '.credentials'
