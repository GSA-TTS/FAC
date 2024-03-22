source tools/util_startup.sh

function create_materialized_views {
    startup_log "MATERIALIZED_VIEWS_CREATE" "BEGIN"
    python manage.py materialized_views --create
    local result=$?
    startup_log "MATERIALIZED_VIEWS_CREATE" "END"
    return $result
}

function drop_materialized_views {
    startup_log "MATERIALIZED_VIEWS_DROP" "BEGIN"
    python manage.py materialized_views --drop
    local result=$?
    startup_log "MATERIALIZED_VIEWS_DROP" "END"
    return $result
}

function refresh_materialized_views {
    startup_log "MATERIALIZED_VIEWS_REFRESH" "BEGIN"
    python manage.py materialized_views --refresh
    local result=$?
    startup_log "MATERIALIZED_VIEWS_REFRESH" "END"
    return $result
}
