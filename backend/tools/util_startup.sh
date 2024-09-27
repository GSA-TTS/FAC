declare -a public_api_versions=(
    "api_v1_0_3" 
    "api_v1_1_0" 
    "public_api_v2_0_0_alpha"
    )

declare -a admin_api_versions=(
    "admin_api_v1_1_0"
    "admin_api_v1_1_1"
    )

function startup_log {
    local tag="$1"
    local msg="$2"
    echo STARTUP $tag $msg
}

# gonogo
# helps determine if we should continue or quit
function gonogo {
  if [ $? -eq 0 ]; then
    startup_log "STARTUP_CHECK" "$1 PASS"
  else
    startup_log "STARTUP_CHECK" "$1 FAIL"
    exit -1
  fi
}

function check_table_exists() {
    local db_uri="$1"
    local dbname="$2"
    $PSQL_EXE $db_uri -c "SELECT '$dbname'::regclass"  >/dev/null 2>&1
    result=$?
    return $result
}

function run_sql () {
    local db_uri="$1"
    local base_path="$2"
    local location="$3"
    local api_version="$4"
    local sql_file="$5"

    $PSQL_EXE $db_uri < ${base_path}/${location}/${api_version}/${sql_file}
    gonogo "run_sql < ${base_path}/${location}/${api_version}/${sql_file}"
}

function run_sql_for_public_apis () {
    local location="$1"
    local sql_file="$2"
    local base_path='dissemination/sql'

    for api_version in "${public_api_versions[@]}"
    do
        if [ -f ${base_path}/${location}/${api_version}/${sql_file} ]; then
          # $PSQL_EXE $FAC_DB_URI < ${base_path}/${location}/${api_version}/${sql_file}
          run_sql $FAC_DB_URI $base_path $location $api_version $sql_file
        else
          echo "API FILE NOT FOUND/SKIPPED ${location}/${api_version}/${sql_file}"
        fi
      done
  
    # for api_version in "${admin_api_versions[@]}"
    # do
    #     echo "VERSION $api_version"
    #     if [ -f ${base_path}/${location}/${api_version}/${sql_file} ]; then
    #       $PSQL_EXE $FAC_DB_URI < ${base_path}/${location}/${api_version}/${sql_file}
    #       gonogo "psql < ${location}/${api_version}/${sql_file}"
    #     else
    #       echo "API FILE NOT FOUND/SKIPPED ${location}/${api_version}/${sql_file}"
    #     fi
    #   done
}
