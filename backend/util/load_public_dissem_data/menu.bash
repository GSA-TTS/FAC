#!/bin/bash

DATABASE=postgres
USERNAME=postgres
HOST=localhost
PORT=5432
RAW_FILENAME=${RAW_FILENAME:-data/sac-user-access-valwaiver-pdf-xlsx-event-data-03-28-25.dump}
DATE=$(date '+%Y%m%d')

count_audit_singleauditchecklist=354222
count_audit_access=1195595
count_auth_user=75461
count_dissemination_additionalein=59251
count_dissemination_additionaluei=15101
count_dissemination_captext=116694
count_dissemination_federalaward=5811960
count_dissemination_finding=507895
count_dissemination_findingtext=120290
count_dissemination_general=343116
count_dissemination_note=530407
count_dissemination_passthrough=4025800
count_dissemination_secondaryauditor=1803
count_audit_ueivalidationwaiver=0
count_audit_sacvalidationwaiver=1
count_audit_singleauditreportfile=362229
count_audit_excelfile=339149
count_audit_submissionevent=1591563

############################################################
# truncate
############################################################
truncate () {
  echo "Truncating test data tables."
  psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
		-w \
    -v ON_ERROR_STOP=1 \
    <<EOF
	begin;
		truncate
      audit_access,
      audit_singleauditchecklist,
      audit_audit,
      auth_user,
      dissemination_additionalein,
      dissemination_additionaluei,
      dissemination_captext,
      dissemination_federalaward,
      dissemination_finding,
      dissemination_findingtext,
      dissemination_general,
      dissemination_note,
      dissemination_passthrough,
      dissemination_secondaryauditor,
      audit_ueivalidationwaiver,
      audit_sacvalidationwaiver,
      audit_singleauditreportfile,
      audit_excelfile,
      audit_submissionevent,
      users_userprofile
    cascade;
	commit;
EOF

  if [ $? = 0 ]; then
    echo "Truncate completed successfully."
  fi
}

############################################################
# reset_migrated_to_audit
############################################################
reset_migrated_to_audit () {

  echo "Setting migrated_to_audit to false"

  psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
    -t \
    -v ON_ERROR_STOP=1 \
		-w -c "UPDATE audit_singleauditchecklist SET migrated_to_audit = false"

  if [ $? = 0 ]; then
    echo "Done"
  else
    echo "Failed to reset migrated_to_audit"
  fi

    psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
    -t \
		-w -c "SELECT COUNT(*) FROM audit_singleauditchecklist WHERE migrated_to_audit = false" > count.tmp

  local VALUE=$(head -n 1 count.tmp)

  if [ $VALUE -ge 0 ]; then
      if [ $VALUE -eq ${count_audit_singleauditchecklist} ]; then
        echo "[PASS] audit_singleauditchecklist has ${count_audit_singleauditchecklist} rows with migrated_to_audit = false"
      else
        echo "[FAIL] reset of audit_singleauditchecklist failed"
      fi
  fi
  rm -f count.tmp
}

############################################################
# load_raw_data
############################################################
load_raw_data () {
  echo "Loading ${RAW_FILENAME}"
  cat ${RAW_FILENAME} | \
    grep -v "transaction_timeout" | \
    psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
    -v ON_ERROR_STOP=1 \
		-w

  if [ $? = 0 ]; then
    echo "Data loaded successfully."
  fi

  reset_migrated_to_audit
}


############################################################
# load_finished_data
############################################################
load_finished_data () {
  read -p "Enter the finished file (default: data/use_with_generate_resubmissions.dump): " finished_filename
  if [ -z "$finished_filename" ]; then
    finished_filename="data/use_with_generate_resubmissions.dump"
  fi

  echo "Loading ${finished_filename}"

  cat ${finished_filename} | \
    grep -v "transaction_timeout" | \
    psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
    -v ON_ERROR_STOP=1 \
		-w

  if [ $? = 0 ]; then
    echo "Data loaded successfully."
  fi
}

############################################################
# fake_by_year
############################################################
fake_by_year () {
  YEAR=$1
  psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
		-w \
    -v ON_ERROR_STOP=1 \
    <<EOF
    begin;
      update audit_singleauditchecklist
      set tribal_data_consent = '{"is_tribal_information_authorized_to_be_public": false, "tribal_authorization_certifying_official_name": "GSA Name", "tribal_authorization_certifying_official_title": "GSA Title"}'
      where report_id in (
        SELECT report_id FROM audit_singleauditchecklist
        TABLESAMPLE BERNOULLI(70)
        where general_information->>'auditee_fiscal_period_end' like '%${YEAR}%'
        limit 500
      );
    commit;
EOF
}

############################################################
# fake_suppressed_reports
############################################################
fake_suppressed_reports () {
  for year in $(seq 2016 2023)
  do
    fake_by_year $year
  done

  psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
		-w \
    -v ON_ERROR_STOP=1 \
    <<EOF
  begin;
  update audit_singleauditchecklist
    set general_information = jsonb_set(general_information, '{user_provided_organization_type}', '"tribal"', false)
    where tribal_data_consent->>'is_tribal_information_authorized_to_be_public' = 'false';
  commit;
EOF
}

############################################################
# re_disseminate_sacs
############################################################
re_disseminate_sacs () {
  docker compose run --rm web python manage.py delete_and_regenerate_dissemination_from_intake
}


