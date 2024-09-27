source tools/util_startup.sh

function sling_public_tables () {
    # run_sql has its own gonogo built in.
    run_sql $FAC_DB_URI 'dissemination/sql' 'sling' 'public_data_v1_0_0' 'teardown.sql'
    $SLING_EXE run -r dissemination/sql/sling/public_data_v1_0_0/public_data_v1_0_0.yaml
    local result=$?
    return $result
}
