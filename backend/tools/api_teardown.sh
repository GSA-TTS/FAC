source tools/util_startup.sh

function teardown_public_tables () {
    run_sql $FAC_DB_URI 'dissemination/sql' 'sling' 'public_data_v1_0_0' 'teardown.sql'
    return 0
}

function standup_public_table_placeholders () {
    # run_sql has its own gonogo built in.
    # $SLING_EXE run -r dissemination/sql/sling/public_data_v1_0_0/public_data_v1_0_0.yaml
    run_sql $FAC_DB_URI 'dissemination/sql' 'sling' 'public_data_v1_0_0' 'standup.sql'
    return 0
}

function run_sql_for_public_apis () {
    local location="$1"
    local sql_file="$2"
    local base_path='dissemination/sql'
    local location='api'

    for api_version in "${public_api_versions[@]}"
    do
        if [ -f ${base_path}/${location}/${api_version}/${sql_file} ]; then
          # $PSQL_EXE $FAC_DB_URI < ${base_path}/${location}/${api_version}/${sql_file}
          run_sql $FAC_DB_URI $base_path $location $api_version $sql_file
        else
          echo "API FILE NOT FOUND/SKIPPED ${location}/${api_version}/${sql_file}"
        fi
      done
  
}



function api_teardown {
    startup_log "API_TEARDOWN" "BEGIN"
    local base_path='dissemination/sql'
    local location='api'
    local sql_file='teardown.sql'

    # The API now relies on actual tables.
    # We can tear down the API safely, because we're tearing down
    # just the permissions at this point. That is, we're tearing down
    # the API portion. The data will remain in the DB.

    #run_sql_for_public_apis 'api' 'teardown.sql'
    for api_version in "${public_api_versions[@]}"
    do
        if [ -f ${base_path}/${location}/${api_version}/${sql_file} ]; then
            # $PSQL_EXE $FAC_DB_URI < ${base_path}/${location}/${api_version}/${sql_file}
            run_sql $FAC_DB_URI $base_path $location $api_version $sql_file
            gonogo "$api_version teardown.sql"
        else
          echo "API FILE NOT FOUND/SKIPPED ${location}/${api_version}/${sql_file}"
        fi
    done

    startup_log "API_TEARDOWN" "END"
    
    # If these are both zero, we're all good.
    return 0
}
