#!/bin/bash

############################################################
# for data download, you will need to be logged into
# the `cf` API. And, you'll need to be a FAC developer.
############################################################

# Do not exit on error.
set +e

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

# DESTINATION=${args[0]}
DESTINATION="data/"
EMAIL=${args[0]}

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

if [[ -z "${EMAIL}" ]]; then
  echo "Please pass a staff user email as the second arg."
  echo "Exiting."
  exit
fi

# https://stackoverflow.com/a/6569837
cmd=jq
[[ $(type -P "$cmd") ]] && echo "$cmd is in PATH. Good."  || { echo "$cmd is NOT in PATH" 1>&2; exit 1; }

cmd=cf
[[ $(type -P "$cmd") ]] && echo "$cmd is in PATH. Good."  || { echo "$cmd is NOT in PATH" 1>&2; exit 1; }

# Make sure we are in `production` via `cf`.
cf t | grep -q 'production'

if [ $? -ne 0 ];
then
  echo "You are not in production."
  read -p "Switch to production via cf? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || false
  # The above prompt exits if you say no.
  if [[ $confirm =~ 'y' ]];
  then
    echo "Switching to production."
    cf login -a api.fr.cloud.gov --sso
    cf t -s production
  else
    echo "Did not switch."
  fi
else
  echo "You are in 'production' via 'cf'. Beware of dragons."
fi

echo -e "\n"

# This can be changed via the menu.
# Better, when a new backup is targeted, to 
# make the change and commit back to the repo.
DESIRED_BACKUP="07-27-12"

############################################################
# environment variables
############################################################
DATABASE=postgres
USERNAME=postgres
HOST=db
PORT=5432
DATE=$(date '+%Y%m%d')

# This gives us TARGET_TABLES
source "tables.source"

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
  # You need to do this yourself.
  # cf t -s production
  # Be careful when connecting to prod.
  
  # We want the backups bucket
  BACKUP_SERVICE_INSTANCE_NAME=backups

  # Create a key for this operation
  # If two people run this at the same time, this could collide.
  # This is not likely an issue.

  CLEANED_EMAIL=$(echo "${EMAIL}" | tr -cd '[:alnum:]_-')
  BACKUP_KEY_NAME="data_prep_service_key-${CLEANED_EMAIL}"

  cf service-key "${BACKUP_SERVICE_INSTANCE_NAME}" "${BACKUP_KEY_NAME}" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Service key does not exist. Creating."
    cf create-service-key "${BACKUP_SERVICE_INSTANCE_NAME}" "${BACKUP_KEY_NAME}" || true
  fi

  BACKUP_S3_CREDENTIALS=$(cf service-key "${BACKUP_SERVICE_INSTANCE_NAME}" "${BACKUP_KEY_NAME}" | tail -n +2) || true
  # Extract data from the JSON that comes back.
  BACKUP_AWS_ACCESS_KEY_ID=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.access_key_id')
  BACKUP_AWS_SECRET_ACCESS_KEY=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.secret_access_key')
  BACKUP_BUCKET_NAME=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.bucket')
  BACKUP_URI=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.uri')
  BACKUP_AWS_DEFAULT_REGION=$(echo "${BACKUP_S3_CREDENTIALS}" | jq -r '.credentials.region')

  # Set variables in this script for use with the AWS CLI.
  export AWS_ACCESS_KEY_ID=$BACKUP_AWS_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY=$BACKUP_AWS_SECRET_ACCESS_KEY
  export AWS_DEFAULT_REGION=$BACKUP_AWS_DEFAULT_REGION
  export BUCKET_NAME=${BACKUP_BUCKET_NAME}

  # Download the tables.
  for dump in ${TARGET_TABLES[@]}; 
  do
    SRC="s3://${BUCKET_NAME}/backups/scheduled/${DESIRED_BACKUP}/${dump}"
    DST="${DESTINATION}/${dump}"
    echo -e "Downloading...\n\t${SRC}\n\t->\n\t${DST}"
    # Remove any lingering files from previous runs if they exist.
    rm -f "${DST}"
    # Download a fresh dumpfile
    aws s3 cp "${SRC}" "${DST}"
    if [ $? -ne 0 ]; then 
      echo "DOWNLOAD FAILED."
      echo "Exiting."
      exit
    fi
  done
 
  cf delete-service-key -f "${BACKUP_SERVICE_INSTANCE_NAME}" "${BACKUP_KEY_NAME}" || true

  # We automatically dump back to preview, just-in-case.
  cf t -s preview
}

