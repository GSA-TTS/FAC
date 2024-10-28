source tools/util_startup.sh

function migrate_app_tables {
    startup_log "MIGRATE_APP_TABLES" "BEGIN"
    python manage.py migrate
    local result=$?
    startup_log "MIGRATE_APP_TABLES" "END"
    return $result
}
