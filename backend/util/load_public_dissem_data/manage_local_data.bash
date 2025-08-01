#!/bin/bash

############################################################
# environment variables
############################################################
DATABASE=postgres
USERNAME=postgres
HOST=localhost
PORT=5432
DATE=$(date '+%Y%m%d')


############################################################
# process command-line arguments
############################################################
# Fetch the command line arguments in an array.
# https://stackoverflow.com/a/2740967
args=("$@")
# args[0] is the first argument, and not the name of the script.

DUMPFILE=${args[0]}
EMAIL=${args[1]}

if [[ -z "${DUMPFILE}" ]]; then
  echo "Please pass a sanitized dumpfile as the first command-line argument."
  echo "Exiting."
  exit
fi

if [ -f "$DUMPFILE" ]; then
  echo "Found file '$DUMPFILE'."
else
  echo "File '$DESTINATION' does not exist."
  echo "Exiting."
  exit
fi

if [[ -z "${EMAIL}" ]]; then
  echo "Please pass a staff user email as the second arg."
  echo "Exiting."
  exit
fi

# Source in the target tables
source "tables.source"

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
load_sanitized_data_dump () {
  echo "test_sanitized_production_dump"

  # We must truncate everything before loading.
  truncate_all_local_tables

  echo "Restoring data from sanitized-${DATE}.dump"

  TEMPFILE="_tmp.sql"
  pg_restore --data-only -f "${TEMPFILE}" "${DUMPFILE}"

  if [ $? -ne 0 ]; then
    echo "pg_restore failed."
    exit
  fi

  psql \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w < "${TEMPFILE}"

  if [ $? -ne 0 ]; then
    echo "psql failed."
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
# test_sanitized_production_dump
############################################################
shrink_to_20k_records () {
  echo "Shrinking to 20K records. Deleting from many tables."

  psql \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w < "shrink_the_tables.sql"

  if [ $? -ne 0 ]; then
    echo "psql failed."
    exit
  fi
}

############################################################
# generate_fake_suppressed_reports
############################################################
generate_fake_suppressed_reports () {
  echo "generate_fake_suppressed_reports"
    psql \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w < "gen_fake_suppressed_audits.sql"

  if [ $? -ne 0 ]; then
    echo "psql failed."
    exit
  fi
}

############################################################
# generate_resubmissions
############################################################
generate_resubmissions () {
  echo "generate_resubmissions"
  docker compose exec web python manage.py generate_resubmissions --email ${EMAIL}
}

############################################################
# generate_materialized_view
############################################################
generate_materialized_view () {
  echo "generate_materialized_view"
  docker compose exec web python manage.py materialized_views --create
}

############################################################
# redisseminate_all_sac_records
############################################################
redisseminate_all_sac_records () {
  echo "redisseminate_all_sac_records"
  docker compose exec web python manage.py delete_and_regenerate_dissemination_from_intake
}

############################################################
# truncate_dissemination_tables
############################################################
truncate_dissemination_tables () {
  echo "truncate_dissemination_tables"
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

  re="dissemination_"
  if [[ "${TABLENAME}" =~ $re ]]; 
  then
    echo "Truncating ${TABLENAME}"
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
  fi
  done
}

############################################################
# DAS MENU
############################################################
PS3='Please enter your choice: '
options=(\
  "Load sanitized data dump" \
  "Shrink the dump to 20K records" \
  "Generate fake suppressed reports" \
  "Generate resubmissions" \
  "TRUNCATE the dissemination tables" \
  "Re-disseminate all SAC records" \
  "Generate MATERIALIZED VIEW" \
  "TRUNCATE *all* tables" \ 
  "Run (most) all back-to-back" \
  "Quit"
)
select opt in "${options[@]}"
do
    case $opt in
      "Load sanitized data dump")
        load_sanitized_data_dump
        ;;
      "Shrink the dump to 20K records")
        shrink_to_20k_records
        ;;
      "Generate fake suppressed reports")
        generate_fake_suppressed_reports
        ;;
      "Generate resubmissions")
        generate_resubmissions
        ;;
      "Generate MATERIALIZED VIEW")
        generate_materialized_view
        ;;
      "TRUNCATE the dissemination tables")
        truncate_dissemination_tables
        ;;
      "Re-disseminate all SAC records")
        redisseminate_all_sac_records
        ;;
      "TRUNCATE *all* tables")
        truncate_all_local_tables
        ;;
      "Run (most) all back-to-back")
        load_sanitized_data_dump
        shrink_to_20k_records
        generate_fake_suppressed_reports
        generate_resubmissions
        truncate_dissemination_tables
        redisseminate_all_sac_records
        generate_materialized_view
        ;;
      "Quit")
          break
          ;;
      *) echo "invalid option $REPLY";;
    esac
done
