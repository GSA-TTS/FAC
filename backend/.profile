#!/bin/bash

export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

export https_proxy="$(echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "https-proxy-creds" ".[][] | select(.name == \$service_name) | .credentials.uri")"
export smtp_proxy_domain="$(echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "smtp-proxy-creds" ".[][] | select(.name == \$service_name) | .credentials.domain")"
export smtp_proxy_port="$(echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "smtp-proxy-creds" ".[][] | select(.name == \$service_name) | .credentials.port")"

S3_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-public-s3" ".[][] | select(.name == \$service_name) | .credentials.endpoint")"
S3_FIPS_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-public-s3" ".[][] | select(.name == \$service_name) | .credentials.fips_endpoint")"
S3_PRIVATE_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-private-s3" ".[][] | select(.name == \$service_name) | .credentials.endpoint")"
S3_PRIVATE_FIPS_ENDPOINT_FOR_NO_PROXY="$(echo $VCAP_SERVICES | jq --raw-output --arg service_name "fac-private-s3" ".[][] | select(.name == \$service_name) | .credentials.fips_endpoint")"
export no_proxy="${S3_ENDPOINT_FOR_NO_PROXY},${S3_FIPS_ENDPOINT_FOR_NO_PROXY},${S3_PRIVATE_ENDPOINT_FOR_NO_PROXY},${S3_PRIVATE_FIPS_ENDPOINT_FOR_NO_PROXY},apps.internal"


# Grab the New Relic license key from the newrelic-creds user-provided service instance
export NEW_RELIC_LICENSE_KEY="$(echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "newrelic-creds" ".[][] | select(.name == \$service_name) | .credentials.NEW_RELIC_LICENSE_KEY")"

# Set the application name for New Relic telemetry.
export NEW_RELIC_APP_NAME="$(echo "$VCAP_APPLICATION" | jq -r .application_name)"

# Set the environment name for New Relic telemetry.
export NEW_RELIC_ENVIRONMENT="$(echo "$VCAP_APPLICATION" | jq -r .space_name)"

# Set Agent logging to stdout to be captured by CF Logs
export NEW_RELIC_LOG=stdout

# Logging level, (critical, error, warning, info and debug). Default to info
#export NEW_RELIC_LOG_LEVEL=

# https://docs.newrelic.com/docs/security/security-privacy/compliance/fedramp-compliant-endpoints/
export NEW_RELIC_HOST="gov-collector.newrelic.com"

export API_VERSIONS=v1_0_0-beta

create_views() {
    for version in ${API_VERSIONS//,/ }
    do
        python manage.py create_views --api_version ${version}
    done
}

# We only want to run migrate and collecstatic for the first app instance, not
# for additional app instances, so we gate all of this behind CF_INSTANCE_INDEX
# being 0.
[ "$CF_INSTANCE_INDEX" = 0 ] &&
echo 'Starting migrate' &&
python manage.py migrate &&
echo 'Finished migrate' &&
echo 'Starting view creation' &&
create_views() &&
echo 'Finished view creation' &&
echo 'Starting collectstatic' &&
python manage.py collectstatic --noinput &&
echo 'Finished collectstatic'
