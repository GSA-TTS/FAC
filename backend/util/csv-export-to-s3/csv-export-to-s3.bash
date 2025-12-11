#!/bin/bash

# 1. A copy of each table as a single CSV
# 2. A copy of each table, broken out by year (calendar/audit year)
# 3. A copy of each table, broken out by federal fiscal year

# https://stackoverflow.com/questions/1120109/how-to-export-table-as-csv-with-headings-on-postgresql
# https://stackoverflow.com/questions/1517635/save-pl-pgsql-output-from-postgresql-to-a-csv-file

####################################################
# This should be a schema in the API.
API_VERSION="api_v1_1_0"

endpoints=(
  "additional_eins"
  "additional_ueis"
  "corrective_action_plans"
  "federal_awards"
  "findings_text"
  "findings"
  "general"
  "notes_to_sefa"
  "passthrough"
  "resubmission"
  "secondary_auditors"
) 

####################################################
# Get the bucket variables for use with AWS CLI
# These come out of VCAP_SERVICES if we are in the cloud.
# If we are local, we need to set up our env vars differently.
export AWSCLI="/tmp/aws-cli/v2/current/bin/aws"
# Where we'll store the temporary CSVs
export ROOT="/tmp/csv"

if [[ "$ENV" = "LOCAL" ]]; then
  echo "WE ARE LOCAL"
  export AWS_ACCESS_KEY_ID="minioadmin"
  export AWS_SECRET_ACCESS_KEY="minioadmin"
  export BUCKET="gsa-fac-private-s3"
  export REGION="usa-east-1"
  export AWS_ENDPOINT="http://minio:9000"
  export AWSCLI="${AWSCLI} --endpoint-url ${AWS_ENDPOINT}"
  export DAS_DB_HOST="db"
  export DAS_DB_USER="postgres"
  export DAS_DB_NAME="postgres"
  export DAS_DB_PASSWORD=""
  export PGPASSWORD="${DAS_DB_PASSWORD}"

else
  echo "WE ARE ON CGOV"
  export AWS_ACCESS_KEY_ID=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.access_key_id')
  export AWS_SECRET_ACCESS_KEY=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.secret_access_key')
  export BUCKET=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.bucket')
  export AWS_REGION=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.region')
  export AWS_DEFAULT_REGION=${AWS_REGION}
  
  export DAS_DB_HOST=$(echo $VCAP_SERVICES |  jq -rc '."aws-rds"[] | select(.name | contains("fac-db")) | .credentials.host')
  export DAS_DB_USER=$(echo $VCAP_SERVICES |  jq -rc '."aws-rds"[] | select(.name | contains("fac-db")) | .credentials.username')
  export DAS_DB_NAME=$(echo $VCAP_SERVICES |  jq -rc '."aws-rds"[] | select(.name | contains("fac-db")) | .credentials.db_name')
  export DAS_DB_PASSWORD=$(echo $VCAP_SERVICES |  jq -rc '."aws-rds"[] | select(.name | contains("fac-db")) | .credentials.password')
  export PGPASSWORD="${DAS_DB_PASSWORD}"

  alias psql='/home/vcap/deps/0/apt/usr/lib/postgresql/*/bin/psql'
  export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
fi

####################################################
# FUNCTIONS
# These keep things further down more readable.
install_aws_cli() {
  rm -rf /tmp/aws-cli
  cd /tmp
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip -u -q awscliv2.zip
  /tmp/aws/install -i /tmp/aws-cli -b /tmp/sym --update
  if [ $? -ne 0 ]; then
    echo FAILED TO INSTALL AWS
    exit -1
  fi
  rm -f awscliv2.zip
  rm -rf aws
}

cleanup_aws() {
  rm -rf /tmp/aws-cli
}

SAVED_PROXY=""
unset_proxy() {
  SAVED_PROXY="${https_proxy}"
  unset https_proxy
  # echo "PROXY AFTER UNSET: ${https_proxy}"
}

restore_proxy() {
  set https_proxy "${SAVED_PROXY}"
  # echo "PROXY AFTER RESTORE: ${https_proxy}"
}

download_full_csv() {
  local endpoint=$1

  echo downloading csv for ${endpoint}
  env PGOPTIONS='-c client_min_messages=WARNING' psql \
    -d "${DAS_DB_NAME}" \
    -h "${DAS_DB_HOST}" \
    -U "${DAS_DB_USER}" \
    -t -A \
    -c "\COPY (SELECT * FROM ${API_VERSION}.${endpoint}) TO '${ROOT}/${endpoint}.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');" \
    |& grep -v "has_tribal"

  if [ $? -ne 0 ]; then
    echo "PSQL FAILED IN FULL TABLE DOWNLOAD"
    exit -1
  fi
}

