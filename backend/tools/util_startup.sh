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
    return 0
  else
    startup_log "STARTUP_CHECK" "$1 FAIL"
    exit -1
  fi
}

function check_table_exists() {
    local db_uri="$1"
    local dbname="$2"
    echo "CHECK_TABLE_EXISTS: $dbname"
    # >/dev/null 2>&1
    $PSQL_EXE $db_uri -c "SELECT '$dbname'::regclass"  
    result=$?
    echo "CHECK_TABLE_EXISTS $dbname: $result"
    return $result
}

function check_schema_exists () {
    local db_uri="$1"
    local schema_name="$2"
    echo "CHECK_SCHEMA_EXISTS $schema_name"
    local result=$($PSQL_EXE $db_uri -qtAX -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = '$schema_name');")
    echo "CHECK_SCHEMA_EXISTS $schema_name: $result"
    if [ "$result" = "t" ]; then
      return 0;
    else
      return 1;
    fi
}

function run_sql () {
    local db_uri="$1"
    local path="$2"
    echo "BEGIN run_sql < $path"
    $PSQL_EXE $db_uri < $path
    gonogo "GONOGO run_sql < $path"
}
