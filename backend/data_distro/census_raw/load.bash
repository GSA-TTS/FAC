#!/bin/bash

# Make sure the copy_commands file ends in a newline,
# or we will drop the last line!

if [[ $# -eq 0 ]]; then
    echo "Pass the name of the source folder and cleaned folder on the command line."
    echo "e.g. ./load.bash 20230623 CLEANED DUMP"
    exit
fi

# python repair-sql.py > tables.sql
# fac census_create_raw -f tables.sql

data_dir="$1"
cleaned_dir="$2"
dump_dir="$3"

echo "Stripping repeated headers"
for csv in ${data_dir}/*.csv; do
    echo "Processing ${csv}"
    python strip-repeated-headers.py ${csv} ${cleaned_dir}
done

# Delete and create tables
echo "Repairing tables"
python repair-sql.py _tables.sql tables.sql
psql -d postgres -h localhost -p 5432 -U postgres -f tables.sql

while read p; do
    pushd ${cleaned_dir};
        echo ${p};
        psql -d postgres -h localhost -p 5432 -U postgres -c "${p}";
    popd
done < copy_commands

# Dump the resulting tables
mkdir -p ${dump_dir}/plaintext
mkdir -p ${dump_dir}/compressed

for table in `cat dump_tables`; do
    echo Dumping $table as plaintext
    pg_dump \
        --no-owner \
        --schema=public \
        --dbname="postgres://postgres@localhost:5432/postgres" \
        --format=plain \
        --file=${dump_dir}/plaintext/${table}.sql \
        --table="public.\"${table}\"" 
done

for table in `cat dump_tables`; do
    echo Dumping $table as compressed
    pg_dump \
        --no-owner \
        --schema=public \
        -Fc \
        -Z 9 \
        --dbname="postgres://postgres@localhost:5432/postgres" \
        --format=plain \
        --file=${dump_dir}/compressed/${table}.dump \
        --table="public.\"${table}\"" 
done

