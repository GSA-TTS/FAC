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
# https://github.com/GSA-TTS/fac-periodic-scanner/archive/refs/heads/main.zip
curl -s -L https://github.com/GSA-TTS/fac-periodic-scanner/archive/"${GITREF}".zip --output "${tmpdir}/scanner-dist.zip"

# Remove the leading directory; the .zip needs to have the files at the top
cd "${tmpdir}"
unzip -o "${tmpdir}/scanner-dist.zip" > /dev/null

# To deterministically create the same .zip file every time, we want to set the
# same timestamp no matter when the files were actually checked out. So we set
# them to the time of the last commit. We do this in a subshell so that it won't
# be fatal if (for some reason) this is run outside of a git checkout. See blog
# post about this topic and solution here:
# https://zerostride.medium.com/building-deterministic-zip-files-with-built-in-commands-741275116a19
cd "${popdir}"
$(git config --global --add safe.directory /github/workspace && \
  find "${tmpdir}" -exec touch -t `git ls-files -z "${popdir}" | \
  xargs -0 -I{} -- git log -1 --date=format:"%Y%m%d%H%M" --format="%ad" {} | \
  sort -r | head -n 1` {} + && \
  git config --global --unset safe.directory /github/workspace
)

cd "${tmpdir}/fac-periodic-scanner-main" && zip -r -o -X "${popdir}/scanner.zip" ./ > /dev/null

# Tell Terraform where to find it
cat << EOF
{ "path": "scanner.zip" }
EOF
