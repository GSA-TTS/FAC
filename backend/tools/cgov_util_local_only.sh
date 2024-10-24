source tools/util_startup.sh

function cgov_util_local_only() {
    startup_log "CGOV_LOCAL_ONLY" "Making an initial 'backup'"

    check_table_exists $FAC_SNAPSHOT_URI 'public' 'dissemination_general'
    local is_general_table=$FUNCTION_RESULT
    if [ $is_general_table -ne 0 ]; then
        # This is the first run.
        startup_log "CGOV_LOCAL_ONLY" "Running cgov-util INITIAL."
        $CGOV_UTIL_EXE db_to_db \
            --src_db fac-db \
            --dest_db fac-snapshot-db \
            --operation initial
    fi

    startup_log "CGOV_LOCAL_ONLY" "Done"
    return 0
}
