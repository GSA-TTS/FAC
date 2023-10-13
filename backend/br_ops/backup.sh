#!/bin/bash

# Set basic runtime settings
echo "Environment set as: $1"
echo "Backup type: $2"

export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
date=$(date '+%Y-%m-%d-%H%M')
prefix="$date"_"$2"_"$1"
log_file="$prefix"_backup_log.txt

# Collect metrics about what is currently in the db
python manage.py collect_metrics >> "$log_file"

# Backup the database
echo "Database Backup File: "$prefix"-db-backup.psql.bin >> "$log_file"
python manage.py dbbackup -o "$prefix"-db-backup.psql.bin >&1 >> "$log_file"

# Backup the media contents
echo "Media Backup File: "$prefix"-media-backup.tar >> "$log_file"
python manage.py mediabackup -o "$prefix"-media-backup.tar >&1 >> "$log_file"

# Upload logfile to s3://backups/logs
python manage.py fac_s3 backups --upload --src "$log_file" --tgt logs/"$log_file"

# Cleanup on disk log file
cat "$log_file"
rm "$log_file"
