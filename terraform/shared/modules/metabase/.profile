#!/bin/bash
# export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
# export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
# export https_proxy="$(echo "$VCAP_SERVICES" | jq --raw-output --arg service_name "https-proxy-creds" ".[][] | select(.name == \$service_name) | .credentials.https_uri")"

# export MB_DB_DBNAME=$(echo $VCAP_SERVICES | jq -r '.["aws-rds"][] | select(.name=="fac-db") | .credentials.name')
# export MB_DB_HOST=$(echo $VCAP_SERVICES | jq -r '.["aws-rds"][] | select(.name=="fac-db") | .credentials.host')
# export MB_DB_PORT=$(echo $VCAP_SERVICES | jq -r '.["aws-rds"][] | select(.name=="fac-db") | .credentials.port')
# export MB_DB_USER=$(echo $VCAP_SERVICES | jq -r '.["aws-rds"][] | select(.name=="fac-db") | .credentials.username')
# export MB_DB_PASS=$(echo $VCAP_SERVICES | jq -r '.["aws-rds"][] | select(.name=="fac-db") | .credentials.password')


# Get database 1 values
# echo $VCAP_SERVICES | grep -o '"db_name":\s*"[^"]*' | sed 's/"db_name":\s*//' | cut -d '"' -f2 | head -1
# echo $VCAP_SERVICES | grep -o '"host":\s*"[^"]*' | sed 's/"host":\s*//' | cut -d '"' -f2 | head -1
# echo $VCAP_SERVICES | grep -o '"port":\s*"[^"]*' | sed 's/"port":\s*//' | cut -d '"' -f2 | head -1
# echo $VCAP_SERVICES | grep -o '"username":\s*"[^"]*' | sed 's/"username":\s*//' | cut -d '"' -f2 | head -1
# echo $VCAP_SERVICES | grep -o '"password":\s*"[^"]*' | sed 's/"password":\s*//' | cut -d '"' -f2 | head -1


export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Necessary for the terraform, but not necessarily used if we want to do it another way
# MB_DB_CONNECTION_URI=$(echo "$VCAP_SERVICES" | grep -o '"uri":\s*"[^"]*' | sed 's/"uri":\s*//' | cut -d '"' -f2 | tail -1)
# export MB_DB_CONNECTION_URI

# export https_proxy=$(echo $json | grep -oP '"https_uri":\s*"[^"]*' | sed 's/"https_uri":\s*//' | cut -d '"' -f2 | head -1)

# Get database 2 values
export MB_DB_TYPE='postgres'
MB_DB_DBNAME=$(echo "$VCAP_SERVICES" | grep -o '"db_name":\s*"[^"]*' | sed 's/"db_name":\s*//' | cut -d '"' -f2 | tail -1)
MB_DB_HOST=$(echo "$VCAP_SERVICES" | grep -o '"host":\s*"[^"]*' | sed 's/"host":\s*//' | cut -d '"' -f2 | tail -1)
MB_DB_PORT=$(echo "$VCAP_SERVICES" | grep -o '"port":\s*"[^"]*' | sed 's/"port":\s*//' | cut -d '"' -f2 | tail -1)
MB_DB_USER=$(echo "$VCAP_SERVICES" | grep -o '"username":\s*"[^"]*' | sed 's/"username":\s*//' | cut -d '"' -f2 | tail -1)
MB_DB_PASS=$(echo "$VCAP_SERVICES" | grep -o '"password":\s*"[^"]*' | sed 's/"password":\s*//' | cut -d '"' -f2 | tail -1)
export MB_DB_DBNAME; export MB_DB_HOST; export MB_DB_PORT; export MB_DB_USER; export MB_DB_PASS;
