source tools/util_startup.sh

function api_teardown {
    startup_log "API_TEARDOWN" "BEGIN"
    
    startup_log "DROP_DEPRECATED_API_SCHEMA_AND_VIEWS" "BEGIN"
    python manage.py drop_deprecated_api_schema_and_views
    local d1=$?
    startup_log "DROP_DEPRECATED_API_SCHEMA_AND_VIEWS" "END"
    startup_log "DROP_API_SCHEMA" "BEGIN"
    python manage.py drop_api_schema
    local d2=$?
    startup_log "DROP_API_SCHEMA" "END"

    startup_log "API_TEARDOWN" "END"
    
    result=$(($d1 + $d2))
    # If these are both zero, we're all good.
    return $result
}
