source tools/util_startup.sh

function setup_cgov_env {
    set -e

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
    export NEW_RELIC_APP_NAME="$(echo "$VCAP_APPLICATION" | jq -r .application_name)-$(echo "$VCAP_APPLICATION" | jq -r .space_name)"

    # Set the environment name for New Relic telemetry.
    export NEW_RELIC_ENVIRONMENT="$(echo "$VCAP_APPLICATION" | jq -r .space_name)"

    # Set Agent logging to stdout to be captured by CF Logs
    export NEW_RELIC_LOG=stdout

    # Logging level, (critical, error, warning, info and debug). Default to info
    export NEW_RELIC_LOG_LEVEL=info

    # Used for configuring the logging details sent to new relic
    export NEW_RELIC_CONFIG_FILE=newrelic.ini

    # https://docs.newrelic.com/docs/security/security-privacy/compliance/fedramp-compliant-endpoints/
    export NEW_RELIC_HOST="gov-collector.newrelic.com"
    # https://docs.newrelic.com/docs/apm/agents/python-agent/configuration/python-agent-configuration/#proxy
    export NEW_RELIC_PROXY_HOST="$https_proxy"
    return 0
}
