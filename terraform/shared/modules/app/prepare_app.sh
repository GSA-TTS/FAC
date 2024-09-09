#!/bin/sh

# Exit if any step fails
set -e

eval "$(jq -r '@sh "GITREF=\(.gitref)"')"

popdir=$(pwd)

# Portable construct so this will work everywhere
# https://unix.stackexchange.com/a/84980
tmpdir=$(mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir')
cd "$tmpdir"

# Grab a copy of the zip file for the specified ref
curl -s -L https://github.com/gsa-tts/fac/archive/${GITREF}.zip --output local.zip

# Zip up just the FAC-main/ subdirectory for pushing
unzip -q -u local.zip \*"FAC-main/backend/*"\*
cd "${tmpdir}/FAC-main/backend/" && zip -r -o -X "${popdir}/app.zip" ./ > /dev/null
# zip -q -j -r ${popdir}/app.zip fac-*/backend

# Tell Terraform where to find it
cat << EOF
{ "path": "app.zip" }
EOF

