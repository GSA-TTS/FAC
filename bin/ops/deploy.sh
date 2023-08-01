#!/usr/bin/env bash

usage="
Checks droplet GUID before and after cf push to assert that the running application actually changed.
"

set -e

cfspace=$(cf target |tail -1|cut -d':' -f2|xargs)
appguid=$(cf app gsa-fac --guid)
before_sha=$(cf curl /v3/apps/"${appguid}"/relationships/current_droplet | jq -r .data.guid)
echo "${before_sha}"
cf push -f backend/manifests/manifest-fac.yml --vars-file backend/manifests/vars/vars-"${cfspace}".yml --strategy rolling
after_sha=$(cf curl /v3/apps/"${appguid}"/relationships/current_droplet | jq -r .data.guid)
echo "${after_sha}"
if [[ "${before_sha}" == "${after_sha}" ]]; then
    exit 1
fi