############################################################
# load_raw_prod_dump
############################################################
load_raw_prod_dump () {
  echo "load_raw_prod_dump"
 
  for ndx in ${!TARGET_TABLES[@]};
  do
    dump=${TARGET_TABLES[$ndx]}
    DUMPFILE="${DESTINATION}/${dump}"
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}

    SQL="BEGIN; TRUNCATE ${TABLENAME} CASCADE; COMMIT;"
    echo "SQL: ${SQL}"

    # Truncate the table.
    PGOPTIONS='--client-min-messages=warning' psql \
    -q \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
    -v ON_ERROR_STOP=1 \
		-w \
    -c "${SQL}"

    echo "Locally loading ${DUMPFILE}"

    # Custom dumpfiles have to be restored with
    # pg_restore. What is absolutely unclear here is why we need to
    # filter out the "transaction_timeout". This should be a Pg v17 flag,
    # and there is no way it should be in our v15 pipeline. But. Here we are.
    # So, we have to dump the file through pg_restore (to unpack the custom format)
    # and then pipe the result through `psql` to load it into the DB.

    # For each file, dump it to a temp SQL file.
    TEMPFILE="_tmp.sql"
    echo -e "\t...restoring to tempfile"
    rm -f "${TEMPFILE}"
    pg_restore --data-only -f "${TEMPFILE}" "${DUMPFILE}"

    # Now, filter out 'transaction_timeout'
    TEMP2="_tmp2.sql"
    cat "$TEMPFILE" | grep -v 'transaction_timeout' > "${TEMP2}"
    mv "${TEMP2}" "${TEMPFILE}"

    # Then load that file
    echo -e "\t...loading via psql"
    psql \
      -q \
      -d ${DATABASE} \
      -U ${USERNAME} \
      -p ${PORT} \
      -h ${HOST} \
      -v ON_ERROR_STOP=1 \
      -w < "${TEMPFILE}"
    
    if [ $? -ne 0 ]; then
      echo "RESTORE FAILED: ${TABLENAME}"
      echo "Exiting."
      exit
    fi

    # Then remove the tmpfile
    rm -f "${TEMPFILE}"
    
  done
}

############################################################
# remove_suppressed_tribal_audits
############################################################
# https://dba.stackexchange.com/questions/334191/cascade-delete-per-statement
remove_suppressed_tribal_audits () {
  echo "remove_suppressed_tribal_audits"
  psql \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w < remove_tribal_audits.sql

  if [ $? -ne 0 ]; then
    echo "Removal of Tribal audits failed."
    echo "Exiting."
    exit
  fi
}

############################################################
# export_sanitized_dump_for_reuse
############################################################
export_sanitized_dump_for_reuse () {
  echo "export_sanitized_dump_for_reuse"

  table_flags=""
  for ndx in ${!TARGET_TABLES[@]};
  do
    dump=${TARGET_TABLES[$ndx]}
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}
    # echo "include table ${TABLENAME}" >> dump_filters.pg
    table_flags="${table_flags} -t ${TABLENAME}"
  done

  # Make sure this isn't stale when we're done/if we fail.
  rm -f "sanitized-${DATE}.dump"

  cmd="pg_dump -d ${DATABASE} -h ${HOST} -p ${PORT} -U ${USERNAME} -w -F c --no-acl --no-owner --data-only ${table_flags} "
  cmd="${cmd} -f ${DESTINATION}/sanitized-${DATE}.dump"
  echo "${cmd}"
  eval "${cmd}"

  if [ $? -ne 0 ]; then
    echo "Dump failed."
    echo "Exiting."
    exit
  fi
}

