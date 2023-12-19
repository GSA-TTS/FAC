source tools/util_startup.sh

function migrate_historic_tables {    
    startup_log "HISTORIC_TABLE_MIGRATION" "BEGIN"
    python manage.py migrate
    local result=$?
    startup_log "HISTORIC_TABLE_MIGRATION" "END"
    return $result
}
