source tools/util_startup.sh


function api_standup {
    startup_log "API_STANDUP" "BEGIN"
    local base_path='dissemination/sql'
    local location='api'

    # This loops by index, so we can use two arrays.
    # public_api_versions and public_api_required_tables
    for index in "${!api_versions[@]}"
    do
        local api_version="${api_versions[index]}"
        local required_table="${api_required_tables[index]}"
        # If the file to stand up the API exists...
        if [ -f ${base_path}/${location}/${api_version}/standup.sql ]; then
            check_table_exists $FAC_SNAPSHOT_URI $required_table
            local result=$?
            echo "check_table_exists $required_table $result"
            if [ $result -eq 0 ]; then
                run_sql $FAC_SNAPSHOT_URI $base_path $location $api_version 'standup.sql'
                gonogo "$api_version standup.sql"
            else 
                echo "API TABLE NOT FOUND/SKIPPED $required_table not found for $api_version"
            fi
        else
          echo "API FILE NOT FOUND/SKIPPED dissemination/sql/api/${api_version}/standup.sql"
        fi
    done
    
    startup_log "API_STANDUP" "END"

    return 0
}

