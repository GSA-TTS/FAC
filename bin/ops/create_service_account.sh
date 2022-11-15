#!/usr/bin/env bash

org="gsa-tts-oros-fac"

usage="
$0: Create a Service User Account for a given space

Usage:
  $0 -h
  $0 -s <SPACE NAME> -u <USER NAME> [-r <ROLE NAME>] [-o <ORG NAME>]

Options:
-h: show help and exit
-s <SPACE NAME>: configure the space to act on. Required
-u <USER NAME>: set the service user name. Required
-r <ROLE NAME>: set the service user's role to either space-deployer or space-auditor. Default: space-deployer
-o <ORG NAME>: configure the organization to act on. Default: $org
"

set -e
set -o pipefail

space=""
service=""
role="space-deployer"

while getopts ":hs:u:r:o:" opt; do
  case "$opt" in
    s)
      space=${OPTARG}
      ;;
    u)
      service=${OPTARG}
      ;;
    r)
      role=${OPTARG}
      ;;
    o)
      org=${OPTARG}
      ;;
    h)
      echo "$usage"
      exit 0
      ;;
  esac
done

if [[ $space = "" || $service = "" ]]; then
  echo "$usage"
  exit 1
fi

>&2 echo "Targeting org $org and space $space"
cf target -o $org -s $space 1>&2

# create user account service
cf create-service cloud-gov-service-account $role $service 1>&2

# create service key
cf create-service-key $service service-account-key 1>&2

# output service key to stdout in secrets.auto.tfvars format
creds=`cf service-key $service service-account-key | tail -n 7`
username=`echo $creds | jq '.credentials.username'`
password=`echo $creds | jq '.credentials.password'`

cat << EOF
# generated with $0 -s $space -u $service -r $role -o $org
# revoke with $(dirname $0)/destroy_service_account.sh -s $space -u $service -o $org

cf_user = $username
cf_password = $password
EOF