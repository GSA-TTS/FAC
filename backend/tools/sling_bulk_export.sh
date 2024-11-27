source tools/util_startup.sh

function sling_bulk_export() {
    startup_log "SLING_BULK_EXPORT" "Slinging data CSVs"

    SLING_ALLOW_EMPTY=1
    $SLING_EXE run -r dissemination/sql/sling/bulk_data_export/public_data_v1_0_0_single_csv.yaml
    gonogo "sling_bulk_export"

    startup_log "SLING_BULK_EXPORT" "Done"
    return 0
}
