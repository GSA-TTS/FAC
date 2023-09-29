#!/bin/bash

# Set basic runtime settings
echo "Environment set as: $1"
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
date=$(date '+%Y-%m-%d-%H%M')
log_file="$date"_backup_log.txt

# Collect metrics about what is currently in the db
python manage.py collect_metrics >> "$log_file"

# Backup the database
echo "Database Backup File: $1-db-backup-$date.psql.bin" >> "$log_file"
python manage.py dbbackup -o "$1-db-backup-$date.psql.bin" >&1 >> "$log_file"

# Backup the media contents
echo "Media Backup File: $1-media-backup-$date.tar" >> "$log_file"
python manage.py mediabackup -o "$1-media-backup-$date.tar" >&1 >> "$log_file"

# Upload logfile to s3://backups/logs
python manage.py fac_s3 backups --upload --src "$log_file" --tgt logs/"$log_file"

# Cleanup on disk log file
cat "$log_file"
rm "$log_file"
