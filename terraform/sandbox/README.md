### WIP Readme
`cd terraform/sandbox/`
` ../../bin/ops/create_service_account.sh -o sandbox-gsa -s <firstname.lasname> -u <username>-workspace-deployer > secrets.auto.tfvars`
The script will output the `username` (as `cf_user`) and `password` (as `cf_password`) for your `<ACCOUNT_NAME>`. Read more in the [cloud.gov service account documentation](https://cloud.gov/docs/services/cloud-gov-service-account/).

`cf create-service s3 basic workspace-terraform-state`
`cf create-service-key <key-name> workspace-terraform-state`
`cf service-key workspace-terraform-state <key-name>`
Copy `access_key_id`, `secret_access_key`, `bucket`, `region` and `endpoint` values into `shared/condig/sandbox.tfvars`

Make sure to have CF CLI on WSL2 Ubuntu
```
# ...first add the Cloud Foundry Foundation public key and package repository to your system
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
# ...then, update your local package index, then finally install the cf CLI
sudo apt-get update
sudo apt-get install cf8-cli
```
