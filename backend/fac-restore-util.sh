#!/bin/bash
set -e
source tools/util_startup.sh
run_option=$1
date_of_backup=$2
s3_name="fac-private-s3"
backup_s3_name="backups"
db_name="fac-db"
backup_db_name="fac-snapshot-db"
mkdir backups_tmp && cd backups_tmp || return

GetUtil() {
    local version="v0.1.0"
    curl -x "$https_proxy" -L "https://github.com/GSA-TTS/fac-backup-utility/releases/download/$version/gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz" -O
    tar -xvf gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz && rm gov.gsa.fac.cgov-util-$version-linux-amd64.tar.gz
}
InstallAWS() {
    ./gov.gsa.fac.cgov-util install_aws
}
AWSS3Sync() {
    ./gov.gsa.fac.cgov-util s3_sync --source_s3 s3://"$1"/ --dest_s3 s3://"$2"/
}
RDSToRDS() {
    ./gov.gsa.fac.cgov-util db_to_db --src_db "$1" --dest_db "$2"
}
S3ToRDSTableRestore() {
    ./gov.gsa.fac.cgov-util s3_to_db --db "$1" --s3path s3://"$2"/"$3"/
}

if [ "$run_option" == "s3_restore" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    S3ToRDSTableRestore "$db_name" "$backup_s3_name" "$date_of_backup"
    gonogo "s3_to_db"
    AWSS3Sync "$backup_s3_name" "$s3_name"
    gonogo "s3_sync"
elif [ "$run_option" == "db_restore" ]; then
    GetUtil
    InstallAWS
    gonogo "install_aws"
    RDSToRDS "$backup_db_name" "$db_name"
    gonogo "db_to_db"
    AWSS3Sync "$backup_s3_name" "$s3_name"
    gonogo "s3_sync"
fi
