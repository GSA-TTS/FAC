#!/bin/sh

# Exit if any step fails
set -e

popdir=$(pwd)
eval "$(jq -r '@sh "GITREF=\(.gitref)"')"

# Portable construct so this will work everywhere
# https://unix.stackexchange.com/a/84980
tmpdir=$(mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir')
cd "${tmpdir}"

# Grab a copy of the zip file for the specified ref
# https://github.com/GSA-TTS/cg-logshipper/archive/refs/heads/main.zip
curl -s -L https://github.com/GSA-TTS/cg-logshipper/archive/"${GITREF}".zip --output "${tmpdir}/logshipper-dist.zip"

# Remove the leading directory; the .zip needs to have the files at the top
cd "${tmpdir}"
unzip -o "${tmpdir}/logshipper-dist.zip" > /dev/null
cat "${popdir}/fluentbit_config/fluentbit.conf" > "${tmpdir}/cg-logshipper-main/fluentbit.conf"
cd "${tmpdir}/cg-logshipper-main" && zip -r -o "${popdir}/logshipper.zip" ./ > /dev/null

# Tell Terraform where to find it
cat << EOF
{ "path": "logshipper-dist.zip" }
EOF
