source tools/util_startup.sh

function sling_first_run() {
    startup_log "SLING_FIRST_RUN" "Slinging data to fac-snapshot if needed"

    check_table_exists $FAC_SNAPSHOT_URI 'public.dissemination_general'
    local is_general_table=$?
    if [ $is_general_table -ne 0 ]; then
        # This is the first run.
        startup_log "SLING_FIRST_RUN" "Running cgov-util INITIAL."
        $CGOV_UTIL_EXE db_to_db \
            --src_db fac-db \
            --dest_db fac-snapshot-db \
            --operation initial
    fi

    # If the metadata table exists, it means sling has run to completion.
    check_table_exists $FAC_SNAPSHOT_URI 'public_data_v1_0_0.metadata'
    local is_metadata_table=$?
    # We need to load some functions for sling to complete, because
    # we use those functions as part of the metadata table generation.
    local base_path='dissemination/sql'
    local location='sling'

    # Only run sling if the tables in the secondary DB do not exist.
    if [ $is_metadata_table -ne 0 ]; then 
        startup_log "SLING_FIRST_RUN" "API tables don't exist; running sling."
        $SLING_EXE run -r dissemination/sql/sling/public_data_v1_0_0/public_data_v1_0_0.yaml
        gonogo "sling public data for API tables"
        $SLING_EXE run -r dissemination/sql/sling/public_data_v1_0_0/tribal_data_v1_0_0.yaml
        gonogo "sling tribal data for API tables"
        $SLING_EXE run -r dissemination/sql/sling/public_data_v1_0_0/public_metadata_v1_0_0.yaml
        gonogo "sling tribal data for API tables"
        startup_log "SLING_FIRST_RUN" "Successfully ran sling to generate tables."
    else
        startup_log "SLING_FIRST_RUN" "API tables exist; skipping sling."
    fi
    startup_log "SLING_FIRST_RUN" "Done"
    return 0
}
