#!/bin/bash

# Set basic runtime settings
echo "dbbackup name: $1"
echo "mediabackup name: $2"
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
date=$(date '+%Y-%m-%d-%H%M')
log_file="$date"_restore_log.txt

# Restore the database
echo "Database Backup File: $1" >> "$log_file"
python manage.py dbrestore -i "$1" --noinput

# Restore the media contents
echo "Media Backup File: $2" >> "$log_file"
python manage.py mediarestore -i "$2" --noinput

# Collect metrics about what is currently in the db after restore
python manage.py collect_metrics >> "$log_file"

# Upload logfile to s3://backups/logs
python manage.py fac_s3 backups --ls --tgt "$date" >> "$log_file"
python manage.py fac_s3 backups --upload --src "$log_file" --tgt logs/"$log_file"

# Cleanup on disk log file
cat "$log_file"
rm "$log_file"
