source tools/util_startup.sh

function api_standup {
    startup_log "API_STANDUP" "BEGIN"
    # Loop by index.
    for index in "${!standup_scripts[@]}"
    do
      local subdir="${standup_scripts[index]}"
      local path="dissemination/sql/api/${subdir}/standup.sql"
      run_sql $FAC_SNAPSHOT_URI $path
    done
    startup_log "API_STANDUP" "END"
    return 0
}

