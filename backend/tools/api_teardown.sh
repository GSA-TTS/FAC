source tools/util_startup.sh

function api_teardown {
    startup_log "API_TEARDOWN" "BEGIN"
    
    # startup_log "DROP_DEPRECATED_API_SCHEMA_AND_VIEWS" "BEGIN"
    # # python manage.py drop_deprecated_api_schema_and_views
    # local d1=$?
    # startup_log "DROP_DEPRECATED_API_SCHEMA_AND_VIEWS" "END"
    # startup_log "DROP_API_SCHEMA" "BEGIN"
    # python manage.py drop_api_schema

    # for api_version in "${public_api_versions[@]}"
    # do
    #     echo "VERSION $api_version"
    #     $PSQL_EXE $FAC_SNAPSHOT_URI < dissemination/sql/api/${api_version}/drop_schema.sql
    #     gonogo "$api_version teardown.sql"
    # done

    run_sql_for_public_apis 'api' 'teardown.sql'

    startup_log "API_TEARDOWN" "END"
    
    # If these are both zero, we're all good.
    return 0
}
