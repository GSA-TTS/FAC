#!/bin/bash

############################################################
# environment variables
############################################################
DATABASE=postgres
USERNAME=postgres
HOST=db
PORT=5432
DATE=$(date '+%Y%m%d')

############################################################
# process command-line arguments
############################################################
# Fetch the command line arguments in an array.
# https://stackoverflow.com/a/2740967
args=("$@")
# args[0] is the first argument, and not the name of the script.

export DUMPFILE="${args[0]:-}"
export EMAIL="${args[1]:-}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

export TABLES_FILE=$"$SCRIPT_DIR/tables.source"
if [ -f "$TABLES_FILE" ]; then
  source "$SCRIPT_DIR/tables.source"
else
  echo "File '$TABLES_FILE' does not exist."
  echo "Exiting."
  exit
fi

ensure_dumpfile () {
  # Checks if the dumpfile was already provided in the script args
  if [[ -n "$DUMPFILE" && -f "$DUMPFILE" ]]; then
    echo "Found file '$DUMPFILE'."
    return 0
  elif [[ -n "$DUMPFILE" ]]; then
    echo "File '$DUMPFILE' does not exist."
    DUMPFILE=""
  fi

  # Grabs the latest-dated sanitized dumpfile from /data to use as the default
  local default_dumpfile=""
  local latest_date=""
  local candidate candidate_date entered_dumpfile

  for candidate in "$SCRIPT_DIR"/data/sanitized-????????.dump; do
    [[ -f "$candidate" ]] || continue
    candidate_date=${candidate##*/sanitized-}
    candidate_date=${candidate_date%.dump}
    [[ "$candidate_date" =~ ^[0-9]{8}$ ]] || continue

    if [[ -z "$latest_date" || "$candidate_date" > "$latest_date" ]]; then
      latest_date=$candidate_date
      default_dumpfile=$candidate
    fi
  done

  # Prompts until given a file that exists
  while true; do
    if [[ -n "$default_dumpfile" ]]; then
      if ! IFS= read -r -p "Path to sanitized dumpfile [$default_dumpfile]: " entered_dumpfile; then
        echo "No dumpfile provided."
        return 1
      fi
      DUMPFILE=${entered_dumpfile:-$default_dumpfile}
    elif ! IFS= read -r -p "Path to sanitized dumpfile: " DUMPFILE; then
      echo "No dumpfile provided."
      return 1
    fi

    if [[ -f "$DUMPFILE" ]]; then
      echo "Found file '$DUMPFILE'."
      return 0
    fi

    if [[ -n "$DUMPFILE" ]]; then
      echo "File '$DUMPFILE' does not exist."
    fi
  done
}

ensure_email () {
  while [[ -z "$EMAIL" ]]; do
    if ! IFS= read -r -p "Staff user email: " EMAIL; then
      echo "No staff user email provided."
      return 1
    fi
  done
}

############################################################
# truncate_all_local_tables
############################################################
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
# load_sanitized_production_dump
############################################################
load_sanitized_data_dump () {
  echo "test_sanitized_production_dump"

  if ! ensure_dumpfile; then
    return 1
  fi

  # We must truncate everything before loading.
  truncate_all_local_tables


  echo "Restoring data from ${DUMPFILE}"

  TEMPFILE="_tmp.sql"

  pg_restore --data-only -f "${TEMPFILE}" "${DUMPFILE}"

  if [ $? -ne 0 ]; then
    echo "pg_restore failed."
    exit
  fi

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

  # Then remove the tmpfile
  rm -f "${TEMPFILE}"

  if [ $? -ne 0 ]; then
    echo "RESTORE FAILED: ${TABLENAME}"
    echo "Exiting."
    exit
  fi

}

############################################################
# shrink_to_20k_records
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
    -w < "$SCRIPT_DIR/shrink_the_tables.sql"

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
    -w < "$SCRIPT_DIR/gen_fake_suppressed_audits.sql"

  if [ $? -ne 0 ]; then
    echo "psql failed."
    exit
  fi

  echo "Done."
}

############################################################
# generate_fake_resubmission_dissemination_data
############################################################
generate_fake_resubmission_dissemination_data () {
  echo "generate_fake_resubmission_dissemination_data"
    psql \
    -q \
    -d ${DATABASE} \
    -U ${USERNAME} \
    -p ${PORT} \
    -h ${HOST} \
    -v ON_ERROR_STOP=1 \
    -w < "$SCRIPT_DIR/gen_fake_resub_dissem_data.sql"

  if [ $? -ne 0 ]; then
    echo "psql failed."
    exit
  fi

  echo "Done."
}

############################################################
# generate_resubmissions
############################################################
generate_resubmissions () {
  if ! ensure_email; then
    return 1
  fi

  echo "generate_resubmissions"
  (cd "$BACKEND_DIR" && python manage.py generate_resubmissions --email "$EMAIL")
}

############################################################
# generate_materialized_view
############################################################
generate_materialized_view () {
  echo "generate_materialized_view"
  (cd "$BACKEND_DIR" && python manage.py materialized_views --create)
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
# redisseminate_all_sac_records
############################################################
redisseminate_all_sac_records () {
  echo "redisseminate_all_sac_records"
  (cd "$BACKEND_DIR" && python manage.py delete_and_regenerate_dissemination_from_intake)
}


############################################################
# snapshot_current_db
############################################################
snapshot_current_db () {
  echo "snapshot_current_db"

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
  TS=$(date '+%Y%m%d-%T')
  rm -f "snapshot-${TS}.dump"

  cmd="pg_dump -d ${DATABASE} -h ${HOST} -p ${PORT} -U ${USERNAME} -w -F c --no-acl --no-owner --data-only ${table_flags} "
  cmd="mkdir -p data/ ; ${cmd} -f data/snapshot-${TS}.dump"
  echo "${cmd}"
  eval "${cmd}"

  if [ $? -ne 0 ]; then
    echo "Dump failed."
    echo "Exiting."
    exit
  fi
}

############################################################
# DAS MENU
############################################################
PS3='Please enter your choice (supply no # to view options): '
options=(\
  "Load sanitized data dump" \
  "Shrink the dump to 20K records" \
  "Generate fake suppressed reports" \
  "Generate fake resubmission dissemination data" \
  "Generate resubmissions" \
  "TRUNCATE the dissemination tables" \
  "Re-disseminate all SAC records" \
  "Generate MATERIALIZED VIEW" \
  "Snapshot the current DB" \
  "TRUNCATE all tables" \
  "Run most all back-to-back" \
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
    "Generate fake resubmission dissemination data")
      generate_fake_resubmission_dissemination_data
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
    "Snapshot the current DB")
      snapshot_current_db
      ;;
    "TRUNCATE all tables")
      truncate_all_local_tables
      ;;
    "Run most all back-to-back")
      # `continue` will make it skip the rest. Used for dumpfile or email exceptions.
      load_sanitized_data_dump || continue
      shrink_to_20k_records
      generate_fake_suppressed_reports
      generate_fake_resubmission_dissemination_data
      generate_resubmissions || continue
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
