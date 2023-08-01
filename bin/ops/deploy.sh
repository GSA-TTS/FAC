#!/usr/bin/env bash

usage="
Checks droplet GUID before and after cf push to assert that the running application actually changed.
"

set -e

cfspace=$(cf target |tail -1|cut -d':' -f2|xargs)
appguid=$(cf app gsa-fac --guid)
before_sha=$(cf curl "/v3/apps/${appguid}/relationships/current_droplet"|head -n 3|tail -n 1|cut -d':' -f2|xargs)
echo "${before_sha}"
echo cf push -f backend/manifests/manifest-fac.yml --vars-file backend/manifests/vars/vars-"${cfspace}".yml --strategy rolling
after_sha=$(cf curl "/v3/apps/${appguid}/relationships/current_droplet"|head -n 3|tail -n 1|cut -d':' -f2|xargs)
echo "${after_sha}"
if [[ "${before_sha}" == "${after_sha}" ]]; then
    echo "Failed due to unchanged droplet SHA."
    exit 1
fi
