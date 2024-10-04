source tools/util_startup.sh

function api_teardown {
    startup_log "API_TEARDOWN" "BEGIN"
    local base_path='dissemination/sql'
    local location='api'
    local sql_file='teardown.sql'

    # The API now relies on actual tables.
    # We can tear down the API safely, because we're tearing down
    # just the permissions at this point. That is, we're tearing down
    # the API portion. The data will remain in the DB.

    for index in "${!api_versions[@]}"
    do
      local api_version="${api_versions[index]}"      
      if [ -f ${base_path}/${location}/${api_version}/${sql_file} ]; then
          run_sql $FAC_SNAPSHOT_URI $base_path $location $api_version $sql_file
          gonogo "$api_version teardown.sql"
      else
        echo "API FILE NOT FOUND/SKIPPED ${location}/${api_version}/${sql_file}"
      fi
    done

    startup_log "API_TEARDOWN" "END"
    
    # If these are both zero, we're all good.
    return 0
}
