#!/bin/bash
set -e

# Make sure we get the right number of arguments to the
# bash script. I don't want to make a mess of my filesystem
# or my Minio bucket, if I can avoid it.
if [ "$#" -ne 2 ]; 
  then
    echo "Pass two arguments."
    echo "  The first is a directory containing Census CSVs"
    echo "  The second is the destination path in the bucket"
    exit
fi

# We are using this bucket in our production code, and
# it gets created automatically in Minio. So.
BUCKET_NAME="fac-c2g-s3"

# I want to know the filenames in advance.
# If the filenames don't have these names, 
# then I don't want to load them.

declare -a arr=(\
    "ELECAUDITFINDINGS" \
    "ELECAUDITHEADER" \
    "ELECAUDITS" \
    "ELECCAPTEXT" \
    "ELECCPAS" \
    "ELECEINS" \
    "ELECFINDINGSTEXT" \
    "ELECNOTES" \
    "ELECPASSTHROUGH" \
    "ELECUEIS")

# For convenience
fac ()
{
  docker compose run web python manage.py ${@}
}

# Cleanup the parameters passed in. Get rid of trailing slashes.
LOCAL_DIRECTORY=$(echo "$1" | sed 's:/*$::')
DESTINATION_PATH=$(echo "$2" | sed 's:/*$::')

# Use the Minio client to set up a local alias.
mc alias set local http://localhost:9001 minioadmin minioadmin

# First, load the CSVs into the Minio instance.
for file in `ls $LOCAL_DIRECTORY/*.csv`
do
  # Get rid of the path to the file
  just_filename="$(basename -- $file)"
  echo "Copying $just_filename into Minio at the path $DESTINATION_PATH"
  # Copy the file into our bucket at the destination path requested
  mc cp "$file" "local/$BUCKET_NAME/$DESTINATION_PATH/$just_filename"
done

# https://stackoverflow.com/questions/8880603/loop-through-an-array-of-strings-in-bash
for file in "${arr[@]}"
do
  echo "Running load_csv_from_s3 on $LOCAL_DIRECTORY/$file.csv"
  # Run the Django command to load each CSV in S3 into the PG DB.
  # This should work just as well in production.
  fac load_csv_from_s3 --bucket $BUCKET_NAME --object "$DESTINATION_PATH/$file.csv"
done
