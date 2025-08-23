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
else
  echo "WE ARE ON CGOV"
  export AWS_ACCESS_KEY_ID=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.access_key_id')
  export AWS_SECRET_ACCESS_KEY=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.secret_access_key')
  export BUCKET=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.bucket')
  export REGION=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.region')
  export AWS_ENDPOINT=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.endpoint')
  export AWS_FIPS_ENDPOINT=$(echo $VCAP_SERVICES |  jq -rc '.s3[] | select(.name | contains("fac-private-s3")) | .credentials.fips_endpoint')
fi

####################################################
# FUNCTIONS
# These keep things further down more readable.
install_aws_cli() {
  rm -rf /tmp/aws-cli
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip -u awscliv2.zip
  sudo ./aws/install --install-dir /tmp/aws-cli --update
  rm -f awscliv2.zip
  rm -rf aws
}

cleanup_aws() {
  rm -rf /tmp/aws-cli
}

download_full_csv() {
  local endpoint=$1

  echo downloading csv for ${endpoint}
  psql \
    -d postgres \
    -h db \
    -U postgres \
    -t -A \
    -c "\COPY (SELECT * FROM ${API_VERSION}.${endpoint}) TO '${ROOT}/${endpoint}.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');"
}

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
  psql \
    -d postgres \
    -h db \
    -U postgres \
    -t -A \
    -c "${query}"
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
    ${AWSCLI} s3 cp "${ROOT}/${endpoint}.csv" "s3://${BUCKET}/${path_in_s3}"
  fi
}

####################################################
# Install the AWS CLI
install_aws_cli

####################################################
# Create a destination directory (in the container/cloud env.)
mkdir -p "${ROOT}"


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
# In a loop, download, upload, and delete the full CSVs.
# public-data/gsa/full/{table_name}.csv
for endpoint in ${endpoints[@]}; do
  # Download the endpoint from Postgres as a CSV.
  download_full_csv ${endpoint}
  copy_to_s3 ${endpoint} "public-data/gsa/full/${endpoint}.csv"
  rm -f "${ROOT}/${endpoint}.csv"
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
