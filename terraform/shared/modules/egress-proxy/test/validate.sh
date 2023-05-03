#!/bin/sh
set -e

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
eval "$(jq -r '@sh "APPNAME=\(.APPNAME) ORGNAME=\(.ORGNAME) SPACENAME=\(.SPACENAME)"')"

# Target the place where we think stuff is
cf t -o "$ORGNAME" -s "$SPACENAME" > /dev/null 2>&1

# Check that the egress app exists
cf app "${APPNAME}" > /dev/null 2>&1

# Check that the egress app has the appropriate env vars set
# TODO: Improve this to ensure the var content is as expected.
cf env "${APPNAME}" | grep -q PROXY_ALLOW
cf env "${APPNAME}" | grep -q PROXY_DENY
cf env "${APPNAME}" | grep -q PROXY_USERNAME
cf env "${APPNAME}" | grep -q PROXY_PASSWORD

# Check that a network policy with appropriate values exists 
# TODO: Improve this to use just one robust regexp (or use "cf curl" and "jq").
cf network-policies | grep test | grep "${APPNAME}" | grep 61443 | grep "$ORGNAME" | grep -q "$SPACENAME" 

# Check that a user-provided service with the egress credentials exists
cf service "${APPNAME}"-creds > /dev/null 2>&1

# Bind the creds to the test app and ensure it knows about them
cf bind-service test "${APPNAME}"-creds > /dev/null 2>&1
cf restart test > /dev/null 2>&1

# Test that curl requests through the proxy are succeeding/failing as expected
output="$(cf ssh test -t -c "/home/vcap/app/.profile")"
expected_output="www.yahoo.com: 403
www.google.com: 200
mail.google.com: 403"

[ "$output" = "$expected_output" ] && result="PASSED"

