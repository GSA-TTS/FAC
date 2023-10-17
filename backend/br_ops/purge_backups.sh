#!/usr/bin/env bash
set -e


echo "This script works only in dev amd production spaces as we take backups only in these spaces"
echo "It relies on naming conventions used in br_nackup.sh"
echo "It assumes that the S3 bucket named 'backups' has been bound"

cfspace=$(cf target |tail -1|cut -d':' -f2|xargs)
echo "Space: ${cfspace}"

if [[ "$cfspace" != "dev" && "$cfspace" != "production" ]]; then
  echo "Error: Backups may only be purged fromr dev or production"
  exit 1
fi
prefix=$(date '+%Y-%m-%d-%H%M')
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin:$PATH
python manage.py fac_s3 backups --ls | awk '{print $1}' | grep "db\-backup" | sort -r > "$prefix"_backup_list.txt

# retain 2 PR backups, 7 CRON backups and 2 non-std backups
grep "\_PR\_" "$prefix"_backup_list.txt | tail +3 > "$prefix"_purge_list.txt
grep "\_CRON\_" "$prefix"_backup_list.txt | tail +8 >> "$prefix"_purge_list.txt
grep -v -e "\_PR\_" -e "\_CRON\_" "$prefix"_backup_list.txt | tail +3 >> "$prefix"_purge_list.txt

echo "Purging backups ..."
while read line; do
  db_backup_name="$line"
  echo "DB" "$db_backup_name"
  media_backup_name=$(echo "$line" | sed -e 's/-db-backup.psql.bin/-media-backup.tar/g')
  echo "MEDIA" "$media_backup_name"
  python manage.py fac_s3 backups --rm $db_backup_name
  python manage.py fac_s3 backups --rm $media_backup_name
done < "$prefix"_purge_list.txt

rm "$prefix"_backup_list.txt "$prefix"_purge_list.txt
