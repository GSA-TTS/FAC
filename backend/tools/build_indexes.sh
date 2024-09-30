source tools/util_startup.sh

function build_indexes {
    startup_log "BUILD INDEXES" "BEGIN"
    local base_path='dissemination/sql'
    local location='indexes'
    local which_db='fac-snapshot-db'
    # This loops by index, so we can use two arrays.
    for index in "${!db2_indexes[@]}"
    do
        local dbindex="${db2_indexes[index]}"
        local required_table="${db2_indexes_required_tables[index]}"
        # If the file to stand up the API exists...
        if [ -f ${base_path}/${location}/$which_db/${dbindex}.sql ]; then
            check_table_exists $FAC_SNAPSHOT_URI $required_table
            local result=$?
            echo "check_table_exists $required_table $result"
            if [ $result -eq 0 ]; then
                run_sql $FAC_SNAPSHOT_URI $base_path $location $which_db ${dbindex}.sql
                gonogo "${dbindex}"
            else 
                echo "API TABLE NOT FOUND/SKIPPED $required_table not found for $dbindex"
            fi
        else
          echo "API FILE NOT FOUND/SKIPPED ${base_path}/${location}/$which_db/${dbindex}.sql"
        fi
    done
    startup_log "BUILD INDEXES" "END"
}
