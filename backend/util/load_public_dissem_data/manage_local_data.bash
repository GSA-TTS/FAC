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
# truncate
############################################################
truncate_all_tables () {
  echo "TRUNCATE all data tables."
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
      audit_audit,
      audit_excelfile,
      audit_sacvalidationwaiver,
      audit_singleauditchecklist,
      audit_singleauditreportfile,
      audit_submissionevent,
      audit_ueivalidationwaiver,
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
      users_userprofile
    cascade;
	commit;
EOF

  if [ $? = 0 ]; then
    echo "Truncate completed successfully."
  fi
}

PS3='Please enter your choice: '
options=(\
  "Load sanitized data dump" \
  "Shrink the dump to 20K records" \
  "Generate fake suppressed reports" \
  "Generate resubmissions" \
  "Generate MATERIALIZED VIEW" \
  "Re-disseminate all SAC records" \
  "TRUNCATE the dissemination tables" \
  "TRUNCATE *all* tables" \ 
  "Quit"
)
select opt in "${options[@]}"
do
    case $opt in
        "Load sanitized data dump")
            load_sanitized_data_dump
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
        "Generate MATERIALIZED VIEW")
            generate_materialized_view
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
