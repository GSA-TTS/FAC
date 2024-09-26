source tools/util_startup.sh

function run_collectstatic {
    startup_log "RUN_MATERIALIZEDVIEWS" "BEGIN"
    python manage.py materialized_views --create &&
    local result=$?
    startup_log "RUN_MATERIALIZEDVIEWS" "END"
    return $result
}
