#!/bin/bash

export CGOV_UTIL_VERSION=v0.1.8
export FAC_DB_URI=postgresql://postgres@db:5432/postgres?sslmode=disable
export FAC_SNAPSHOT_URI=postgresql://postgres@db2:5432/postgres?sslmode=disable


function check_table_exists() {
    local db_uri="$1"
    local dbname="$2"
    psql $db_uri -c "SELECT '$dbname'::regclass"  >/dev/null 2>&1
    result=$?
    return $result
}

echo "This will unzip ~3.3GB of data, and load it into a local FAC."
echo "Make sure the FAC is running."
echo "Make sure you have disk space."
echo "Sleeping for 4 seconds..."
sleep 4

# First, we cleanup the local filesystem.
# This removes any temporary files from any
# previous data loads
rm -f /app/data/db_dissem_dump
rm -rf /app/data/__MACOSX

# # Next, we drop the public_data schema.
# # This is because we want to make sure it is
# # regenerated fresh.
# psql $FAC_SNAPSHOT_URI -c "DROP SCHEMA IF EXISTS public_data_v1_0_0 CASCADE"

# # Now, the schema for the public_data is
# # created. This provies a place for the tables to
# # land when we run sling
# psql $FAC_SNAPSHOT_URI -c "CREATE SCHEMA IF NOT EXISTS public_data_v1_0_0"
# psql $FAC_SNAPSHOT_URI -c "CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_combined START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE"

# Unzip the compressed historical data dump.
pushd /app/data
echo "Unzipping data."
unzip db_dissem_dump.zip
popd

# Truncate the dissemination_* tables if they exist. 
# CASCADE as well. This makes sure we don't duplicate data,
# which causes PK/FK problems.
echo "select 'TRUNCATE TABLE '||tablename||' CASCADE;' FROM pg_tables WHERE tablename LIKE 'dissemination_%'" | \
    psql $FAC_DB_URI -t | \
    psql $FAC_DB_URI

# Load the large historic dataset.
psql $FAC_DB_URI -v ON_ERROR_STOP=on < /app/data/db_dissem_dump
result=$?
if [ $result -ne 0 ]; then
    echo "Something went wrong."
    exit -1
else
    echo "Loaded lots of data without error, apparently."
fi

# We'll stop here. Now, on first boot, the FAC should see if things are
# in place in DB2. If not, the app startup process will take
# care of creating new tables, etc.

# # Download cgov-util.
# # This will let us do a backup from the main database (fac-db)
# # to the secondary database (fac-snapshot-db). This mirrors what
# # happens in production.
# pushd /app/data

# Run the backup of the dissemination_ tables from
# fac-db to fac-snapshot-db.
check_table_exists $FAC_SNAPSHOT_URI "public" "dissemination_general"
result=$?
# cgov-util wants to know the environment it is in.
export ENV="LOCAL"
if [ $result -ne 0 ]; then
    # First run if it does not exist.
    /layered/cgov-util db_to_db \
        --src_db fac-db \
        --dest_db fac-snapshot-db \
        --operation initial
else
    /layered/cgov-util db_to_db \
        --src_db fac-db \
        --dest_db fac-snapshot-db \
        --operation backup
fi

# # Now, we're going to run sling.
# # This will create the API tables. It essentially does a copy of
# # data from fac-snapshot-db (in the dissem_* tables) to a set of 
# # tables that the API will point at. 
# sling run -r /layered/sling.yaml
# sling run -r /layered/tribal_sling.yaml
