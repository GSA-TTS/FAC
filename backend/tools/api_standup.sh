source tools/util_startup.sh

function api_standup {
    startup_log "API_STANDUP" "BEGIN"
    
    # First create non-managed tables
    startup_log "CREATE_API_ACCESS_TABLES" "BEGIN"
    python manage.py create_api_access_tables
    local d1=$?
    startup_log "CREATE_API_ACCESS_TABLES" "END"

    # Bring the API back, possibly installing a new API
    startup_log "CREATE_API_SCHEMA" "BEGIN"
    python manage.py create_api_schema
    local d2=$?
    startup_log "CREATE_API_SCHEMA" "END"
    
    startup_log "CREATE_API_VIEWS" "BEGIN"
    python manage.py create_api_views &&
    local d3=$?
    startup_log "CREATE_API_VIEWS" "END"

    startup_log "API_STANDUP" "END"

    r1=$(($d1+$d2))
    result=$(($r1+$d3))
    # If these are all zero, we're all good.
    return $result
}

