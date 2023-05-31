#!/bin/sh

# Exit if any step fails
set -e

# To deterministically create the same .zip file every time, we want to set the
# same timestamp no matter when the files were actually checked out. So we set
# them to the time of the last commit. We do this in a subshell so that it won't
# be fatal if (for some reason) this is run outside of a git checkout. See blog
# post about this topic and solution here:
# https://zerostride.medium.com/building-deterministic-zip-files-with-built-in-commands-741275116a19
$(git config --global --add safe.directory /github/workspace && \
  find app -exec touch -t `git ls-files -z app | \
  xargs -0 -n1 -I{} -- git log -1 --date=format:"%Y%m%d%H%M" --format="%ad" {} | \
  sort -r | head -n 1` {} + && \
  git config --global --unset safe.directory /github/workspace
)

zip -q -j -r proxy.zip app

# Tell Terraform where to find it
cat << EOF
{ "path": "proxy.zip" }
EOF

