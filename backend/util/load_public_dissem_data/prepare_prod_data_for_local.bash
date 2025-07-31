#!/bin/bash

############################################################
# for data download, you will need to be logged into
# the `cf` API. And, you'll need to be a FAC developer.
############################################################

# Do not exit on error.
set -e

# When called from the command line, pass a target
# destination directory for the downloaded files.
# Preferably outside the tree.

############################################################
# process command-line arguments
############################################################
# Fetch the command line arguments in an array.
# https://stackoverflow.com/a/2740967
args=("$@")
# args[0] is the first argument, and not the name of the script.

DESTINATION=${args[0]}
if [[ -z "${DESTINATION}" ]]; then
  echo "Please pass a destination folder as the first argument."
  echo "Exiting."
  exit
fi

if [ -d "$DESTINATION" ]; then
  echo "Found destination '$DESTINATION'."
else
  echo "Directory '$DESTINATION' does not exist."
  echo "Exiting."
  exit
fi

# This can be changed via the menu.
# Better, when a new backup is targeted, to 
# make the change and commit back to the repo.
DESIRED_BACKUP="07-27-12"

############################################################
# environment variables
############################################################
DATABASE=postgres
USERNAME=postgres
HOST=localhost
PORT=5432
DATE=$(date '+%Y%m%d')

# This gives us TARGET_TABLES
source "tables.bash"

# read -p "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

############################################################
# select_target_backup_for_download
############################################################
select_target_backup_for_download () {
  echo "select_target_backup_for_download"
  # https://stackoverflow.com/a/18546416
  read -p "Target backup (MM-DD-HH): " TARGET
  DESIRED_BACKUP=$TARGET
  echo "Targeting ${TARGET}"
}

############################################################
# download_dumpfiles
############################################################
download_dumpfiles () {
  echo "download_dumpfiles"
  # Source in the tables we want to download.

  # Target the production environment
  cf target -s production
  # We want the backups bucket
  BACKUP_SERVICE_INSTANCE_NAME=backups

  # Create a key for this operation
  # If two people run this at the same time, this could collide.
  # This is not likely an issue.
  BACKUP_KEY_NAME=data_prep_service_key
  cf create-service-key "${BACKUP_SERVICE_INSTANCE_NAME}" "${BACKUP_KEY_NAME}" || true
  BACKUP_S3_CREDENTIALS=$(cf service-key "${BACKUP_SERVICE_INSTANCE_NAME}" "${BACKUP_KEY_NAME}" | tail -n +2) || true

  # Extract data from the JSON that comes back.
  BACKUP_AWS_ACCESS_KEY_ID=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.access_key_id')
  BACKUP_AWS_SECRET_ACCESS_KEY=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.secret_access_key')
  BACKUP_BUCKET_NAME=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.bucket')
  BACKUP_URI=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.uri')
  BACKUP_AWS_DEFAULT_REGION=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.region')

  # Set variables in this script for use with the AWS CLI.
  AWS_ACCESS_KEY_ID=$BACKUP_AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY=$BACKUP_AWS_SECRET_ACCESS_KEY
  AWS_DEFAULT_REGION=$BACKUP_AWS_DEFAULT_REGION
  BUCKET_NAME=${BACKUP_BUCKET_NAME}

  # Download the tables.
  for dump in ${TARGET_TABLES[@]}; 
  do
    SRC="s3://${BUCKET_NAME}/backups/scheduled/${DESIRED_BACKUP}/${dump}"
    DST="${DESTINATION}/${dump}"
    echo "Downloading ${SRC}"
    aws s3 cp "${SRC}" "${DST}"
  done
 
  cf delete-service-key -f "${BACKUP_SERVICE_INSTANCE_NAME}" "${BACKUP_KEY_NAME}" || true
}

############################################################
# load_raw_prod_dump
############################################################
load_raw_prod_dump () {
  echo "load_raw_prod_dump"
 
  for dump in ${TARGET_TABLES[@]};
  do
    DUMPFILE=$(readlink -m "${DESTINATION}/${dump}")
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}

    SQL="BEGIN; TRUNCATE ${TABLENAME} CASCADE; COMMIT;"
    echo "SQL: ${SQL}"

    # Truncate the table.
    psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
		-w \
    -v ON_ERROR_STOP=1 \
    -c "${SQL}"

    echo "Locally loading ${DUMPFILE}"

    # Custom dumpfiles have to be restored with
    # pg_restore
    cat ${DUMPFILE} | \
    pg_restore \
      --data-only \
      -d ${DATABASE} \
		  -U ${USERNAME} \
		  -p ${PORT} \
		  -h ${HOST}
  done
}

