#!/bin/bash

export CGOV_UTIL_VERSION=v0.1.8
export FAC_DB_URI=postgresql://postgres@localhost:5432/postgres?sslmode=disable
export FAC_SNAPSHOT_URI=postgresql://postgres@localhost:5431/postgres?sslmode=disable


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

echo <<EOM
First, we cleanup the local filesystem.
This removes any temporary files from any
previous data loads
EOM
rm -f db_dissem_dump
rm -rf __MACOSX

echo <<EOM
Next, we drop the public_data schema.
This is because we want to make sure it is
regenerated fresh.
EOM
psql $FAC_SNAPSHOT_URI -c "DROP SCHEMA IF EXISTS public_data_v1_0_0 CASCADE"

echo <<EOM
Now, the schema for the public_data is
created. This provies a place for the tables to
land when we run `sling`
EOM
psql $FAC_SNAPSHOT_URI -c "CREATE SCHEMA IF NOT EXISTS public_data_v1_0_0"
psql $FAC_SNAPSHOT_URI -c "CREATE SEQUENCE IF NOT EXISTS public_data_v1_0_0.seq_combined START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE"

echo <<EOM
Unzip the compressed historical data dump.
EOM
unzip db_dissem_dump.zip

echo <<EOM
Truncate the dissemination_ tables if they exist. 
CASCADE as well. This makes sure we don't duplicate data,
which causes PK/FK problems.
EOM 
echo "select 'TRUNCATE TABLE '||tablename||' CASCADE;' FROM pg_tables WHERE tablename LIKE 'dissemination_%'" | \
    psql $FAC_DB_URI -t | \
    psql $FAC_DB_URI

echo <<EOM
Load the large historic dataset.
EOM
psql $FAC_DB_URI -v ON_ERROR_STOP=on < db_dissem_dump
result=$?

if [ $result -ne 0 ]; then
    echo "Something went wrong."
    exit -1
else
    echo "Loaded lots of data without error, apparently."
fi

echo <<EOM
Download cgov-util.
This will let us do a backup from the main database (fac-db)
to the secondary database (fac-snapshot-db). This mirrors what
happens in production.
EOM
curl -L -O https://github.com/GSA-TTS/fac-backup-utility/releases/download/${CGOV_UTIL_VERSION}/gov.gsa.fac.cgov-util-v0.1.8-linux-amd64.tar.gz
tar xvzf gov.gsa.fac.cgov-util-${CGOV_UTIL_VERSION}-linux-amd64.tar.gz
chmod 755 gov.gsa.fac.cgov-util
curl -L -O https://raw.githubusercontent.com/GSA-TTS/fac-backup-utility/refs/heads/main/config.json

echo <<EOM
Run the backup of the dissemination_ tables from
fac-db to fac-snapshot-db.
EOM
check_table_exists $FAC_SNAPSHOT_URI "public.dissemination_general"
result=$?
if [ $result -ne 0 ]; then
    # First run if it does not exist.
    ./gov.gsa.fac.cgov-util db_to_db \
        --src_db fac-db \
        --dest_db fac-snapshot-db \
        --operation initial
else
    ./gov.gsa.fac.cgov-util db_to_db \
        --src_db fac-db \
        --dest_db fac-snapshot-db \
fi

echo <<EOM
Now, we're going to run `sling`.
This will create the API tables. It essentially does a copy of
data from fac-snapshot-db (in the dissem_* tables) to a set of 
tables that the API will point at. 
EOM
sling run -r ../../backend/dissemination/sql/sling/public_data_v1_0_0/public_data_v1_0_0.yaml

exit 0