############################################################
# truncate_all_local_tables
############################################################
declare -a PRE_TRUNCATE_TABLE_COUNTS
truncate_all_local_tables () {
  echo "truncate_all_local_tables"
  # Combining two arrays into one.
  # (This may not be strictly necessary.)
  FOR_TRUNCATE=( "${TARGET_TABLES[@]}" "${TRUNCATE_ONLY[@]}" )

  # Truncate in reverse order. Why? Because otherwise,
  # the counts get messed up. The first table cascades.
  # https://stackoverflow.com/a/13360181
  for (( ndx=${#FOR_TRUNCATE[@]}-1 ; ndx>=0 ; ndx-- ));
  do
    dump=${FOR_TRUNCATE[$ndx]}
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}
  
  cmd="SELECT COUNT(*) FROM ${TABLENAME}"
  PRE_TRUNCATE_TABLE_COUNTS+=($(psql \
    -t \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w \
    -c "${cmd}"))

  echo "${cmd}: ${PRE_TRUNCATE_TABLE_COUNTS[$ndx]}"

  # TRUNCATE is not guaranteed to be complete if we call a 
  # `pg_restore` immediately after. Wrap it in a transaction.
  # https://petereisentraut.blogspot.com/2010/03/running-sql-scripts-with-psql.html
  PGOPTIONS='--client-min-messages=warning' psql \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w \
    -c "BEGIN; TRUNCATE ${TABLENAME} CASCADE; COMMIT;"
  
  if [ $? -ne 0 ]; then
    echo "Truncate failed: ${TABLENAME}"
    echo "Exiting."
    exit
  fi

  done
}


############################################################
# test_sanitized_production_dump
############################################################
declare -a TEST_LOAD_TABLE_COUNTS
test_sanitized_production_dump () {
  echo "test_sanitized_production_dump"

  # We must truncate everything before loading.
  truncate_all_local_tables

  echo "Restoring data from sanitized-${DATE}.dump"

  cat "${DESTINATION}/sanitized-${DATE}.dump" | \
  pg_restore \
    --data-only \
    --no-privileges \
    --no-owner \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -f - | grep -v "transaction_timeout" | psql \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w    

  if [ $? -ne 0 ]; then
    echo "pg_restore failed."
    exit
  fi

  FOR_TRUNCATE=( "${TARGET_TABLES[@]}" "${TRUNCATE_ONLY[@]}" )
  for (( ndx=${#FOR_TRUNCATE[@]}-1 ; ndx>=0 ; ndx-- ));
  do
    dump=${FOR_TRUNCATE[$ndx]}
    prefix="public-"
    suffix=".dump"
    TABLENAME=${dump/#$prefix}
    TABLENAME=${TABLENAME/%$suffix}

    cmd="SELECT COUNT(*) FROM ${TABLENAME}"
    TEST_LOAD_TABLE_COUNTS+=($(psql \
      -t \
      -q \
      -d ${DATABASE} \
      -U ${USERNAME} \
      -p ${PORT} \
      -h ${HOST} \
      -w \
      -c "${cmd}"))
  done

  all_same=1
  for i in "${!TEST_LOAD_TABLE_COUNTS[@]}"; do
      if [ "${PRE_TRUNCATE_TABLE_COUNTS[$i]}" != "${TEST_LOAD_TABLE_COUNTS[$i]}" ]; then
        printf '${%s}=%s %s\n' "$i" "${PRE_TRUNCATE_TABLE_COUNTS[$i]}" "${TEST_LOAD_TABLE_COUNTS[$i]}"
        all_same=0
      fi
  done

  if [ "${all_same}" == "1" ]; then
    echo "All table counts the same."
  else
    echo "Table counts differed."
  fi
}

############################################################
# DAS MENU
############################################################
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
