#!/bin/bash

set -e

# Configure vars for https-proxy
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Set the https_proxy env var based on egress-creds
function vcap_get_service () {
  local path name
  name="$1"
  path="$2"
  echo $VCAP_SERVICES | jq --raw-output --arg service_name "$name" ".[][] | select(.name == \$service_name) | $path"
}
export https_proxy=$(vcap_get_service egress-creds .credentials.uri)

# Should fail via deny-all
echo www.yahoo.com: $(curl -s -o /dev/null -I -L  -w "%{http_connect}" https://www.yahoo.com)

# Should succeed via allow
echo www.google.com: $(curl -s -o /dev/null -I -L -w "%{http_connect}" https://www.google.com)

# Should fail via deny
echo mail.google.com: $(curl -s -o /dev/null -I -L -w "%{http_connect}" https://mail.google.com)

