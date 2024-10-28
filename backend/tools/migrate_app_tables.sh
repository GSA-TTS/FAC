source tools/util_startup.sh

function migrate_app_tables {
    startup_log "MIGRATE_APP_TABLES" "BEGIN"
    # python manage.py migrate
    python manage.py migrate --fake audit
    local result=$?
    startup_log "MIGRATE_APP_TABLES" "END"
    return $result
}
