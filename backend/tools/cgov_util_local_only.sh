source tools/util_startup.sh

function cgov_util_local_only() {
    
    # Really, really only run this locally. Or in a GH runner.

    if [[ "${ENV}" == "LOCAL" || "${ENV}" == "TESTING" ]]; then
        startup_log "CGOV_LOCAL_ONLY" "Making an initial 'backup'"

        $PSQL_EXE $FAC_SNAPSHOT_URI -c "DROP SCHEMA IF EXISTS public CASCADE"
        gonogo "DROP PUBLIC in fac-snapshot-db"
        $PSQL_EXE $FAC_SNAPSHOT_URI -c "CREATE SCHEMA public"
        gonogo "CREATE PUBLIC fac-snapshot-db"

        # This is the first run.
        startup_log "CGOV_LOCAL_ONLY" "Running cgov-util INITIAL."
        $CGOV_UTIL_EXE db_to_db \
            --src_db fac-db \
            --dest_db fac-snapshot-db \
            --operation initial

        startup_log "CGOV_LOCAL_ONLY" "Done"
    fi

    return 0
}
