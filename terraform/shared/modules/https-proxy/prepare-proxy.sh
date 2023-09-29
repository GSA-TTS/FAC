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
curl -s -L https://github.com/GSA-TTS/cg-egress-proxy/archive/${GITREF}.zip --output local.zip 

# Zip up just the proxy/ subdirectory for pushing
unzip -q -u local.zip \*/proxy/\*
zip -q -j -r ${popdir}/proxy.zip cg-egress-proxy-*/proxy

# Tell Terraform where to find it
cat << EOF
{ "path": "proxy.zip" }
EOF