############################################################
# check_row_counts
############################################################
check_row_counts () {
  local TABLE="$1"
  local EXPECT="$2"

  psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
    -t \
		-w -c "SELECT COUNT(*) FROM ${TABLE}" > count.tmp

  local VALUE=$(head -n 1 count.tmp)

  if [ $VALUE -ge 0 ]; then
      if [ $VALUE -eq $EXPECT ]; then
        echo "[PASS] $TABLE has $EXPECT rows"
      else
        echo "[FAIL] $TABLE should have $EXPECT rows; it has $VALUE"
      fi
  fi
  rm -f count.tmp
}


############################################################
# check_all_row_counts
############################################################
check_all_row_counts () {
  echo "Checking counts"
  check_row_counts "audit_singleauditchecklist" ${count_audit_singleauditchecklist}
  check_row_counts "audit_access" ${count_audit_access}
  check_row_counts "auth_user" ${count_auth_user}
  check_row_counts "dissemination_additionalein" ${count_dissemination_additionalein}
  check_row_counts "dissemination_additionaluei" ${count_dissemination_additionaluei}
  check_row_counts "dissemination_captext" ${count_dissemination_captext}
  check_row_counts "dissemination_federalaward" ${count_dissemination_federalaward}
  check_row_counts "dissemination_finding" ${count_dissemination_finding}
  check_row_counts "dissemination_findingtext" ${count_dissemination_findingtext}
  check_row_counts "dissemination_general" ${count_dissemination_general}
  check_row_counts "dissemination_note" ${count_dissemination_note}
  check_row_counts "dissemination_passthrough" ${count_dissemination_passthrough}
  check_row_counts "dissemination_secondaryauditor" ${count_dissemination_secondaryauditor}
  check_row_counts "audit_ueivalidationwaiver" ${count_audit_ueivalidationwaiver}
  check_row_counts "audit_sacvalidationwaiver" ${count_audit_sacvalidationwaiver}
  check_row_counts "audit_singleauditreportfile" ${count_audit_singleauditreportfile}
  check_row_counts "audit_excelfile" ${count_audit_excelfile}
  check_row_counts "audit_submissionevent" ${count_audit_submissionevent}
}


############################################################
# dump_for_reuse
############################################################
dump_for_reuse () {
  default_dumpfile=data/internal-and-external-${DATE}.dump

  read -p "Enter the finished file (default: $default_dumpfile): " dumpfile
  if [ -z "$dumpfile" ]; then
    echo "Using default dump file: $default_dumpfile"
    dumpfile=$default_dumpfile
  fi

  echo "Dumping data to ${dumpfile}"

  rm -f "${dumpfile}"

  pg_dump \
  -a \
  -F p \
  -f "${dumpfile}" \
  -d postgres \
  -h localhost \
  -p 5432 \
  -U postgres \
  -w \
  -t audit_singleauditchecklist \
  -t audit_audit \
  -t audit_access \
  -t auth_user \
  -t dissemination_additionalein \
  -t dissemination_additionaluei \
  -t dissemination_captext \
  -t dissemination_federalaward \
  -t dissemination_finding \
  -t dissemination_findingtext \
  -t dissemination_general \
  -t dissemination_note \
  -t dissemination_passthrough \
  -t dissemination_secondaryauditor \
  -t audit_ueivalidationwaiver \
  -t audit_sacvalidationwaiver \
  -t audit_singleauditreportfile \
  -t audit_excelfile \
  -t audit_submissionevent \
  -t users_userprofile
}


############################################################
# truncate_sourceoftruth
############################################################
truncate_sourceoftruth () {
  echo "Truncating audit_audit"
  psql \
		-d ${DATABASE} \
		-U ${USERNAME} \
		-p ${PORT} \
		-h ${HOST} \
		-w \
    -v ON_ERROR_STOP=1 \
    <<EOF
	begin;
		truncate audit_audit cascade;
	commit;
EOF

  if [ $? = 0 ]; then
    echo "Truncate completed successfully."
  fi

  reset_migrated_to_audit
}

generate_resubmissions () {
  echo "Running `docker compose` for generate_resubmissions"
  docker compose run \
    --rm web \
    python manage.py generate_resubmissions
}


PS3='Please enter your choice: '
options=(\
  "Truncate tables" \
  "Load finished data" \
  "Load raw data" \
  "Generate fake suppressed reports" \
  "Re-disseminate SAC records" \
  "Check row counts" \
  "Dump tables for reuse" \
  "Reset migrated_to_audit" \
  "Truncate audit_audit" \
  "Generate resubmissions"
  "Quit"\
)
select opt in "${options[@]}"
do
    case $opt in
        "Truncate tables")
            truncate
            ;;
        "Load finished data")
            load_finished_data
            ;;
        "Load raw data")
            load_raw_data
            ;;
        "Generate fake suppressed reports")
            fake_suppressed_reports
            ;;
        "Re-disseminate SAC records")
            re_disseminate_sacs
            ;;
        "Check row counts")
            check_all_row_counts
            ;;
        "Dump tables for reuse")
            dump_for_reuse
            ;;
        "Reset migrated_to_audit")
            reset_migrated_to_audit
            ;;
        "Truncate audit_audit")
            truncate_sourceoftruth
            ;;
        "Generate resubmissions")
            generate_resubmissions
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
