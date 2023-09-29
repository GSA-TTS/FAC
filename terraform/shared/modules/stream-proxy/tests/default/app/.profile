#!/bin/bash

set -e

# Use platform-provided certificate bundle
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Set the https_proxy env var based on egress-creds
function vcap_get_service () {
  local path name
  name="$1"
  path="$2"
  echo $VCAP_SERVICES | jq --raw-output --arg service_name "$name" ".[][] | select(.name == \$service_name) | $path"
}
export proxydomain=$(vcap_get_service stream-proxy-creds .credentials.domain)
export proxyport=$(vcap_get_service stream-proxy-creds .credentials.port)

# If all is working correctly, this should be same as the content of `public/index.html`
[ "$(curl -s http://${proxydomain}:${proxyport})" = "$(cat /home/vcap/app/public/index.html)" ] && echo "PASSED" || echo "FAILED"