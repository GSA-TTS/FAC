source tools/util_startup.sh

# Aliases need to be outside of function scope

function setup_cgov_env {
    startup_log "CGOV_ENV" "We are in a cloud.gov envirnoment."

    # https://stackoverflow.com/questions/48712545/break-jq-query-string-into-lines
    # jq is fine with line breaks in strings. Just don't escape them.
    # Makes long queries more readable. Maybe.
    export AWS_PRIVATE_BUCKET_NAME=$(echo $VCAP_SERVICES \
        | jq '.s3 
            | map(select(.instance_name 
                         | contains("fac-private-s3"))) 
            | .[] .credentials.bucket')
    export AWS_PUBLIC_BUCKET_NAME=$(echo $VCAP_SERVICES \
        | jq '.s3 
            | map(select(.instance_name 
                         | contains("fac-public-s3"))) 
            | .[] .credentials.bucket')

    get_aws_s3 "fac-private-s3" "access_key_id"
    export AWS_PRIVATE_ACCESS_KEY_ID=$_GET_AWS_RESULT
    get_aws_s3 "fac-private-s3" "secret_access_key"
    export AWS_PRIVATE_SECRET_ACCESS_KEY=$_GET_AWS_RESULT
    get_aws_s3 "fac-private-s3" "endpoint"
    export AWS_S3_PRIVATE_ENDPOINT=$_GET_AWS_RESULT

    get_aws_s3 "fac-public-s3" "access_key_id"
    export AWS_PUBLIC_ACCESS_KEY_ID=$_GET_AWS_RESULT
    get_aws_s3 "fac-public-s3" "secret_access_key"
    export AWS_PUBLIC_SECRET_ACCESS_KEY=$_GET_AWS_RESULT
    get_aws_s3 "fac-public-s3" "endpoint"
    export AWS_S3_PUBLIC_ENDPOINT=$_GET_AWS_RESULT


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

    # For database work
    export FAC_DB_URI="$(echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "fac-db" ".[][] | select(.name == \$service_name) | .credentials.uri")"
    export FAC_SNAPSHOT_URI="$(echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "fac-snapshot-db" ".[][] | select(.name == \$service_name) | .credentials.uri")"
    # https://stackoverflow.com/questions/37072245/check-return-status-of-psql-command-in-unix-shell-scripting
    export PSQL_EXE='/home/vcap/deps/0/apt/usr/lib/postgresql/*/bin/psql --single-transaction -v ON_ERROR_STOP=on'
    export PSQL_EXE_NO_TXN='/home/vcap/deps/0/apt/usr/lib/postgresql/*/bin/psql -v ON_ERROR_STOP=on'

    export SLING_EXE='/home/vcap/app/sling'

    return 0
}
