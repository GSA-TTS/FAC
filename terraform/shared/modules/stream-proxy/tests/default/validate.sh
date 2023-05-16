#!/bin/sh

set -ex

# A quick script to validate that the deployed config is what we expect

# If we exit for any reason before this is explicitly changed, then something
# went wrong.
result="FAILED"

# Tell Terraform what happened when we're done
finish() {
cat << EOF
{ 
  "status": "${result}"
}
EOF
}
trap finish EXIT

# Get our parameters from the JSON input into env vars
eval "$(jq -r '@sh "APPNAME=\(.APPNAME) CLIENTNAME=\(.CLIENTNAME) ORGNAME=\(.ORGNAME) SPACENAME=\(.SPACENAME)"')"

# Target the place where we think stuff is
cf t -o "$ORGNAME" -s "$SPACENAME" > /dev/null 2>&1

# Check that the egress app exists
cf app "${APPNAME}" > /dev/null 2>&1

# Check that the egress app has the appropriate env vars set
# TODO: Improve this to ensure the var content is as expected.
cf env "${APPNAME}" | grep -q STREAM_DOMAIN
cf env "${APPNAME}" | grep -q STREAM_PORT

# Check that a network policy with appropriate values exists 
# TODO: Improve this to use just one robust regexp (or use "cf curl" and "jq").
cf network-policies | grep "${CLIENTNAME}" | grep "${APPNAME}" | grep 8080 | grep "$ORGNAME" | grep -q "$SPACENAME" 

# Check that a user-provided service with the egress credentials exists
cf service "${APPNAME}"-creds > /dev/null 2>&1

# Bind the creds to the test app and ensure it knows about them
cf bind-service "${CLIENTNAME}" "${APPNAME}"-creds > /dev/null 2>&1
cf restart "${CLIENTNAME}" > /dev/null 2>&1

# Test that curl requests through the proxy are succeeding/failing as expected
output="$(cf ssh "${CLIENTNAME}" -c "/home/vcap/app/.profile")"
expected_output="PASSED"

[ "$output" = "$expected_output" ] && result="PASSED"
