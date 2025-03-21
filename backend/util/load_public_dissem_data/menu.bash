#!/bin/bash

DATABASE=postgres
USERNAME=postgres
HOST=localhost
PORT=5432
FILENAME=${FILENAME:-data/internal-and-external-20250320.dump}

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
  check_row_counts "audit_singleauditchecklist" 354222
  check_row_counts "audit_access" 1195595 
  check_row_counts "auth_user" 75461 
  check_row_counts "dissemination_additionalein" 59251
  check_row_counts "dissemination_additionaluei" 15101
  check_row_counts "dissemination_captext" 116694
  check_row_counts "dissemination_federalaward" 5811948
  check_row_counts "dissemination_finding" 507895
  check_row_counts "dissemination_findingtext" 120290
  check_row_counts "dissemination_general" 343114
  check_row_counts "dissemination_note" 530405
  check_row_counts "dissemination_passthrough" 4025800
  check_row_counts "dissemination_secondaryauditor" 1803
}

PS3='Please enter your choice: '
options=("Truncate tables" "Load data" "Check row counts" "Quit")
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
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
