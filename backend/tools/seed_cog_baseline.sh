source tools/util_startup.sh

function seed_cog_baseline {
    startup_log "SEED_COG_BASELINE" "BEGIN"
    python manage.py seed_cog_baseline
    local result=$?
    startup_log "SEED_COG_BASELINE" "END"
    return $result
}
