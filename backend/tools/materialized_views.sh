source tools/util_startup.sh

function materialized_views {
    startup_log "RUN_MATERIALIZEDVIEWS" "BEGIN"
    python manage.py materialized_views --create &&
    local result=$?
    startup_log "RUN_MATERIALIZEDVIEWS" "END"
    return $result
}
