#!/bin/sh

# Exit if any step fails
set -e

# Zip up a staticfile client app 
zip -q -j -r ./client.zip app

cat << EOF
{
  "path": "client.zip",
  "buildpacks": "staticfile_buildpack"
}
EOF

