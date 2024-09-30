source tools/variables.sh

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

function check_schema_exists () {
    local db_uri="$1"
    local schema_name="$2"
    local result=$(psql $db_uri -qtAX -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = '$schema_name');")
    if [ "$result" = "t" ]; then
      return 0;
    else
      return 1;
    fi
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
