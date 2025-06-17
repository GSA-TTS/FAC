#!/bin/sh

# Exit if any step fails
set -e

# Comment out the above and use this to see what the script does
#set -ex

# eval "$(jq -r '@sh "GITREF=\(.gitref)"')"

# Useful for debugging the script. Comment out the eval if running for debugging purposes
# GITREF="refs/heads/<branch-name>"

popdir=$(pwd)

# Portable construct so this will work everywhere
# https://unix.stackexchange.com/a/84980
tmpdir=$(mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir')
cd "$tmpdir"

# Grab a copy of the jar file for the specified ref
curl -s -L "https://downloads.metabase.com/v0.55.3.x/metabase.jar" -o "metabase.jar"
cp "$popdir/.profile" .
zip -r -o -X "${popdir}/app.zip" metabase.jar .profile > /dev/null

# Tell Terraform where to find it
cat << EOF
{ "path": "app.zip" }
EOF
