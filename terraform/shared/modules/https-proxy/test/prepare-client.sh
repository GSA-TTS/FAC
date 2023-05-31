#!/bin/sh

# Exit if any step fails
set -e

# Zip up a staticfile client app 
zip -q -j -r ./client.zip index.html .profile

# Tell Terraform where to find it
cat << EOF
{ 
  "path": "client.zip",
  "buildpack": "staticfile_buildpack" 
}
EOF

