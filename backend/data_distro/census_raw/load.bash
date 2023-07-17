#!/bin/bash

# Make sure the copy_commands file ends in a newline,
# or we will drop the last line!

if [[ $# -ne 3 ]]; then
    echo "Pass the name of the source folder and cleaned folder on the command line."
    echo "e.g. ./load.bash 20230623 CLEANED DUMP"
    exit
fi

# python repair-sql.py > tables.sql
# fac census_create_raw -f tables.sql

assume_clean_data=0
mapped_schema="mapped_schema.sql"

data_dir="$1"
cleaned_dir="$2"
rm -rf $cleaned_dir
mkdir -p $cleaned_dir
dump_dir="$3"
rm -rf $dump_dir
mkdir -p $dump_dir

if [ "$assume_clean_data" -eq 0 ];
then 
    echo "Stripping repeated headers"
    for csv in ${data_dir}/*.csv; do
        echo "Processing ${csv}"
        python strip-repeated-headers.py ${csv} ${cleaned_dir}
        python write-schema-in-order.py ${csv} ${dump_dir}
    done
fi

# Delete and create tables
#echo "Repairing tables"
#python repair-sql.py _tables.sql tables.sql
psql -d postgres -h localhost -p 5432 -U postgres -f $dump_dir/$mapped_schema

while read p; do
    if [ "$assume_clean_data" -eq 0 ];
    then
        pushd ${cleaned_dir};
    else
        pushd ${data_dir};
    fi
        echo ${p};
        psql -d postgres -h localhost -p 5432 -U postgres -c "${p}";
    popd
done < copy_commands

# Dump the resulting tables
mkdir -p ${dump_dir}/plaintext

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
