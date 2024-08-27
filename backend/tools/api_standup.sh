source tools/util_startup.sh

function api_standup {
    startup_log "API_STANDUP" "BEGIN"
    
    # First create non-managed tables
    startup_log "CREATE_API_ACCESS_TABLES" "BEGIN"
    python manage.py create_api_access_tables
    local d1=$?
    startup_log "CREATE_API_ACCESS_TABLES" "END"

    # Bring the API down completely
    startup_log "DROP_API_SCHEMA" "BEGIN"
    python manage.py drop_api_schema
    local d2=$?
    startup_log "DROP_API_SCHEMA" "END"

    # Bring the API back, possibly installing a new API
    startup_log "CREATE_API_SCHEMA" "BEGIN"
    python manage.py create_api_schema
    local d3=$?
    startup_log "CREATE_API_SCHEMA" "END"

    # Drop all views, if they already exist
    startup_log "DROP_API_VIEWS" "BEGIN"
    python manage.py drop_api_views &&
    local d4=$?
    startup_log "CREATE_API_VIEWS" "END"

    # Create/recreate the materialized views. The 'combined' view is the important one for the API.
    startup_log "CREATE_MATERIALIZED_VIEWS" "BEGIN"
    python manage.py materialized_views --create &&
    local d5=$?
    startup_log "CREATE_MATERIALIZED_VIEWS" "END"
    
    # Create the API views, which may rely on the 'combined' view from above.
    startup_log "CREATE_API_VIEWS" "BEGIN"
    python manage.py create_api_views &&
    local d6=$?
    startup_log "CREATE_API_VIEWS" "END"

    startup_log "API_STANDUP" "END"

    result=$(((((($d1 + $d2) + $d3) + $d4) + $d5) + $d6))
    # If these are all zero, we're all good.
    return $result
}

