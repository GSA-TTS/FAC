#####
# CREATE STAFF USERS
# Prepares staff users for Django admin
source tools/util_startup.sh

function create_staffusers {
    startup_log "CREATE_STAFFUSERS" "BEGIN"
    python manage.py create_staffusers
    startup_log "CREATE_STAFFUSERS" "END"
}
