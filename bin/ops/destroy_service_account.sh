#!/usr/bin/env bash

org="gsa-tts-oros-fac"

usage="
$0: Destroy a Service User Account in a given space

Usage:
  $0 -h
  $0 -s <SPACE NAME> -u <USER NAME> [-o <ORG NAME>]

Options:
-h: show help and exit
-s <SPACE NAME>: configure the space to act on. Required
-u <USER NAME>: configure the service user name to destroy. Required
-o <ORG NAME>: configure the organization to act on. Default: $org
"

set -e

space=""
service=""

while getopts ":hs:u:o:" opt; do
  case "$opt" in
    s)
      space=${OPTARG}
      ;;
    u)
      service=${OPTARG}
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

cf target -o $org -s $space

# destroy service key
cf delete-service-key $service ${service}-key -f

# destroy service
cf delete-service $service -f