# NEAT TRICK
# Note the pipe-ampersand (|&) below. It says
# "keep all the lines except for the ones where this matches"
# https://stackoverflow.com/a/16321435
# We do this to quiet some INFO messages from psql.
download_date_range_csv () {
  local endpoint=$1
  local start_date=$2
  local end_date=$3

  local query="\COPY "
  query+="( SELECT * FROM ${API_VERSION}.${endpoint} "
  query+="  WHERE report_id in ( "
  query+="    SELECT report_id from ${API_VERSION}.general "
  query+="    WHERE fac_accepted_date >= '${start_date}' "
  query+="    AND fac_accepted_date <= '${end_date}' "
  query+=")) "
  query+="TO '${ROOT}/${endpoint}.csv' "
  query+="WITH (FORMAT CSV, HEADER, DELIMITER ',');"

  echo "${query}"

  echo downloading audit year csv for ${endpoint}
  # TODO: Consider adding a quiet flag or routing output to /dev/null to suppress
  # warnings like "INFO:  api_v1_1_0 has_tribal <NULL> f". We will see a lot of them
  # because we're using the API in an un-authenticated way (which is intentional!).
  env PGOPTIONS='-c client_min_messages=WARNING' psql \
    -d "${DAS_DB_NAME}" \
    -h "${DAS_DB_HOST}" \
    -U "${DAS_DB_USER}" \
    -t -A \
    -c "${query}" |& \
    grep -v "has_tribal"

  if [ $? -ne 0 ]; then
    echo "PSQL FAILED IN DATE RANGE DOWNLOAD"
    exit -1
  fi
}

copy_to_s3() {
  local endpoint=$1
  local path_in_s3=$2

  if [[ "$ENV" = "LOCAL" ]]; then
    # Use the low-level API to avoid multipart.
    # (Minio does not like the multipart.)
    cmd=$(echo ${AWSCLI} s3api put-object --bucket ${BUCKET} --key "${path_in_s3}" --body "${ROOT}/${endpoint}.csv")
    echo $cmd
    eval $cmd
  else
    cmd=$(echo ${AWSCLI} s3 cp "${ROOT}/${endpoint}.csv" "s3://${BUCKET}/${path_in_s3}")
    # cmd=$(echo ${AWSCLI} s3api put-object --bucket ${BUCKET} --key "${path_in_s3}" --body "${ROOT}/${endpoint}.csv")
    echo $cmd
    eval $cmd

    if [ $? -ne 0 ]; then
      echo "S3 COPY FAILED FOR ${path_in_s3}"
    fi
  fi
}

####################################################
# Install the AWS CLI
install_aws_cli

####################################################
# Unset the proxy (so we can upload to S3)
unset_proxy

####################################################
# Create a destination directory (in the container/cloud env.)
mkdir -p "${ROOT}"


####################################################
# In a loop, download, upload, and delete the full CSVs.
# public-data/gsa/full/{table_name}.csv
for endpoint in ${endpoints[@]}; do
  # Download the endpoint from Postgres as a CSV.
  download_full_csv ${endpoint}
  copy_to_s3 ${endpoint} "public-data/gsa/full/${endpoint}.csv"
  rm -f "${ROOT}/${endpoint}.csv"
done

####################################################
# federal fiscal year year CSVs.
# public-data/gsa/federal-fiscal-year/{audit_year}-ffy-{table_name}.csv
for endpoint in ${endpoints[@]}; do
  for year in $(seq 2015 `date -d "+2 year" +'%Y'`); do
    # Download the endpoint from Postgres as a CSV.
    start_date="${year}-10-01"
    next_year=$(($year+1))
    end_date="${next_year}-09-30"
    download_date_range_csv ${endpoint} ${start_date} ${end_date}
    copy_to_s3 ${endpoint} "public-data/gsa/federal-fiscal-year/${year}-ffy-${endpoint}.csv"
    rm -f "${ROOT}/${endpoint}.csv"
  done
done

####################################################
# audit year CSVs.
# public-data/gsa/audit-year/{audit_year}-ay-{table_name}.csv
for endpoint in ${endpoints[@]}; do
  for year in $(seq 2015 `date -d "+2 year" +'%Y'`); do
    # Download the endpoint from Postgres as a CSV.
    start_date="${year}-01-01"
    end_date="${year}-12-31"
    download_date_range_csv ${endpoint} ${start_date} ${end_date}
    copy_to_s3 ${endpoint} "public-data/gsa/audit-year/${year}-ay-${endpoint}.csv"
    rm -f "${ROOT}/${endpoint}.csv"
  done
done


####################################################
# Don't leave things lying around when you're done.
cleanup_aws
