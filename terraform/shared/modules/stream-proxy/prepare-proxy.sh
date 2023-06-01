#!/bin/sh

# Exit if any step fails
set -e
zip -q -j -r proxy.zip app

# Tell Terraform where to find it
cat << EOF
{ "path": "proxy.zip" }
EOF

