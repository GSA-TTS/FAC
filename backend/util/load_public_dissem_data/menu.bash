#!/bin/bash

DATABASE=postgres
USERNAME=postgres
HOST=localhost
PORT=5432
FILENAME=${FILENAME:-data/internal-and-external-20250320.dump}

count_audit_singleauditchecklist=354222
count_audit_access=1195595 
count_auth_user=75461 
count_dissemination_additionalein=59251
count_dissemination_additionaluei=15101
count_dissemination_captext=116694
count_dissemination_federalaward=5811948
count_dissemination_finding=507895
count_dissemination_findingtext=120290
count_dissemination_general=343114
count_dissemination_note=530405
count_dissemination_passthrough=4025800
count_dissemination_secondaryauditor=1803

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
		truncate audit_access,
			audit_singleauditchecklist,
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
			dissemination_secondaryauditor
			cascade;
	commit;
EOF

  if [ $? = 0 ]; then
    echo "Truncate completed successfully."
  fi
}


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

# The dump may contain pg_dump parameters that are inappropriate
# for our local stack. Remove those lines.
load_data () {
  echo "Loading ${FILENAME}"
  cat ${FILENAME} | \
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
}

PS3='Please enter your choice: '
options=("Truncate tables" "Load data" "Check row counts" "Reset migrated_to_audit" "Truncate audit_audit" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Truncate tables")
            truncate
            ;;
        "Load data")
            load_data
            ;;
        "Check row counts")
            check_all_row_counts
            ;;
        "Reset migrated_to_audit")
            reset_migrated_to_audit
            ;;
        "Truncate audit_audit")
            truncate_sourceoftruth
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
