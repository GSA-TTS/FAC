#!/bin/bash
set -e
source tools/util_startup.sh
source tools/setup_env.sh
setup_env
version=$1
run_option=$2
s3_name="fac-private-s3"
backup_s3_name="backups"
db_name="fac-db"
backup_db_name="fac-snapshot-db"
initial_date=$(date +%Y%m%d%H%M)
scheduled_date=$(date +%m-%d-%H)
daily_date=$(date +%m-%d)
mkdir tmp && cd tmp || return

GetUtil() {
    curl -x "$https_proxy" -L "https://github.com/GSA-TTS/fac-backup-utility/releases/download/$version/gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz" -O
    tar -xvf "gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz" && rm "gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz"
}
InstallAWS() {
    ./gov.gsa.fac.cgov-util install_aws
}
AWSS3Sync() {
    ./gov.gsa.fac.cgov-util s3_sync --source_s3 s3://"$1"/ --dest_s3 s3://"$2"/
}
RDSToS3Dump() {
    ./gov.gsa.fac.cgov-util db_to_s3 --db "$1" --s3path s3://"$2"/"$3"/
}
RDSToRDS() {
    ./gov.gsa.fac.cgov-util db_to_db --src_db "$1" --dest_db "$2" --operation "$3"
}
CheckTables() {
    ./gov.gsa.fac.cgov-util check_db --db "$1"
}
RowCount() {
    ./gov.gsa.fac.cgov-util row_count --db "$1"
}

if [ "$run_option" == "initial_backup" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    RDSToS3Dump "$db_name" "$backup_s3_name" "initial/$initial_date"
    gonogo "db_to_s3"
    RDSToRDS "$db_name" "$backup_db_name" "initial"
    gonogo "db_to_db"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "deploy_backup" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    RDSToRDS "$db_name" "$backup_db_name" "backup"
    gonogo "db_to_db"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "scheduled_backup" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    RDSToS3Dump "$db_name" "$backup_s3_name" "scheduled/$scheduled_date"
    gonogo "db_to_s3"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "daily_backup" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    RDSToS3Dump "$db_name" "$backup_s3_name" "daily/$daily_date"
    gonogo "db_to_s3"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "media_sync" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    AWSS3Sync "$s3_name" "$backup_s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "check_tables" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    CheckTables "$db_name"
    gonogo "check_tables"
    RowCount "$db_name"
    gonogo "row_count"
fi
