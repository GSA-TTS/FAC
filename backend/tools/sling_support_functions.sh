source tools/util_startup.sh

function sling_support_functions() {
    startup_log "SLING_SUPPORT_FUNCTIONS" "Loading functions needed by sling"

    check_table_exists $FAC_SNAPSHOT_URI 'public_data_v1_0_0.general'
    gonogo "sling_support_functions general exists"

    # We need to load some functions for sling to complete, because
    # we use those functions as part of the metadata table generation.
    local base_path='dissemination/sql'
    local location='sling'
    run_sql $FAC_SNAPSHOT_URI $base_path $location 'public_data_v1_0_0' 'sling_functions.sql'
    return $?
}
