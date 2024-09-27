source tools/util_startup.sh


function api_standup {
    startup_log "API_STANDUP" "BEGIN"
    
    run_sql_for_public_apis 'api' 'standup.sql'

    # First create non-managed tables
    #startup_log "CREATE_API_ACCESS_TABLES" "BEGIN"
    # python manage.py create_api_access_tables
    #run_sql_for_public_apis 'api' 'create_access_tables.sql'
    #startup_log "CREATE_API_ACCESS_TABLES" "END"

    # Bring the API back, possibly installing a new API
    # startup_log "CREATE_API_SCHEMA" "BEGIN"
    # # python manage.py create_api_schema
    # run_sql_for_public_apis 'api' 'base.sql'    
    # run_sql_for_public_apis 'api' 'create_schema.sql'    
    # startup_log "CREATE_API_SCHEMA" "END"
    
    # startup_log "CREATE_API_VIEWS" "BEGIN"
    # # python manage.py create_api_views &&
    # run_sql_for_public_apis 'api' 'create_functions.sql'
    # run_sql_for_public_apis 'api' 'create_views.sql'
    # startup_log "CREATE_API_VIEWS" "END"
    startup_log "API_STANDUP" "END"

    return 0
}