############################################################
# remove_suppressed_tribal_audits
############################################################
# https://dba.stackexchange.com/questions/334191/cascade-delete-per-statement
remove_suppressed_tribal_audits () {
  echo "remove_suppressed_tribal_audits"
  psql \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -w < remove_tribal_audits.sql
}

############################################################
# export_sanitized_dump_for_reuse
############################################################
export_sanitized_dump_for_reuse () {
  echo "export_sanitized_dump_for_reuse"

  rm -f dump_filters.pg
  for dump in ${TARGET_TABLES[@]};
  do
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}
    echo "include table ${TABLENAME}" >> dump_filters.pg
  done

  pg_dump -F c \
    --no-acl \
    --no-owner \
    --data-only \
    --filter dump_filters.pg \
    -f sanitized-${DATE}.dump \
    postgresql://${USERNAME}@${HOST}:${PORT}/${DATABASE}
}

declare -a PRE_TRUNCATE_TABLE_COUNTS
############################################################
# truncate_all_local_tables
############################################################
truncate_all_local_tables () {
  echo "truncate_all_local_tables"

  for dump in ${TARGET_TABLES[@]};
  do
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}
  PRE_TRUNCATE_TABLE_COUNTS+=($(psql \
    -t \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -w \
    -c "SELECT COUNT(*) FROM ${TABLENAME}"))

  psql \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -w \
    -c "TRUNCATE ${TABLENAME} CASCADE"
  
  done
}


declare -a TEST_LOAD_TABLE_COUNTS
############################################################
# test_sanitized_production_dump
############################################################
test_sanitized_production_dump () {
  echo "test_sanitized_production_dump"
  pg_restore \
      --data-only \
      -d ${DATABASE} \
		  -U ${USERNAME} \
		  -p ${PORT} \
		  -h ${HOST} < sanitized-${DATE}.dump

  for dump in ${TARGET_TABLES[@]};
  do
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}
  TEST_LOAD_TABLE_COUNTS+=($(psql \
    -t \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -w \
    -c "SELECT COUNT(*) FROM ${TABLENAME}"))
  done

  all_same=1
  for i in "${!TEST_LOAD_TABLE_COUNTS[@]}"; do
      if [ "${PRE_TRUNCATE_TABLE_COUNTS[i]}" != "${TEST_LOAD_TABLE_COUNTS[i]}" ]; then
        printf '${%s}=%s %s\n' "$i" "${PRE_TRUNCATE_TABLE_COUNTS[i]}" "${TEST_LOAD_TABLE_COUNTS[i]}"
        all_same=0
      fi
  done

  if [ "${all_same}" == "1" ]; then
    echo "All table counts the same."
  else
    echo "Table counts differed."
  fi
}

PS3='Please enter your choice: '
options=(\
  "Select target backup date for download" \
  "Download dumpfiles" \
  "Locally load raw production dump" \
  "Remove all suppressed tribal audits" \
  "Export sanitized production dump for reuse" \
  "Truncate all local tables" \
  "Reload/test sanitized production dump" \
  "Run everything straight through" \
  "Quit"
)

select opt in "${options[@]}"
do
    case $opt in
      "Select target backup date for download")
        select_target_backup_for_download
        ;;
      "Download dumpfiles")
        download_dumpfiles
        ;;
      "Locally load raw production dump")
        load_raw_prod_dump
        ;;
      "Remove all suppressed tribal audits")
        remove_suppressed_tribal_audits
        ;;
      "Export sanitized production dump for reuse")
        export_sanitized_dump_for_reuse
        ;;
      "Truncate all local tables")
        truncate_all_local_tables
        ;;
      "Reload/test sanitized production dump")
        test_sanitized_production_dump
        ;;
      "Run everything straight through")
        download_dumpfiles
        load_raw_prod_dump
        remove_suppressed_tribal_audits
        export_sanitized_dump_for_reuse
        truncate_all_local_tables
        test_sanitized_production_dump
        ;;
      "Quit")
        break
        ;;
      *) echo "invalid option";;
    esac
done
