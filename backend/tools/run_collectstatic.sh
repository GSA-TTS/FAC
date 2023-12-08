source tools/util_startup.sh

function run_collectstatic {
    startup_log "RUN_COLLECTSTATIC" "BEGIN"
    python manage.py collectstatic --noinput &&
    local result=$?
    startup_log "RUN_COLLECTSTATIC" "END"
    return $result
}
