#!/usr/bin/env bash

usage="
Checks droplet GUID before and after cf push to assert that the running application actually changed.
"

set -e

cfspace=$(cf target |tail -1|cut -d':' -f2|xargs)
echo "Space: ${cfspace}"
appguid=$(cf app gsa-fac --guid)
echo "GUID: ${appguid}"
curlurl="/v3/apps/${appguid}/relationships/current_droplet"
echo "curl URL: ${curlurl}"
before_data=$(cf curl "/v3/apps/${appguid}/relationships/current_droplet")
echo "Before data: ${before_data}"
before_sha=$(echo "${before_data}"|head -n 3|tail -n 1|cut -d':' -f2|xargs)
echo "Before SHA: ${before_sha}"
cf push -f backend/manifests/manifest-fac.yml --vars-file backend/manifests/vars/vars-"${cfspace}".yml --strategy rolling
after_data=$(cf curl "/v3/apps/${appguid}/relationships/current_droplet")
echo "After data: ${after_data}"
after_sha=$(echo "${after_data}"|head -n 3|tail -n 1|cut -d':' -f2|xargs)
echo "After SHA: ${after_sha}"
if [[ "${before_sha}" == "${after_sha}" ]]; then
    echo "Failed due to unchanged droplet SHA."
    exit 1
fi
