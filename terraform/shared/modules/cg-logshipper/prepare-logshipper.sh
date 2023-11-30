#!/bin/sh

# Exit if any step fails
set -e

popdir=$(pwd)

eval "$(jq -r '@sh "GITREF=\(.gitref)"')"

# Portable construct so this will work everywhere
# https://unix.stackexchange.com/a/84980
tmpdir=$(mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir')
cd "$tmpdir"

# Grab a copy of the zip file for the specified ref
# https://github.com/GSA-TTS/cg-logshipper/archive/refs/heads/main.zip
curl -s -L https://github.com/GSA-TTS/cg-logshipper/archive/${GITREF}.zip --output "${popdir}/logshipper.zip"

# Tell Terraform where to find it
cat << EOF
{ "path": "logshipper.zip" }
EOF
