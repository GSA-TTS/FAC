#!/bin/bash

# Set basic runtime settings
echo "Restoring from env: $1"
echo "Restoring backup type: $2"
echo "Restoring backup dated: $3"
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
date=$(date '+%Y-%m-%d-%H%M')
prefix="$date"_"$2"_"$1"
log_file="$prefix"_restore_log.txt
prefix="$3"_"$2"_"$1"

# Restore the database
echo "Database Backup File: "$prefix"-db-backup.psql.bin" >> "$log_file"
python manage.py dbrestore -i "$prefix"-db-backup.psql.bin --noinput >&1 >> "$log_file"

# Restore the media contents
echo "Media Backup File: "$prefix"-media-backup.tar >> "$log_file"
python manage.py mediarestore -i "$prefix"-media-backup.tar --noinput >&1 >> "$log_file"

# Collect metrics about what is currently in the db after restore
python manage.py collect_metrics >> "$log_file"

# Upload logfile to s3://backups/logs
python manage.py fac_s3 backups --upload --src "$log_file" --tgt logs/"$log_file"

# Cleanup on disk log file
cat "$log_file"
rm "$log_file"
