#!/bin/sh

# Exit if any step fails
set -e

# Comment out the above and use this to see what the script does
# set -ex

eval "$(jq -r '@sh "GITREF=\(.gitref)"')"

# Useful for debugging the script. Comment out the eval if running for debugging purposes
# GITREF="refs/heads/<branch-name>"

popdir=$(pwd)

# Portable construct so this will work everywhere
# https://unix.stackexchange.com/a/84980
tmpdir=$(mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir')
cd "$tmpdir"

# Grab a copy of the zip file for the specified ref
curl -s -L "https://github.com/gsa-tts/fac/archive/${GITREF}.zip" --output local.zip
branch=$(echo "$GITREF" | cut -f3 -d"/")

# Zip up just the FAC-main/ subdirectory for pushing
# Before zip stage, run [ npm ci --production | npm run build ] in /backend/ to get the compiled assets for the site in /static/compiled/
unzip -q -u local.zip \*"FAC-$branch/backend/*"\*
cd "${tmpdir}/FAC-$branch/backend/" &&
npm ci --production --silent &&
npm run build > '/dev/null' 2>&1 &&
zip -r -o -X "${popdir}/app.zip" ./ > /dev/null
# zip -q -j -r ${popdir}/app.zip fac-*/backend

# Tell Terraform where to find it
cat << EOF
{ "path": "app.zip" }
EOF
