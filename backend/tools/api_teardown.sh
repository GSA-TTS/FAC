source tools/util_startup.sh

function api_teardown {
    startup_log "API_TEARDOWN" "BEGIN"
    # Loop by index.
    for index in "${!teardown_scripts[@]}"
    do
      local subdir="${teardown_scripts[index]}"
      local path="dissemination/sql/api/${subdir}/teardown.sql"
      run_sql $FAC_SNAPSHOT_URI $path
    done
    startup_log "API_TEARDOWN" "END"
    return 0
}
